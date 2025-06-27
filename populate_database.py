import mysql.connector
from mysql.connector import Error
import json
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def populate_database():
    try:
        # Read the JSON data
        logger.info("Reading crimes_data.json...")
        try:
            with open('crimes_data.json', 'r') as file:
                data = json.load(file)
            logger.info(f"Successfully loaded JSON data with {len(data['crimes'])} crimes")
        except FileNotFoundError:
            logger.error("crimes_data.json file not found!")
            return
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {str(e)}")
            return
        
        # Connect to MySQL database
        logger.info("Connecting to database...")
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="pass",
                database="legal_ai"
            )
            logger.info("Successfully connected to database")
        except Error as e:
            logger.error(f"Error connecting to database: {str(e)}")
            return
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Clear existing data
            logger.info("Clearing existing data...")
            try:
                cursor.execute("DELETE FROM crime_ipc_mapping")
                cursor.execute("DELETE FROM crimes")
                cursor.execute("DELETE FROM ipc_sections")
                connection.commit()
                logger.info("Successfully cleared existing data")
            except Error as e:
                logger.error(f"Error clearing data: {str(e)}")
                return
            
            # Insert crimes
            logger.info("Starting to insert crimes...")
            for crime in data['crimes']:
                try:
                    # Insert crime
                    logger.info(f"Inserting crime: {crime['name']}")
                    cursor.execute("""
                        INSERT INTO crimes (name, description, severity, category, bailable, cognizable, compoundable)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        crime['name'],
                        crime['description'],
                        crime['severity'],
                        crime['category'],
                        crime['bailable'],
                        crime['cognizable'],
                        crime['compoundable']
                    ))
                    crime_id = cursor.lastrowid
                    logger.info(f"Successfully inserted crime: {crime['name']} (ID: {crime_id})")
                    
                    # Insert IPC sections and create mappings
                    logger.info(f"Processing IPC sections for {crime['name']}...")
                    for section_number in crime['ipc_sections']:
                        try:
                            # Check if IPC section exists
                            cursor.execute("SELECT id FROM ipc_sections WHERE section_number = %s", (section_number,))
                            section = cursor.fetchone()
                            
                            if not section:
                                # Insert new IPC section
                                logger.info(f"Inserting new IPC section: {section_number}")
                                cursor.execute("""
                                    INSERT INTO ipc_sections (section_number, title, description, punishment)
                                    VALUES (%s, %s, %s, %s)
                                """, (
                                    section_number,
                                    f"IPC Section {section_number}",
                                    f"Description for IPC Section {section_number}",
                                    f"Punishment for IPC Section {section_number}"
                                ))
                                section_id = cursor.lastrowid
                                logger.info(f"Successfully inserted IPC section: {section_number} (ID: {section_id})")
                            else:
                                section_id = section['id']
                                logger.info(f"Found existing IPC section: {section_number} (ID: {section_id})")
                            
                            # Create mapping
                            logger.info(f"Creating mapping for {crime['name']} -> IPC Section {section_number}")
                            cursor.execute("""
                                INSERT INTO crime_ipc_mapping (crime_id, ipc_section_id)
                                VALUES (%s, %s)
                            """, (crime_id, section_id))
                            logger.info(f"Successfully mapped {crime['name']} to IPC Section {section_number}")
                            
                        except Error as e:
                            logger.error(f"Error processing IPC section {section_number} for {crime['name']}: {str(e)}")
                            continue
                    
                except Error as e:
                    logger.error(f"Error inserting crime {crime['name']}: {str(e)}")
                    continue
            
            try:
                connection.commit()
                logger.info("Successfully committed all changes to database")
            except Error as e:
                logger.error(f"Error committing changes: {str(e)}")
                connection.rollback()
                return

    except Error as e:
        logger.error(f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    populate_database() 