import io
from interractor.base_interractor import BaseInterractor
from google.cloud import speech
from openai import OpenAI
from pydub import AudioSegment

class SpeechToTextInterractor(BaseInterractor):
    def __init__(self, vendor="openai"):
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz=16000,
            language_code="id-ID",
        )
        self.vendor = vendor

        vendors = {
            "openai" : OpenAI(),
            "google" : speech.SpeechClient() 
        }

        self.client = vendors[vendor]
    
    def transcribe_file(self, content) -> str:
        """Transcribe the given audio file."""

        if self.vendor == "google":
            audio = speech.RecognitionAudio(content=content)

            response = self.client.recognize(config=self.config, audio=audio)

            # Each result is for a consecutive portion of the audio. Iterate through
            # them to get the transcripts for the entire audio file.
            for result in response.results:
                # The first alternative is the most likely one for this portion.
                print(f"Transcript: {result.alternatives[0].transcript}")

            return response.results[0].alternatives[0].transcript if response.results else ""
        
        if self.vendor == "openai":
            audio_file = open("current_mp3.mp3", "rb")
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="id",
                prompt="Percakapan ini dalam Bahasa Indonesia, antara Rayza (yang ngomong) dengan Song (yang dituju)"
            )

            return transcript.text

    async def interract(self, content):

        print(f"interract!")

        return self.transcribe_file(content)

    def exit(self):
        pass
