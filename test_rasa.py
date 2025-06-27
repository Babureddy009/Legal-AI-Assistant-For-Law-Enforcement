import requests
import json

def send_message(message):
    url = "http://localhost:5006/webhooks/rest/webhook"
    payload = {
        "sender": "user",
        "message": message
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.json()

if __name__ == "__main__":
    # Test the model with some example queries
    test_queries = [
        "what is the punishment for murder?",
        "tell me about IPC section 302",
        "what is the punishment for theft?"
    ]
    
    for query in test_queries:
        print(f"\nUser: {query}")
        response = send_message(query)
        for message in response:
            print(f"Bot: {message.get('text', '')}") 