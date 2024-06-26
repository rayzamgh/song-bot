import discord
import time
import asyncio
import wavelink
from discord.ext import commands
from discord import VoiceClient
from module import VoiceModule

discord.opus._load_default()

TIME_TO_LISTEN = 5

class VoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connections = {}
        self.voice_module = VoiceModule()
        print("Voice Cog Registered!")
        
    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready() # wait until the bot is ready

        await wavelink.NodePool.create_node(
            bot=self.bot,
            host='0.0.0.0',
            port=2333,
            password='youshallnotpass'
        )

    async def on_ready(self):
        await self.connect_nodes() 
    
    async def on_wavelink_node_ready(node: wavelink.Node):
        print(f"{node.identifier} is ready.") # print a message

    async def once_done(self, sink: discord.sinks, channel: discord.TextChannel, vc : VoiceClient, *args):  # Our voice client already passes these in.
        start_time = time.perf_counter()
        recorded_users = {}

        for user_id, audio in sink.audio_data.items():
            this_user = self.bot.get_user(user_id)
            recorded_users[user_id] = {
                "id" : f"<@{user_id}>",
                "name" : this_user.name,
                "audio" : audio
            }

        # Calculate the elapsed time
        print(f"Passing mark 1 : {time.perf_counter() - start_time}")

        print("recorded_users")
        print(recorded_users)
        
        files = [discord.File(payload["audio"].file, f"{user_id}.{sink.encoding}") for user_id, payload in recorded_users.items()]  # List down the files.
        await channel.send(f"finished recording audio for: {', '.join(list([str(key) for key in recorded_users.keys()]))}.", files=files)  # Send a message with the accumulated files.

        # Calculate the elapsed time
        print(f"Passing mark 2 : {time.perf_counter() - start_time}")

        await self.voice_module.execute(sink, channel, recorded_users, vc, start_time=start_time)

    @commands.command()
    async def speak(self, ctx):
        print("~~SPEAKING NOW~~")
        await ctx.send("~~SPEAKING NOW~~")

    @commands.command()
    async def talk(self, ctx):
        print("Talking")
        voice = ctx.author.voice

        if not voice:
            await ctx.send("You aren't in a voice channel!")

        vc : VoiceClient = await voice.channel.connect()  # Connect to the voice channel the author is in.
        self.connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.

        await ctx.send("before Initiating recording!!")

        try:
            while True:
                await ctx.send("Initiating recording!!")
                vc.start_recording(
                    discord.sinks.MP3Sink(),  # The sink type to use.
                    self.once_done,  # What to do once done.
                    ctx.channel,  # The channel to disconnect from.
                    vc,  # The voice channel.
                )

                print(f"Listening for {TIME_TO_LISTEN} seconds")
                await asyncio.sleep(TIME_TO_LISTEN)
                print(f"Listened for {TIME_TO_LISTEN} seconds")

                vc.stop_recording()
                await ctx.send("Stopping recording!!")
        except KeyboardInterrupt:
            print("Interrupted by user")

    @commands.command()
    async def small_talk(self, ctx):
        # DONT FORGET TO ADD:
        # RELATIONSHIP METER WITH EACH PERSON?
        # RANDOMIZE THE SMALL TALK
        
        print("Small talking")
        voice = ctx.author.voice

        if not voice:
            await ctx.send("You aren't in a voice channel!")
            return

        vc: VoiceClient = await voice.channel.connect()  # Connect to the voice channel the author is in.
        self.connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.

        await ctx.send("Initiating small talk!")

        try:
            while True:
                # Generate a random small talk message
                small_talk_message = await self.voice_module.generate_small_talk()

                # Convert the small talk message to speech
                speech_file = await self.voice_module.text_to_speech(small_talk_message)

                # Play the speech file in the voice channel
                vc.play(discord.FFmpegPCMAudio(speech_file))

                # Wait for a certain duration before generating the next small talk message
                await asyncio.sleep(30)  # Adjust the duration as needed

        except KeyboardInterrupt:
            print("Interrupted by user")

    @commands.command()
    async def stop(self, ctx):
        if ctx.guild.id in self.connections: 
            del self.connections[ctx.guild.id]  # Remove the guild from the cache.
        else:
            await ctx.send("I am currently not recording here.")  # Respond with this if we aren't recording.

    @commands.command()
    async def die(self, ctx):
        ctx.voice_client.stop()
        await ctx.bot.close()