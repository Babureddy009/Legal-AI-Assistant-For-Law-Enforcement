import mysql.connector
from mysql.connector import Error
import logging
from tabulate import tabulate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root1",
            password="pass",
            database="legal_ai"
        )
        if connection.is_connected():
            logger.info("Successfully connected to MySQL database")
            return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL database: {e}")
        return None

def check_table_structure(connection):
    """Check the structure of the ipc_sections table"""
    try:
        cursor = connection.cursor()
        cursor.execute("DESCRIBE ipc_sections")
        columns = cursor.fetchall()
        logger.info("\nTable Structure:")
        print(tabulate(columns, headers=['Field', 'Type', 'Null', 'Key', 'Default', 'Extra'], tablefmt='grid'))
        cursor.close()
    except Error as e:
        logger.error(f"Error checking table structure: {e}")

def show_sample_records(connection, limit=5):
    """Show sample records from the ipc_sections table"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT section_number, title, description, punishment 
            FROM ipc_sections 
            LIMIT %s
        """, (limit,))
        records = cursor.fetchall()
        logger.info(f"\nSample Records (showing {limit}):")
        print(tabulate(records, headers=['Section', 'Title', 'Description', 'Punishment'], tablefmt='grid'))
        cursor.close()
    except Error as e:
        logger.error(f"Error showing sample records: {e}")

def check_empty_fields(connection):
    """Check for empty fields in the ipc_sections table"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN title IS NULL OR title = '' THEN 1 ELSE 0 END) as empty_titles,
                SUM(CASE WHEN description IS NULL OR description = '' THEN 1 ELSE 0 END) as empty_descriptions,
                SUM(CASE WHEN punishment IS NULL OR punishment = '' THEN 1 ELSE 0 END) as empty_punishments
            FROM ipc_sections
        """)
        result = cursor.fetchone()
        logger.info("\nEmpty Fields Check:")
        print(tabulate([result], headers=['Total Records', 'Empty Titles', 'Empty Descriptions', 'Empty Punishments'], tablefmt='grid'))
        cursor.close()
    except Error as e:
        logger.error(f"Error checking empty fields: {e}")

def check_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root1",
            password="pass",
            database="legal_ai"
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Check tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            logger.info("Available tables:")
            for table in tables:
                table_name = list(table.values())[0]
                logger.info(f"- {table_name}")
                
                # Get table structure
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                logger.info(f"  Columns in {table_name}:")
                for column in columns:
                    logger.info(f"  - {column['Field']}: {column['Type']}")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()['count']
                logger.info(f"  Number of rows: {count}")
                
                # Show sample data for crimes table
                if table_name == 'crimes':
                    cursor.execute("SELECT * FROM crimes LIMIT 5")
                    crimes = cursor.fetchall()
                    logger.info("  Sample crimes:")
                    for crime in crimes:
                        logger.info(f"  - {crime}")
                
                # Show sample data for ipc_sections table
                if table_name == 'ipc_sections':
                    cursor.execute("SELECT * FROM ipc_sections LIMIT 5")
                    sections = cursor.fetchall()
                    logger.info("  Sample IPC sections:")
                    for section in sections:
                        logger.info(f"  - {section}")
                
                # Show sample data for crime_ipc_mapping table
                if table_name == 'crime_ipc_mapping':
                    cursor.execute("SELECT * FROM crime_ipc_mapping LIMIT 5")
                    mappings = cursor.fetchall()
                    logger.info("  Sample crime-IPC mappings:")
                    for mapping in mappings:
                        logger.info(f"  - {mapping}")
                
                logger.info("")  # Empty line for readability

    except Error as e:
        logger.error(f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def main():
    connection = connect_to_db()
    if not connection:
        return
    
    try:
        check_table_structure(connection)
        show_sample_records(connection)
        check_empty_fields(connection)
    except Exception as e:
        logger.error(f"Error in main process: {e}")
    finally:
        connection.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    check_database() 