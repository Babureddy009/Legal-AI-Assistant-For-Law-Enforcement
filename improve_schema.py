import mysql.connector
from mysql.connector import Error
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def improve_schema():
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
            
            # Add created_at timestamp to crime_ipc_mapping if it doesn't exist
            try:
                cursor.execute("""
                    ALTER TABLE crime_ipc_mapping 
                    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """)
                logger.info("Added created_at timestamp to crime_ipc_mapping table")
            except Error as e:
                logger.warning(f"Could not add created_at timestamp: {str(e)}")

            # Add composite index on crime_id and ipc_section_id
            try:
                cursor.execute("""
                    ALTER TABLE crime_ipc_mapping 
                    ADD INDEX idx_crime_ipc (crime_id, ipc_section_id)
                """)
                logger.info("Added composite index on crime_id and ipc_section_id")
            except Error as e:
                logger.warning(f"Could not add composite index: {str(e)}")

            # Add UNIQUE constraint on crime_id and ipc_section_id
            try:
                cursor.execute("""
                    ALTER TABLE crime_ipc_mapping 
                    ADD CONSTRAINT uc_crime_ipc UNIQUE (crime_id, ipc_section_id)
                """)
                logger.info("Added UNIQUE constraint on crime_id and ipc_section_id")
            except Error as e:
                logger.warning(f"Could not add UNIQUE constraint: {str(e)}")

            connection.commit()
            logger.info("Successfully improved database schema")

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
    improve_schema() 