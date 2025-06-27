import mysql.connector
from mysql.connector import Error

def update_ipc_sections():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root1",
            password="pass",
            database="legal_ai"
        )
        
        if connection.is_connected():
            print("Connected to MySQL database")
            cursor = connection.cursor()
            
            # Update important IPC sections
            sections = [
                {
                    'number': '302',
                    'title': 'Murder',
                    'description': 'Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.',
                    'punishment': 'Death, or imprisonment for life, and fine'
                },
                {
                    'number': '304',
                    'title': 'Culpable Homicide not amounting to Murder',
                    'description': 'Whoever commits culpable homicide not amounting to murder shall be punished with imprisonment for life, or imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine.',
                    'punishment': 'Imprisonment for life, or imprisonment up to 10 years, and fine'
                },
                {
                    'number': '378',
                    'title': 'Theft',
                    'description': 'Whoever, intending to take dishonestly any moveable property out of the possession of any person without that person\'s consent, moves that property in order to such taking, is said to commit theft.',
                    'punishment': 'Imprisonment up to 3 years, or fine, or both'
                },
                {
                    'number': '390',
                    'title': 'Robbery',
                    'description': 'In all robbery there is either theft or extortion. When theft is robbery, it is robbery when the offender voluntarily causes or attempts to cause to any person death or hurt or wrongful restraint, or fear of instant death or of instant hurt or of instant wrongful restraint.',
                    'punishment': 'Imprisonment up to 10 years, and fine'
                }
            ]
            
            for section in sections:
                update_query = """
                    UPDATE ipc_sections 
                    SET title = %s,
                        description = %s,
                        punishment = %s
                    WHERE section_number = %s
                """
                values = (
                    section['title'],
                    section['description'],
                    section['punishment'],
                    section['number']
                )
                cursor.execute(update_query, values)
                connection.commit()
                print(f"Updated IPC Section {section['number']}")
            
            cursor.close()
            connection.close()
            print("\nDatabase update completed")
            
    except Error as e:
        print(f"Error: {str(e)}")

# Connect to the database
conn = mysql.connector.connect(
    host="localhost",
    user="root1",
    password="pass",
    database="legal_ai"
)
cursor = conn.cursor(dictionary=True)

# Find IPC sections with missing or incomplete data
def find_incomplete_ipc_sections():
    query = """
        SELECT section_number, title, description, punishment
        FROM ipc_sections
        WHERE title = '' OR description = '' OR punishment = ''
           OR title IS NULL OR description IS NULL OR punishment IS NULL
    """
    cursor.execute(query)
    results = cursor.fetchall()
    if not results:
        print("All IPC sections have complete data.")
    else:
        print("Incomplete IPC sections:")
        for row in results:
            print(f"Section {row['section_number']}: Title='{row['title']}', Description='{row['description']}', Punishment='{row['punishment']}'")
    return results

# Placeholder for updating a section (to be filled with real data)
def update_ipc_section(section_number, title, description, punishment):
    query = """
        UPDATE ipc_sections
        SET title = %s, description = %s, punishment = %s
        WHERE section_number = %s
    """
    cursor.execute(query, (title, description, punishment, section_number))
    conn.commit()
    print(f"Updated IPC section {section_number}.")

# Update IPC Section 302
cursor.execute("""
    UPDATE ipc_sections
    SET title = %s,
        description = %s,
        punishment = %s
    WHERE section_number = %s
""", (
    'Murder',
    'Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.',
    'Death, or imprisonment for life, and fine',
    '302'
))

# Update IPC Section 304
cursor.execute("""
    UPDATE ipc_sections
    SET title = %s,
        description = %s,
        punishment = %s
    WHERE section_number = %s
""", (
    'Culpable Homicide not amounting to Murder',
    'Whoever commits culpable homicide not amounting to murder shall be punished with imprisonment for life, or imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine.',
    'Imprisonment for life, or imprisonment up to 10 years, and fine',
    '304'
))

conn.commit()
print("Updated IPC sections 302 and 304 with correct punishment info.")

# Find and print all sections with empty punishment fields
cursor.execute("""
    SELECT section_number, title FROM ipc_sections WHERE punishment = '' OR punishment IS NULL
""")
results = cursor.fetchall()
if results:
    print("Sections with empty punishment fields:")
    for row in results:
        print(f"Section {row['section_number']}: {row['title']}")
else:
    print("All sections have punishment info.")

cursor.close()
conn.close()

if __name__ == "__main__":
    update_ipc_sections()
    incomplete_sections = find_incomplete_ipc_sections()
    # Example usage to update a section (uncomment and fill in real data):
    # update_ipc_section('212', 'Harbouring offender', 'Whoever harbours or conceals a person whom he knows or has reason to believe to be an offender...', 'Imprisonment for up to 5 years, or fine, or both.')

    cursor.close()
    conn.close() 