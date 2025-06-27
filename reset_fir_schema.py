import mysql.connector
from config import get_db_config

SCHEMA_FILES = ['schema.sql', 'fir_schema.sql']

# List of objects to drop in order (views first, then tables, respecting FKs)
OBJECTS_TO_DROP = [
    'DROP VIEW IF EXISTS fir_report_details;',
    'DROP TABLE IF EXISTS crime_ipc_mapping;',
    'DROP TABLE IF EXISTS crimes;',
    'DROP TABLE IF EXISTS ipc_sections;',
    'DROP TABLE IF EXISTS fir_reports;',
    'DROP TABLE IF EXISTS fir_complainants;'
]

def drop_objects(cursor):
    for stmt in OBJECTS_TO_DROP:
        try:
            cursor.execute(stmt)
            print(f"Executed: {stmt.strip()}")
        except Exception as e:
            print(f"Warning: Could not execute {stmt.strip()}: {e}")

def execute_schema():
    db_config = get_db_config()
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        drop_objects(cursor)
        for schema_file in SCHEMA_FILES:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            for stmt in statements:
                try:
                    cursor.execute(stmt)
                except Exception as e:
                    print(f"Error executing statement: {stmt[:80]}...\n{e}")
        conn.commit()
        cursor.close()
        conn.close()
        print('All schemas reset and executed successfully.')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    execute_schema() 