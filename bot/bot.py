from router import Router
from .plugin import (
    GamespotPlugin,
    BabblePlugin,
    ClockPlugin
)

# SongBot is a custom Discord bot designed to interact with users, specifically around the topic of songs and games.
class SongBot(BabblePlugin, GamespotPlugin, ClockPlugin):
    
    def __init__(self, *args, **kwargs):
        # Initializer

        # Flag to check if bot is active
        self.isactive = True

        # Setup for message routing and song management
        self.active_router: Router = Router()

        # Call the base class's initializer
        super().__init__(*args, **kwargs)
        
    async def on_ready(self):
        # Triggered when the bot is fully operational

        # Log to console
        print('Logged on as', self.user)

        await ClockPlugin.on_ready(self)
        await BabblePlugin.on_ready(self)
        await GamespotPlugin.on_ready(self)

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

