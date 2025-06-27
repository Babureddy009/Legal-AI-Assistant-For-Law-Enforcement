import mysql.connector
from mysql.connector import Error
import logging
from tabulate import tabulate

# Configure logging
logging.basicConfig(level=logging.INFO)
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

def get_section_details(connection, section_number):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT section_number, title, description, punishment
            FROM ipc_sections
            WHERE section_number = %s
        """, (section_number,))
        result = cursor.fetchone()
        
        if result:
            print(f"\n=== IPC Section {result['section_number']} ===")
            print(f"Title: {result['title']}")
            print(f"\nDescription:\n{result['description']}")
            if result['punishment']:
                print(f"\nPunishment:\n{result['punishment']}")
        else:
            print(f"\nNo information found for IPC Section {section_number}")
            
    except Error as e:
        logger.error(f"Error fetching section details: {e}")
    finally:
        cursor.close()

def search_sections(connection, keyword):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT section_number, title, description
            FROM ipc_sections
            WHERE LOWER(title) LIKE %s 
            OR LOWER(description) LIKE %s
            LIMIT 10
        """, (f"%{keyword.lower()}%", f"%{keyword.lower()}%"))
        results = cursor.fetchall()
        
        if results:
            print(f"\n=== Search Results for '{keyword}' ===")
            print(tabulate(results, headers="keys", tablefmt="grid"))
        else:
            print(f"\nNo sections found matching '{keyword}'")
            
    except Error as e:
        logger.error(f"Error searching sections: {e}")
    finally:
        cursor.close()

def main():
    connection = connect_to_db()
    if not connection:
        return
    
    try:
        while True:
            print("\nIPC Section Query Tool")
            print("1. Get section details")
            print("2. Search sections")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == "1":
                section = input("Enter section number (e.g., 302): ")
                get_section_details(connection, section)
            elif choice == "2":
                keyword = input("Enter search keyword: ")
                search_sections(connection, keyword)
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please try again.")
                
    except Error as e:
        logger.error(f"Database error: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    main() 