import mysql.connector
from mysql.connector import Error

def insert_crime_mappings():
    # Common crimes and their IPC sections
    crime_mappings = [
        {
            'name': 'Murder',
            'description': 'The unlawful killing of a human being with malice aforethought',
            'severity': 'heinous',
            'ipc_sections': ['302', '304']
        },
        {
            'name': 'Theft',
            'description': 'The act of taking someone else\'s property without their permission',
            'severity': 'major',
            'ipc_sections': ['378', '379', '380']
        },
        {
            'name': 'Robbery',
            'description': 'The act of taking property from a person by force or threat of force',
            'severity': 'heinous',
            'ipc_sections': ['390', '391', '392', '393', '394', '395', '396', '397', '398', '399', '400', '401', '402']
        },
        {
            'name': 'Assault',
            'description': 'The act of causing physical harm or injury to another person',
            'severity': 'major',
            'ipc_sections': ['351', '352', '353', '354', '355', '356', '357']
        },
        {
            'name': 'Fraud',
            'description': 'The act of deceiving someone for personal gain',
            'severity': 'major',
            'ipc_sections': ['415', '416', '417', '418', '419', '420']
        },
        {
            'name': 'Cyber Crime',
            'description': 'Criminal activities carried out using computers or the internet',
            'severity': 'major',
            'ipc_sections': ['66', '66A', '66B', '66C', '66D', '66E', '66F']
        },
        {
            'name': 'Domestic Violence',
            'description': 'Violence or abuse in a domestic setting',
            'severity': 'major',
            'ipc_sections': ['498A', '304B']
        },
        {
            'name': 'Kidnapping',
            'description': 'The act of taking someone away illegally by force',
            'severity': 'heinous',
            'ipc_sections': ['359', '360', '361', '362', '363', '364', '364A', '365', '366', '367', '368', '369']
        },
        {
            'name': 'Rape',
            'description': 'Sexual assault or non-consensual sexual intercourse',
            'severity': 'heinous',
            'ipc_sections': ['375', '376', '376A', '376B', '376C', '376D', '376E']
        }
    ]

    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="pass",
            database="legal_ai"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Insert crimes and create mappings
            for crime in crime_mappings:
                # Insert crime
                crime_query = """
                INSERT INTO crimes (name, description, severity)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                description = VALUES(description),
                severity = VALUES(severity)
                """
                
                crime_values = (crime['name'], crime['description'], crime['severity'])
                cursor.execute(crime_query, crime_values)
                connection.commit()
                
                # Get crime ID
                cursor.execute("SELECT id FROM crimes WHERE name = %s", (crime['name'],))
                crime_id_row = cursor.fetchone()
                crime_id = crime_id_row[0] if crime_id_row else None
                # Clear any unread results
                while cursor.nextset():
                    pass
                
                # Create mappings with IPC sections
                for section_number in crime['ipc_sections']:
                    # Get IPC section ID
                    cursor.execute("SELECT id FROM ipc_sections WHERE section_number = %s", (section_number,))
                    result = cursor.fetchone()
                    ipc_section_id = result[0] if result else None
                    # Clear any unread results
                    while cursor.nextset():
                        pass
                    
                    if ipc_section_id:
                        # Insert mapping
                        mapping_query = """
                        INSERT INTO crime_ipc_mapping (crime_id, ipc_section_id)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE crime_id = VALUES(crime_id)
                        """
                        
                        mapping_values = (crime_id, ipc_section_id)
                        cursor.execute(mapping_query, mapping_values)
                        connection.commit()
                
                print(f"Processed crime: {crime['name']}")
            
            print("All crime mappings processed successfully!")
            
    except Error as e:
        print(f"Error connecting to MySQL: {str(e)}")
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    print("Starting crime mappings insertion...")
    insert_crime_mappings()
    print("Process completed!") 