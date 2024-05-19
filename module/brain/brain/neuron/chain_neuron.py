
from langchain.chains import LLMChain
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    MessagesPlaceholder,
                                    SystemMessagePromptTemplate)
from langchain.prompts.prompt import PromptTemplate
from langchain.prompts import (
    FewShotChatMessagePromptTemplate,
    ChatPromptTemplate,
)
from utils import get_original_message
from interractor.image import ImageInterractor
from PIL import Image
# from ..promptsv2 import (ENTITY_SUMMARIZATION_PROMPT,
#                       ENTITY_EXTRACTION_PROMPT,
#                       SONG_PREFIX,
#                       SONG_ENTITY_MEMORY_CONVERSATION_TEMPLATE,
#                       SONG_INPUT_TEMPLATE,
#                       SONG_YES_LANG_TEMPLATE,
#                       SONG_TALK_TEMPLATE)
from ..promptsv3 import TemplateManager

class ChainNeuron():

    def __init__(self):
        self.tm = TemplateManager()

    def load_neuron(self) -> LLMChain:
        """
        Load the language learning model chain.
        """

        SONG_SYSTEM_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE = PromptTemplate(
            input_variables=["entities"] + list(self.keeper.status.keys()),
            template=self.tm.get_template_string("song_prefix") + self.tm.get_template_string("song_entity_memory_conversation_template"),
        )

        SONG_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE = PromptTemplate(
            input_variables=["input"],
            template=self.tm.get_template_string("song_input_template"),
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
            template=self.tm.get_template_string("song_prefix") + self.tm.get_template_string("song_entity_memory_conversation_template"),
        )

        SONG_ENTITY_MEMORY_CONVERSATION_PROMPT_TEMPLATE = PromptTemplate(
            input_variables=["input"],
            template=self.tm.get_template_string("song_input_template"),
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