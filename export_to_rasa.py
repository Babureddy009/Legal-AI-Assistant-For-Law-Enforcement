import mysql.connector
import json
import os
from mysql.connector import Error
from config import get_db_config
from db_utils import get_cursor

def connect_to_db():
    return mysql.connector.connect(**get_db_config())

def generate_rasa_training_data():
    try:
        with get_cursor(dictionary=True) as (cursor, connection):
            # Create rasa data directory if it doesn't exist
            os.makedirs('rasa_data', exist_ok=True)
            
            # Fetch all IPC sections
            cursor.execute("""
                SELECT section_number, title, description, punishment 
                FROM ipc_sections 
                WHERE title IS NOT NULL 
                AND (description IS NOT NULL OR punishment IS NOT NULL)
                ORDER BY 
                    CASE 
                        WHEN section_number REGEXP '^[0-9]+$' THEN CAST(section_number AS UNSIGNED)
                        ELSE 999999
                    END,
                    section_number
            """)
            
            sections = cursor.fetchall()
            
            # Generate nlu.yml content
            nlu_content = "version: '3.1'\n\nnlu:\n"
            
            # Generate stories.yml content
            stories_content = "version: '3.1'\n\nstories:\n"
            
            # Generate domain.yml content
            domain_content = """version: '3.1'

intents:
  - greet
  - goodbye
  - ask_section
  - ask_punishment
  - ask_description
  - ask_title
  - affirm
  - deny

entities:
  - section_number

slots:
  section_number:
    type: text
    mappings:
    - type: from_entity
      entity: section_number

responses:
  utter_greet:
  - text: "Hello! I can help you with information about IPC sections. What would you like to know?"

  utter_goodbye:
  - text: "Goodbye! Feel free to ask if you need more information about IPC sections."

  utter_ask_section:
  - text: "Which IPC section would you like to know about?"

  utter_ask_more:
  - text: "Would you like to know more about this section?"

actions:
"""
            
            # Add section-specific responses
            for section in sections:
                section_num = section['section_number']
                title = section['title'] or ""
                description = section['description'] or ""
                punishment = section['punishment'] or ""
                
                # Add NLU training examples
                nlu_content += f"""
- intent: ask_section_{section_num}
  examples: |
    - what is section {section_num}
    - tell me about section {section_num}
    - explain section {section_num}
    - what does section {section_num} say
    - what is ipc section {section_num}
    - what is the meaning of section {section_num}
    - what is the definition of section {section_num}
    - what is the purpose of section {section_num}
    - what is the scope of section {section_num}
    - what is the applicability of section {section_num}
"""
                
                # Add stories
                stories_content += f"""
- story: section {section_num} flow
  steps:
  - intent: ask_section_{section_num}
  - action: utter_section_{section_num}
  - intent: ask_more
  - action: utter_ask_more
"""
                
                # Add domain responses
                domain_content += f"""
  utter_section_{section_num}:
  - text: "Section {section_num}: {title}\\n\\nDescription: {description}\\n\\nPunishment: {punishment}"
"""
            
            # Write files
            with open('rasa_data/nlu.yml', 'w', encoding='utf-8') as f:
                f.write(nlu_content)
                
            with open('rasa_data/stories.yml', 'w', encoding='utf-8') as f:
                f.write(stories_content)
                
            with open('rasa_data/domain.yml', 'w', encoding='utf-8') as f:
                f.write(domain_content)
                
            print("Successfully generated Rasa training data!")
            
    except Error as e:
        print(f"Database error: {str(e)}")

if __name__ == "__main__":
    generate_rasa_training_data() 