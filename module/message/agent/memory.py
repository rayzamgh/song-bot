from typing import Dict
from typing import Any, List, Optional
from langchain.memory.entity import BaseEntityStore
from google.cloud import firestore
from langchain.memory import ConversationEntityMemory

from langchain.schema import (
    AIMessage,
    BaseChatMessageHistory,
    BaseMessage,
    HumanMessage,
    _message_to_dict,
    messages_from_dict,
)

from langchain.memory.utils import get_prompt_input_key
from langchain.prompts.base import BasePromptTemplate
from langchain.schema import BaseMessage, get_buffer_string
from langchain.chains import LLMChain


class FirestoreEntityStore(BaseEntityStore):
    """Firestore-backed Entity store.
    """

    firestore_client: Any
    session_id: str = "song_brain"
    key_prefix: str = "memory_store"

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

    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve the messages from Firestore"""
        query = self.collection.document(self.session_id).get()
        if query.exists:
            items = query.to_dict().get("messages", [])
            messages = messages_from_dict(items)
            return messages
        return []

    def add_user_message(self, message: str) -> None:
        self.add_message(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
        self.add_message(AIMessage(content=message))

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

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.

        :meta private:
        """
        return ["entities"]
    
    def save_knowledge(self, inputs: Dict[str, Any]) -> None:
        """
        Save knowledge from this conversation history to the entity store.

        Generates a summary for each entity in the entity cache by prompting
        the model, and saves these summaries to the entity store.
        """


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

    def save_knowledge_person(self, inputs: Dict[str, Any]) -> None:
        """
        Save knowledge from this conversation history to the entity store.

        Generates a summary for each entity in the entity cache by prompting
        the model, and saves these summaries to the entity store.
        """


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
        name = inputs["name"]

        # Create an LLMChain for predicting entity summarization from the context
        chain = LLMChain(llm=self.llm, prompt=self.human_entity_summarization_prompt)

        # Get existing summary if it exists
        existing_summary = self.entity_store.get(name, "")
        output = chain.predict(
            summary=existing_summary,
            name=name,
            history=buffer_string,
            input=input_data,
        )
        # Save the updated summary to the entity store
        self.entity_store.set(name, output.strip())

