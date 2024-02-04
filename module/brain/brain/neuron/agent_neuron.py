import io
import requests
from typing import Dict, List
from discord import Message, User, MessageType
from google.cloud import firestore
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.base_language import BaseLanguageModel
from langchain.utilities import WikipediaAPIWrapper, GoogleSearchAPIWrapper, ArxivAPIWrapper
from langchain.chains import LLMChain
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    MessagesPlaceholder,
                                    SystemMessagePromptTemplate)
from langchain.prompts.prompt import PromptTemplate
from langchain.agents import OpenAIFunctionsAgent
from langchain.prompts import (
    FewShotChatMessagePromptTemplate,
    ChatPromptTemplate,
)
from utils import get_original_message
from interractor.image import ImageInterractor
from PIL import Image
from ..prompts import (ENTITY_SUMMARIZATION_PROMPT,
                      ENTITY_EXTRACTION_PROMPT,
                      PERSON_INFORMATION_EXTRACTION_PROMPT,
                      SONG_PREFIX,
                      SONG_ENTITY_MEMORY_CONVERSATION_TEMPLATE,
                      SONG_INPUT_TEMPLATE,
                      SONG_YES_LANG_TEMPLATE,
                      SONG_TALK_TEMPLATE)
from ..memory import FirestoreEntityStore, FirestoreChatMessageHistory, ChatConversationEntityMemory
from ..keeper import SongKeeper

class AgentNeuron():

    def __init__(self):
        self.toolkit: List[Tool] = self.load_toolkit()
    
    def load_toolkit(self) -> List[Tool]:
        """
        Load the default tools for the bot: Google Search and Wikipedia.
        """
        search = GoogleSearchAPIWrapper()
        wikipedia = WikipediaAPIWrapper()
        arxiv = ArxivAPIWrapper(top_k_results=2)

        default_toolkit = [
            Tool(
                name="Search",
                func=search.run,
                description="For when you are trying to search the internet for informations you are not aware the answer to."),
            Tool(
                name="Wikipedia",
                func=wikipedia.run,
                description="For when you need to find detailed information on a topic or famous things."),
            Tool(
                name="Arxiv",
                func=arxiv.run,
                description="""For when you need to answer questions about scientific papers and journals, the input must be an exact DOI or title of the scientific paper."""
            ),
        ]

        return default_toolkit
    
    def load_neuron(self) -> OpenAIFunctionsAgent:
        """
        Load the language learning model thinking agent.
        """

        SONG_SYSTEM_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE = PromptTemplate(
            input_variables=["entities", "sender", "sender_summary"] + list(self.keeper.status.keys()),
            template=SONG_PREFIX + SONG_ENTITY_MEMORY_CONVERSATION_TEMPLATE,
        )

        SONG_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE = PromptTemplate(
            input_variables=["input"],
            template=SONG_INPUT_TEMPLATE,
        )

        messages = [
            SystemMessagePromptTemplate(
                prompt=SONG_SYSTEM_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE, additional_kwargs={}),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate(
                prompt=SONG_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE, additional_kwargs={}),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]

        input_variables = list(set(SONG_SYSTEM_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE.input_variables +
                                   SONG_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE.input_variables)) + ["history", "agent_scratchpad"]

        print("input_variables MAIN AGENT")
        print(input_variables)

        final_prompt = ChatPromptTemplate(
            input_variables=input_variables,
            messages=messages
        )

        agent_executor = initialize_agent(
            llm=self.chat_model,
            tools=self.toolkit,
            agent=AgentType.OPENAI_FUNCTIONS,
            memory=self.main_memory,
            verbose=True,
            prompt=final_prompt,
        )

        return agent_executor