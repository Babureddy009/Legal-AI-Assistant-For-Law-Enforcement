import mysql.connector

def run_sql_file(cursor, filename):
    with open(filename, 'r') as f:
        sql = f.read()
    # Split on semicolon, filter out empty statements
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    for stmt in statements:
        cursor.execute(stmt)

def main():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'pass',
        'database': 'legal_ai'
    }
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    run_sql_file(cursor, 'chathistory.sql')
    conn.commit()
    cursor.close()
    conn.close()
    print('Chat history tables created/updated successfully!')

if __name__ == '__main__':
    main() 