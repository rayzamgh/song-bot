from typing import Dict, List, Optional
from discord import Message, User, MessageType
from datetime import datetime
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.base_language import BaseLanguageModel
from langchain.utilities import WikipediaAPIWrapper, GoogleSearchAPIWrapper, ArxivAPIWrapper
from langchain.chains import LLMChain
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from .prompts import (ENTITY_SUMMARIZATION_PROMPT,
                      ENTITY_EXTRACTION_PROMPT,
                      SONG_PREFIX,
                      SONG_ENTITY_MEMORY_CONVERSATION_TEMPLATE,
                      SONG_INPUT_TEMPLATE,
                      SONG_YES_LANG_TEMPLATE)
from .memory import FirestoreEntityStore, FirestoreChatMessageHistory, ChatConversationEntityMemory
from .agent_keeper import SongKeeper
from google.cloud import firestore
from langchain.prompts.prompt import PromptTemplate
from langchain.agents import OpenAIFunctionsAgent
from langchain.agents import AgentExecutor
from langchain.chains import SequentialChain

# TODO

# In addition to the existing keeper status parameters ("mood", "busyness", "current_activity"), you might want to consider including the following:

# Datetime: The current date and time would be useful, especially if the bot's responses depend on the time of day.

# Activity Duration: How long the bot has been performing the current activity.

# Location: If the bot is designed to simulate being in a particular place, this could be a useful attribute.

# Energy Level: This could simulate the bot's "endurance" and may influence how it interacts with users.

# Task Progress: If the bot is performing a long-running task, it could be useful to track how much of the task has been completed.

# Interaction Count: You can track how many interactions the bot has had in a given period.

# Last Interaction: Time since the last interaction.

# Mode: The bot could have different modes, like "idle", "busy", "interactive", "do not disturb", etc.

# Previous Task: What the bot was doing before the current activity.

# Upcoming Task: What the bot is scheduled to do next.


class SongAgent:
    """
    A language learning model (LLM) chatbot for Discord servers. It uses OpenAI's GPT-3.5-turbo for chat and memory operations, and incorporates Google Search and Wikipedia APIs for search operations.
    """

    mem_model: BaseLanguageModel = ChatOpenAI(
        model_name="gpt-3.5-turbo-0301", temperature=0)
    chat_model: BaseLanguageModel = ChatOpenAI(
        model_name="gpt-3.5-turbo-16k", temperature=0.8)

    def __init__(self, complex_agent = True):
        """
        Initialize the SongAgent with default keeper, toolkit, memory and chain.
        """
        self.keeper: SongKeeper = self.load_keeper()
        self.toolkit: List[Tool] = self.load_toolkit()
        self.main_memory: ChatConversationEntityMemory = self.load_memory()

        # Chain construction
        self.executor = self.load_agent() if complex_agent else self.load_chain()
        self.talking_style_chain  = self.load_talking_style_chain()

    def load_keeper(self) -> Dict[str, str]:
        """
        Load the default keeper of the bot.
        """

        return SongKeeper()

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
                description="Useful for when you are tryint to search the internet for information, on the latest news that you are unsure about"),
            Tool(
                name="Wikipedia", 
                func=wikipedia.run,
                description="Useful for when you need to find detailed information on a topic or famous things."),
            Tool(
                name="Arxiv",
                func=arxiv.run,
                description="""Useful for when you need to answer questions about scientific papers and journals, the input must be an exact DOI or title of the scientific paper."""
            ),
        ]

        return default_toolkit

    def load_memory(self) -> ChatConversationEntityMemory:
        """
        Load the memory system of the bot using Firestore for chat history and entity storage.
        """
        firestore_client = firestore.Client()

        message_history = FirestoreChatMessageHistory(client=firestore_client)
        main_memory = ChatConversationEntityMemory(llm=self.mem_model,
                                                   k=8,
                                                   input_key="input",
                                                   chat_history_key="history",
                                                   chat_memory=message_history,
                                                   entity_summarization_prompt=ENTITY_SUMMARIZATION_PROMPT,
                                                   entity_extraction_prompt=ENTITY_EXTRACTION_PROMPT,
                                                   return_messages=True,
                                                   entity_store=FirestoreEntityStore(
                                                       client=firestore_client),
                                                   max_token_limit=3000)

        return main_memory
    
    def load_talking_style_chain(self) -> LLMChain:
        """
        Load the talking style chain for Song
        """

        llm_chain = LLMChain(
            llm=self.mem_model,
            prompt=PromptTemplate.from_template(SONG_YES_LANG_TEMPLATE)
        )

        return llm_chain

    def load_chain(self) -> LLMChain:
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

        print("input_variables")
        print(input_variables)

        final_prompt = ChatPromptTemplate(
            input_variables=input_variables, messages=messages)

        return LLMChain(llm=self.chat_model, verbose=True, prompt=final_prompt, memory=self.main_memory)
    
    def load_agent(self) -> OpenAIFunctionsAgent:
        """
        Load the language learning model thinking agent.
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
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]

        input_variables = list(set(SONG_SYSTEM_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE.input_variables +
                                   SONG_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE.input_variables)) + ["history", "agent_scratchpad"]

        print("input_variables")
        print(input_variables)

        final_prompt = ChatPromptTemplate(
            input_variables=input_variables, messages=messages)

        agent = OpenAIFunctionsAgent(llm=self.chat_model, tools=self.toolkit, prompt=final_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.toolkit, memory=self.main_memory, verbose=True)


        # TODO: BROKEN ABOUT RIGHT HERE:

        return agent_executor

    def preprocess_message(self, raw_input: str) -> str:
        """
        Preprocess the raw input message, replacing any mentions of the bot with its name.
        """
        return raw_input.replace('<@1132625921636048977>', 'Adelia')
    
    def prep_message(self, message : Message) -> str:
        """
        Prepare message as a whole for the chain to run
        """
        incoming_message: str = message.content
        mentioned_users: list[User] = message.mentions
        sender: User = message.author

        # Get the current date and time
        current_datetime = datetime.now()

        # Format it into a more readable string
        self.keeper.status["time"] = current_datetime.strftime(
            '%Y-%m-%d %H:%M:%S')

        for user in mentioned_users:
            incoming_message = incoming_message.replace(
                f"<@{user.id}>", user.name)

        if message.type is MessageType.reply:
            original_message: Message = message.reference
            input_message = f"{sender.name} replies to {self.preprocess_message(original_message.content)}, with: {self.preprocess_message(incoming_message)}"
        else:
            input_message = f"{sender.name} says : {self.preprocess_message(incoming_message)}"

        return input_message

    def run(self, message: Message) -> str:
        """
        Process a new message and generate an appropriate response using the chat chain.
        """
        input_message = self.prep_message(message)
        
        raw_output = self.executor.run(input=input_message, **self.keeper.status)
        final_output = self.talking_style_chain.run(raw_output)

        return final_output

    async def arun(self, message: Message) -> str:
        """
        Process a new message and generate an appropriate response using the chat chain, async.
        """
        input_message = self.prep_message(message)
        raw_output = await self.executor.arun(input=input_message, **self.keeper.status)
        final_output = await self.talking_style_chain.arun(raw_output)

        return final_output