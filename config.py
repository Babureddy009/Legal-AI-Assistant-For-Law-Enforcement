import os

def get_db_config():
    return {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'root'),
        'password': os.environ.get('DB_PASSWORD', 'pass'),
        'database': os.environ.get('DB_NAME', 'legal_ai'),
        'autocommit': True
    } 