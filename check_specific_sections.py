import mysql.connector
from mysql.connector import Error
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_specific_sections():
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
            
            # Check specific sections
            sections = ['299', '300', '301', '302']
            for section in sections:
                cursor.execute("""
                    SELECT section_number, title, description, punishment,
                           LENGTH(punishment) as punishment_length,
                           punishment IS NULL as is_null,
                           punishment = '' as is_empty,
                           TRIM(punishment) = '' as is_whitespace
                    FROM ipc_sections 
                    WHERE section_number = %s
                """, (section,))
                result = cursor.fetchone()
                
                if result:
                    logger.info(f"\nSection {section}:")
                    logger.info(f"Title: {result['title']}")
                    logger.info(f"Description length: {len(result['description']) if result['description'] else 0}")
                    logger.info(f"Punishment length: {result['punishment_length']}")
                    logger.info(f"Is NULL: {result['is_null']}")
                    logger.info(f"Is empty string: {result['is_empty']}")
                    logger.info(f"Is whitespace only: {result['is_whitespace']}")
                    logger.info(f"Raw punishment value: '{result['punishment']}'")

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
    check_specific_sections() 