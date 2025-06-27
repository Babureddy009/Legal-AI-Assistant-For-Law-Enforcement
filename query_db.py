import sqlite3

def execute_query(query, params=None):
    try:
        conn = sqlite3.connect('ipc_sections.db')
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def print_results(results, headers=None):
    if not results:
        print("No results found.")
        return
    
    if headers:
        print("\n" + " | ".join(headers))
        print("-" * (sum(len(h) for h in headers) + 3 * (len(headers) - 1)))
    
    for row in results:
        print(" | ".join(str(item) for item in row))

def main():
    while True:
        print("\n=== IPC Sections Database Query Tool ===")
        print("1. Search section by number")
        print("2. Search sections by keyword")
        print("3. List all sections")
        print("4. Show empty sections")
        print("5. Show latest updates")
        print("6. Show database statistics")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ")
        
        if choice == "0":
            break
            
        elif choice == "1":
            section_num = input("Enter section number: ")
            query = """
                SELECT section_number, title, description, punishment, last_updated 
                FROM ipc_sections 
                WHERE section_number = ?
            """
            results = execute_query(query, (section_num,))
            headers = ["Section", "Title", "Description", "Punishment", "Last Updated"]
            print_results(results, headers)
            
        elif choice == "2":
            keyword = input("Enter keyword to search: ")
            query = """
                SELECT section_number, title, substr(description, 1, 100) as description
                FROM ipc_sections 
                WHERE description LIKE ? OR title LIKE ? OR punishment LIKE ?
            """
            search_term = f"%{keyword}%"
            results = execute_query(query, (search_term, search_term, search_term))
            headers = ["Section", "Title", "Description (first 100 chars)"]
            print_results(results, headers)
            
        elif choice == "3":
            limit = input("Enter number of sections to show (press Enter for all): ")
            query = """
                SELECT section_number, title, substr(description, 1, 100) as description
                FROM ipc_sections
            """
            if limit.strip():
                query += f" LIMIT {int(limit)}"
            results = execute_query(query)
            headers = ["Section", "Title", "Description (first 100 chars)"]
            print_results(results, headers)
            
        elif choice == "4":
            query = """
                SELECT section_number, title, last_updated
                FROM ipc_sections
                WHERE description IS NULL OR description = ''
            """
            results = execute_query(query)
            headers = ["Section", "Title", "Last Updated"]
            print_results(results, headers)
            
        elif choice == "5":
            limit = input("Enter number of recent updates to show (default 5): ") or "5"
            query = """
                SELECT section_number, title, last_updated
                FROM ipc_sections
                ORDER BY last_updated DESC
                LIMIT ?
            """
            results = execute_query(query, (int(limit),))
            headers = ["Section", "Title", "Last Updated"]
            print_results(results, headers)
            
        elif choice == "6":
            queries = [
                ("Total sections:", "SELECT COUNT(*) FROM ipc_sections"),
                ("Empty sections:", "SELECT COUNT(*) FROM ipc_sections WHERE description IS NULL OR description = ''"),
                ("Latest update:", "SELECT MAX(last_updated) FROM ipc_sections"),
                ("Oldest update:", "SELECT MIN(last_updated) FROM ipc_sections")
            ]
            print("\nDatabase Statistics:")
            for label, query in queries:
                result = execute_query(query)
                if result and result[0]:
                    print(f"{label} {result[0][0]}")
        
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 