import os
from dotenv import load_dotenv
from discord.ext.commands import Bot

# load all environment variables
print("Loading envs")
load_dotenv(override=True)

from discord import Intents
from bot import SongBot

intents = Intents.all()
intents.message_content = True
client = SongBot(command_prefix="", intents=intents)


# ADD COGS HERE

discord_token = os.getenv('DISCORD_TOKEN')
client.run(discord_token)
