import os
from interractor.base_interractor import BaseInterractor
from elevenlabs import Voice, VoiceSettings, generate, save, set_api_key


class TextToSpeechInterractor(BaseInterractor):
    def __init__(self):
        super().__init__()
        set_api_key(os.environ["ELEVENLABS_API_KEY"])

    async def interract(self, args: dict = None):
        if args is None or 'text' not in args or 'filename' not in args:
            raise ValueError("Arguments 'text' and 'filename' are required")

        text = args['text']
        filename = args['filename']

        # Set up voice settings
        voice_settings = VoiceSettings(stability=0.46, similarity_boost=0.62, style=0.51, use_speaker_boost=True)
        voice = Voice(voice_id='ISUjskmTEvs1ZLX0Fy3E', settings=voice_settings)

        # Generate audio
        audio = generate(
            text=text,
            voice=voice,
            model="eleven_multilingual_v2"
        )

        # Save audio file
        save(audio, filename)

    def exit(self):
        # Implement any necessary cleanup
        pass