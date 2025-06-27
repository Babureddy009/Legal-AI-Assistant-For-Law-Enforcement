import mysql.connector
from mysql.connector import Error

def test_database_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="pass",
            database="legal_ai"
        )
        
        if connection.is_connected():
            print("Successfully connected to MySQL database")
            
            # Test query for murder-related sections
            cursor = connection.cursor(dictionary=True)
            
            # First, check the crimes table
            print("\nChecking crimes table:")
            cursor.execute("SELECT * FROM crimes WHERE name LIKE '%murder%'")
            crimes = cursor.fetchall()
            print(f"Found {len(crimes)} crimes related to murder")
            for crime in crimes:
                print(f"Crime: {crime['name']}, Description: {crime['description']}")
            
            # Then, check the ipc_sections table
            print("\nChecking ipc_sections table:")
            cursor.execute("SELECT * FROM ipc_sections WHERE section_number = '302'")
            sections = cursor.fetchall()
            print(f"Found {len(sections)} IPC sections")
            for section in sections:
                print(f"Section {section['section_number']}: {section['title']}")
                print(f"Description: {section['description']}")
                print(f"Punishment: {section['punishment']}")
            
            cursor.close()
            connection.close()
            print("\nDatabase connection closed")
            
    except Error as e:
        print(f"Error connecting to MySQL: {str(e)}")

if __name__ == "__main__":
    test_database_connection() 