# Required libraries and modules
from router import Router
from discord.ext.commands import Bot
from module.message.agent import SongAgent
from discord.ext import tasks
from datetime import datetime, time
from utils import get_current_datetime, get_day_state, get_current_formatted_datetime
from bot.apis import GameSpotAPI
import os

# SongBot is a custom Discord bot designed to interact with users, specifically around the topic of songs and games.
class SongBot(Bot):

    # Static dictionary mapping channel names to their respective IDs
    CHANNEL_NAME_2_ID = {
        "command": 597400055644815400,
        "general": 596681723593621570,
        "memes": 926870487534026792
    }

    def __init__(self, *args, **kwargs):
        # Initializer

        # Flag to check if bot is active
        self.isactive = True

        # Setup for message routing and song management
        self.active_router: Router = Router()
        self.local_agent: SongAgent = self.active_router.modules[Router.RouterTypes.MESSAGE].song_agent

        # Setup for GameSpot API utility
        self.gamespot: GameSpotAPI = GameSpotAPI(os.environ.get("GAMESPOT_API_KEY"))

        # Call the base class's initializer
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        # Triggered when the bot is fully operational

        # Log to console
        print('Logged on as', self.user)

        # Start scheduled tasks for messaging and advancing song clock
        self.gamespot_scheduled_message.start()
        self.convo_scheduled_message.start()
        self.advance_song_clock.start()

    async def on_message(self, message):
        # Event handler for receiving messages

        # Logic for custom bot commands (e.g., "song diem" and "halo song")
        if message.content == "song diem":
            if message.author.name == "bwsong": 
                await message.channel.send("Ok Ray!")
                self.isactive = False
            else:
                await message.channel.send("??? siapa lo nyuruh gw diem wkwkwk")

        if message.content == "halo song":
            if message.author.name == "bwsong": 
                await message.channel.send("Halo Ray!")
                self.isactive = True
            else:
                await message.channel.send("zzzzz (lagi bobo)")

        # If bot is active, route the message to the appropriate handler
        if self.isactive:
            await self.active_router.route(
                client=self,
                message=message,
                route=Router.RouterTypes
            )

    # Scheduled message from GameSpot (every 12 hours)
    @tasks.loop(hours=30)
    async def gamespot_scheduled_message(self):
        channel = self.get_channel(self.CHANNEL_NAME_2_ID["general"])
        daystate = get_day_state()

        if channel and self.isactive:
            # Get a talking point from GameSpot API
            talking_point = self.gamespot.get_song_babble(GameSpotAPI.Topics.ARTICLES)
            print("=============== talking_point ===============")
            print(talking_point)

            # Convert talking point into a message via SongAgent
            talk = await self.local_agent.atalk(talking_point)
            await channel.send(talk)

    # Additional error handling for the scheduled GameSpot message task
    @gamespot_scheduled_message.before_loop
    async def before_gamespot_scheduled_message(self):
        await self.wait_until_ready()

    @gamespot_scheduled_message.after_loop
    async def after_gamespot_scheduled_message(self):
        if self.gamespot_scheduled_message.failed():
            pass

    # Scheduled conversation starter (every 6 hours)
    @tasks.loop(hours=12)
    async def convo_scheduled_message(self):
        channel = self.get_channel(self.CHANNEL_NAME_2_ID["general"])
        daystate = get_day_state()

        # Only post message if during day, morning or evening
        if channel and daystate in ["morning", "day", "evening"] and self.isactive:
            talking_point = f"Hi guys, baru aja gue {self.local_agent.keeper.activity_log[-1]}, ngapain lagi yak {daystate} gini?"
            print("=============== talking_point ===============")
            print(talking_point)

            # Convert talking point into a message via SongAgent
            talk = await self.local_agent.atalk(talking_point)
            await channel.send(talk)

    # Additional error handling for the scheduled conversation message task
    @convo_scheduled_message.before_loop
    async def before_convo_scheduled_message(self):
        await self.wait_until_ready()

    @convo_scheduled_message.after_loop
    async def after_convo_scheduled_message(self):
        if self.convo_scheduled_message.failed():
            pass

    # Scheduled task to advance the song clock (every 15 minutes)
    @tasks.loop(minutes=15)
    async def advance_song_clock(self):
        await self.local_agent.keeper.advance_clock()

    # Additional error handling for the song clock advancing task
    @advance_song_clock.before_loop
    async def before_advance_song_clock(self):
        await self.wait_until_ready()

    @advance_song_clock.after_loop
    async def after_advance_song_clock(self):
        if self.advance_song_clock.failed():
            pass
