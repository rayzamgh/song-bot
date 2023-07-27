import discord
from router import Router, RouterTypes

active_router = Router()

class SongClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        await active_router.route(
            client = self,
            message = message, 
            route = RouterTypes
            )