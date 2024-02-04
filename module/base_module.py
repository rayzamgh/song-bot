from abc import ABC, abstractmethod
from typing import Any

class BaseModule(ABC):
    def __init__(self):
        # Initiate module dependencies e.g. openai client & youtube client
        pass
    
    @abstractmethod
    async def execute(self, *args, **kwargs):
        pass

    @abstractmethod
    def exit(self):
        pass
