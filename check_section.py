import mysql.connector
from mysql.connector import Error

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="pass",
        database="legal_ai",
        autocommit=True
    )

def check_section(section_number):
    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)
        
        # Check IPC section
        print(f"\n=== Checking IPC Section {section_number} ===")
        cursor.execute("""
            SELECT section_number, title, description, punishment, updated_at
            FROM ipc_sections 
            WHERE section_number = %s
        """, (section_number,))
        section = cursor.fetchone()
        
        if section:
            print(f"\nSection Number: {section['section_number']}")
            print(f"Title: {section['title']}")
            print(f"Description: {section['description']}")
            print(f"Punishment: {section['punishment']}")
            print(f"Last Updated: {section['updated_at']}")
            
            # Check related crimes
            cursor.execute("""
                SELECT c.name, c.description, c.severity
                FROM crimes c
                JOIN crime_ipc_mapping m ON c.id = m.crime_id
                JOIN ipc_sections i ON i.id = m.ipc_section_id
                WHERE i.section_number = %s
            """, (section_number,))
            crimes = cursor.fetchall()
            
            if crimes:
                print("\nRelated Crimes:")
                for crime in crimes:
                    print(f"\nCrime: {crime['name']}")
                    print(f"Description: {crime['description']}")
                    print(f"Severity: {crime['severity']}")
        else:
            print(f"Section {section_number} not found in database")
        
    except Error as e:
        print(f"Database error: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        check_section(sys.argv[1])
    else:
        print("Usage: python check_section.py <section_number>") 