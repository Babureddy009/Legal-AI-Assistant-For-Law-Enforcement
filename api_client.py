import requests
import json
import uuid
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class RasaClient:
    def __init__(self, base_url="http://localhost:5005"):
        self.base_url = base_url
        self.sessions = {}
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4 seconds between retries
            status_forcelist=[500, 502, 503, 504]  # HTTP status codes to retry on
        )
        
        # Create a session with the retry strategy
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def send_message(self, message, session_id=None):
        """
        Send a message to Rasa and get the response
        """
        if not session_id:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = True

        url = f"{self.base_url}/webhooks/rest/webhook"
        payload = {
            "sender": session_id,
            "message": message
        }

        try:
            # Try to connect to the server
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            # Process the response
            data = response.json()
            if not data:
                return [{"type": "error", "text": "No response received from the server."}]
            
            # Format the response
            formatted_response = []
            for item in data:
                if "text" in item:
                    formatted_response.append({
                        "type": "bot_message",
                        "text": item["text"]
                    })
                elif "error" in item:
                    formatted_response.append({
                        "type": "error",
                        "text": item["error"]
                    })
            
            return formatted_response if formatted_response else [{"type": "error", "text": "No valid response received."}]
            
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: Could not connect to Rasa server at {self.base_url}")
            return [{"type": "error", "text": "Could not connect to the server. Please make sure the Rasa server is running."}]
        except requests.exceptions.Timeout as e:
            print(f"Timeout error: Request to Rasa server timed out")
            return [{"type": "error", "text": "Request timed out. Please try again."}]
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Rasa: {str(e)}")
            return [{"type": "error", "text": f"Error communicating with the server: {str(e)}"}]
        except json.JSONDecodeError as e:
            print(f"Error parsing response: {str(e)}")
            return [{"type": "error", "text": "Invalid response from server."}]
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return [{"type": "error", "text": "An unexpected error occurred."}]

    def get_tracker(self, session_id):
        """
        Get the conversation tracker for a specific session
        """
        if not session_id or session_id not in self.sessions:
            return None

        url = f"{self.base_url}/conversations/{session_id}/tracker"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting tracker: {str(e)}")
            return None

# Example usage:
if __name__ == "__main__":
    client = RasaClient()
    response = client.send_message("What is murder?")
    print(json.dumps(response, indent=2)) 