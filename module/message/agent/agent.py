

from langchain.agents import AgentType, initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage
)
from langchain.utilities import (WikipediaAPIWrapper, GoogleSearchAPIWrapper)
from langchain.llms import OpenAI
from typing import Any
from pydantic import BaseModel, Field
from google.cloud import firestore
from discord import Message, User, MessageType
from .prompts import (
    HUMAN_ENTITY_MEMORY_CONVERSATION_TEMPLATE, 
    ENTITY_SUMMARIZATION_PROMPT, 
    ENTITY_EXTRACTION_PROMPT, 
    SYSTEM_ENTITY_MEMORY_CONVERSATION_TEMPLATE
    )
from .memory import FirestoreEntityStore, FirestoreChatMessageHistory, ChatConversationEntityMemory
# from .chain import ChatLLMChain
from langchain.chains import LLMChain 
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

class SongAgent():
    def __init__(self):

        search = GoogleSearchAPIWrapper()
        wikipedia = WikipediaAPIWrapper()

        toolkit = [
            Tool(
                name="Search",
                func=search.run,
                description="""Search the internet for information, useful for when you need to answer questions about current events or the current state of the world. the input to this should be a single search term."""
            ),
            Tool(
                name="Wikipedia",
                func=wikipedia.run,
                description="""Useful for when you need to find detailed information on a topic or famous things such as : famous people, famous movies, famous places."""
            )
        ]
        
        # TODO
        # Change message history to firestore again, cheap
        # Make my own ConversationEntityMemory derivative
        #   Gk pake graph, instead store for every entity as a firestore key, 
        #   Valuenya adalah summarized information of said key

        firestore_client = firestore.Client()

        message_history = FirestoreChatMessageHistory(client=firestore_client)
        main_memory = ChatConversationEntityMemory(llm=OpenAI(temperature=0), 
                                                    k=3,
                                                    input_key="input",
                                                    chat_history_key="history",
                                                    chat_memory=message_history, 
                                                    entity_summarization_prompt = ENTITY_SUMMARIZATION_PROMPT,
                                                    entity_extraction_prompt = ENTITY_EXTRACTION_PROMPT,
                                                    return_messages=True, 
                                                    entity_store=FirestoreEntityStore(client=firestore_client),
                                                    max_token_limit=2000)
        
        
        messages = [
            SystemMessagePromptTemplate(prompt=SYSTEM_ENTITY_MEMORY_CONVERSATION_TEMPLATE, additional_kwargs={}),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate(prompt=HUMAN_ENTITY_MEMORY_CONVERSATION_TEMPLATE, additional_kwargs={}),
        ]
        final_prompt = ChatPromptTemplate(input_variables=["history", "input", "entities"], messages=messages)

        self.agent  = LLMChain(
            llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.70), 
            verbose=True,
            prompt=final_prompt,
            memory=main_memory,
        )
    
    def preprocess_message(self, raw_input : str) -> str:
        return raw_input.replace('<@1132625921636048977>', 'Song')

    def run(self, message : Message) -> str:
        incoming_message : str = message.content
        mentioned_users : list[User] = message.mentions
        sender : User = message.author
        
        for user in mentioned_users:
            print(f"{user.id} : {user.name}")
            incoming_message = incoming_message.replace(f"<@{user.id}>", user.name)

        if message.type is MessageType.reply:            
            original_message : Message = message.reference

            return self.agent.run(input=f"{sender.name} replies to {self.preprocess_message(message.system_content)} by {original_message.author}, with: {self.preprocess_message(incoming_message)}")

        else:
            return self.agent.run(input=f"{sender.name} says : {self.preprocess_message(incoming_message)}")

    def model_call(self) -> str:
        pass