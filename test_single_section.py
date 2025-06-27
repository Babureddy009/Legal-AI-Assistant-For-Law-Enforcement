import requests
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_section_details():
    # Try different URL formats
    urls = [
        "https://devgan.in/ipc/section_302.php",
        "https://devgan.in/ipc/302.php",
        "https://devgan.in/all_sections_ipc/302.php"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1'
    }
    
    for url in urls:
        try:
            print(f"\nTrying URL: {url}")
            response = requests.get(url, verify=False, timeout=10, headers=headers)
            
            if response.status_code == 200:
                print(f"Success! Content length: {len(response.text)}")
                print("\nFirst 1000 characters of raw response:")
                print(response.text[:1000])
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try to find the section content
                print("\nLooking for section content...")
                
                # Method 1: Look for article or section tags
                content = soup.find(['article', 'section'])
                if content:
                    print("\nFound content in article/section tag:")
                    print(content.text.strip())
                
                # Method 2: Look for main content area
                main = soup.find('main')
                if main:
                    print("\nFound content in main tag:")
                    print(main.text.strip())
                
                # Method 3: Look for specific section content
                section_content = soup.find(id=lambda x: x and ('content' in x.lower() or 'section' in x.lower()))
                if section_content:
                    print("\nFound content by ID:")
                    print(section_content.text.strip())
                
        except Exception as e:
            print(f"Error with {url}: {str(e)}")
            continue

if __name__ == "__main__":
    get_section_details() 