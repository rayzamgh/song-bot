import discord
from discord.ext.commands import Bot
from discord.ext import tasks
from utils import get_day_state
from bot.apis import GameSpotAPI
import os
from .config import CHANNEL_NAME_2_ID

class GamespotPlugin(Bot):

    # Static dictionary mapping channel names to their respective IDs
    CHANNEL_NAME_2_ID = CHANNEL_NAME_2_ID

    async def on_ready(self):
        # Log to console
        print('Gamespottin')
        # Setup for GameSpot API utility
        self.gamespot: GameSpotAPI = GameSpotAPI(os.environ.get("GAMESPOT_API_KEY"))

        # Start scheduled tasks for messaging and advancing song clock
        self.gamespot_scheduled_message.start()

    # Scheduled message from GameSpot (every 9 hours)
    @tasks.loop(hours=10)
    async def gamespot_scheduled_message(self):

        print("Scheduled gamestop!")

        channel = self.get_channel(self.CHANNEL_NAME_2_ID[os.getenv("ACTIVE_CHANNEL_NAME")])
        daystate = get_day_state()

        if channel and self.isactive:
            # Get a talking point from GameSpot API
            talking_point, extra_info = await self.gamespot.get_song_babble(GameSpotAPI.Topics.ARTICLES)
            print("=============== talking_point ===============")
            print(talking_point)

            # Convert talking point into a message via SongBrain
            talk = await self.chat_agent.atalk(talking_point)

            for key, value in extra_info.items():
                talk = value + "\n" + talk

            await channel.send(talk)

    # Additional error handling for the scheduled GameSpot message task
    @gamespot_scheduled_message.before_loop
    async def before_gamespot_scheduled_message(self):
        await self.wait_until_ready()

    @gamespot_scheduled_message.after_loop
    async def after_gamespot_scheduled_message(self):
        if self.gamespot_scheduled_message.failed():
            pass