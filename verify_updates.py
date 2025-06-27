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

def verify_updates():
    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)
        
        # Check IPC sections
        print("\n=== IPC Sections Status ===")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN title != 'A Lawyers Reference' THEN 1 ELSE 0 END) as updated,
                SUM(CASE WHEN description IS NOT NULL AND description != '' THEN 1 ELSE 0 END) as with_description,
                SUM(CASE WHEN punishment IS NOT NULL AND punishment != '' THEN 1 ELSE 0 END) as with_punishment
            FROM ipc_sections
        """)
        stats = cursor.fetchone()
        print(f"Total sections: {stats['total']}")
        print(f"Updated titles: {stats['updated']}")
        print(f"Sections with description: {stats['with_description']}")
        print(f"Sections with punishment: {stats['with_punishment']}")
        
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
        
        # Show sample of updated sections
        print("\n=== Sample Updated Sections ===")
        cursor.execute("""
            SELECT section_number, title, 
                   LEFT(description, 100) as description_preview,
                   LEFT(punishment, 100) as punishment_preview
            FROM ipc_sections
            WHERE title != 'A Lawyers Reference'
            ORDER BY RAND()
            LIMIT 5
        """)
        samples = cursor.fetchall()
        for sample in samples:
            print(f"\nSection {sample['section_number']}:")
            print(f"Title: {sample['title']}")
            print(f"Description: {sample['description_preview']}...")
            print(f"Punishment: {sample['punishment_preview']}...")
        
    except Error as e:
        print(f"Database error: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    verify_updates() 