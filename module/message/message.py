from discord import Message
from module.base_module import BaseModule
from module.message.agent import SongAgent

class MessageModule(BaseModule):
    def __init__(self):
        # Initiate module dependencies e.g. openai client & youtube client
        self.song_agent = SongAgent()
    
    async def execute(self, message : Message, args : dict = None):
        
        async with message.channel.typing():
            song_said = self.song_agent.run(message)
        
            await message.channel.send(song_said)

        # if message.content.startswith("rayza ganteng"):
        #     await message.channel.send("Dat's false!")
        # else:
        #     await message.channel.send("Shmuckerooni")

    def exit(self):
        pass
