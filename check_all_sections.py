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

def check_all_sections():
    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)
        
        # Get overall statistics
        print("\n=== Overall Database Status ===")
        cursor.execute("""
            SELECT 
                COUNT(*) as total_sections,
                SUM(CASE WHEN title = 'A Lawyers Reference' THEN 1 ELSE 0 END) as placeholder_titles,
                SUM(CASE WHEN description IS NULL OR description = '' THEN 1 ELSE 0 END) as missing_descriptions,
                SUM(CASE WHEN punishment IS NULL OR punishment = '' THEN 1 ELSE 0 END) as missing_punishments,
                SUM(CASE WHEN updated_at IS NULL THEN 1 ELSE 0 END) as never_updated
            FROM ipc_sections
        """)
        stats = cursor.fetchone()
        print(f"Total Sections: {stats['total_sections']}")
        print(f"Sections with placeholder titles: {stats['placeholder_titles']}")
        print(f"Sections missing descriptions: {stats['missing_descriptions']}")
        print(f"Sections missing punishments: {stats['missing_punishments']}")
        print(f"Sections never updated: {stats['never_updated']}")
        
        # Get sections with placeholder data
        print("\n=== Sections with Placeholder Data ===")
        cursor.execute("""
            SELECT section_number, title, 
                   CASE WHEN description IS NULL OR description = '' THEN 'Missing' ELSE 'Present' END as description_status,
                   CASE WHEN punishment IS NULL OR punishment = '' THEN 'Missing' ELSE 'Present' END as punishment_status,
                   updated_at
            FROM ipc_sections
            WHERE title = 'A Lawyers Reference'
               OR description IS NULL 
               OR description = ''
               OR punishment IS NULL 
               OR punishment = ''
            ORDER BY 
                CASE 
                    WHEN section_number REGEXP '^[0-9]+$' THEN CAST(section_number AS UNSIGNED)
                    ELSE 999999
                END,
                section_number
        """)
        placeholder_sections = cursor.fetchall()
        
        if placeholder_sections:
            print("\nSections needing updates:")
            for section in placeholder_sections:
                print(f"\nSection {section['section_number']}:")
                print(f"Title: {section['title']}")
                print(f"Description: {section['description_status']}")
                print(f"Punishment: {section['punishment_status']}")
                print(f"Last Updated: {section['updated_at']}")
        else:
            print("No sections with placeholder data found!")
        
        # Check crime mappings
        print("\n=== Crime Mappings Status ===")
        cursor.execute("""
            SELECT c.name as crime, COUNT(m.id) as section_count
            FROM crimes c
            LEFT JOIN crime_ipc_mapping m ON c.id = m.crime_id
            GROUP BY c.name
        """)
        mappings = cursor.fetchall()
        print("\nCrime to Section Mappings:")
        for mapping in mappings:
            print(f"{mapping['crime']}: {mapping['section_count']} sections")
        
    except Error as e:
        print(f"Database error: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_all_sections() 