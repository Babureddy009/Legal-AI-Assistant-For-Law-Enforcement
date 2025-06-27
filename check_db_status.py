import mysql.connector
from tabulate import tabulate

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root1",
        password="pass",
        database="legal_ai"
    )

def check_database_status():
    conn = connect_to_db()
    cursor = conn.cursor()
    
    print("\n=== Database Status Check ===\n")
    
    # Check for any locks
    cursor.execute("SHOW PROCESSLIST")
    processes = cursor.fetchall()
    print("\nActive Processes:")
    print(tabulate(processes, headers=['Id', 'User', 'Host', 'db', 'Command', 'Time', 'State', 'Info'], tablefmt='grid'))
    
    # Check table status
    cursor.execute("SHOW TABLE STATUS LIKE 'ipc_sections'")
    table_status = cursor.fetchone()
    print("\nIPC Sections Table Status:")
    print(f"Name: {table_status[0]}")
    print(f"Engine: {table_status[1]}")
    print(f"Rows: {table_status[4]}")
    print(f"Auto Increment: {table_status[10]}")
    print(f"Create Time: {table_status[11]}")
    print(f"Update Time: {table_status[12]}")
    
    # Check for any long-running transactions
    cursor.execute("""
        SELECT * FROM information_schema.innodb_trx 
        WHERE trx_state = 'RUNNING'
    """)
    transactions = cursor.fetchall()
    if transactions:
        print("\nLong-running Transactions:")
        print(tabulate(transactions, headers=['trx_id', 'trx_state', 'trx_started', 'trx_requested_lock_id', 'trx_wait_started', 'trx_weight', 'trx_mysql_thread_id', 'trx_query'], tablefmt='grid'))
    else:
        print("\nNo long-running transactions found.")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_database_status() 