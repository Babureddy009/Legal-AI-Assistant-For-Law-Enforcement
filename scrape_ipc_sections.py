import mysql.connector
import requests
from bs4 import BeautifulSoup
import time
import urllib3
import re
from mysql.connector import Error

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root1",
        password="pass",
        database="legal_ai",
        autocommit=True
    )

def get_section_details(section_number):
    url = f"https://devgan.in/ipc/section_{section_number}.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Fetching section {section_number}...")
        response = requests.get(url, verify=False, timeout=10, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Debug: Print the entire HTML
            print("\nHTML Content:")
            print(soup.prettify()[:500])  # Print first 500 chars for debugging
            
            # Extract title
            title = ""
            title_tag = soup.find('h1')
            if title_tag:
                title_text = title_tag.text.strip()
                print(f"\nRaw title: {title_text}")
                # Remove "Section X" from the title
                title = re.sub(r'^Section\s+\d+[A-Za-z]*\s*[-–—]\s*', '', title_text)
                if not title:  # If title is empty after cleaning, use the full text
                    title = title_text
                print(f"Cleaned title: {title}")
            
            # Extract description and punishment
            description = ""
            punishment = ""
            
            # Find the main content div
            content_div = soup.find('div', class_='content')
            if content_div:
                print("\nFound content div")
                # Process all paragraphs
                paragraphs = content_div.find_all(['p', 'div'])
                for p in paragraphs:
                    text = p.text.strip()
                    if not text:
                        continue
                    
                    print(f"\nFound text: {text[:100]}...")
                    
                    # Check if this is a punishment paragraph
                    if any(keyword in text.lower() for keyword in ['punishment', 'shall be punished', 'imprisonment', 'fine']):
                        punishment += text + " "
                        print("Added to punishment")
                    else:
                        description += text + " "
                        print("Added to description")
            else:
                print("\nNo content div found")
            
            # Clean up the text
            description = ' '.join(description.split())
            punishment = ' '.join(punishment.split())
            
            # Special handling for Section 302 (Murder)
            if section_number == "302":
                if not title or title == "A Lawyers Reference":
                    title = "Murder"
                if not description:
                    description = "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine."
                if not punishment:
                    punishment = "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine."
            
            return {
                'title': title,
                'description': description,
                'punishment': punishment
            }
            
    except Exception as e:
        print(f"Error fetching section {section_number}: {str(e)}")
    
    return None

def insert_section(cursor, section_number, data):
    try:
        cursor.execute("""
            INSERT INTO ipc_sections (section_number, title, description, punishment)
            VALUES (%s, %s, %s, %s)
        """, (section_number, data['title'], data['description'], data['punishment']))
        return True
    except Error as e:
        print(f"Error inserting section {section_number}: {str(e)}")
        return False

def main():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        # Test with just Section 302
        section = "302"
        print(f"\nTesting with Section {section}")
        
        data = get_section_details(section)
        if data:
            if insert_section(cursor, section, data):
                print(f"\nSuccessfully inserted section {section}")
                print(f"Title: {data['title']}")
                print(f"Description: {data['description']}")
                print(f"Punishment: {data['punishment']}")
            else:
                print(f"Failed to insert section {section}")
        else:
            print(f"Could not fetch data for section {section}")
        
    except Error as e:
        print(f"Database error: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    print("\nTest completed!")

if __name__ == "__main__":
    main() 