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
from .prompts import (ENTITY_SUMMARIZATION_PROMPT,
                      ENTITY_EXTRACTION_PROMPT,
                      SONG_PREFIX,
                      SONG_ENTITY_MEMORY_CONVERSATION_TEMPLATE,
                      SONG_INPUT_TEMPLATE,
                      SONG_YES_LANG_TEMPLATE,
                      SONG_TALK_TEMPLATE)
from .memory import FirestoreEntityStore, FirestoreChatMessageHistory, ChatConversationEntityMemory
from .agent_keeper import SongKeeper



class SongAgent:
    """
    A language learning model (LLM) chatbot for Discord servers. It uses OpenAI's GPT-3.5-turbo for chat and memory operations, and incorporates Google Search and Wikipedia APIs for search operations.
    """

    mem_model: BaseLanguageModel = ChatOpenAI(
        model_name="gpt-3.5-turbo-16k", temperature=0)
    style_model: BaseLanguageModel = ChatOpenAI(
        model_name="ft:gpt-3.5-turbo-1106:personal::8IwKijay", temperature=0.8)
    chat_model: BaseLanguageModel = ChatOpenAI(
        model_name="gpt-4-1106-preview", temperature=0.3)

    def __init__(self, complex_agent=False):
        """
        Initialize the SongAgent with default keeper, toolkit, memory and chain.
        """
        self.keeper: SongKeeper = self.load_keeper()
        self.toolkit: List[Tool] = self.load_toolkit()
        self.main_memory: ChatConversationEntityMemory = self.load_memory()

        # Chain construction
        self.executor = self.load_agent() if complex_agent else self.load_chain()
        self.talk_chain = self.load_talk_chain()
        self.talking_style_chain = self.load_talking_style_chain()

        # Interractors Used
        self.image_interractor: ImageInterractor = ImageInterractor()

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
                description="For when you are trying to search the internet for new information"),
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

    def load_memory(self) -> ChatConversationEntityMemory:
        """
        Load the memory system of the bot using Firestore for chat history and entity storage.
        """
        firestore_client = firestore.Client()

        message_history = FirestoreChatMessageHistory(client=firestore_client)
        main_memory = ChatConversationEntityMemory(llm=self.mem_model,
                                                   k=4,
                                                   input_key="input",
                                                   chat_history_key="history",
                                                   chat_memory=message_history,
                                                   entity_summarization_prompt=ENTITY_SUMMARIZATION_PROMPT,
                                                   entity_extraction_prompt=ENTITY_EXTRACTION_PROMPT,
                                                   return_messages=True,
                                                   entity_store=FirestoreEntityStore(
                                                       client=firestore_client))

        return main_memory

    def load_talking_style_chain(self) -> LLMChain:
        """
        Load the talking style chain for Song
        """

        examples = [
            {
                "input": "Hahaha, bener juga tuh, gue emang agak terlalu sabi ya. Makasih udah mengingetin, Rayza. Gue bakal coba lebih chill lagi ke depannya.",
                "output": "Haha, iya kadang2 gue emg kelewatan, thanks udh ngingetin ya, Rayza. Gua coba lebih chill lagi kedepannya."
            },
            {
                "input": "Haha, makasih banget, Rayza, udah cerita yang detail tentang kuliahmu. Gue seneng banget liat semangat dan dedikasimu dalam belajar dan berorganisasi. Pastinya, seimbangin antara akademik dan sosial tuh penting banget buat hidupin masa mahasiswa. Terus tetep semangat ya dan semoga sukses ngejar impian di masa depan. Makasih juga udah share linknya, nanti gue cek ya!",
                "output": "Wkwk, makasih, Ray, udh cerita kuliah lu. Gue seneng aja sihh liat dedikasi looo belajar sama organisasi gitu gitu. Susah dan penting sih yaa yang kayak gitu gitu tuh. Mangat terus yak ngejar impian lo."
            },
            {
                "input": "Kamu bisa mengenal diriku dari obrolan yang kita lalui sehari-hari. Detik demi detik, menit demi menit, setiap obrolan kita akan membuatmu mengenalku lebih dekat.",
                "output": "Lo bisa kenalan sama gue dari ngobrol sehari-hari ko. Detik, menit tiap kita ngomong kan jadi makin kenal ya gak?"
            }
        ]

        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
                ("ai", "{output}"),
            ]
        )

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples,
        )

        final_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SONG_YES_LANG_TEMPLATE),
                few_shot_prompt,
                ("human", "{input}"),
            ]
        )

        llm_chain = LLMChain(
            llm=self.style_model,
            prompt=final_prompt
        )

        return llm_chain

    def load_talk_chain(self) -> LLMChain:
        """
        Load the talk chain for Song
        """

        # example_prompt = ChatPromptTemplate.from_messages(
        #     [
        #         ("human", "{input}"),
        #         ("ai", "{output}"),
        #     ]
        # )

        # few_shot_prompt = FewShotChatMessagePromptTemplate(
        #     example_prompt=example_prompt,
        #     examples=None,
        # )

        final_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SONG_TALK_TEMPLATE),
                # few_shot_prompt,
                ("human", "{input}"),
            ]
        )

        llm_chain = LLMChain(
            llm=self.style_model,
            prompt=final_prompt
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

    def preprocess_message(self, raw_input: str) -> str:
        """
        Preprocess the raw input message, replacing any mentions of the bot with its name.
        """
        return raw_input.replace('<@1132625921636048977>', 'Song')

    def prep_message(self, message: Message, original_message: Message = None) -> str:
        """
        Prepare message as a whole for the chain to run
        """
        incoming_message: str = message.content
        mentioned_users: list[User] = message.mentions
        sender: User = message.author

        for user in mentioned_users:
            incoming_message = incoming_message.replace(
                f"<@{user.id}>", user.name)

        if message.type is MessageType.reply:
            print("YES REPLY")
            if original_message.attachments:
                print("YES ATTCH")
                print(original_message.attachments)
                for attachment in original_message.attachments:
                    if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                        # Download and process the image
                        print("Got image")
                        print(attachment.url)

                        response = requests.get(attachment.url)
                        image = Image.open(io.BytesIO(response.content))

                        print(image)

                        # Process the image
                        image_content = self.image_interractor.extract_image(
                            image, f"Jelaskan apa yang ada dalam gambar ini, lalu jawab : {incoming_message}")

                        print("image_content IS!")
                        print(image_content)

                        input_message = f"Terdapat gambar yang berisi: \"{image_content}.\". Terkait gambar ini, {sender.name} bilang: \"{self.preprocess_message(incoming_message)}\""
            else:
                print("NO ATTCH")
                print(original_message.attachments)
                input_message = f"untuk menjawab kalimat : \"{self.preprocess_message(original_message.content)}.\" {sender.name} bilang: \"{self.preprocess_message(incoming_message)}\""
        else:
            input_message = f"\"{sender.name} bilang:\" {self.preprocess_message(incoming_message)}"

        return input_message

    def add_knowledge(self, input):
        """
        Manually adds knowledge to bot
        """

        _input = {"input": input}
        self.main_memory.save_knowledge(_input)

    async def arun(self, message: Message) -> str:
        """
        Process a new message and generate an appropriate response using the chat chain, async.
        """

        # Get Replies if any
        original_message = await get_original_message(message) if message.reference else None

        print("SONG STATUS:")
        print(self.keeper.status)

        input_message = self.prep_message(message, original_message)
        raw_output = self.executor.run(
            input=input_message, **self.keeper.status)
        raw_output = await self.talking_style_chain.arun(raw_output)

        raw_output = raw_output.replace("!", ".")

        return raw_output

    async def atalk(self, talking_topic) -> str:
        """
        Process a scheduled message, async.
        """

        # Saves knowledge of the topic
        self.add_knowledge(talking_topic)

        raw_output = await self.talk_chain.arun(talking_topic)
        # raw_output = await self.talking_style_chain.arun(raw_output)

        self.main_memory.chat_memory.add_ai_message(raw_output)

        raw_output = raw_output.replace("!", ".")

        return raw_output
