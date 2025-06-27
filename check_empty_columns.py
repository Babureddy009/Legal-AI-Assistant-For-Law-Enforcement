import mysql.connector
from mysql.connector import Error
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_empty_columns():
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
            
            # Get list of tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            empty_columns = {}
            
            for table in tables:
                table_name = table[list(table.keys())[0]]
                logger.info(f"\nChecking table: {table_name}")
                
                # Get column names
                cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                columns = cursor.fetchall()
                
                for column in columns:
                    column_name = column['Field']
                    # Skip primary key and foreign key columns
                    if column['Key'] in ['PRI', 'MUL']:
                        continue
                        
                    # Check if column is empty
                    cursor.execute(f"""
                        SELECT COUNT(*) as total_rows,
                               COUNT({column_name}) as non_null_rows
                        FROM {table_name}
                    """)
                    result = cursor.fetchone()
                    
                    if result['non_null_rows'] == 0:
                        if table_name not in empty_columns:
                            empty_columns[table_name] = []
                        empty_columns[table_name].append(column_name)
                        logger.info(f"  Column '{column_name}' is empty")
            
            return empty_columns

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
    empty_columns = check_empty_columns()
    if empty_columns:
        logger.info("\nEmpty columns found:")
        for table, columns in empty_columns.items():
            logger.info(f"\nTable: {table}")
            for column in columns:
                logger.info(f"  - {column}")
    else:
        logger.info("\nNo empty columns found") 