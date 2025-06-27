import mysql.connector
from mysql.connector import Error
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_cyber_crime():
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root1",
            password="pass",
            database="legal_ai"
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Check for cyber crime in crimes table
            logger.info("\nChecking crimes table for cyber crime:")
            cursor.execute("""
                SELECT * FROM crimes 
                WHERE name LIKE '%cyber%' 
                   OR category = 'cyber'
            """)
            cyber_crimes = cursor.fetchall()
            
            if cyber_crimes:
                logger.info(f"Found {len(cyber_crimes)} cyber crimes:")
                for crime in cyber_crimes:
                    logger.info(f"\nCrime: {crime['name']}")
                    logger.info(f"Description: {crime['description']}")
                    logger.info(f"Category: {crime['category']}")
                    logger.info(f"Severity: {crime['severity']}")
                    
                    # Get related IPC sections
                    cursor.execute("""
                        SELECT i.section_number, i.title, i.description, i.punishment
                        FROM ipc_sections i
                        JOIN crime_ipc_mapping m ON i.id = m.ipc_section_id
                        WHERE m.crime_id = %s
                    """, (crime['id'],))
                    sections = cursor.fetchall()
                    
                    if sections:
                        logger.info("\nRelated IPC Sections:")
                        for section in sections:
                            logger.info(f"\nSection {section['section_number']}:")
                            logger.info(f"Title: {section['title']}")
                            logger.info(f"Description: {section['description']}")
                            logger.info(f"Punishment: {section['punishment']}")
            else:
                logger.info("No cyber crimes found in the database")

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
            logger.info("\nDatabase connection closed")

if __name__ == "__main__":
    check_cyber_crime() 