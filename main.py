import os
from dotenv import load_dotenv

# load all environment variables
load_dotenv()

from discord import Intents
from client import SongClient

intents = Intents.all()
intents.message_content = True
client = SongClient(intents=intents)
discord_token = os.getenv('DISCORD_TOKEN')
client.run(discord_token)
