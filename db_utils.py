import mysql.connector
from mysql.connector import Error
from config import get_db_config
from contextlib import contextmanager

@contextmanager
def get_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**get_db_config())
        yield connection
    finally:
        if connection and connection.is_connected():
            connection.close()

@contextmanager
def get_cursor(dictionary=False):
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=dictionary)
        try:
            yield cursor, conn
        finally:
            cursor.close() 