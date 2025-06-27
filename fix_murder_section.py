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

def update_murder_section():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        # Update Section 302 with correct murder data
        cursor.execute("""
            UPDATE ipc_sections 
            SET title = 'Murder',
                description = 'Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.',
                punishment = 'Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.',
                updated_at = CURRENT_TIMESTAMP
            WHERE section_number = '302'
        """)
        
        print("Successfully updated Section 302 (Murder)")
        
        # Verify the update
        cursor.execute("""
            SELECT section_number, title, description, punishment, updated_at
            FROM ipc_sections 
            WHERE section_number = '302'
        """)
        section = cursor.fetchone()
        
        if section:
            print("\nUpdated Section Data:")
            print(f"Section Number: {section[0]}")
            print(f"Title: {section[1]}")
            print(f"Description: {section[2]}")
            print(f"Punishment: {section[3]}")
            print(f"Last Updated: {section[4]}")
        
    except Error as e:
        print(f"Database error: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    update_murder_section() 