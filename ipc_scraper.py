import requests
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error
import json
import time
import logging
import re
from datetime import datetime
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ipc_scraping.log'),
        logging.StreamHandler()
    ]
)

def connect_to_db():
    """Connect to the MySQL database."""
    return mysql.connector.connect(
        host="localhost",
        user="root1",
        password="pass",
        database="legal_ai",
        autocommit=True
    )

def get_all_sections_from_main_page():
    """Get all IPC sections data from the main page."""
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
        logging.info("Fetching main sections page...")
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all section links
            sections = []
            for link in soup.find_all('a', href=re.compile(r'/ipc/section/\d+/')):
                # Extract section number from href
                match = re.search(r'/ipc/section/(\d+)/', link['href'])
                if not match:
                    continue
                
                section_number = match.group(1)
                
                # Get the title from the title attribute
                title = link.get('title', '').strip()
                if title:
                    # Remove the "IPC Section XXX » " prefix
                    title = re.sub(r'^IPC Section \d+[A-Za-z]* » ', '', title)
                else:
                    # If no title attribute, try getting text from sectionlink span
                    title = link.find('span', class_='sectionlink')
                    if title:
                        title = title.text.strip()
                
                sections.append({
                    'section_number': section_number,
                    'title': title,
                    'description': '',  # Will be filled by get_section_details
                    'punishment': '',    # Will be filled by get_section_details
                    'scraped_at': datetime.now().isoformat()
                })
                
                logging.info(f"Found section {section_number}: {title}")
            
            logging.info(f"Successfully extracted {len(sections)} sections from main page")
            return sections
            
    except Exception as e:
        logging.error(f"Error fetching main page: {str(e)}")
    
    return []

def get_section_details(section_number, max_retries=3):
    """
    Fetch details for a specific IPC section.
    Returns a dictionary containing description and punishment.
    """
    url = f"https://devgan.in/ipc/section/{section_number}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1'
    }
    
    for attempt in range(max_retries):
        try:
            logging.info(f"Attempting to fetch section {section_number} details (Attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, headers=headers, verify=False, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find the main content div
                content_div = soup.find('div', class_='content')
                if not content_div:
                    raise ValueError("Could not find content div")
                
                # Extract description and punishment
                description = ""
                punishment = ""
                
                # Process all paragraphs
                paragraphs = content_div.find_all(['p', 'div'])
                for p in paragraphs:
                    text = p.text.strip()
                    if not text:
                        continue
                    
                    # Check if this is a punishment paragraph
                    if any(keyword in text.lower() for keyword in ['punishment', 'shall be punished', 'imprisonment', 'fine']):
                        punishment += text + " "
                    else:
                        description += text + " "
                
                # Clean up the text
                description = ' '.join(description.split())
                punishment = ' '.join(punishment.split())
                
                # Validate the data
                if not description and not punishment:
                    raise ValueError("No content found")
                
                return {
                    'description': description,
                    'punishment': punishment
                }
            
        except Exception as e:
            logging.error(f"Error processing section {section_number}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(5)  # Wait before retrying
                continue
    
    return None

def save_to_json(data, filename):
    """Save scraped data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_from_json(filename):
    """Load scraped data from a JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def insert_section(cursor, section_data):
    """Insert or update a section in the database."""
    try:
        cursor.execute("""
            INSERT INTO ipc_sections (section_number, title, description, punishment)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            title = VALUES(title),
            description = VALUES(description),
            punishment = VALUES(punishment)
        """, (
            section_data['section_number'],
            section_data['title'],
            section_data['description'],
            section_data['punishment']
        ))
        return True
    except Error as e:
        logging.error(f"Database error for section {section_data['section_number']}: {str(e)}")
        return False

def scrape_all_sections():
    """Scrape all IPC sections and save to JSON file."""
    try:
        # First get all sections from main page
        sections = get_all_sections_from_main_page()
        
        if not sections:
            logging.error("Could not fetch any sections from main page")
            return [], []
        
        # Now get details for each section
        for section in sections:
            section_number = section['section_number']
            logging.info(f"\nProcessing details for Section {section_number}")
            
            details = get_section_details(section_number)
            if details:
                section.update(details)
                logging.info(f"Successfully fetched details for section {section_number}")
                logging.info(f"Description: {section['description'][:100]}...")
                logging.info(f"Punishment: {section['punishment'][:100]}...")
            else:
                logging.error(f"Could not fetch details for section {section_number}")
            
            # Add a small delay between requests
            time.sleep(2)
            
            # Save progress every 10 sections
            if len([s for s in sections if s.get('description')]) % 10 == 0:
                save_to_json({
                    'sections': sections,
                    'last_updated': datetime.now().isoformat()
                }, 'ipc_sections_temp.json')
        
        # Save final data
        save_to_json({
            'sections': sections,
            'last_updated': datetime.now().isoformat()
        }, 'ipc_sections.json')
        
        logging.info("\n=== Scraping Summary ===")
        logging.info(f"Total sections found: {len(sections)}")
        logging.info(f"Successfully fetched details: {len([s for s in sections if s.get('description')])}")
        
        return sections, []
            
    except Exception as e:
        logging.error(f"Scraping error: {str(e)}")
        return [], []

def update_database(scraped_data):
    """Update the database with scraped data."""
    conn = None
    cursor = None
    successful_updates = 0
    failed_updates = []
    
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        for section_data in scraped_data:
            if insert_section(cursor, section_data):
                successful_updates += 1
                logging.info(f"Successfully updated section {section_data['section_number']}")
            else:
                failed_updates.append(section_data['section_number'])
                logging.error(f"Failed to update section {section_data['section_number']}")
        
        logging.info("\n=== Database Update Summary ===")
        logging.info(f"Total sections to update: {len(scraped_data)}")
        logging.info(f"Successfully updated: {successful_updates}")
        logging.info(f"Failed updates: {len(failed_updates)}")
        if failed_updates:
            logging.info("Failed section numbers: " + ", ".join(map(str, failed_updates)))
            
    except Exception as e:
        logging.error(f"Database update error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    """Main function to scrape and update IPC sections."""
    # Step 1: Scrape all sections
    logging.info("Starting IPC sections scraping...")
    scraped_data, failed_sections = scrape_all_sections()
    
    if not scraped_data:
        logging.error("No data was scraped successfully. Aborting database update.")
        return
    
    # Step 2: Update database
    logging.info("\nStarting database update...")
    update_database(scraped_data)
    
    logging.info("Script execution completed!")

if __name__ == "__main__":
    main() 