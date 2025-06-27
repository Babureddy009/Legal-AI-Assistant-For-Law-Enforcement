import mysql.connector
from mysql.connector import Error
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_murder_data():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root1",
            password="pass",
            database="legal_ai"
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Check crimes table
            logger.info("\nChecking crimes table:")
            cursor.execute("SELECT * FROM crimes WHERE LOWER(name) LIKE %s", ("%murder%",))
            crimes = cursor.fetchall()
            logger.info(f"Crimes found: {crimes}")
            
            # Check crime_ipc_mapping table
            logger.info("\nChecking crime_ipc_mapping table:")
            cursor.execute("""
                SELECT m.*, c.name as crime_name, i.section_number
                FROM crime_ipc_mapping m
                JOIN crimes c ON m.crime_id = c.id
                JOIN ipc_sections i ON m.ipc_section_id = i.id
                WHERE LOWER(c.name) LIKE %s
            """, ("%murder%",))
            mappings = cursor.fetchall()
            logger.info(f"Mappings found: {mappings}")
            
            # Check ipc_sections table
            logger.info("\nChecking ipc_sections table:")
            cursor.execute("""
                SELECT i.*
                FROM ipc_sections i
                JOIN crime_ipc_mapping m ON i.id = m.ipc_section_id
                JOIN crimes c ON m.crime_id = c.id
                WHERE LOWER(c.name) LIKE %s
            """, ("%murder%",))
            sections = cursor.fetchall()
            logger.info(f"IPC sections found: {sections}")

    except Error as e:
        logger.error(f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    check_murder_data() 