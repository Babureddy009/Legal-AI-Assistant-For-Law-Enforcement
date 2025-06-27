import mysql.connector
from mysql.connector import Error
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_cyber_crime_data():
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="pass",
            database="legal_ai"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Update IPC sections for cyber crimes
            updates = [
                ('66A', 'Sending offensive messages through communication service', 
                 'Imprisonment up to 3 years and fine'),
                ('66B', 'Dishonestly receiving stolen computer resource or communication device',
                 'Imprisonment up to 3 years or fine up to Rs. 1 lakh or both'),
                ('66C', 'Identity theft and cheating by personation using computer resource',
                 'Imprisonment up to 3 years and fine up to Rs. 1 lakh'),
                ('66D', 'Cheating by personation using computer resource',
                 'Imprisonment up to 3 years and fine up to Rs. 1 lakh'),
                ('66E', 'Violation of privacy',
                 'Imprisonment up to 3 years or fine up to Rs. 2 lakhs or both'),
                ('66F', 'Cyber terrorism',
                 'Imprisonment for life')
            ]
            
            for section, description, punishment in updates:
                cursor.execute("""
                    UPDATE ipc_sections 
                    SET description = %s,
                        punishment = %s
                    WHERE section_number = %s
                """, (description, punishment, section))
                logger.info(f"Updated Section {section}")
            
            connection.commit()
            logger.info("All cyber crime sections updated successfully")

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
    update_cyber_crime_data() 