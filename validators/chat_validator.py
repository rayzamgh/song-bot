from .base_validator import BaseValidator
from router import RouterTypes
from discord import Message, Client
from enum import Enum

class ChatValidatorErrors(Enum):
    UNIDENTIFIED_INTENT_ERROR: Exception("Unidentified intent!")


class ChatValidator(BaseValidator):

    def __call__(self, func):
        def wrapper(*args, **kwargs):

            message : Message = kwargs["message"]
            client : Client = kwargs["client"]
            intent : RouterTypes = None

            if message.author != client.user:                
                if client.user.mentioned_in(message):
                    intent = RouterTypes.Message
                elif message.content.startswith("!sc"):
                    intent = RouterTypes.Command
            
            kwargs["route"] = intent

            return func(*args, **kwargs)
        return wrapper
