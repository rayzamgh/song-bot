from abc import abstractmethod

class BaseInterractor():
    def __init__(self):
        # Initiate Interractor dependencies e.g. openai client & youtube client
        pass
    
    @abstractmethod
    async def interract(self, args : dict = None):
        pass

    @abstractmethod
    def exit(self):
        pass
