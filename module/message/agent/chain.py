"""Chat Chain specifically for ChatModels"""
from __future__ import annotations

import warnings
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from pydantic import Extra, Field

from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import (
    AsyncCallbackManager,
    AsyncCallbackManagerForChainRun,
    CallbackManager,
    CallbackManagerForChainRun,
    Callbacks,
)
from langchain.chains.base import Chain
from langchain.input import get_colored_text
from langchain.load.dump import dumpd
from langchain.prompts.base import BasePromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import (
    BaseLLMOutputParser,
    LLMResult,
    NoOpOutputParser,
    BaseMessage,
    PromptValue,
)
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate, ChatPromptTemplate
from langchain.chains import ConversationChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

# class ChatLLMChain(ConversationChain):

#     system_prompt : BasePromptTemplate
    
#     def prep_prompts(
#         self,
#         input_list: List[Dict[str, Any]],
#         run_manager: Optional[CallbackManagerForChainRun] = None,
#     ) -> Tuple[List[PromptValue], Optional[List[str]]]:
#         """Prepare prompts from inputs."""
#         stop = None
#         if "stop" in input_list[0]:
#             stop = input_list[0]["stop"]
#         messages = []
#         prompts = []
#         for inputs in input_list:
#             selected_inputs = {k: inputs[k] for k in self.prompt.input_variables}
#             del selected_inputs['input']

#             sys_prompt = self.system_prompt.format_prompt(**selected_inputs)

#             messages.append(sys_prompt)

#             history : List[BaseMessage] = inputs["history"]

#             for ind_conv_history in history:
                
#                 temp = PromptTemplate.from_template(template="{content}")

#                 prompt = temp.format_prompt(content=ind_conv_history.content)

                
#                 # messages = [
#                 #     SystemMessagePromptTemplate.from_template(system_message),
#                 #     MessagesPlaceholder(variable_name="chat_history"),
#                 #     HumanMessagePromptTemplate.from_template(final_prompt),
#                 #     MessagesPlaceholder(variable_name="agent_scratchpad"),
#                 # ]
#                 # return ChatPromptTemplate(input_variables=input_variables, messages=messages)

#                 _colored_text = get_colored_text(prompt.to_string(), "green")
#                 _text = "Prompt after formatting:\n" + _colored_text
#                 if run_manager:
#                     run_manager.on_text(_text, end="\n", verbose=self.verbose)
#                 if "stop" in inputs and inputs["stop"] != stop:
#                     raise ValueError(
#                         "If `stop` is present in any inputs, should be present in all."
#                     )
#                 prompts.append(prompt)
#             prompts.append(self.prompt.format_prompt(input=inputs["input"], entities=inputs["entities"]) )

#         print("FULL ALL PROMPTS")
#         print(prompts)


#         return prompts, stop
