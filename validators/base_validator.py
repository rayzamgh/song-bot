from abc import abstractclassmethod
from discord import Client

class BaseValidator():
    def __init__(self):
        pass

    @abstractclassmethod
    def __call__(self, func):
        pass
