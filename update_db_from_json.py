import json
import mysql.connector

# Load the cleaned JSON data
with open('ipc_sections.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="pass",
    database="legal_ai"
)
cursor = conn.cursor()

for section in data.get('sections', []):
    section_number = section.get('section_number')
    title = section.get('title', '')
    description = section.get('description', '')
    punishment = section.get('punishment', '')

    # Check if section exists
    cursor.execute("SELECT id FROM ipc_sections WHERE section_number = %s", (section_number,))
    exists = cursor.fetchone()

    if exists:
        # Update existing record
        cursor.execute(
            """
            UPDATE ipc_sections SET title=%s, description=%s, punishment=%s WHERE section_number=%s
            """,
            (title, description, punishment, section_number)
        )
    else:
        # Insert new record
        cursor.execute(
            """
            INSERT INTO ipc_sections (section_number, title, description, punishment) VALUES (%s, %s, %s, %s)
            """,
            (section_number, title, description, punishment)
        )
    conn.commit()

cursor.close()
conn.close()
print('MySQL database updated from ipc_sections.json.') 