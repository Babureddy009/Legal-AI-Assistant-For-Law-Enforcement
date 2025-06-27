from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ActionExecuted, FollowupAction
import mysql.connector
from mysql.connector import Error
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionQueryIPCSection(Action):
    def name(self) -> Text:
        return "action_query_ipc_section"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            # Try to get the entity first
            ipc_section = None
            # Prefer the longest entity value
            entities = list(tracker.get_latest_entity_values("ipc_section"))
            if entities:
                ipc_section = max(entities, key=len)
            # If not found, try to extract from intent name
            if not ipc_section:
                intent = tracker.latest_message['intent'].get('name')
                if intent and intent.startswith("ask_section_"):
                    ipc_section = intent.replace("ask_section_", "")
            if not ipc_section:
                dispatcher.utter_message(text="I couldn't find the IPC section you're asking about. Could you please specify the section number?")
                return []

            # Extract the section number (e.g., 120B, 1, 302)
            match = re.search(r"([0-9]+[A-Z]?)", ipc_section.upper())
            if match:
                section_number = match.group(1)
            else:
                section_number = ipc_section.strip().upper()
            
            # Connect to MySQL database
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="pass",
                database="legal_ai"
            )
            
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                query = "SELECT * FROM ipc_sections WHERE section_number = %s"
                cursor.execute(query, (section_number,))
                result = cursor.fetchone()

                if result:
                    response = f"IPC Section {result['section_number']}:\n"
                    response += f"Title: {result['title']}\n"
                    response += f"Description: {result['description']}\n"
                    if result['punishment']:
                        response += f"Punishment: {result['punishment']}"
                else:
                    response = f"I couldn't find information about IPC Section {section_number}."
                
                dispatcher.utter_message(text=response)

        except Error as e:
            logger.error(f"Database error: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while accessing the database.")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            dispatcher.utter_message(text="Sorry, something went wrong while processing your request.")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
        return []

class ActionQueryCrime(Action):
    def name(self) -> Text:
        return "action_query_crime"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the crime entity from the latest message
        crime_entity = next(tracker.get_latest_entity_values("crime"), None)
        
        # Get the latest message and clean it
        latest_message = tracker.latest_message.get('text', '').lower()
        # Remove question marks and clean the message
        latest_message = latest_message.replace('?', '').strip()
        
        # Check if this is a question about a crime
        question_patterns = [
            'what is', 'tell me about', 'can you explain', 'what does',
            'i want to know', 'i need information', 'can you tell me',
            'i would like to know', 'please explain'
        ]
        
        is_question = any(pattern in latest_message for pattern in question_patterns)
        
        if is_question:
            # Handle as a normal crime query
            try:
                # Connect to MySQL database
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="pass",
                    database="legal_ai"
                )
                
                if connection.is_connected():
                    cursor = connection.cursor(dictionary=True)
                    
                    # If no crime entity found, check for cyber crime terms
                    if not crime_entity:
                        cyber_terms = ['cyber', 'online', 'internet', 'digital', 'computer', 'electronic']
                        if any(term in latest_message for term in cyber_terms):
                            crime_entity = 'cyber fraud'
                    
                    if not crime_entity:
                        dispatcher.utter_message(text="I couldn't identify which crime you're asking about. Please specify a crime.")
                        return []
                    
                    # Normalize crime name
                    crime_name = crime_entity.lower().strip()
                    
                    # Common typos mapping
                    typo_mapping = {
                        'fruad': 'fraud',
                        'cyber fruad': 'cyber fraud',
                        'onlne': 'online',
                        'intrnet': 'internet',
                        'digtal': 'digital',
                        'comuter': 'computer',
                        'electonic': 'electronic'
                    }
                    
                    # Check for typos
                    if crime_name in typo_mapping:
                        crime_name = typo_mapping[crime_name]
                    
                    # Get crime information with LIKE query to handle variations
                    cursor.execute("""
                        SELECT * FROM crimes 
                        WHERE LOWER(name) LIKE %s
                    """, (f"%{crime_name}%",))
                    crime_info = cursor.fetchone()
                    
                    if not crime_info:
                        # Try alternative names for cyber crimes
                        if any(term in crime_name for term in ['cyber', 'online', 'internet', 'digital', 'computer', 'electronic']):
                            cursor.execute("""
                                SELECT * FROM crimes 
                                WHERE LOWER(name) LIKE %s
                            """, ('%cyber fraud%',))
                            crime_info = cursor.fetchone()
                    
                    if not crime_info:
                        # Try fuzzy matching for common cyber crime terms
                        cyber_terms = ['cyber', 'online', 'internet', 'digital', 'computer', 'electronic', 'fraud', 'crime']
                        if any(term in crime_name for term in cyber_terms):
                            cursor.execute("""
                                SELECT * FROM crimes 
                                WHERE LOWER(name) LIKE %s
                            """, ('%cyber fraud%',))
                            crime_info = cursor.fetchone()
                    
                    if not crime_info:
                        # If still no match, try to suggest the correct term
                        if 'fruad' in crime_name:
                            dispatcher.utter_message(text="I think you might have meant 'fraud'. Here's information about cyber fraud:")
                            cursor.execute("""
                                SELECT * FROM crimes 
                                WHERE LOWER(name) LIKE %s
                            """, ('%cyber fraud%',))
                            crime_info = cursor.fetchone()
                        else:
                            dispatcher.utter_message(text=f"I don't have information about {crime_name} in my database. Did you mean 'cyber fraud'?")
                            return []
                    
                    # Get related IPC sections
                    cursor.execute("""
                        SELECT i.* FROM ipc_sections i
                        JOIN crime_ipc_mapping m ON i.id = m.ipc_section_id
                        JOIN crimes c ON c.id = m.crime_id
                        WHERE LOWER(c.name) LIKE %s
                    """, (f"%{crime_name}%",))
                    ipc_sections = cursor.fetchall()
                    
                    # If no IPC sections found, try with cyber fraud
                    if not ipc_sections and any(term in crime_name for term in ['cyber', 'online', 'internet', 'digital']):
                        cursor.execute("""
                            SELECT i.* FROM ipc_sections i
                            JOIN crime_ipc_mapping m ON i.id = m.ipc_section_id
                            JOIN crimes c ON c.id = m.crime_id
                            WHERE LOWER(c.name) LIKE %s
                        """, ('%cyber fraud%',))
                        ipc_sections = cursor.fetchall()
                    
                    # Format response
                    response = f"Here's what I found about **{crime_name.capitalize()}**:\n\n"
                    
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
                                # Clean up punishment text to avoid repetition
                                punishment = section['punishment']
                                if '|' in punishment:
                                    punishment = punishment.split('|')[0].strip()
                                response += f"  - **Punishment:** {punishment}\n"
                            else:
                                response += f"  - **Punishment:** Not specified in the IPC\n"
                    
                    # Add a note about reporting
                    response += "\n**Important Note:** If you need to report a crime or seek legal assistance, please contact your local law enforcement authorities or legal professionals."
                    dispatcher.utter_message(text=response)
                    
                    cursor.close()
                    connection.close()
                    
            except Error as e:
                logger.error(f"Database error: {str(e)}")
                dispatcher.utter_message(text=f"Sorry, I encountered a database error: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                dispatcher.utter_message(text=f"Sorry, something went wrong while processing your request: {str(e)}")
            
            return []
        
        # If not a question, check for confession patterns
        confession_patterns = [
            # Direct confessions
            'i committed', 'i have committed', 'i am committing',
            'i did', 'i have done', 'i am doing',
            'i took', 'i have taken', 'i am taking',
            'i made', 'i have made', 'i am making',
            'i am going to commit', 'i will commit', 'i am planning to commit',
            # Past tense actions
            'i robbed', 'i have robbed', 'i stole', 'i have stolen',
            'i killed', 'i have killed', 'i murdered', 'i have murdered',
            'i assaulted', 'i have assaulted', 'i kidnapped', 'i have kidnapped',
            'i defrauded', 'i have defrauded', 'i cheated', 'i have cheated',
            'i hacked', 'i have hacked', 'i hacked into', 'i have hacked into',
            # Present tense actions
            'i am robbing', 'i am stealing', 'i am killing', 'i am murdering',
            'i am assaulting', 'i am kidnapping', 'i am defrauding', 'i am cheating',
            'i am hacking', 'i am hacking into',
            # Future tense actions
            'i will rob', 'i will steal', 'i will kill', 'i will murder',
            'i will assault', 'i will kidnap', 'i will defraud', 'i will cheat',
            'i will hack', 'i will hack into',
            # Planning actions
            'i am going to rob', 'i am going to steal', 'i am going to kill',
            'i am going to murder', 'i am going to assault', 'i am going to kidnap',
            'i am going to defraud', 'i am going to cheat',
            'i am going to hack', 'i am going to hack into',
            # Simple present with crime verbs
            'i rob', 'i steal', 'i kill', 'i murder', 'i assault', 'i kidnap',
            'i defraud', 'i cheat', 'i hack', 'i hack into'
        ]
        
        # Also check for crime-related words in the message
        crime_verbs = [
            'rob', 'steal', 'kill', 'murder', 'assault', 'kidnap',
            'defraud', 'cheat', 'hack', 'threaten', 'extort', 'bribe',
            'hack into', 'break into', 'access illegally', 'penetrate',
            'compromise', 'infiltrate', 'bypass security'
        ]
        
        # Check for confession patterns
        is_confession = False
        
        # First check exact patterns
        for pattern in confession_patterns:
            if pattern in latest_message:
                is_confession = True
                break
        
        # Then check crime verbs with different forms
        if not is_confession:
            for verb in crime_verbs:
                if (f"i {verb}" in latest_message or
                    f"i have {verb}" in latest_message or
                    f"i am {verb}" in latest_message or
                    f"i will {verb}" in latest_message or
                    f"i am going to {verb}" in latest_message):
                    is_confession = True
                    break
        
        # Log the detection process
        logger.info(f"Message: {latest_message}")
        logger.info(f"Is confession: {is_confession}")
        
        if is_confession:
            # First show the warning message
            warning_response = "I notice you're mentioning a crime. If you have committed a crime or are planning to commit one, I strongly advise you to:\n\n"
            warning_response += "1. Contact law enforcement immediately\n"
            warning_response += "2. Seek legal counsel\n"
            warning_response += "3. If you're in immediate danger or experiencing a crisis, please call emergency services\n\n"
            warning_response += "This is an AI assistant for legal information only. I cannot provide legal advice or handle actual crime reports. For any real legal matters, please consult with law enforcement and legal professionals."
            dispatcher.utter_message(text=warning_response)
            
            # Then try to get and show crime information
            try:
                # Connect to MySQL database
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="pass",
                    database="legal_ai"
                )
                
                if connection.is_connected():
                    cursor = connection.cursor(dictionary=True)
                    
                    # Try to identify the crime from the message
                    crime_name = None
                    crime_keywords = {
                        'robbery': ['rob', 'robbed', 'robbing', 'bank robbery'],
                        'theft': ['steal', 'stole', 'stealing', 'theft'],
                        'murder': ['kill', 'killed', 'killing', 'murder', 'murdered'],
                        'assault': ['assault', 'assaulted', 'assaulting'],
                        'kidnapping': ['kidnap', 'kidnapped', 'kidnapping'],
                        'fraud': ['fraud', 'defraud', 'defrauded', 'cheat', 'cheated'],
                        'cyber fraud': ['hack', 'hacked', 'hacking', 'cyber', 'online fraud', 'cyber crime', 'cybercrime']
                    }
                    
                    # Check for cyber-related terms first
                    cyber_terms = ['hack', 'hacked', 'hacking', 'cyber', 'online', 'internet', 'digital', 'computer', 'electronic']
                    if any(term in latest_message for term in cyber_terms):
                        crime_name = 'cyber fraud'
                    
                    # If no cyber crime detected, check other crimes
                    if not crime_name:
                        for crime, keywords in crime_keywords.items():
                            if any(keyword in latest_message for keyword in keywords):
                                crime_name = crime
                                break
                    
                    if crime_name:
                        # Get crime information
                        cursor.execute("""
                            SELECT * FROM crimes 
                            WHERE LOWER(name) LIKE %s
                        """, (f"%{crime_name}%",))
                        crime_info = cursor.fetchone()
                        
                        if crime_info:
                            # Get related IPC sections
                            cursor.execute("""
                                SELECT i.* FROM ipc_sections i
                                JOIN crime_ipc_mapping m ON i.id = m.ipc_section_id
                                JOIN crimes c ON c.id = m.crime_id
                                WHERE c.name = %s
                            """, (crime_name,))
                            ipc_sections = cursor.fetchall()
                            
                            # Format response
                            response = f"\nHere's the legal information about **{crime_name.capitalize()}**:\n\n"
                            
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
                                        # Clean up punishment text to avoid repetition
                                        punishment = section['punishment']
                                        if '|' in punishment:
                                            punishment = punishment.split('|')[0].strip()
                                        response += f"  - **Punishment:** {punishment}\n"
                                    else:
                                        response += f"  - **Punishment:** Not specified in the IPC\n"
                            
                            dispatcher.utter_message(text=response)
                    
                    cursor.close()
                    connection.close()
                    
            except Error as e:
                logger.error(f"Database error: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
            
            return []
        
        # If neither a question nor a confession, treat as a general query
        dispatcher.utter_message(text="I'm not sure what you're asking about. Could you please rephrase your question?")
        return []

class ActionQueryIPCPunishment(Action):
    def name(self) -> Text:
        return "action_query_ipc_punishment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Get the IPC section entity from the latest message
            ipc_section = next(tracker.get_latest_entity_values("ipc_section"), None)
            
            if not ipc_section:
                dispatcher.utter_message(text="I'm sorry, I couldn't identify which IPC section you're asking about. Could you please specify the section number?")
                return []

            # Connect to MySQL database
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="pass",
                database="legal_ai"
            )

            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                
                # Query the ipc_sections table
                cursor.execute("SELECT * FROM ipc_sections WHERE section_number = %s", (ipc_section,))
                section = cursor.fetchone()
                
                if not section:
                    dispatcher.utter_message(text=f"I'm sorry, I don't have information about the punishment under IPC Section {ipc_section}.")
                    return []

                # Format the response
                response = f"Here's the punishment under IPC Section {ipc_section}:\n\n"
                response += f"{section['punishment']}\n\n"
                response += "Note: This is general information. For specific legal advice, please consult a qualified legal professional."

                dispatcher.utter_message(text=response)

        except Error as e:
            logger.error(f"Database error: {str(e)}")
            dispatcher.utter_message(text="I'm sorry, I encountered an error while accessing the database.")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            dispatcher.utter_message(text="I'm sorry, something went wrong while processing your request.")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

        return []

class ActionHandleCrimeConfession(Action):
    def name(self) -> Text:
        return "action_handle_crime_confession"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Get the crime entity from the latest message
            crime = next(tracker.get_latest_entity_values("crime"), None)
            
            # If no crime entity found, try to extract from the last message
            if not crime:
                last_message = tracker.latest_message.get('text', '').lower()
                if 'murder' in last_message or 'killed' in last_message:
                    crime = 'murder'
                elif 'rape' in last_message or 'sexually assaulted' in last_message:
                    crime = 'rape'
                elif 'theft' in last_message or 'stole' in last_message:
                    crime = 'theft'
                elif 'robbery' in last_message or 'robbed' in last_message:
                    crime = 'robbery'
                elif 'assault' in last_message:
                    crime = 'assault'
                elif 'kidnapping' in last_message or 'kidnapped' in last_message:
                    crime = 'kidnapping'
                elif 'burglary' in last_message or 'broke in' in last_message:
                    crime = 'burglary'
                elif 'extortion' in last_message or 'extorted' in last_message:
                    crime = 'extortion'
                elif 'forgery' in last_message or 'forged' in last_message:
                    crime = 'forgery'
                elif 'cybercrime' in last_message:
                    crime = 'cybercrime'
                elif 'fraud' in last_message:
                    crime = 'fraud'
                elif 'embezzlement' in last_message or 'embezzled' in last_message:
                    crime = 'embezzlement'
                elif 'perjury' in last_message:
                    crime = 'perjury'
                elif 'bribery' in last_message or 'took a bribe' in last_message:
                    crime = 'bribery'

            # Format the response
            response = "I notice you're mentioning a crime. If you have committed a crime or are planning to commit one, I strongly advise you to:\n\n"
            response += "1. Contact law enforcement immediately\n"
            response += "2. Seek legal counsel\n"
            response += "3. If you're in immediate danger or experiencing a crisis, please call emergency services\n\n"
            
            if crime:
                response += f"Regarding {crime}, please understand that this is a serious matter that requires immediate attention from law enforcement and legal professionals.\n\n"
            
            response += "This is an AI assistant for legal information only. I cannot provide legal advice or handle actual crime reports. For any real legal matters, please consult with law enforcement and legal professionals."

            dispatcher.utter_message(text=response)
            return []

        except Exception as e:
            logger.error(f"Error handling crime confession: {str(e)}")
            dispatcher.utter_message(text="I apologize, but I cannot assist with actual crime reports. Please contact law enforcement if you need to report a crime.")
            return []
