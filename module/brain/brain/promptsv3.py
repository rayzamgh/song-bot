import os
import threading
import time
import logging
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

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TemplateManager:
    def __init__(self):
        # Initialize Firestore client using environment variables
        self.db = firestore.Client()
        self.templates = {
            "entity_extraction_template": T_DEFAULT_ENTITY_EXTRACTION_TEMPLATE,
            "entity_summarization_template": T_DEFAULT_ENTITY_SUMMARIZATION_TEMPLATE,
            "person_information_summarization_template": T_PERSON_INFORMATION_SUMMARIZATION_TEMPLATE,
            "person_information_summarization_template_system": T_PERSON_INFORMATION_SUMMARIZATION_TEMPLATE_SYSTEM,
            "song_yes_lang_template": T_SONG_YES_LANG_TEMPLATE,
            "song_prefix": T_SONG_PREFIX,
            "song_entity_memory_conversation_template": T_SONG_ENTITY_MEMORY_CONVERSATION_TEMPLATE,
            "song_input_template": T_SONG_INPUT_TEMPLATE,
            "song_talk_template": T_SONG_TALK_TEMPLATE
        }
        self.upload_templates_to_firestore()
        self.load_templates()
        self.start_background_update()

    def upload_templates_to_firestore(self):
        for key, template in self.templates.items():
            doc_ref = self.db.collection("song_templates").document(key)
            doc = doc_ref.get()
            if not doc.exists:
                doc_ref.set({"template": template})
                logging.info(f"Template '{key}' uploaded.")
            else:
                logging.info(f"Template '{key}' already exists. No action taken.")

    def get_template_from_firestore(self, template_name):
        doc_ref = self.db.collection("song_templates").document(template_name)
        doc =  doc_ref.get()
        if doc.exists:
            return doc.to_dict()['template']
        else:
            logging.error(f"Template {template_name} not found in Firestore.")
            raise ValueError(f"Template {template_name} not found in Firestore.")

    def load_templates(self):
        try:
            for key in self.templates.keys():
                self.templates[key] = self.get_template_from_firestore(key)
            logging.info("Templates successfully loaded from Firestore.")
        except Exception as e:
            logging.error(f"Failed to load templates: {e}")

    def update_templates(self):
        while True:
            try:
                updated_templates = {}
                for key in self.templates.keys():
                    updated_templates[key] = self.get_template_from_firestore(key)
                self.templates = updated_templates
                logging.info("Templates updated")
            except Exception as e:
                logging.error(f"Failed to update templates: {e}")
            time.sleep(600)

    def start_background_update(self):
        thread = threading.Thread(target=self.update_templates)
        thread.daemon = True
        thread.start()

    def create_prompt_template(self, template_type, input_variables):
        template = self.templates.get(template_type)
        if template:
            return PromptTemplate(input_variables=input_variables, template=template)
        else:
            logging.error(f"Template type '{template_type}' is not loaded.")
            raise ValueError(f"Template type '{template_type}' is not loaded.")
        
    def get_template_string(self, template_type):
        # Simply retrieve the template string from the templates dictionary
        if template_type in self.templates:
            return self.templates[template_type]
        else:
            logging.error(f"Template type '{template_type}' not found.")
            raise ValueError(f"Template type '{template_type}' not found.")

# Example usage# Example usage
if __name__ == "__main__":
    tm = TemplateManager()
    entity_extraction_prompt = tm.create_prompt_template("entity_extraction_template", ["history", "input"])
    entity_summarization_prompt = tm.create_prompt_template("entity_summarization_template", ["entity", "summary", "history", "input"])
    person_information_summarization_prompt = tm.create_prompt_template("person_information_summarization_template", ["name", "history"])
