import mysql.connector
from mysql.connector import Error
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_additional_crimes():
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="pass",
            database="legal_ai"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Define the additional crimes with their details
            additional_crimes = [
                {
                    'name': 'Dowry',
                    'description': 'Demanding, giving, or taking dowry in connection with marriage, including dowry death.',
                    'severity': 'heinous',
                    'category': 'violent',
                    'bailable': False,
                    'cognizable': True,
                    'compoundable': False,
                    'ipc_sections': ['304B', '498A']
                },
                {
                    'name': 'Sexual Harassment',
                    'description': 'Unwelcome sexual advances, requests for sexual favors, and other verbal or physical conduct of a sexual nature.',
                    'severity': 'major',
                    'category': 'sexual',
                    'bailable': True,
                    'cognizable': True,
                    'compoundable': False,
                    'ipc_sections': ['354A', '354B', '354C', '354D']
                },
                {
                    'name': 'Terrorism',
                    'description': 'Acts of violence or intimidation intended to create fear and terror in the public, often for political or ideological purposes.',
                    'severity': 'heinous',
                    'category': 'violent',
                    'bailable': False,
                    'cognizable': True,
                    'compoundable': False,
                    'ipc_sections': ['121', '121A', '122', '123', '124', '124A', '125', '126', '127', '128', '129', '130']
                }
            ]
            
            # Update or insert each crime
            for crime in additional_crimes:
                # Check if crime exists
                cursor.execute("SELECT id FROM crimes WHERE name = %s", (crime['name'],))
                result = cursor.fetchone()
                
                if result:
                    # Update existing crime
                    crime_id = result[0]
                    cursor.execute("""
                        UPDATE crimes 
                        SET description = %s,
                            severity = %s,
                            category = %s,
                            bailable = %s,
                            cognizable = %s,
                            compoundable = %s
                        WHERE id = %s
                    """, (
                        crime['description'],
                        crime['severity'],
                        crime['category'],
                        crime['bailable'],
                        crime['cognizable'],
                        crime['compoundable'],
                        crime_id
                    ))
                    logger.info(f"Updated crime: {crime['name']}")
                else:
                    # Insert new crime
                    cursor.execute("""
                        INSERT INTO crimes (name, description, severity, category, bailable, cognizable, compoundable)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        crime['name'],
                        crime['description'],
                        crime['severity'],
                        crime['category'],
                        crime['bailable'],
                        crime['cognizable'],
                        crime['compoundable']
                    ))
                    crime_id = cursor.lastrowid
                    logger.info(f"Inserted new crime: {crime['name']}")
                
                # Clear existing mappings for this crime
                cursor.execute("DELETE FROM crime_ipc_mapping WHERE crime_id = %s", (crime_id,))
                
                # Create new mappings
                for section in crime['ipc_sections']:
                    # Get IPC section ID
                    cursor.execute("SELECT id FROM ipc_sections WHERE section_number = %s", (section,))
                    ipc_result = cursor.fetchone()
                    
                    if ipc_result:
                        ipc_id = ipc_result[0]
                        cursor.execute("""
                            INSERT INTO crime_ipc_mapping (crime_id, ipc_section_id)
                            VALUES (%s, %s)
                        """, (crime_id, ipc_id))
                        logger.info(f"Mapped {crime['name']} to IPC Section {section}")
                    else:
                        logger.warning(f"IPC Section {section} not found in database")
            
            connection.commit()
            logger.info("Successfully updated additional crimes and their mappings")

    except Error as e:
        logger.error(f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    update_additional_crimes() 