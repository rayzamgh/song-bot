import requests
import io
from PIL import Image
from discord import Message, User, MessageType
from module.base_module import BaseModule
from module import SongBrain
from utils import get_original_message
from interractor.image import ImageInterractor

class MessageModule(BaseModule):
    def __init__(self):
        # Initiate module dependencies e.g. openai client & youtube client
        self.song_agent : SongBrain = SongBrain()

        # Interractors Used
        self.image_interractor: ImageInterractor = ImageInterractor()
    
    async def execute(self, message : Message, *args, **kwargs):
        
        async with message.channel.typing():
            # Get Replies if any
            author = message.author.name
            original_message = await get_original_message(message) if message.reference else None

            input_message = self.prep_message(message, original_message)    
            
            song_said = await self.song_agent.arun(input_message, author)

            print("song_said")
            print(song_said)
        
            await message.channel.send(song_said)

    def preprocess_message(self, raw_input: str) -> str:
        """
        Preprocess the raw input message, replacing any mentions of the bot with its name.
        """
        return raw_input.replace('<@1132625921636048977>', 'Song')

    def prep_message(self, message: Message, original_message: Message = None) -> str:
        """
        Prepare message as a whole for the chain to run
        """
        incoming_message: str = message.content
        mentioned_users: list[User] = message.mentions
        sender: User = message.author

        for user in mentioned_users:
            incoming_message = incoming_message.replace(
                f"<@{user.id}>", user.name)

        if message.type is MessageType.reply:
            if original_message.attachments:
                for attachment in original_message.attachments:
                    if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):

                        response = requests.get(attachment.url)
                        image = Image.open(io.BytesIO(response.content))

                        # Process the image
                        image_content = self.image_interractor.extract_image(
                            image, f"Jelaskan apa yang ada dalam gambar ini, lalu jawab : {incoming_message}")


                        input_message = f"Terdapat gambar yang berisi: \"{image_content}.\". Terkait gambar ini, {sender.name} bilang: \"{self.preprocess_message(incoming_message)}\""
            else:
                print(original_message.attachments)
                input_message = f"untuk menjawab kalimat, \"{self.preprocess_message(original_message.content)}.\" dari {original_message.author.name}. {sender.name} bilang, \"{self.preprocess_message(incoming_message)}\""
        else:
            input_message = f"\"{sender.name} bilang:\" {self.preprocess_message(incoming_message)}"

        return input_message
    
    def exit(self):
        pass
