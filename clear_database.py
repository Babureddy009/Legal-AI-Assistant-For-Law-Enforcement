import mysql.connector
from mysql.connector import Error

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root1",
        password="pass",
        database="legal_ai",
        autocommit=True
    )

def clear_database():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        # Clear crime_ipc_mapping table
        cursor.execute("DELETE FROM crime_ipc_mapping")
        print("Cleared crime_ipc_mapping table")
        
        # Clear ipc_sections table
        cursor.execute("DELETE FROM ipc_sections")
        print("Cleared ipc_sections table")
        
        # Reset auto-increment counters
        cursor.execute("ALTER TABLE crime_ipc_mapping AUTO_INCREMENT = 1")
        cursor.execute("ALTER TABLE ipc_sections AUTO_INCREMENT = 1")
        print("Reset auto-increment counters")
        
    except Error as e:
        print(f"Error clearing database: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("Database cleared successfully!")

if __name__ == "__main__":
    clear_database() 