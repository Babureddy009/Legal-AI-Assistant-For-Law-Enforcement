import mysql.connector
from mysql.connector import Error
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_punishment_storage():
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
            
            # Check ipc_sections table structure
            logger.info("\nChecking IPC Sections table structure:")
            cursor.execute("SHOW COLUMNS FROM ipc_sections")
            columns = cursor.fetchall()
            for column in columns:
                logger.info(f"Column: {column['Field']}, Type: {column['Type']}, Null: {column['Null']}, Key: {column['Key']}")
            
            # Check if punishment exists in crimes table
            logger.info("\nChecking if punishment exists in crimes table:")
            cursor.execute("SHOW COLUMNS FROM crimes")
            columns = cursor.fetchall()
            has_punishment = False
            for column in columns:
                if column['Field'].lower() == 'punishment':
                    has_punishment = True
                logger.info(f"Column: {column['Field']}, Type: {column['Type']}, Null: {column['Null']}, Key: {column['Key']}")
            
            # Get sample data from ipc_sections
            logger.info("\nSample data from ipc_sections:")
            cursor.execute("""
                SELECT section_number, title, description, punishment
                FROM ipc_sections
                LIMIT 3
            """)
            rows = cursor.fetchall()
            for row in rows:
                logger.info("\nSection Details:")
                for key, value in row.items():
                    logger.info(f"{key}: {value}")

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
    check_punishment_storage() 