from discord import Message, Client
from module import MessageModule, CommandModule, BaseModule
from enum import Enum
from discord import Message, Client
from enum import Enum

class Router:

    class RouterValidator:

        class ChatValidatorErrors:
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

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            print("FIRST INIT SINGLETON ROUTER")
            cls._instance = super(Router, cls).__new__(cls, *args, **kwargs)
            
            cls._instance.modules = {
                cls._instance.RouterTypes.MESSAGE: MessageModule(),
                cls._instance.RouterTypes.COMMAND: CommandModule(),
            }

        return cls._instance

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
