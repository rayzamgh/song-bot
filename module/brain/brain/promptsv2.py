import threading
import time
from google.cloud import firestore
from langchain.prompts.prompt import PromptTemplate
from .prompts_template import (
    T_DEFAULT_ENTITY_EXTRACTION_TEMPLATE,
    T_DEFAULT_ENTITY_SUMMARIZATION_TEMPLATE,
    T_PERSON_INFORMATION_SUMMARIZATION_TEMPLATE,
    T_PERSON_INFORMATION_SUMMARIZATION_TEMPLATE_SYSTEM,
    T_SONG_YES_LANG_TEMPLATE,
    T_SONG_PREFIX,
    T_SONG_ENTITY_MEMORY_CONVERSATION_TEMPLATE,
    T_SONG_INPUT_TEMPLATE,
    T_SONG_TALK_TEMPLATE
)

# Global Var Initiation templates
_DEFAULT_ENTITY_EXTRACTION_TEMPLATE = None
_DEFAULT_ENTITY_SUMMARIZATION_TEMPLATE = None
_PERSON_INFORMATION_SUMMARIZATION_TEMPLATE = None
_PERSON_INFORMATION_SUMMARIZATION_TEMPLATE_SYSTEM = None
SONG_YES_LANG_TEMPLATE = None
SONG_PREFIX = None
SONG_ENTITY_MEMORY_CONVERSATION_TEMPLATE = None
SONG_INPUT_TEMPLATE = None
SONG_TALK_TEMPLATE = None

# Initialize Firestore client
db = firestore.Client()

def upload_templates_to_firestore():
    templates = {
        "entity_extraction_template" : T_DEFAULT_ENTITY_EXTRACTION_TEMPLATE,
        "entity_summarization_template" : T_DEFAULT_ENTITY_SUMMARIZATION_TEMPLATE,
        "person_information_summarization_template" : T_PERSON_INFORMATION_SUMMARIZATION_TEMPLATE,
        "person_information_summarization_template_system" : T_PERSON_INFORMATION_SUMMARIZATION_TEMPLATE_SYSTEM,
        "song_yes_lang_template" : T_SONG_YES_LANG_TEMPLATE,
        "song_prefix" : T_SONG_PREFIX,
        "song_entity_memory_conversation_template" : T_SONG_ENTITY_MEMORY_CONVERSATION_TEMPLATE,
        "song_input_template" : T_SONG_INPUT_TEMPLATE,
        "song_talk_template" : T_SONG_TALK_TEMPLATE,
    }

    for key, template in templates.items():
        doc_ref = db.collection("templates").document(key)
        doc = doc_ref.get()  # Retrieve the document
        if not doc.exists:  # Check if the document does not exist
            doc_ref.set({"template": template})  # Only set the template if the document does not exist
            print(f"Template '{key}' uploaded.")
        else:
            print(f"Template '{key}' already exists. No action taken.")

# Uncomment the following line to upload templates if they are not already in Firestore
upload_templates_to_firestore()

def get_template_from_firestore(template_name):
    doc_ref = db.collection("templates").document(template_name)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()['template']
    else:
        raise ValueError(f"Template {template_name} not found in Firestore.")

def update_templates():
    global SONG_INPUT_TEMPLATE, _DEFAULT_ENTITY_EXTRACTION_TEMPLATE, _DEFAULT_ENTITY_SUMMARIZATION_TEMPLATE
    while True:
        try:
            _DEFAULT_ENTITY_EXTRACTION_TEMPLATE = get_template_from_firestore("entity_extraction_template")
            _DEFAULT_ENTITY_SUMMARIZATION_TEMPLATE = get_template_from_firestore("entity_summarization_template")
            _PERSON_INFORMATION_SUMMARIZATION_TEMPLATE = get_template_from_firestore("person_information_summarization_template")
            _PERSON_INFORMATION_SUMMARIZATION_TEMPLATE_SYSTEM = get_template_from_firestore("person_information_summarization_template_system")
            SONG_YES_LANG_TEMPLATE = get_template_from_firestore("song_yes_lang_template")
            SONG_PREFIX = get_template_from_firestore("song_prefix")
            SONG_ENTITY_MEMORY_CONVERSATION_TEMPLATE = get_template_from_firestore("song_entity_memory_conversation_template")
            SONG_INPUT_TEMPLATE = get_template_from_firestore("song_input_template")
            SONG_TALK_TEMPLATE = get_template_from_firestore("song_talk_template")
            
            print("Templates updated")
        except Exception as e:
            print(f"Failed to update templates: {e}")
        time.sleep(60)  # Wait for 60 seconds before updating again

# Start the background thread
thread = threading.Thread(target=update_templates)
thread.daemon = True  # This ensures the thread will exit when the main program does
thread.start()

# Create PromptTemplate instances using the retrieved templates
ENTITY_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=_DEFAULT_ENTITY_EXTRACTION_TEMPLATE
)

ENTITY_SUMMARIZATION_PROMPT = PromptTemplate(
    input_variables=["entity", "summary", "history", "input"],
    template=_DEFAULT_ENTITY_SUMMARIZATION_TEMPLATE,
)

PERSON_INFORMATION_SUMMARIZATION_PROMPT = PromptTemplate(
    input_variables=["name", "history"],
    template=_PERSON_INFORMATION_SUMMARIZATION_TEMPLATE,
)