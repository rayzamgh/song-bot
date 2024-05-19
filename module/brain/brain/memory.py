from typing import Dict
from typing import Any, List, Optional
from langchain.memory.entity import BaseEntityStore
from google.cloud import firestore
from langchain.memory import ConversationEntityMemory
from langchain.memory.chat_memory import BaseChatMemory

from langchain.schema import (
    AIMessage,
    BaseChatMessageHistory,
    SystemMessage,
    ChatMessage,
    FunctionMessage,
    BaseMessage,
    HumanMessage,
    _message_to_dict,
    messages_from_dict,
)

from langchain.prompts import (
    FewShotChatMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain.memory.utils import get_prompt_input_key
from langchain.prompts.base import BasePromptTemplate
from langchain.schema import BaseMessage
from langchain.chains import LLMChain
from utils import get_buffer_string, SongMessage, DiscordMessage
from .promptsv3 import TemplateManager
from .pydantic.person import Profile
from typing import List

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

class FirestoreEntityStore(BaseEntityStore):
    """Firestore-backed Entity store.
    """

    firestore_client: Any
    session_id: str = "song_brain"
    key_prefix: str = "memory_store"
    tm: TemplateManager = None

    def __init__(
        self,
        client,
        session_id: str = "song_brain",
        key_prefix: str = "memory_store",
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)

        self.firestore_client = client

        self.session_id = session_id
        self.key_prefix = key_prefix
        self.tm = TemplateManager()

    class Config:
        arbitrary_types_allowed = True
        
    @property
    def full_key_prefix(self) -> str:
        return f"{self.key_prefix}:{self.session_id}"

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        key = key.lower()
        doc_ref = self.firestore_client.document(
            f'{self.full_key_prefix}/{key}')
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get('value', default)
        else:
            return default

    def set(self, key: str, value: Optional[str]) -> None:
        key = key.lower()
        if not value:
            return self.delete(key)
        doc_ref = self.firestore_client.document(
            f'{self.full_key_prefix}/{key}')
        doc_ref.set({'value': value})

    def delete(self, key: str) -> None:
        key = key.lower()
        doc_ref = self.firestore_client.document(
            f'{self.full_key_prefix}/{key}')
        doc_ref.delete()

    def exists(self, key: str) -> bool:
        key = key.lower()
        doc_ref = self.firestore_client.document(
            f'{self.full_key_prefix}/{key}')
        return doc_ref.get().exists

    def clear(self) -> None:
        # Get a batch instance
        batch = self.firestore_client.batch()

        docs = self.firestore_client.collection(
            self.full_key_prefix).list_documents()
        for doc in docs:
            batch.delete(doc)

        # Commit the batch
        batch.commit()


class FirestoreChatMessageHistory(BaseChatMessageHistory):
    def __init__(
        self,
        client: firestore.Client,
        session_id: str = "default",
        key_prefix: str = "message_store",
    ):
        self.session_id = session_id
        self.firestore_client = client
        self.key_prefix = key_prefix
        self.collection = self.firestore_client.collection(self.key_prefix)
        self.tm = TemplateManager()


    def _message_from_dict(self, message: dict) -> BaseMessage:
        
        if "user" in message["data"]:
            return DiscordMessage(**message["data"])
        
        _type = message["type"]
        if _type == "human":
            return HumanMessage(**message["data"])
        elif _type == "song":
            return SongMessage(**message["data"])
        elif _type == "ai":
            return AIMessage(**message["data"])
        elif _type == "system":
            return SystemMessage(**message["data"])
        elif _type == "chat":
            return ChatMessage(**message["data"])
        elif _type == "function":
            return FunctionMessage(**message["data"])
        else:
            raise ValueError(f"Got unexpected message type: {_type}")

    def messages_from_dict(self, messages: List[dict]) -> List[BaseMessage]:
        """Convert a sequence of messages from dicts to Message objects.

        Args:
            messages: Sequence of messages (as dicts) to convert.

        Returns:
            List of messages (BaseMessages).
        """
        return [self._message_from_dict(m) for m in messages]

    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve the messages from Firestore"""
        query = self.collection.document(self.session_id).get()
        if query.exists:
            items = query.to_dict().get("messages", [])
            messages = self.messages_from_dict(items)
            return messages
        return []

    def add_user_message(self, message: str, discord_username: str) -> None:
        self.add_message(DiscordMessage(content=message, user=discord_username))

    def add_ai_message(self, message: str) -> None:
        self.add_message(SongMessage(content=message))

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in Firestore"""
        doc_ref = self.collection.document(self.session_id)
        doc = doc_ref.get()
        if doc.exists:
            messages = doc.to_dict().get("messages", [])
            messages.append(_message_to_dict(message))
            doc_ref.update({"messages": messages})
        else:
            doc_ref.set({"messages": [_message_to_dict(message)]})

    def clear(self) -> None:
        """Clear session memory from Firestore"""
        self.collection.document(self.session_id).delete()
    
class ChatConversationEntityMemory(ConversationEntityMemory):

    human_entity_summarization_prompt: BasePromptTemplate
    tm : TemplateManager
    human_prefix: str = "Human"
    ai_prefix: str = "Song"

    class Config:
        arbitrary_types_allowed = True

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.

        :meta private:
        """
        return ["entities"]
    
    def save_knowledge(self, inputs: Dict[str, Any], type_knowledge: Optional[str] = None) -> None:
        """
        Saves knowledge based on the provided inputs. It supports different types of knowledge entities,
        specifically handling 'person' type differently by storing it as a structured object.

        Args:
            inputs (Dict[str, Any]): The inputs containing the knowledge to be saved.
            type_knowledge (Optional[str]): The type of the entity. If set to 'person', 
                                            the data is saved using a structured format.

        Returns:
            None
        """

        # Extract buffer string from recent interactions for context
        buffer_string = get_buffer_string(
            self.buffer[-self.k * 2:],
            human_prefix=self.human_prefix,
            ai_prefix=self.ai_prefix,
        )

        # Extract the main input data from inputs
        input_data = inputs.get("input", None)
        name_data = inputs.get("name", None)

        # Handle knowledge type 'person' with a structured data format
        if type_knowledge == "person":
            print(f"NAMEOF : {name_data}")
            existing_summary = self.entity_store.get(name_data, "")
            
            # Define the parser for structured JSON output
            parser = JsonOutputParser(pydantic_object=Profile)
            
            # Prepare a template and chain for processing
            final_prompt = ChatPromptTemplate.from_messages([
                ("system", self.tm.get_template_string("person_information_summarization_template_system") +
                self.tm.get_template_string("person_information_summarization_template")),
            ])
            chain = final_prompt | self.llm | parser
            
            # Invoke the chain with provided and formatted inputs
            output = chain.invoke({
                "summary": existing_summary,
                "name": name_data,
                "history": buffer_string,
                "input": input_data,
                "format_instructions": parser.get_format_instructions(),
            })

            # Debugging output
            print("====================OUTPUT====================")
            print(output)
            print("====================OUTPUT====================")
            
            # Save the structured output in the entity store
            self.entity_store.set(name_data, output)
        
        # Handle other types of knowledge
        else:
            # Chain for general entity summarization
            chain = self.entity_summarization_prompt | self.llm
            
            # Determine entities to process
            if name_data is None:
                entities = self.entity_cache
            else:
                entities = [name_data]

            # Process each entity
            for entity in entities:
                existing_summary = self.entity_store.get(entity, "")
                output = chain.invoke({
                    "summary": existing_summary,
                    "entity": entity,
                    "history": buffer_string,
                    "input": input_data,
                })
                
                # Save the summarization result
                self.entity_store.set(entity, output.strip())

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        Save context from this conversation history to the entity store.

        Generates a summary for each entity in the entity cache by prompting
        the model, and saves these summaries to the entity store.
        """

        """Save context from this conversation to buffer."""
        input_str, output_str = self._get_input_output(inputs, outputs)
        self.chat_memory.add_user_message(input_str, inputs["discord_username"])
        self.chat_memory.add_ai_message(output_str)


        if self.input_key is None:
            prompt_input_key = get_prompt_input_key(inputs, self.memory_variables)
        else:
            prompt_input_key = self.input_key

        # Extract an arbitrary window of the last message pairs from
        # the chat history, where the hyperparameter k is the
        # number of message pairs:
        buffer_string = get_buffer_string(
            self.buffer[-self.k * 2 :],
            human_prefix=self.human_prefix,
            ai_prefix=self.ai_prefix,
        )

        input_data = inputs[prompt_input_key]

        # Create an LLMChain for predicting entity summarization from the context
        chain = LLMChain(llm=self.llm, prompt=self.entity_summarization_prompt)

        # Generate new summaries for entities and save them in the entity store
        for entity in self.entity_cache:
            # Get existing summary if it exists
            existing_summary = self.entity_store.get(entity, "")
            output = chain.predict(
                summary=existing_summary,
                entity=entity,
                history=buffer_string,
                input=input_data,
            )
            # Save the updated summary to the entity store
            self.entity_store.set(entity, output.strip())

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns chat history and all generated entities with summaries if available,
        and updates or clears the recent entity cache.

        New entity name can be found when calling this method, before the entity
        summaries are generated, so the entity cache values may be empty if no entity
        descriptions are generated yet.
        """

        # Create an LLMChain for predicting entity names from the recent chat history:
        chain = LLMChain(llm=self.llm, prompt=self.entity_extraction_prompt)

        if self.input_key is None:
            prompt_input_key = get_prompt_input_key(inputs, self.memory_variables)
        else:
            prompt_input_key = self.input_key

        # Extract an arbitrary window of the last message pairs from
        # the chat history, where the hyperparameter k is the
        # number of message pairs:
        buffer_string = get_buffer_string(
            self.buffer[-self.k * 2 :],
            human_prefix=self.human_prefix,
            ai_prefix=self.ai_prefix,
        )

        # Generates a comma-separated list of named entities,
        # e.g. "Jane, White House, UFO"
        # or "NONE" if no named entities are extracted:
        output = chain.predict(
            history=buffer_string,
            input=inputs[prompt_input_key],
        )

        # If no named entities are extracted, assigns an empty list.
        if output.strip() == "NONE":
            entities = []
        else:
            # Make a list of the extracted entities:
            entities = [w.strip() for w in output.split(",")]

        # Make a dictionary of entities with summary if exists:
        entity_summaries = {}

        for entity in entities:
            entity_summaries[entity] = self.entity_store.get(entity, "")

        # Replaces the entity name cache with the most recently discussed entities,
        # or if no entities were extracted, clears the cache:
        self.entity_cache = entities

        # Should we return as message objects or as a string?
        if self.return_messages:
            # Get last `k` pair of chat messages:
            buffer: Any = self.buffer[-self.k * 2 :]
        else:
            # Reuse the string we made earlier:
            buffer = buffer_string

        return {
            self.chat_history_key: buffer,
            "entities": entity_summaries,
        }