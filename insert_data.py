import json
from db_utils import get_cursor
from config import get_db_config

def create_database():
    try:
        with get_cursor() as (cursor, connection):
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS legal_ai")
            print("Database created successfully!")
            
            # Use the database
            cursor.execute("USE legal_ai")
            
            # Drop existing tables
            cursor.execute("DROP TABLE IF EXISTS crime_ipc_mapping")
            cursor.execute("DROP TABLE IF EXISTS crimes")
            cursor.execute("DROP TABLE IF EXISTS ipc_sections")
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ipc_sections (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    section_number VARCHAR(10) UNIQUE NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    punishment TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_section_number (section_number)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crimes (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    severity ENUM('minor', 'major', 'heinous') NOT NULL,
                    category ENUM('violent', 'property', 'financial', 'cyber', 'sexual', 'drug', 'other') NOT NULL,
                    bailable BOOLEAN NOT NULL,
                    cognizable BOOLEAN NOT NULL,
                    compoundable BOOLEAN NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_crime_name (name),
                    INDEX idx_crime_category (category),
                    INDEX idx_crime_severity (severity)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crime_ipc_mapping (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    crime_id INT NOT NULL,
                    ipc_section_id INT NOT NULL,
                    is_primary BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (crime_id) REFERENCES crimes(id),
                    FOREIGN KEY (ipc_section_id) REFERENCES ipc_sections(id)
                )
            """)
            
            print("Tables created successfully!")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def insert_data():
    try:
        # Read the JSON data
        with open('crimes_data.json', 'r') as file:
            data = json.load(file)
        
        with get_cursor(dictionary=True) as (cursor, connection):
            
            # Insert crimes
            for crime in data['crimes']:
                # Insert crime
                cursor.execute("""
                    INSERT INTO crimes (name, description, severity, category, bailable, cognizable, compoundable)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    crime['name'],
                    crime['description'],
                    crime['severity'],
                    crime['category'],
                    crime['bailable'],
                    crime['cognizable'],
                    crime['compoundable']
                ))
                crime_id = cursor.lastrowid
                
                # Insert IPC sections if they don't exist and create mappings
                for section_number in crime['ipc_sections']:
                    # Check if IPC section exists
                    cursor.execute("""
                        SELECT id FROM ipc_sections WHERE section_number = %s
                    """, (section_number,))
                    section = cursor.fetchone()
                    
                    if not section:
                        # Insert new IPC section
                        cursor.execute("""
                            INSERT INTO ipc_sections (section_number, title, description, punishment)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            section_number,
                            f"IPC Section {section_number}",
                            f"Description for IPC Section {section_number}",
                            f"Punishment for IPC Section {section_number}"
                        ))
                        section_id = cursor.lastrowid
                    else:
                        section_id = section['id']
                    
                    # Create mapping
                    cursor.execute("""
                        INSERT INTO crime_ipc_mapping (crime_id, ipc_section_id)
                        VALUES (%s, %s)
                    """, (crime_id, section_id))
            
            connection.commit()
            print("Data inserted successfully!")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    create_database()
    insert_data() 