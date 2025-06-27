import mysql.connector
from tabulate import tabulate

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root1",
        password="pass",
        database="legal_ai"
    )

def analyze_database():
    conn = connect_to_db()
    cursor = conn.cursor()
    
    print("\n=== IPC Database Analysis ===\n")
    
    # 1. Total number of sections
    cursor.execute("SELECT COUNT(*) FROM ipc_sections")
    total_sections = cursor.fetchone()[0]
    print(f"Total number of IPC sections: {total_sections}")
    
    # 2. Sections with missing punishments
    cursor.execute("""
        SELECT COUNT(*) 
        FROM ipc_sections 
        WHERE punishment IS NULL OR punishment = ''
    """)
    missing_punishments = cursor.fetchone()[0]
    print(f"Sections with missing punishments: {missing_punishments}")
    print(f"Percentage complete: {((total_sections - missing_punishments) / total_sections * 100):.2f}%")
    
    # 3. Sections with missing titles
    cursor.execute("""
        SELECT COUNT(*) 
        FROM ipc_sections 
        WHERE title IS NULL OR title = ''
    """)
    missing_titles = cursor.fetchone()[0]
    print(f"Sections with missing titles: {missing_titles}")
    
    # 4. Sections with missing descriptions
    cursor.execute("""
        SELECT COUNT(*) 
        FROM ipc_sections 
        WHERE description IS NULL OR description = ''
    """)
    missing_descriptions = cursor.fetchone()[0]
    print(f"Sections with missing descriptions: {missing_descriptions}")
    
    # 5. Breakdown of section types
    cursor.execute("""
        SELECT 
            CASE 
                WHEN section_number REGEXP '^[0-9]+$' THEN 'Numeric'
                WHEN section_number REGEXP '^[0-9]+[A-Z]+$' THEN 'Alphanumeric'
                ELSE 'Other'
            END as section_type,
            COUNT(*) as count
        FROM ipc_sections
        GROUP BY section_type
    """)
    section_types = cursor.fetchall()
    print("\nSection Type Breakdown:")
    print(tabulate(section_types, headers=['Type', 'Count'], tablefmt='grid'))
    
    # 6. Sample of sections with missing punishments
    print("\nSample of sections with missing punishments:")
    cursor.execute("""
        SELECT section_number, title 
        FROM ipc_sections 
        WHERE punishment IS NULL OR punishment = ''
        LIMIT 10
    """)
    missing_samples = cursor.fetchall()
    print(tabulate(missing_samples, headers=['Section', 'Title'], tablefmt='grid'))
    
    # 7. Sample of complete sections
    print("\nSample of complete sections:")
    cursor.execute("""
        SELECT section_number, title, 
               LENGTH(punishment) as punishment_length
        FROM ipc_sections 
        WHERE punishment IS NOT NULL AND punishment != ''
        LIMIT 10
    """)
    complete_samples = cursor.fetchall()
    print(tabulate(complete_samples, headers=['Section', 'Title', 'Punishment Length'], tablefmt='grid'))
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    analyze_database() 