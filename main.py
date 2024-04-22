import os
from dotenv import load_dotenv

# load all environment variables
print("Loading envs")
load_dotenv(override=True)

from discord import Intents
from bot import SongBot

intents = Intents.all()
intents.message_content = True
intents.voice_states = True

client = SongBot(command_prefix="$", intents=intents)

print("Bot Ready!")

discord_token = os.getenv('DISCORD_TOKEN')
client.run(discord_token)
