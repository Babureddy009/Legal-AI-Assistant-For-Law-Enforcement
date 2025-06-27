import requests
from bs4 import BeautifulSoup
import mysql.connector
import re
import time
import urllib3
import logging
from datetime import datetime
import json
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ipc_scraping.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root1",
            password="pass",
            database="legal_ai"
        )
        if connection.is_connected():
            logger.info("Successfully connected to MySQL database")
            return connection
    except mysql.connector.Error as e:
        logger.error(f"Error connecting to MySQL database: {e}")
        return None

def get_section_content(soup):
    """Extract section content from the page"""
    content = ""
    try:
        # First, try to find the <tr class='mys-desc'> and extract the <p> text
        desc_tr = soup.find("tr", class_="mys-desc")
        if desc_tr:
            p = desc_tr.find("p")
            if p and p.text.strip():
                content = p.text.strip()
        # Fallback to previous logic if not found
        if not content:
            content_div = soup.find("div", class_="content")
            if content_div:
                main_text = content_div.find("p", class_="main-text")
                if main_text:
                    content = main_text.text.strip()
                else:
                    paragraphs = content_div.find_all("p")
                    for p in paragraphs:
                        text = p.text.strip()
                        if text and not text.startswith("Devgan.in") and not re.match(r"^Section \d+[A-Z]*$", text):
                            if not re.search(r"punishment|shall be punished|imprisonment|fine|rigorous imprisonment|simple imprisonment", text, re.I):
                                content += text + "\n"
                if not content:
                    text = content_div.get_text(separator="\n", strip=True)
                    text = re.sub(r"Section \d+[A-Z]*", "", text)
                    text = re.sub(r"Devgan\.in", "", text)
                    text = re.sub(r"Punishment.*?(?=\n|$)", "", text, flags=re.I)
                    content = text.strip()
                content = re.sub(r"\s+", " ", content)
                content = re.sub(r"\n+", "\n", content)
                content = content.strip()
    except Exception as e:
        logger.error(f"Error extracting section content: {e}")
    return content.strip()

def get_punishment(soup):
    """Extract punishment information from the section page"""
    punishment = ""
    try:
        # First try to find the punishment section
        punishment_div = soup.find("div", class_="punishment")
        if punishment_div:
            punishment = punishment_div.text.strip()
        
        # If no punishment div found, look in the main content
        if not punishment:
            content = soup.find("div", class_="content")
            if content:
                # Look for paragraphs containing punishment-related text
                for p in content.find_all("p"):
                    text = p.text.strip()
                    if re.search(r"punishment|shall be punished|imprisonment|fine|rigorous imprisonment|simple imprisonment", text, re.I):
                        punishment += text + " "
        
        # If still no punishment found, try to find it in any text containing punishment-related words
        if not punishment:
            for text in soup.stripped_strings:
                if re.search(r"punishment|shall be punished|imprisonment|fine|rigorous imprisonment|simple imprisonment", text, re.I):
                    punishment += text + " "
        
        # Clean up the punishment text
        punishment = re.sub(r"Devgan\.in\s*", "", punishment)
        punishment = re.sub(r"\s+", " ", punishment)
        punishment = re.sub(r"^Section \d+[A-Z]*\s*-\s*", "", punishment)
        return punishment.strip()
    except Exception as e:
        logger.error(f"Error extracting punishment: {e}")
        return ""

def fetch_with_retry(url, max_retries=3):
    """Fetch URL with retry logic and random delays"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            # Add random delay between requests
            time.sleep(random.uniform(2, 5))
            response = requests.get(url, headers=headers, verify=False, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(random.uniform(5, 10))  # Longer delay between retries

def main():
    # Removed debug block for Section 2 HTML fetch
    # Now proceed with the full scraping and updating process
    # Connect to database
    conn = connect_to_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    base_url = "https://devgan.in/all_sections_ipc.php"
    section_base = "https://devgan.in/"
    
    try:
        # Get the main page with all section links
        logger.info("Fetching main page...")
        resp = fetch_with_retry(base_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Find all section links
        section_links = []
        for a in soup.find_all("a", href=True):
            match = re.match(r"Section ([0-9]+[A-Z]*)", a.text.strip(), re.I)
            if match:
                section_number = match.group(1)
                section_links.append((section_number, section_base + a['href']))
        
        logger.info(f"Found {len(section_links)} IPC section links")
        
        # Store results in a list for JSON backup
        results = []
        
        # Process each section
        for section_number, url in section_links:
            try:
                logger.info(f"Processing Section {section_number}...")
                sec_resp = fetch_with_retry(url)
                sec_soup = BeautifulSoup(sec_resp.text, "html.parser")
                
                # Title
                title_tag = sec_soup.find("h1")
                title = title_tag.text.strip() if title_tag else f"IPC Section {section_number}"
                
                # Description
                description = get_section_content(sec_soup)
                
                # Punishment
                punishment = get_punishment(sec_soup)
                
                # Store result
                result = {
                    "section_number": section_number,
                    "title": title,
                    "description": description,
                    "punishment": punishment,
                    "scraped_at": datetime.now().isoformat()
                }
                results.append(result)
                
                # Check if section exists
                check_query = "SELECT id FROM ipc_sections WHERE section_number = %s"
                cursor.execute(check_query, (section_number,))
                exists = cursor.fetchone()
                
                if exists:
                    # Update existing record
                    update_query = """
                        UPDATE ipc_sections 
                        SET title = %s, description = %s, punishment = %s
                        WHERE section_number = %s
                    """
                    cursor.execute(update_query, (title, description, punishment, section_number))
                    logger.info(f"Updated Section {section_number}")
                else:
                    # Insert new record
                    insert_query = """
                        INSERT INTO ipc_sections (section_number, title, description, punishment)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (section_number, title, description, punishment))
                    logger.info(f"Inserted Section {section_number}")
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"Error processing Section {section_number}: {e}")
                continue
        
        # Save results to JSON file
        with open('ipc_sections.json', 'w', encoding='utf-8') as f:
            json.dump({"sections": results}, f, indent=2, ensure_ascii=False)
        logger.info("Saved results to ipc_sections.json")
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
    finally:
        cursor.close()
        conn.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    main()