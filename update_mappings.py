import mysql.connector
from mysql.connector import Error

def update_mappings():
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
            
            # Clear existing mappings
            cursor.execute("DELETE FROM crime_ipc_mapping")
            connection.commit()
            print("Cleared existing mappings")
            
            # Define crime-IPC mappings
            mappings = [
                ('Murder', '302'),
                ('Murder', '304'),  # Culpable homicide
                ('Theft', '378'),
                ('Robbery', '390'),
                ('Assault', '323'),
                ('Fraud', '420')
            ]
            
            # Insert new mappings
            for crime_name, section_number in mappings:
                # Get crime ID
                cursor.execute("SELECT id FROM crimes WHERE name = %s", (crime_name,))
                crime_id = cursor.fetchone()[0]
                
                # Get IPC section ID
                cursor.execute("SELECT id FROM ipc_sections WHERE section_number = %s", (section_number,))
                section_id = cursor.fetchone()[0]
                
                # Insert mapping
                insert_query = """
                    INSERT INTO crime_ipc_mapping (crime_id, ipc_section_id)
                    VALUES (%s, %s)
                """
                cursor.execute(insert_query, (crime_id, section_id))
                connection.commit()
                print(f"Mapped {crime_name} to IPC Section {section_number}")
            
            cursor.close()
            connection.close()
            print("\nDatabase update completed")
            
    except Error as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    update_mappings() 