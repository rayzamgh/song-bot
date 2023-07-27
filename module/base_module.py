from abc import abstractmethod
from discord import Message

class BaseModule():
    def __init__(self):
        # Initiate module dependencies e.g. openai client & youtube client
        pass
    
    @abstractmethod
    async def execute(self, message : Message, args : dict = None):
        pass

    @abstractmethod
    def exit(self):
        pass
