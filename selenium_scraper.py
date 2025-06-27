import logging
import random
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import sqlite3
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_driver():
    """Set up and return a configured Chrome driver with anti-detection measures."""
    try:
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument('--window-size=1920,1080')
        
        # Use undetected-chromedriver
        driver = uc.Chrome(options=options)
        
        # Set a realistic user agent
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        })
        
        # Remove webdriver flags
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except Exception as e:
        logging.error(f"Error setting up driver: {str(e)}")
        raise

def connect_to_db():
    """Connect to SQLite database and return connection object."""
    try:
        conn = sqlite3.connect('ipc_sections.db')
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ipc_sections (
                section_number INTEGER PRIMARY KEY,
                title TEXT,
                description TEXT,
                punishment TEXT,
                last_updated TIMESTAMP
            )
        ''')
        
        conn.commit()
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        raise

def get_section_details(driver, section_number, max_retries=3):
    """Fetch details for a specific IPC section with improved error handling."""
    url = f"https://devgan.in/ipc/section_{section_number}.php"
    
    for attempt in range(max_retries):
        try:
            logging.info(f"Attempting to fetch section {section_number} details (Attempt {attempt + 1}/{max_retries})")
            
            # Add random delay between attempts
            time.sleep(random.uniform(2, 5))
            
            driver.get(url)
            
            # Wait for page load
            time.sleep(random.uniform(3, 5))
            
            # Try multiple selectors for content
            content_selectors = [
                (By.CLASS_NAME, 'content'),
                (By.CLASS_NAME, 'section-content'),
                (By.CLASS_NAME, 'main-content'),
                (By.TAG_NAME, 'article'),
                (By.CLASS_NAME, 'post-content')
            ]
            
            content_div = None
            for selector in content_selectors:
                try:
                    wait = WebDriverWait(driver, 15)
                    content_div = wait.until(EC.presence_of_element_located(selector))
                    if content_div:
                        break
                except TimeoutException:
                    continue
            
            if not content_div:
                raise NoSuchElementException("Could not find content div with any selector")
            
            # Get page source and parse with BeautifulSoup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract title
            title = None
            title_selectors = ['h1', '.section-title', '.title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.text.strip()
                    break
            
            # Extract description
            description = None
            desc_selectors = ['.description', '.content p', 'article p']
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    description = desc_elem.text.strip()
                    break
            
            # Extract punishment
            punishment = None
            punishment_selectors = ['.punishment', '.penalty', '.sentence']
            for selector in punishment_selectors:
                punish_elem = soup.select_one(selector)
                if punish_elem:
                    punishment = punish_elem.text.strip()
                    break
            
            if not any([title, description, punishment]):
                raise ValueError("Could not extract any content from the page")
            
            return {
                'section_number': section_number,
                'title': title or '',
                'description': description or '',
                'punishment': punishment or '',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error processing section {section_number}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(5, 10))  # Random delay between retries
                continue
            else:
                raise

def get_all_sections_from_main_page(driver):
    """Extract all section numbers from the main page."""
    try:
        logging.info("Fetching main sections page...")
        driver.get("https://devgan.in/ipc/")
        time.sleep(random.uniform(2, 4))
        
        # Wait for the sections to load
        wait = WebDriverWait(driver, 20)
        sections = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="section_"]')))
        
        section_numbers = []
        for section in sections:
            try:
                href = section.get_attribute('href')
                section_number = int(href.split('_')[1].split('.')[0])
                section_numbers.append(section_number)
                logging.info(f"Found section {section_number}: {section.text}")
            except (ValueError, IndexError) as e:
                logging.warning(f"Could not parse section number from {href}: {str(e)}")
                continue
        
        logging.info(f"Successfully extracted {len(section_numbers)} sections from main page")
        return sorted(section_numbers)
        
    except Exception as e:
        logging.error(f"Error fetching sections from main page: {str(e)}")
        raise

def update_database(conn, section_data):
    """Update the database with section data."""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO ipc_sections 
            (section_number, title, description, punishment, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            section_data['section_number'],
            section_data['title'],
            section_data['description'],
            section_data['punishment'],
            section_data['last_updated']
        ))
        conn.commit()
        logging.info(f"Updated database for section {section_data['section_number']}")
    except Exception as e:
        logging.error(f"Database update error for section {section_data['section_number']}: {str(e)}")
        raise

def scrape_all_sections():
    """Main function to scrape all sections."""
    driver = None
    conn = None
    scraped_data = []
    failed_sections = []
    
    try:
        driver = setup_driver()
        conn = connect_to_db()
        
        # Get all section numbers
        section_numbers = get_all_sections_from_main_page(driver)
        
        # Process each section
        for section_number in section_numbers:
            try:
                details = get_section_details(driver, section_number)
                scraped_data.append(details)
                update_database(conn, details)
                
                # Random delay between sections
                time.sleep(random.uniform(3, 7))
                
            except Exception as e:
                logging.error(f"Failed to process section {section_number}: {str(e)}")
                failed_sections.append(section_number)
                continue
        
        return scraped_data, failed_sections
        
    except Exception as e:
        logging.error(f"Error in main scraping process: {str(e)}")
        raise
        
    finally:
        if driver:
            driver.quit()
        if conn:
            conn.close()

def main():
    """Entry point of the script."""
    try:
        logging.info("Starting IPC sections scraping...")
        scraped_data, failed_sections = scrape_all_sections()
        
        # Save results to JSON file
        with open('scraped_data.json', 'w', encoding='utf-8') as f:
            json.dump({
                'scraped_data': scraped_data,
                'failed_sections': failed_sections,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Scraping completed. Successfully scraped {len(scraped_data)} sections.")
        if failed_sections:
            logging.warning(f"Failed to scrape {len(failed_sections)} sections: {failed_sections}")
            
    except Exception as e:
        logging.error(f"Script execution failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 