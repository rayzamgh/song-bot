import os
from typing import Dict
from google.cloud import firestore
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
from .prompts import (ENTITY_SUMMARIZATION_PROMPT,
                      ENTITY_EXTRACTION_PROMPT,
                      PERSON_INFORMATION_EXTRACTION_PROMPT,
                      SONG_PREFIX,
                      SONG_ENTITY_MEMORY_CONVERSATION_TEMPLATE,
                      SONG_INPUT_TEMPLATE,
                      SONG_YES_LANG_TEMPLATE,
                      SONG_TALK_TEMPLATE)
from .memory import FirestoreEntityStore, FirestoreChatMessageHistory, ChatConversationEntityMemory
from .keeper import SongKeeper
from .neuron import AgentNeuron, ChainNeuron


from langchain_google_genai import ChatGoogleGenerativeAI

is_google = True

class SongBrain(ChainNeuron):
    # Choose between ChainNeuron or AgentNeuron
    """
    A language learning model (LLM) chatbot for Discord servers. It uses OpenAI's GPT-3.5-turbo for chat and memory operations, and incorporates Google Search and Wikipedia APIs for search operations.
    """
    _instance = None  # Class attribute to hold the single instance

    if is_google:
        mem_model: BaseLanguageModel = ChatGoogleGenerativeAI(
            model="gemini-pro", temperature=0, convert_system_message_to_human=True, google_api_key=os.environ["GEMINI_API_KEY"])
        style_model: BaseLanguageModel = ChatGoogleGenerativeAI(
            model="gemini-pro", temperature=0.8, convert_system_message_to_human=True, google_api_key=os.environ["GEMINI_API_KEY"])
        chat_model: BaseLanguageModel = ChatGoogleGenerativeAI(
            model="gemini-pro", temperature=0.3, convert_system_message_to_human=True, google_api_key=os.environ["GEMINI_API_KEY"])
    else:
        mem_model: BaseLanguageModel = ChatOpenAI(
            model_name="gpt-3.5-turbo-16k", temperature=0)
        style_model: BaseLanguageModel = ChatOpenAI(
            model_name="ft:gpt-3.5-turbo-1106:personal::8IwKijay", temperature=0.8)
        chat_model: BaseLanguageModel = ChatOpenAI(
            model_name="gpt-4-0125-preview", temperature=0.3)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SongBrain, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            # Prevent reinitialization
            return
        self._initialized = True

        # Your existing initialization code
        self.keeper: SongKeeper = self.load_keeper()
        self.main_memory: ChatConversationEntityMemory = self.load_memory()
        self.executor = self.load_neuron()
        self.fast_executor = self.load_fast_neuron()
        self.talk_chain = self.load_talk_chain()
        self.talking_style_chain = self.load_talking_style_chain()

        # Super init
        super().__init__()

    def load_keeper(self) -> Dict[str, str]:
        """
        Load the default keeper of the bot.
        """

        return SongKeeper()

    def load_memory(self) -> ChatConversationEntityMemory:
        """
        Load the memory system of the bot using Firestore for chat history and entity storage.
        """
        firestore_client = firestore.Client()

        message_history = FirestoreChatMessageHistory(client=firestore_client)
        main_memory = ChatConversationEntityMemory(llm=self.mem_model,
                                                   k=5,
                                                   input_key="input",
                                                   chat_history_key="history",
                                                   chat_memory=message_history,
                                                   entity_summarization_prompt=ENTITY_SUMMARIZATION_PROMPT,
                                                   human_entity_summarization_prompt=PERSON_INFORMATION_EXTRACTION_PROMPT,
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

        final_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SONG_TALK_TEMPLATE),
                ("human", "{input}"),
            ]
        )

        llm_chain = LLMChain(
            llm=self.style_model,
            prompt=final_prompt
        )
        return llm_chain

    def add_knowledge(self, input, type="generic"):
        """
        Manually adds knowledge to bot
        """

        if type == "generic":
            self.main_memory.save_knowledge(input)
        elif type == "person":
            self.main_memory.save_knowledge_person(input)

    async def arun(self, message: str, author: str, fast_mode=False) -> str:
        """
        Process a new message and generate an appropriate response using the chat chain, async.
        """
        print("SONG STATUS:")
        print(self.keeper.status)

        sender_summary = self.main_memory.entity_store.get(author, "They are a person that you just met")

        print(f"You are speaking to {author}")
        print(sender_summary)


        if not fast_mode:        
            self.add_knowledge({"input" : message, "name": author}, type="person")

            raw_output = self.executor.run(
                input=message, discord_username=author, **self.keeper.status | {
                    "sender" : author, 
                    "sender_summary" : sender_summary
                    })
            raw_output = await self.talking_style_chain.arun(raw_output)

        else:
            raw_output = self.fast_executor.run(
                input=message, discord_username=author, **self.keeper.status | {
                    "sender" : author, 
                    "sender_summary" : sender_summary,
                    "entities" : "",
                    "history" : []
                    })

        return raw_output

    async def atalk(self, talking_topic) -> str:
        """
        Process a scheduled message, async.
        """

        # Saves knowledge of the topic
        self.add_knowledge({"input": talking_topic})

        raw_output = await self.talk_chain.arun(talking_topic)
        
        self.main_memory.chat_memory.add_ai_message(raw_output)

        raw_output = raw_output.replace("!", ".")

        return raw_output
