import discord
from discord.ext.commands import Bot
from router import Router
from module import SongBrain
from interractor.image import ImageInterractor
from discord.ext import tasks
from utils import get_day_state
from .config import CHANNEL_NAME_2_ID
import os
class BabblePlugin(Bot):

    # Static dictionary mapping channel names to their respective IDs
    CHANNEL_NAME_2_ID = CHANNEL_NAME_2_ID

    async def on_ready(self):
        # Log to console
        print('Babbling')
        # Setup for message routing and song management
        self.active_router: Router = Router()

        # Setup for GameSpot API utility
        self.image_interractor: ImageInterractor = ImageInterractor()
        self.chat_agent: SongBrain = self.active_router.modules[Router.RouterTypes.MESSAGE].song_agent

        # Start scheduled tasks for messaging and advancing song clock
        self.convo_scheduled_message.start()


    # Scheduled conversation starter
    @tasks.loop(hours=40)
    async def convo_scheduled_message(self):
        print("Scheduled convo!")

        channel = self.get_channel(self.CHANNEL_NAME_2_ID[os.getenv("ACTIVE_CHANNEL_NAME")])
        daystate = get_day_state()

        # Only post message if during day, morning or evening
        if channel and daystate in ["morning", "day", "evening", "night"] and self.isactive:
            
            # Update Profile Image
            await self.image_interractor.update_song_picture(self.chat_agent.keeper.activity_log[-1], self)

            # Chat the latest activity
            talking_point = f"Hi guys, baru aja gue {self.chat_agent.keeper.activity_log[-1]}, ngapain lagi yak {daystate} gini?"
            print("=============== talking_point ===============")
            print(talking_point)

            # Convert talking point into a message via SongBrain
            talk = await self.chat_agent.atalk(talking_point)
            await channel.send(talk)

    # Additional error handling for the scheduled conversation message task
    @convo_scheduled_message.before_loop
    async def before_convo_scheduled_message(self):
        await self.wait_until_ready()

    @convo_scheduled_message.after_loop
    async def after_convo_scheduled_message(self):
        if self.convo_scheduled_message.failed():
            pass