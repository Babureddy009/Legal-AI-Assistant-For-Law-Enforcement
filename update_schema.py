import mysql.connector
from mysql.connector import Error
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_schema():
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root1",
            password="pass",
            database="legal_ai"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Drop existing tables
            logger.info("Dropping existing tables...")
            cursor.execute("DROP TABLE IF EXISTS crime_ipc_mapping")
            cursor.execute("DROP TABLE IF EXISTS crimes")
            cursor.execute("DROP TABLE IF EXISTS ipc_sections")
            
            # Create tables with updated schema
            logger.info("Creating tables with updated schema...")
            
            # Create ipc_sections table
            cursor.execute("""
                CREATE TABLE ipc_sections (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    section_number VARCHAR(10) UNIQUE NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    punishment TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            logger.info("Created ipc_sections table")
            
            # Create crimes table with all required fields
            cursor.execute("""
                CREATE TABLE crimes (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    severity ENUM('minor', 'major', 'heinous') NOT NULL,
                    category ENUM('violent', 'property', 'financial', 'cyber', 'sexual', 'drug', 'other') NOT NULL,
                    bailable BOOLEAN NOT NULL,
                    cognizable BOOLEAN NOT NULL,
                    compoundable BOOLEAN NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            logger.info("Created crimes table")
            
            # Create crime_ipc_mapping table
            cursor.execute("""
                CREATE TABLE crime_ipc_mapping (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    crime_id INT NOT NULL,
                    ipc_section_id INT NOT NULL,
                    is_primary BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (crime_id) REFERENCES crimes(id),
                    FOREIGN KEY (ipc_section_id) REFERENCES ipc_sections(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("Created crime_ipc_mapping table")
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX idx_section_number ON ipc_sections(section_number)")
            cursor.execute("CREATE INDEX idx_crime_name ON crimes(name)")
            cursor.execute("CREATE INDEX idx_crime_category ON crimes(category)")
            cursor.execute("CREATE INDEX idx_crime_severity ON crimes(severity)")
            logger.info("Created indexes")
            
            connection.commit()
            logger.info("Successfully updated database schema")

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
    update_schema() 