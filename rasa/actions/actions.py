from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from db_utils import get_cursor
from config import get_db_config

class ActionQueryIPCSection(Action):
    def name(self) -> Text:
        return "action_query_ipc_section"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Get the IPC section from the tracker
            ipc_section = next(tracker.get_latest_entity_values("ipc_section"), None)
            
            if not ipc_section:
                dispatcher.utter_message(text="I couldn't find the IPC section you're asking about. Could you please specify the section number?")
                return []

            # Clean the section number
            section_number = ipc_section.replace("IPC section", "").replace("section", "").strip()
            
            with get_cursor(dictionary=True) as (cursor, connection):
                # Query the database
                query = "SELECT * FROM ipc_sections WHERE section_number = %s"
                cursor.execute(query, (section_number,))
                result = cursor.fetchone()

                if result:
                    response = f"IPC Section {result['section_number']}:\n"
                    response += f"Title: {result['title']}\n"
                    response += f"Description: {result['description']}\n"
                    response += f"Punishment: {result['punishment']}"
                else:
                    response = f"I couldn't find information about IPC Section {section_number}."

                dispatcher.utter_message(text=response)

        except Exception as e:
            dispatcher.utter_message(text=f"Sorry, I encountered an error while accessing the database: {str(e)}")

        return []

class ActionQueryCrime(Action):
    def name(self) -> Text:
        return "action_query_crime"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Get the crime from the tracker
            crime = next(tracker.get_latest_entity_values("crime"), None)
            
            if not crime:
                dispatcher.utter_message(text="I couldn't identify the crime you're asking about. Could you please specify the crime?")
                return []

            with get_cursor(dictionary=True) as (cursor, connection):
                # Query the database for the crime and related IPC sections
                query = """
                    SELECT c.*, i.section_number, i.title, i.punishment
                    FROM crimes c
                    JOIN crime_ipc_mapping m ON c.id = m.crime_id
                    JOIN ipc_sections i ON m.ipc_section_id = i.id
                    WHERE c.name LIKE %s
                """
                cursor.execute(query, (f"%{crime}%",))
                results = cursor.fetchall()

                if results:
                    response = f"Information about {crime}:\n\n"
                    response += f"Description: {results[0]['description']}\n"
                    response += f"Severity: {results[0]['severity']}\n\n"
                    response += "Related IPC Sections:\n"
                    
                    for result in results:
                        response += f"\nSection {result['section_number']}:\n"
                        response += f"Title: {result['title']}\n"
                        response += f"Punishment: {result['punishment']}\n"
                else:
                    response = f"I couldn't find information about {crime}."

                dispatcher.utter_message(text=response)

        except Exception as e:
            dispatcher.utter_message(text=f"Sorry, I encountered an error while accessing the database: {str(e)}")

        return [] 