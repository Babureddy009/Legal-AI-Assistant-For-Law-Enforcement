import mysql.connector
from config import get_db_config

SCHEMA_FILE = 'fir_schema.sql'

def execute_schema():
    db_config = get_db_config()
    try:
        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Split on semicolon for multiple statements, but keep semicolons in view/table definitions
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        for stmt in statements:
            try:
                cursor.execute(stmt)
            except Exception as e:
                print(f"Error executing statement: {stmt[:80]}...\n{e}")
        conn.commit()
        cursor.close()
        conn.close()
        print('FIR schema executed successfully.')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    execute_schema() 