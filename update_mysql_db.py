import mysql.connector
from mysql.connector import Error
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    except Error as e:
        logger.error(f"Error connecting to MySQL database: {e}")
        return None

def create_tables(connection):
    try:
        cursor = connection.cursor()
        
        # Create ipc_sections table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ipc_sections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                section_number VARCHAR(10) UNIQUE,
                title TEXT,
                description TEXT,
                punishment TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Create crimes table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crimes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) UNIQUE,
                description TEXT,
                severity VARCHAR(50),
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Create crime_ipc_mapping table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crime_ipc_mapping (
                id INT AUTO_INCREMENT PRIMARY KEY,
                crime_id INT,
                ipc_section_id INT,
                FOREIGN KEY (crime_id) REFERENCES crimes(id),
                FOREIGN KEY (ipc_section_id) REFERENCES ipc_sections(id)
            )
        """)
        
        connection.commit()
        logger.info("Database tables created successfully")
    except Error as e:
        logger.error(f"Error creating tables: {e}")
    finally:
        cursor.close()

def update_ipc_sections(connection, sections_data):
    try:
        cursor = connection.cursor()
        updated = 0
        inserted = 0
        
        for section in sections_data:
            # Check if section exists
            cursor.execute("SELECT id FROM ipc_sections WHERE section_number = %s", (section['section_number'],))
            result = cursor.fetchone()
            
            if result:
                # Update existing section
                cursor.execute("""
                    UPDATE ipc_sections 
                    SET title = %s, description = %s, punishment = %s
                    WHERE section_number = %s
                """, (section['title'], section['description'], section['punishment'], section['section_number']))
                updated += 1
            else:
                # Insert new section
                cursor.execute("""
                    INSERT INTO ipc_sections (section_number, title, description, punishment)
                    VALUES (%s, %s, %s, %s)
                """, (section['section_number'], section['title'], section['description'], section['punishment']))
                inserted += 1
        
        connection.commit()
        logger.info(f"Database update completed: {updated} sections updated, {inserted} sections inserted")
    except Error as e:
        logger.error(f"Error updating sections: {e}")
    finally:
        cursor.close()

def main():
    # Connect to database
    connection = connect_to_db()
    if not connection:
        return
    
    try:
        # Create tables if they don't exist
        create_tables(connection)
        
        # Read scraped data from JSON file
        try:
            with open('ipc_sections.json', 'r', encoding='utf-8') as f:
                sections_data = json.load(f)
        except FileNotFoundError:
            logger.error("ipc_sections.json file not found. Please run the scraper first.")
            return
        
        # Update database with scraped data
        update_ipc_sections(connection, sections_data)
        
    except Error as e:
        logger.error(f"Database error: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    main() 