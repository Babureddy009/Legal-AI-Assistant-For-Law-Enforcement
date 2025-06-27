import mysql.connector
import requests
from bs4 import BeautifulSoup
import time
import urllib3
import re

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root1",
        password="pass",
        database="legal_ai"
    )

def get_empty_punishment_sections(cursor):
    cursor.execute("""
        SELECT section_number, title 
        FROM ipc_sections 
        WHERE punishment IS NULL OR punishment = ''
        ORDER BY 
            CASE 
                WHEN section_number REGEXP '^[0-9]+$' THEN CAST(section_number AS UNSIGNED)
                WHEN section_number REGEXP '^[0-9]+[A-Z]+$' THEN CAST(REGEXP_REPLACE(section_number, '[^0-9]', '') AS UNSIGNED)
                ELSE 999999
            END,
            section_number
    """)
    return cursor.fetchall()

def clean_punishment_text(text):
    # Remove extra whitespace and normalize text
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def get_section_details(section_number):
    # Handle alphanumeric sections
    base_number = re.sub(r'[^0-9]', '', section_number)
    suffix = re.sub(r'[0-9]', '', section_number)
    
    # Try different URL formats for alphanumeric sections
    urls = [
        f"https://devgan.in/ipc/section_{section_number}.php",
        f"https://devgan.in/ipc/{section_number}.php",
        f"https://devgan.in/ipc/section_{section_number.lower()}.php",
        f"https://devgan.in/ipc/section_{base_number}{suffix.lower()}.php",
        f"https://devgan.in/ipc/section_{base_number}_{suffix.lower()}.php"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract punishment
                punishment = ""
                
                # First try to find punishment in specific divs
                punishment_div = soup.find('div', class_='punishment')
                if punishment_div:
                    punishment = clean_punishment_text(punishment_div.text)
                    if punishment:
                        return punishment
                
                # Try to find punishment in the content div
                content_div = soup.find('div', class_='content')
                if content_div:
                    # Look for punishment-related text in paragraphs
                    for p in content_div.find_all('p'):
                        text = p.text.strip()
                        if any(keyword in text.lower() for keyword in [
                            'punishment', 'shall be punished', 'imprisonment', 
                            'fine', 'rigorous imprisonment', 'simple imprisonment',
                            'liable to', 'shall be liable'
                        ]):
                            punishment += text + " "
                
                # If no punishment found in content div, try the entire page
                if not punishment:
                    for text in soup.stripped_strings:
                        if any(keyword in text.lower() for keyword in [
                            'punishment', 'shall be punished', 'imprisonment', 
                            'fine', 'rigorous imprisonment', 'simple imprisonment',
                            'liable to', 'shall be liable'
                        ]):
                            punishment += text + " "
                
                return clean_punishment_text(punishment)
                
        except Exception as e:
            print(f"Error with URL {url}: {str(e)}")
            continue
    
    return None

def update_section_punishment(cursor, section_number, punishment):
    cursor.execute("""
        UPDATE ipc_sections 
        SET punishment = %s 
        WHERE section_number = %s
    """, (punishment, section_number))

def main():
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Get all sections with empty punishment
    empty_sections = get_empty_punishment_sections(cursor)
    print(f"Found {len(empty_sections)} sections with empty punishment fields")
    
    # Update each section
    for section_number, title in empty_sections:
        print(f"Processing Section {section_number}: {title}")
        punishment = get_section_details(section_number)
        
        if punishment:
            update_section_punishment(cursor, section_number, punishment)
            print(f"Updated Section {section_number} with punishment: {punishment[:100]}...")
        else:
            print(f"Could not find punishment for Section {section_number}")
        
        # Add delay to avoid overwhelming the server
        time.sleep(1)
    
    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Update completed!")

if __name__ == "__main__":
    main() 