# Required libraries and modules
from router import Router
from discord.ext.commands import Bot
from module.message.agent import SongAgent
from interractor.image import ImageInterractor
from discord.ext import tasks
from utils import get_day_state
from bot.apis import GameSpotAPI
import os
import random
import discord

# SongBot is a custom Discord bot designed to interact with users, specifically around the topic of songs and games.
class SongBot(Bot):

    # Static dictionary mapping channel names to their respective IDs
    CHANNEL_NAME_2_ID = {
        "command": 597400055644815400,
        "shmucks": 1172603107574808669,
        "memes": 926870487534026792
    }

    def __init__(self, *args, **kwargs):
        # Initializer

        # Flag to check if bot is active
        self.isactive = True

        # Setup for message routing and song management
        self.active_router: Router = Router()
        self.chat_agent: SongAgent = self.active_router.modules[Router.RouterTypes.MESSAGE].song_agent
        self.image_interractor: ImageInterractor = ImageInterractor()

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
    @tasks.loop(hours=9)
    async def gamespot_scheduled_message(self):

        print("Scheduled gamestop!")

        channel = self.get_channel(self.CHANNEL_NAME_2_ID["shmucks"])
        daystate = get_day_state()

        if channel and self.isactive:
            # Get a talking point from GameSpot API
            talking_point, extra_info = self.gamespot.get_song_babble(GameSpotAPI.Topics.ARTICLES)
            print("=============== talking_point ===============")
            print(talking_point)

            # Convert talking point into a message via SongAgent
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

    # Scheduled conversation starter
    @tasks.loop(hours=8)
    async def convo_scheduled_message(self):
        
        print("Scheduled convo!")

        channel = self.get_channel(self.CHANNEL_NAME_2_ID["shmucks"])
        daystate = get_day_state()

        # Only post message if during day, morning or evening
        if channel and daystate in ["morning", "day", "evening", "night"] and self.isactive:
            
            # Update Profile Image
            await self.image_interractor.update_song_picture(self.chat_agent.keeper.activity_log[-1], self)

            # Chat the latest activity
            talking_point = f"Hi guys, baru aja gue {self.chat_agent.keeper.activity_log[-1]}, ngapain lagi yak {daystate} gini?"
            print("=============== talking_point ===============")
            print(talking_point)

            # Convert talking point into a message via SongAgent
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

    # Scheduled task to advance the song clock (every 15 minutes)
    @tasks.loop(minutes=15)
    async def advance_song_clock(self):
        await self.chat_agent.keeper.advance_clock()

        song_choice = [
            "『SHINKIRO』GuraMarine",
            "疾走 Naoshi Mizuta",
            "月追いの都市〜canoue ver.〜 / 歌:霜月はるか",
            "Laufey - From The Start",
            "Laufey - Bewitched · 2023",
            "Laufey - Falling Behind",
            "Laufey - Everything I Know About Love · 2022",
            "Laufey - Let You Break My Heart Again · 2021",
            "Laufey - Valentine",
            "Laufey - Promise",
            "Laufey - A Night To Remember · 2023",
            "Laufey - This Is How It Feels",
            "Laufey - Petals to Thorns · 2023",
            "Laufey - California and Me",
            "廻廻奇譚 (Kaikai Kitan) - Eve (JPN)",
            "ファイトソング (Fight Song) - Eve (JPN)",
            "ドラマツルギー (Dramaturgy) - Eve (JPN)",
            "ぼくらの (Bokurano) - Eve (JPN)",
            "蒼のワルツ (Ao No Waltz) - Eve (JPN)",
            "あの娘シークレット (Anoko Secret) - Eve (JPN)",
            "心海 (Shinkai) - Eve (JPN)",
            "いのちの食べ方 (Inochi no Tabekata) - Eve (JPN)",
            "​Raison d’etre - Eve (JPN)",
            "宵の明星 (Yoino Myojo) - Eve (JPN)",
            "アヴァン (Avant) - Eve (JPN)",
            "As You Like It - Eve (JPN)",
            "杪夏 (Byouka) - Eve (JPN)",
        ]

        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=random.choice(song_choice)))


    # Additional error handling for the song clock advancing task
    @advance_song_clock.before_loop
    async def before_advance_song_clock(self):
        await self.wait_until_ready()

    @advance_song_clock.after_loop
    async def after_advance_song_clock(self):
        if self.advance_song_clock.failed():
            pass
