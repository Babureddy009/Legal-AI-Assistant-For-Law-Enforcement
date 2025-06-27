from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from db_utils import get_cursor
from config import get_db_config

class ActionQueryCrime(Action):
    def name(self) -> Text:
        return "action_query_crime"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Get the crime name from the tracker
            crime_name = next(tracker.get_latest_entity_values("crime"), None)
            
            if not crime_name:
                # Check if this is a cyber crime query
                message = tracker.latest_message.get('text', '').lower()
                if any(term in message for term in ['cyber', 'online', 'internet', 'digital', 'computer', 'electronic']):
                    crime_name = 'cyber fraud'
                else:
                    dispatcher.utter_message(text="I couldn't identify which crime you're asking about. Please specify a crime.")
                    return []
            
            # Normalize crime name
            crime_name = crime_name.lower().strip()
            
            # Handle cyber crime variations
            if any(term in crime_name for term in ['cyber', 'online', 'internet', 'digital', 'computer', 'electronic']):
                crime_name = 'cyber fraud'  # Map to our known cyber crime
            
            # with get_cursor(dictionary=True) as (cursor, connection):
            with get_cursor(dictionary=True) as (cursor, connection):
                if connection.is_connected():
                    print("Successfully connected to database")
                    
                    # Get crime information
                    print(f"Querying crime information for: {crime_name}")
                    cursor.execute("""
                        SELECT * FROM crimes 
                        WHERE name = %s
                    """, (crime_name,))
                    crime_info = cursor.fetchone()
                    
                    if not crime_info:
                        print(f"No crime information found for: {crime_name}")
                        dispatcher.utter_message(text=f"I don't have information about {crime_name} in my database.")
                        return []
                    
                    print(f"Found crime information: {crime_info}")
                    
                    # Get related IPC sections
                    print("Querying related IPC sections")
                    cursor.execute("""
                        SELECT i.* FROM ipc_sections i
                        JOIN crime_ipc_mapping m ON i.id = m.ipc_section_id
                        JOIN crimes c ON c.id = m.crime_id
                        WHERE c.name = %s
                    """, (crime_name,))
                    ipc_sections = cursor.fetchall()
                    print(f"Found {len(ipc_sections)} related IPC sections")
                    
                    # Format response (modern, markdown, engaging)
                    response = f"Here's what I found about **{crime_name.capitalize()}**:\n\n"
                    
                    # Add description if it exists
                    if crime_info.get('description'):
                        response += f"{crime_info['description']}\n\n"
                    
                    # Add each field only if it exists and is not None
                    fields = {
                        'severity': 'Severity',
                        'category': 'Category',
                        'bailable': 'Bailable',
                        'cognizable': 'Cognizable',
                        'compoundable': 'Compoundable'
                    }
                    
                    for field, label in fields.items():
                        if field in crime_info and crime_info[field] is not None:
                            if field in ['bailable', 'cognizable', 'compoundable']:
                                response += f"**{label}:** {'Yes' if crime_info[field] else 'No'}\n"
                            else:
                                response += f"**{label}:** {str(crime_info[field]).capitalize()}\n"
                    
                    if ipc_sections:
                        response += f"\n**Relevant IPC Section(s):**\n"
                        for section in ipc_sections:
                            response += f"- **Section {section['section_number']}**: {section['title']}\n"
                            if section.get('description'):
                                response += f"  - {section['description']}\n"
                            if section.get('punishment') and section['punishment'].strip():
                                response += f"  - **Punishment:** {section['punishment']}\n"
                            else:
                                response += f"  - **Punishment:** Not specified in the IPC\n"
                    response += "\nIf you want to know more about related crimes or reporting procedures, just ask!"
                    dispatcher.utter_message(text=response)
                    
                    cursor.close()
                    connection.close()
                    print("Database connection closed")
                
        except Exception as e:
            print(f"Unexpected error occurred: {str(e)}")
            dispatcher.utter_message(text=f"Sorry, something went wrong while processing your request: {str(e)}")
        
        return []

class ActionQueryIPCSection(Action):
    def name(self) -> Text:
        return "action_query_ipc_section"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        ipc_section = tracker.get_slot("ipc_section")
        if not ipc_section:
            dispatcher.utter_message(text="I couldn't identify the IPC section you're asking about. Could you please specify the section number?")
            return []

        try:
            with get_cursor(dictionary=True) as (cursor, connection):
                if connection.is_connected():
                    cursor.execute("""
                        SELECT * FROM ipc_sections 
                        WHERE section_number = %s
                    """, (ipc_section,))
                    section_info = cursor.fetchone()
                    
                    if not section_info:
                        dispatcher.utter_message(text=f"I don't have information about IPC Section {ipc_section} in my database.")
                        return []
                    
                    # Get related crimes
                    cursor.execute("""
                        SELECT c.* FROM crimes c
                        JOIN crime_ipc_mapping m ON c.id = m.crime_id
                        JOIN ipc_sections i ON i.id = m.ipc_section_id
                        WHERE i.section_number = %s
                    """, (ipc_section,))
                    related_crimes = cursor.fetchall()
                    
                    # Format response
                    response = f"IPC Section {ipc_section}:\n"
                    response += f"Title: {section_info['title']}\n"
                    if section_info['description']:
                        response += f"Description: {section_info['description']}\n"
                    if section_info['punishment'] and section_info['punishment'].strip():
                        response += f"Punishment: {section_info['punishment']}\n"
                    else:
                        response += f"Punishment: Not specified in the IPC\n"
                    
                    if related_crimes:
                        response += "\nRelated Crimes:\n"
                        for crime in related_crimes:
                            response += f"\n{crime['name']}:\n"
                            response += f"Description: {crime['description']}\n"
                            response += f"Severity: {crime['severity']}\n"
                    
                    dispatcher.utter_message(text=response)
                    
        except Exception as e:
            dispatcher.utter_message(text=f"Sorry, I encountered an error while fetching the information: {str(e)}")
        
        return [] 