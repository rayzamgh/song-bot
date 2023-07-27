from discord import Message, Client
from module import MessageModule, CommandModule, BaseModule
from validators import ChatValidator
from .router_types import RouterTypes
    
class Router:
    modules :dict[RouterTypes, BaseModule] = {}

    def __init__(self):

        self.modules = {
            RouterTypes.Message: MessageModule(),
            RouterTypes.Command: CommandModule(),
        }
    
    @ChatValidator()
    async def route(
        self, 
        client : Client,
        route : RouterTypes, 
        message : Message,
    ):  
        for module_name in self.modules.keys():
            if module_name == route:
                await self.modules[module_name].execute(message)
