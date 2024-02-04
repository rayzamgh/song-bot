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

class ChainNeuron():

    def load_neuron(self) -> LLMChain:
        """
        Load the language learning model chain.
        """

        SONG_SYSTEM_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE = PromptTemplate(
            input_variables=["entities"] + list(self.keeper.status.keys()),
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
        ]

        input_variables = list(set(SONG_SYSTEM_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE.input_variables +
                                   SONG_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE.input_variables)) + ["history"]

        print("input_variables MAIN CHAIN")
        print(input_variables)

        final_prompt = ChatPromptTemplate(
            input_variables=input_variables, messages=messages)

        return LLMChain(llm=self.chat_model, verbose=True, prompt=final_prompt, memory=self.main_memory)

    def load_fast_neuron(self) -> LLMChain:
        """
        Load the language learning model chain.
        """

        SONG_SYSTEM_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE = PromptTemplate(
            input_variables=["entities"] + list(self.keeper.status.keys()),
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
        ]

        input_variables = list(set(SONG_SYSTEM_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE.input_variables +
                                   SONG_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE.input_variables)) + ["history"]

        print("input_variables MAIN CHAIN")
        print(input_variables)

        final_prompt = ChatPromptTemplate(
            input_variables=input_variables, messages=messages)

        return LLMChain(llm=self.chat_model, verbose=True, prompt=final_prompt, memory=None)