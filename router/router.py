from discord import Message, Client
from module import MessageModule, CommandModule, BaseModule
from enum import Enum
from discord import Message, Client
from enum import Enum

class Router:

    class RouterValidator():

        class ChatValidatorErrors():
            UNIDENTIFIED_INTENT_ERROR: Exception("Unidentified intent!")

        def __call__(self, func):
            def wrapper(*args, **kwargs):

                message : Message = kwargs["message"]
                client : Client = kwargs["client"]
                intent : Router.RouterTypes = None

                if message.author != client.user:                
                    if client.user.mentioned_in(message):
                        intent = Router.RouterTypes.MESSAGE
                    elif message.content.startswith("!sc"):
                        intent = Router.RouterTypes.COMMAND
                
                kwargs["route"] = intent

                return func(*args, **kwargs)
            return wrapper
    
    class RouterTypes(Enum):
        MESSAGE = "message"
        COMMAND = "command"

    modules :dict[RouterTypes, BaseModule] = {}

    def __init__(self):

        self.modules = {
            self.RouterTypes.MESSAGE: MessageModule(),
            self.RouterTypes.COMMAND: CommandModule(),
        }

    @RouterValidator()
    async def route(
        self, 
        client : Client,
        route : RouterTypes, 
        message : Message,
    ):  
        if route:
            print(f"{route=}")
            await self.modules[route].execute(message)
