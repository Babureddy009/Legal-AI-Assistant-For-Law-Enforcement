import requests
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_html():
    url = "https://devgan.in/all_sections_ipc.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        print("Fetching main page...")
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Print all section links
            print("\nSection Links:")
            for link in soup.find_all('a', href=True):
                print(f"Link: {link['href']}")
                print(f"Text: {link.text.strip()}")
                print(f"Title: {link.get('title', '')}")
                print("-" * 50)
            
            # Print main content structure
            print("\nMain Content Structure:")
            for div in soup.find_all('div', class_=True):
                print(f"Div class: {div.get('class')}")
                print(f"First few characters: {div.text[:100].strip()}")
                print("-" * 50)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_html() 