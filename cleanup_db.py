import mysql.connector
from mysql.connector import Error

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root1",
        password="pass",
        database="legal_ai"
    )

def cleanup_database():
    conn = connect_to_db()
    cursor = conn.cursor()
    
    print("\n=== Cleaning up Database Connections ===\n")
    
    # Kill long-running transactions
    cursor.execute("""
        SELECT trx_mysql_thread_id 
        FROM information_schema.innodb_trx 
        WHERE trx_state = 'RUNNING' 
        AND trx_started < NOW() - INTERVAL 1 HOUR
    """)
    long_running = cursor.fetchall()
    
    for (thread_id,) in long_running:
        print(f"Killing long-running transaction thread {thread_id}")
        cursor.execute(f"KILL {thread_id}")
    
    # Kill sleeping connections
    cursor.execute("""
        SELECT id 
        FROM information_schema.processlist 
        WHERE command = 'Sleep' 
        AND time > 60
    """)
    sleeping = cursor.fetchall()
    
    for (conn_id,) in sleeping:
        print(f"Killing sleeping connection {conn_id}")
        cursor.execute(f"KILL {conn_id}")
    
    # Commit any pending transactions
    conn.commit()
    
    cursor.close()
    conn.close()
    
    print("\nCleanup completed!")

if __name__ == "__main__":
    cleanup_database() 