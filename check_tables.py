import mysql.connector
from mysql.connector import Error

def check_tables():
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
            
            # Get all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("\nTables in database:")
            for table in tables:
                print(f"- {table[0]}")
            
            # Check contents of each table
            for table in tables:
                table_name = table[0]
                print(f"\nContents of {table_name}:")
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                if rows:
                    # Get column names
                    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                    columns = [column[0] for column in cursor.fetchall()]
                    print("Columns:", columns)
                    # Print first 5 rows
                    for row in rows[:5]:
                        print(row)
                    print(f"Total rows: {len(rows)}")
                else:
                    print("Table is empty")
            
            cursor.close()
            connection.close()
            print("\nDatabase connection closed")
            
    except Error as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_tables() 