import os
from typing import Dict
from google.cloud import firestore
from langchain_openai import ChatOpenAI
from langchain_cohere import ChatCohere
from langchain.base_language import BaseLanguageModel
from langchain_community.utilities import WikipediaAPIWrapper, GoogleSearchAPIWrapper, ArxivAPIWrapper
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
from google.generativeai.types.safety_types import HarmBlockThreshold, HarmCategory
from .prompts import (ENTITY_SUMMARIZATION_PROMPT,
                      ENTITY_EXTRACTION_PROMPT,
                      PERSON_INFORMATION_SUMMARIZATION_PROMPT,
                      SONG_PREFIX,
                      SONG_ENTITY_MEMORY_CONVERSATION_TEMPLATE,
                      SONG_INPUT_TEMPLATE,
                      SONG_YES_LANG_TEMPLATE,
                      SONG_TALK_TEMPLATE)
from .memory import FirestoreEntityStore, FirestoreChatMessageHistory, ChatConversationEntityMemory
from .keeper import SongKeeper
from .neuron import AgentNeuron, ChainNeuron
from .utils import trim_quotes


from langchain_google_genai import ChatGoogleGenerativeAI


class SongBrain(ChainNeuron):
    # Choose between ChainNeuron or AgentNeuron
    """
    A language learning model (LLM) chatbot for Discord servers. It uses OpenAI's GPT-3.5-turbo for chat and memory operations, and incorporates Google Search and Wikipedia APIs for search operations.
    """
    _instance = None  # Class attribute to hold the single instance

    MODELSET_OPENAI = 1
    MODELSET_GOOGLE = 2
    MODELSET_COHERE = 3

    model_set = {
        1 : {
            "mem_model" : ChatOpenAI(
                model_name="gpt-4-turbo-preview",
                temperature=0.2),
            "chat_model" : ChatOpenAI(
                model_name="gpt-4",
                temperature=0.7),
            "talk_model" : ChatOpenAI(
                model_name="gpt-4",
                temperature=0.7),
            "style_model" : ChatOpenAI(
                model_name="gpt-4",
                temperature=0.4)
        },
        2 : {
            "mem_model" : ChatOpenAI(
                model_name="gpt-4-turbo-preview",
                temperature=0.2),
            "chat_model" : ChatOpenAI(
                model_name="gpt-4",
                temperature=0.7),
            "talk_model" : ChatOpenAI(
                model_name="gpt-4",
                temperature=0.7),
            "style_model" : ChatGoogleGenerativeAI(
                model="gemini-1.5-pro-latest",
                temperature=0.7,
                top_p=0.95,
                convert_system_message_to_human=True,
                google_api_key=os.environ["GEMINI_API_KEY"],
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                },
                HarmCategory="new")
        },
        3 : {
            "mem_model" : ChatOpenAI(
                model_name="gpt-4-turbo-preview",
                temperature=0.2),
            "chat_model" : ChatCohere(
                model="command-r-plus",
                temperature=0.7,
                connectors=[{"id":"web-search","options":{"site":"wikipedia.org"}}]
                ),
            "talk_model" : ChatOpenAI(
                model_name="gpt-4-turbo-preview",
                temperature=0.7),
            "style_model" : ChatCohere(
                model="command-r-plus",
                temperature=0.7
                ),
        }
    }

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SongBrain, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            # Prevent reinitialization
            return
        self._initialized = True

        modelset = self.MODELSET_COHERE
        
        # Initialize Models
        self.mem_model : BaseLanguageModel = self.model_set[modelset]["mem_model"]
        self.chat_model : BaseLanguageModel = self.model_set[modelset]["chat_model"]
        self.talk_model : BaseLanguageModel = self.model_set[modelset]["talk_model"]
        self.style_model : BaseLanguageModel = self.model_set[modelset]["style_model"]

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
                                                   human_entity_summarization_prompt=PERSON_INFORMATION_SUMMARIZATION_PROMPT,
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
            prompt=final_prompt,
            verbose=True
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
            llm=self.talk_model,
            prompt=final_prompt
        )
        return llm_chain

    def add_knowledge(self, inputs, type_knowledge="generic"):
        """
        Manually adds knowledge to bot
        """
        self.main_memory.save_knowledge(inputs, type_knowledge=type_knowledge)
        
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
            self.add_knowledge({"input" : message, "name": author}, type_knowledge="person")

            raw_output = self.executor.run(
                input=message, discord_username=author, **{**self.keeper.status, "sender" : author, "sender_summary" : sender_summary})
            
            # NOT NEEDED FOR NOW
            # raw_output = await self.talking_style_chain.arun(raw_output)

        else:
            raw_output = self.fast_executor.run(
                input=message, discord_username=author, **{**self.keeper.status, "sender" : author, "sender_summary" : sender_summary, "entities" : "", "history" : []})

        return trim_quotes(raw_output)

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
