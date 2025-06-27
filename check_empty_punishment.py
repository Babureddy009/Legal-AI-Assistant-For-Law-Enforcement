import mysql.connector
from mysql.connector import Error
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_empty_punishment():
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
            
            # Check total rows
            cursor.execute("SELECT COUNT(*) as total FROM ipc_sections")
            total_rows = cursor.fetchone()['total']
            logger.info(f"\nTotal IPC sections: {total_rows}")
            
            # Check rows with empty or NULL punishment
            cursor.execute("""
                SELECT COUNT(*) as empty_count 
                FROM ipc_sections 
                WHERE punishment IS NULL 
                   OR punishment = '' 
                   OR TRIM(punishment) = ''
            """)
            empty_count = cursor.fetchone()['empty_count']
            logger.info(f"IPC sections with empty punishment: {empty_count}")
            
            # Get sample of sections with empty punishment
            if empty_count > 0:
                logger.info("\nSample sections with empty punishment:")
                cursor.execute("""
                    SELECT section_number, title 
                    FROM ipc_sections 
                    WHERE punishment IS NULL 
                       OR punishment = '' 
                       OR TRIM(punishment) = ''
                    LIMIT 5
                """)
                empty_sections = cursor.fetchall()
                for section in empty_sections:
                    logger.info(f"Section {section['section_number']}: {section['title']}")
            
            # Get sample of sections with non-empty punishment
            logger.info("\nSample sections with punishment data:")
            cursor.execute("""
                SELECT section_number, punishment 
                FROM ipc_sections 
                WHERE punishment IS NOT NULL 
                  AND punishment != '' 
                  AND TRIM(punishment) != ''
                LIMIT 3
            """)
            non_empty_sections = cursor.fetchall()
            for section in non_empty_sections:
                logger.info(f"\nSection {section['section_number']}:")
                logger.info(f"Punishment: {section['punishment']}")

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
    check_empty_punishment() 