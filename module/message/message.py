from discord import Message
from module.base_module import BaseModule
from module.message.agent import SongAgent

class MessageModule(BaseModule):
    def __init__(self):
        # Initiate module dependencies e.g. openai client & youtube client
        self.song_agent : SongAgent = SongAgent()
    
    async def execute(self, message : Message, args : dict = None):
        
        async with message.channel.typing():
            song_said = await self.song_agent.arun(message)

            print("song_said")
            print(song_said)
        
            await message.channel.send(song_said)

    def exit(self):
        pass
