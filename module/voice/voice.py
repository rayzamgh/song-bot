import io
import os
from discord import FFmpegOpusAudio, MessageType, TextChannel, sinks
from module.base_module import BaseModule
from module import SongBrain
from interractor.voice import SpeechToTextInterractor, TextToSpeechInterractor
from utils import join_mp3s

class VoiceModule(BaseModule):
    """
    A module for handling voice interactions, including speech-to-text conversion,
    playing audio in voice channels, and processing voice commands.
    """
    def __init__(self):
        """
        Initializes the VoiceModule with required clients and state management variables.
        """
        self.buffer = []
        self.buffer_owner = ""
        self.song_agent = SongBrain()
        self.voice_tts = TextToSpeechInterractor()
        self.voice_stt = SpeechToTextInterractor()

    async def is_over(self, audio_file_name: str) -> bool:
        """
        Checks if the audio contains a specific trigger phrase.

        :param audio_file_name: The name/path of the audio file to be analyzed.
        :return: Boolean indicating whether the trigger phrase exists in the audio.
        """
        transcribed_text = await self.voice_stt.interract(audio_file_name)
        return "song" in transcribed_text.lower()

    async def execute(self, sink: sinks, channel: TextChannel, recorded_users, vc, *args, **kwargs):
        """
        Executes the main logic of processing recorded audio, including checking for trigger phrases,
        concatenating audio files, performing speech-to-text, and responding with text-to-speech output.

        :param sink: A Discord sink containing audio data.
        :param channel: The Discord text channel associated with the voice channel.
        :param recorded_users: A dictionary of users who have been recorded.
        :param vc: The Discord voice client for playback.
        """
        RAYZA_ID = int(os.getenv("RAYZA_ID"))
        INTERIM_OUTPUT_FILENAME = "interim_output.mp3"
        start_time = kwargs["start_time"]

        if RAYZA_ID in sink.audio_data:
            self.buffer_owner = recorded_users[RAYZA_ID]["name"]
            audio = recorded_users[RAYZA_ID]["audio"]
            file_name = audio.file.getvalue()
            self.buffer.append(file_name)

            is_over = await self.is_over(file_name)

            if is_over and self.buffer:
                vc.play(FFmpegOpusAudio(source="hmmsong.mp3"))

                mp3_buffers = [io.BytesIO(raw_bytes) for raw_bytes in self.buffer]
                buffer_combined = join_mp3s(mp3_buffers, INTERIM_OUTPUT_FILENAME)

                transcribed = await self.voice_stt.interract(buffer_combined)
                self.buffer = []

                if transcribed:
                    processed_message = self.preprocess_message(transcribed)
                    input_message = f'"{self.buffer_owner} said:" {processed_message}'

                    song_response = await self.song_agent.arun(input_message, self.buffer_owner, fast_mode=True)
                    song_response = song_response.lower().replace("song says:", "").replace("song said:", "").strip()

                    vc.stop()

                    input_args = {"text": song_response, "filename": INTERIM_OUTPUT_FILENAME}
                    print(f"input_args: \n{input_args}")
                    await self.voice_tts.interract(args=input_args)

                    vc.play(FFmpegOpusAudio(source=INTERIM_OUTPUT_FILENAME))

    def preprocess_message(self, raw_input: str) -> str:
        """
        Preprocesses the raw input message to replace mentions of the bot with its name.

        :param raw_input: The raw message input.
        :return: The processed message.
        """
        return raw_input.replace('<@1132625921636048977>', 'Song')
    
    def exit(self):
        pass