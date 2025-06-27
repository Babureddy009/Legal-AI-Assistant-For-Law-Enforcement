import mysql.connector
from mysql.connector import Error
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="pass",
            database="legal_ai"
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Check crimes table
            logger.info("\nChecking crimes table:")
            cursor.execute("SELECT * FROM crimes")
            crimes = cursor.fetchall()
            logger.info(f"Found {len(crimes)} crimes:")
            for crime in crimes:
                logger.info(f"Crime: {crime['name']} (ID: {crime['id']})")
                logger.info(f"Description: {crime['description']}")
                logger.info(f"Severity: {crime['severity']}")
                logger.info("---")
            
            # Check ipc_sections table
            logger.info("\nChecking ipc_sections table:")
            cursor.execute("SELECT * FROM ipc_sections")
            sections = cursor.fetchall()
            logger.info(f"Found {len(sections)} IPC sections:")
            for section in sections:
                logger.info(f"Section: {section['section_number']} (ID: {section['id']})")
                logger.info(f"Title: {section['title']}")
                logger.info("---")
            
            # Check crime_ipc_mapping table
            logger.info("\nChecking crime_ipc_mapping table:")
            cursor.execute("""
                SELECT c.name as crime_name, i.section_number, m.*
                FROM crime_ipc_mapping m
                JOIN crimes c ON m.crime_id = c.id
                JOIN ipc_sections i ON m.ipc_section_id = i.id
            """)
            mappings = cursor.fetchall()
            logger.info(f"Found {len(mappings)} crime-IPC mappings:")
            for mapping in mappings:
                logger.info(f"Crime: {mapping['crime_name']} -> IPC Section: {mapping['section_number']}")
            
            # Specifically check for forgery
            logger.info("\nChecking specifically for forgery:")
            cursor.execute("SELECT * FROM crimes WHERE LOWER(name) = 'forgery'")
            forgery = cursor.fetchone()
            if forgery:
                logger.info(f"Found forgery crime (ID: {forgery['id']})")
                logger.info(f"Description: {forgery['description']}")
                logger.info(f"Severity: {forgery['severity']}")
                
                # Get IPC sections for forgery
                cursor.execute("""
                    SELECT i.*
                    FROM ipc_sections i
                    JOIN crime_ipc_mapping m ON i.id = m.ipc_section_id
                    WHERE m.crime_id = %s
                """, (forgery['id'],))
                forgery_sections = cursor.fetchall()
                logger.info(f"Found {len(forgery_sections)} IPC sections for forgery:")
                for section in forgery_sections:
                    logger.info(f"Section {section['section_number']}: {section['description']}")
            else:
                logger.info("Forgery crime not found in database!")

    except Error as e:
        logger.error(f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("\nDatabase connection closed")

if __name__ == "__main__":
    check_database() 