import mysql.connector
from mysql.connector import Error
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def remove_empty_columns():
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root1",
            password="pass",
            database="legal_ai"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Columns to remove from user_interactions table
            empty_columns = [
                'bot_response',
                'confidence_score',
                'created_at'
            ]
            
            for column in empty_columns:
                try:
                    # Remove column
                    cursor.execute(f"ALTER TABLE user_interactions DROP COLUMN {column}")
                    logger.info(f"Successfully removed column '{column}' from user_interactions table")
                except Error as e:
                    logger.error(f"Error removing column '{column}': {str(e)}")
            
            connection.commit()
            logger.info("\nAll empty columns have been removed")

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
    remove_empty_columns() 