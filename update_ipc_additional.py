import mysql.connector
from mysql.connector import Error

def update_additional_ipc_sections():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="pass",
            database="legal_ai"
        )
        
        if connection.is_connected():
            print("Connected to MySQL database")
            cursor = connection.cursor()
            
            # Additional IPC sections
            sections = [
                {
                    'number': '323',
                    'title': 'Punishment for voluntarily causing hurt',
                    'description': 'Whoever voluntarily causes hurt shall be punished with imprisonment or fine or both.',
                    'punishment': 'Imprisonment up to 1 year, or fine up to Rs. 1000, or both'
                },
                {
                    'number': '351',
                    'title': 'Assault',
                    'description': 'When a person makes any gesture or preparation, intending or knowing it to be likely that such gesture or preparation will cause any person present to apprehend that the person making the gesture or preparation is about to use criminal force to that person.',
                    'punishment': 'Imprisonment up to 3 months, or fine up to Rs. 500, or both'
                },
                {
                    'number': '420',
                    'title': 'Cheating and dishonestly inducing delivery of property',
                    'description': 'Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person.',
                    'punishment': 'Imprisonment up to 7 years, and fine'
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

if __name__ == "__main__":
    update_additional_ipc_sections() 