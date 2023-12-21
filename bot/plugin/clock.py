from router import Router
from discord.ext.commands import Bot
from module.message.agent import SongAgent
from discord.ext import tasks
import random
import discord
from .config import CHANNEL_NAME_2_ID

class ClockPlugin(Bot):

    # Static dictionary mapping channel names to their respective IDs
    CHANNEL_NAME_2_ID = CHANNEL_NAME_2_ID

    def __init__(self, *args, **kwargs):
        print("Clock initiated")

        # Setup for message routing and song management
        self.active_router: Router = Router()

        self.chat_agent: SongAgent = self.active_router.modules[Router.RouterTypes.MESSAGE].song_agent
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        # Log to console
        print('Clockin')

        # Start scheduled tasks for messaging and advancing song clock
        self.advance_song_clock.start()

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