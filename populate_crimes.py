import mysql.connector
from mysql.connector import Error
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_crimes():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root1",
            password="pass",
            database="legal_ai"
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # First, clear existing data
            cursor.execute("DELETE FROM crime_ipc_mapping")
            cursor.execute("DELETE FROM crimes")
            connection.commit()
            logger.info("Cleared existing data")
            
            # Common crimes with their IPC sections
            crimes_data = [
                {
                    'name': 'Murder',
                    'description': 'The unlawful killing of a human being with malice aforethought.',
                    'severity': 'heinous',
                    'ipc_sections': ['302', '304']
                },
                {
                    'name': 'Rape',
                    'description': 'Sexual intercourse with a person without their consent.',
                    'severity': 'heinous',
                    'ipc_sections': ['376', '376A', '376B', '376C', '376D']
                },
                {
                    'name': 'Theft',
                    'description': 'The act of taking someone else\'s property without their permission.',
                    'severity': 'major',
                    'ipc_sections': ['378', '379']
                },
                {
                    'name': 'Robbery',
                    'description': 'The act of taking someone else\'s property by force or threat of force.',
                    'severity': 'heinous',
                    'ipc_sections': ['390', '391', '392', '393', '394', '395', '396', '397', '398', '399', '400', '401', '402']
                },
                {
                    'name': 'Assault',
                    'description': 'The act of causing physical harm or injury to another person.',
                    'severity': 'major',
                    'ipc_sections': ['351', '352', '353', '354', '355', '356', '357']
                }
            ]
            
            # Insert crimes
            for crime in crimes_data:
                # Insert new crime
                cursor.execute("""
                    INSERT INTO crimes (name, description, severity)
                    VALUES (%s, %s, %s)
                """, (crime['name'], crime['description'], crime['severity']))
                crime_id = cursor.lastrowid
                logger.info(f"Inserted crime '{crime['name']}' with ID {crime_id}")
                
                # Insert IPC mappings
                for section in crime['ipc_sections']:
                    # Get IPC section ID
                    cursor.execute("SELECT id FROM ipc_sections WHERE section_number = %s", (section,))
                    ipc_section = cursor.fetchone()
                    
                    if ipc_section:
                        cursor.execute("""
                            INSERT INTO crime_ipc_mapping (crime_id, ipc_section_id)
                            VALUES (%s, %s)
                        """, (crime_id, ipc_section['id']))
                        logger.info(f"Mapped crime '{crime['name']}' to IPC Section {section}")
                    else:
                        logger.warning(f"IPC Section {section} not found in database")
            
            connection.commit()
            logger.info("Successfully populated crimes and mappings")

    except Error as e:
        logger.error(f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    populate_crimes() 