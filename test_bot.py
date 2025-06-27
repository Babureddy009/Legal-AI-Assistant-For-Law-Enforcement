import requests
import json

def send_message(message):
    url = "http://localhost:5005/webhooks/rest/webhook"
    payload = {
        "sender": "user",
        "message": message
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        return []

def test_queries():
    # Test queries covering different aspects of the legal system
    test_queries = [
        "what is the punishment for murder?",
        "tell me about IPC section 302",
        "what is theft?",
        "what is the punishment for robbery?",
        "explain IPC section 304",
        "what are the laws about assault?"
    ]
    
    print("Testing the Legal AI Assistant...\n")
    for query in test_queries:
        print(f"\nUser: {query}")
        response = send_message(query)
        if response:
            for message in response:
                print(f"Bot: {message.get('text', '')}")
        else:
            print("Bot: Sorry, I couldn't process your request.")
        print("-" * 50)

if __name__ == "__main__":
    test_queries() 