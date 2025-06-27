import mysql.connector
from mysql.connector import Error
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_schema():
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
            
            # Check database version
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            logger.info(f"Database version: {version['VERSION()']}")
            
            # Get list of tables
            logger.info("\nChecking tables in database:")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            for table in tables:
                table_name = table[list(table.keys())[0]]
                logger.info(f"\nTable: {table_name}")
                
                # Get table schema
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                logger.info("Columns:")
                for column in columns:
                    logger.info(f"  {column['Field']}: {column['Type']} (Null: {column['Null']}, Key: {column['Key']}, Default: {column['Default']})")
                
                # Get indexes
                cursor.execute(f"SHOW INDEX FROM {table_name}")
                indexes = cursor.fetchall()
                logger.info("Indexes:")
                for index in indexes:
                    logger.info(f"  {index['Key_name']}: Column: {index['Column_name']}, Non_unique: {index['Non_unique']}")
                
                # Get foreign keys
                cursor.execute(f"""
                    SELECT 
                        CONSTRAINT_NAME,
                        COLUMN_NAME,
                        REFERENCED_TABLE_NAME,
                        REFERENCED_COLUMN_NAME
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = '{table_name}'
                    AND REFERENCED_TABLE_NAME IS NOT NULL
                """)
                foreign_keys = cursor.fetchall()
                if foreign_keys:
                    logger.info("Foreign Keys:")
                    for fk in foreign_keys:
                        logger.info(f"  {fk['CONSTRAINT_NAME']}: {fk['COLUMN_NAME']} -> {fk['REFERENCED_TABLE_NAME']}({fk['REFERENCED_COLUMN_NAME']})")
                
                # Get sample data count
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()
                logger.info(f"Row count: {count['count']}")

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
    check_schema() 