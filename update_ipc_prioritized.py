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
    # Handle alphanumeric sections
    base_number = re.sub(r'[^0-9]', '', section_number)
    suffix = re.sub(r'[0-9]', '', section_number)
    
    urls = [
        f"https://devgan.in/ipc/section_{section_number}.php",
        f"https://devgan.in/ipc/{section_number}.php",
        f"https://devgan.in/ipc/section_{section_number.lower()}.php",
        f"https://devgan.in/ipc/section_{base_number}{suffix.lower()}.php",
        f"https://devgan.in/ipc/section_{base_number}_{suffix.lower()}.php"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for url in urls:
        try:
            print(f"Trying URL: {url}")
            response = requests.get(url, verify=False, timeout=10, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title - look for the actual section title
                title = ""
                title_tag = soup.find('h1')
                if title_tag:
                    title_text = title_tag.text.strip()
                    print(f"Raw title: {title_text}")
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
                    # Process all paragraphs
                    paragraphs = content_div.find_all(['p', 'div'])
                    for p in paragraphs:
                        text = p.text.strip()
                        if not text:
                            continue
                            
                        # Check if this is a punishment paragraph
                        if any(keyword in text.lower() for keyword in ['punishment', 'shall be punished', 'imprisonment', 'fine']):
                            punishment += text + " "
                            print(f"Found punishment: {text}")
                        else:
                            description += text + " "
                            print(f"Found description: {text}")
                
                # If no punishment found in paragraphs, look for punishment div
                if not punishment:
                    punishment_div = soup.find('div', class_='punishment')
                    if punishment_div:
                        punishment = punishment_div.text.strip()
                        print(f"Found punishment in div: {punishment}")
                
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
                
                # If we have any data, return it
                if title or description or punishment:
                    return {
                        'title': title,
                        'description': description,
                        'punishment': punishment
                    }
                
        except requests.exceptions.Timeout:
            print(f"Timeout error with URL {url}")
            continue
        except requests.exceptions.RequestException as e:
            print(f"Request error with URL {url}: {str(e)}")
            continue
        except Exception as e:
            print(f"Error with URL {url}: {str(e)}")
            continue
    
    return None

def update_section(cursor, section_number, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            cursor.execute("""
                UPDATE ipc_sections 
                SET title = %s,
                    description = %s,
                    punishment = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE section_number = %s
            """, (data['title'], data['description'], data['punishment'], section_number))
            return True
        except Error as e:
            if e.errno == 1205 and attempt < max_retries - 1:  # Lock timeout error
                print(f"Lock timeout for section {section_number}, retrying... (attempt {attempt + 1})")
                time.sleep(2)  # Wait before retrying
                continue
            else:
                print(f"Error updating section {section_number}: {str(e)}")
                return False
    return False

def update_crime_mappings(cursor):
    # Common crime to IPC section mappings
    crime_mappings = {
        'Murder': ['302'],
        'Theft': ['378', '379', '380', '381', '382'],
        'Rape': ['376', '376A', '376B', '376C', '376D', '376E'],
        'Robbery': ['390', '391', '392', '393', '394', '395', '396', '397', '398', '399', '400', '401', '402'],
        'Fraud': ['420', '421', '422', '423', '424', '425', '426', '427', '428', '429', '430', '431', '432', '433', '434', '435', '436', '437', '438', '439', '440', '441', '442', '443', '444', '445', '446', '447', '448', '449', '450', '451', '452', '453', '454', '455', '456', '457', '458', '459', '460', '461', '462', '463', '464', '465', '466', '467', '468', '469', '470', '471', '472', '473', '474', '475', '476', '477', '478', '479', '480', '481', '482', '483', '484', '485', '486', '487', '488', '489', '490', '491', '492', '493', '494', '495', '496', '497', '498', '499', '500'],
        'Assault': ['323', '324', '325', '326', '327', '328', '329', '330', '331', '332', '333', '334', '335', '336', '337', '338', '339', '340', '341', '342', '343', '344', '345', '346', '347', '348', '349', '350', '351', '352', '353', '354', '355', '356', '357', '358', '359', '360', '361', '362'],
        'Kidnapping': ['363', '364', '365', '366', '367', '368', '369'],
        'Domestic Violence': ['498A', '498B', '498C', '498D', '498E', '498F', '498G', '498H', '498I', '498J', '498K', '498L', '498M', '498N', '498O', '498P', '498Q', '498R', '498S', '498T', '498U', '498V', '498W', '498X', '498Y', '498Z'],
        'Cyber Crime': ['66', '66A', '66B', '66C', '66D', '66E', '66F', '67', '67A', '67B', '67C', '67D', '67E', '67F', '67G', '67H', '67I', '67J', '67K', '67L', '67M', '67N', '67O', '67P', '67Q', '67R', '67S', '67T', '67U', '67V', '67W', '67X', '67Y', '67Z']
    }
    
    try:
        # Clear existing mappings
        cursor.execute("DELETE FROM crime_ipc_mapping")
        
        # Insert new mappings
        for crime_name, sections in crime_mappings.items():
            # Get crime_id
            cursor.execute("SELECT id FROM crimes WHERE name = %s", (crime_name,))
            crime_result = cursor.fetchone()
            if crime_result:
                crime_id = crime_result[0]
                
                # Insert mappings for each section
                for section in sections:
                    cursor.execute("""
                        INSERT INTO crime_ipc_mapping (crime_id, ipc_section_id)
                        SELECT %s, id FROM ipc_sections WHERE section_number = %s
                    """, (crime_id, section))
        
        print("Successfully updated crime mappings!")
        
    except Error as e:
        print(f"Error updating crime mappings: {str(e)}")

def main():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        # Get all sections from database
        cursor.execute("""
            SELECT section_number 
            FROM ipc_sections 
            ORDER BY 
                CASE 
                    WHEN section_number REGEXP '^[0-9]+$' THEN CAST(section_number AS UNSIGNED)
                    ELSE 999999
                END,
                section_number
        """)
        sections = cursor.fetchall()
        
        # Process sections in batches
        batch_size = 10
        for i in range(0, len(sections), batch_size):
            batch = sections[i:i + batch_size]
            print(f"\n=== Processing Batch {i//batch_size + 1} of {(len(sections) + batch_size - 1)//batch_size} ===")
            
            for (section,) in batch:
                print(f"\nProcessing Section {section}...")
                data = get_section_details(section)
                if data:
                    if update_section(cursor, section, data):
                        print(f"Updated Section {section}")
                        print(f"Title: {data['title']}")
                        print(f"Description: {data['description'][:100]}...")
                        print(f"Punishment: {data['punishment'][:100]}...")
                    else:
                        print(f"Failed to update Section {section}")
                else:
                    print(f"Could not find data for Section {section}")
                time.sleep(1)  # Be nice to the server
            
            # Add a longer pause between batches
            if i + batch_size < len(sections):
                print("\nPausing between batches...")
                time.sleep(5)
        
        # Update crime mappings
        print("\n=== Updating Crime Mappings ===")
        update_crime_mappings(cursor)
        
    except Error as e:
        print(f"Database error: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    print("\nUpdate completed!")

if __name__ == "__main__":
    main() 