
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


class FirestoreEntityStore(BaseEntityStore):
    """Firestore-backed Entity store.
    """

    firestore_client: Any
    session_id: str = "default"
    key_prefix: str = "memory_store"

    def __init__(
        self,
        client,
        session_id: str = "default",
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
        doc_ref = self.firestore_client.document(
            f'{self.full_key_prefix}/{key}')
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get('value', default)
        else:
            return default

    def set(self, key: str, value: Optional[str]) -> None:
        if not value:
            return self.delete(key)
        doc_ref = self.firestore_client.document(
            f'{self.full_key_prefix}/{key}')
        doc_ref.set({'value': value})

    def delete(self, key: str) -> None:
        doc_ref = self.firestore_client.document(
            f'{self.full_key_prefix}/{key}')
        doc_ref.delete()

    def exists(self, key: str) -> bool:
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
        self.append(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
        self.append(AIMessage(content=message))

    def append(self, message: BaseMessage) -> None:
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

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.

        :meta private:
        """
        return ["entities"]
