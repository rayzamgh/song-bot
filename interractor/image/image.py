import os
from interractor.base_interractor import BaseInterractor
from interractor.image.imagerecog.gptvision import extract_image
from interractor.image.imagegen.dalle import DalleInteractor
import aiohttp
import io

class ImageInterractor(BaseInterractor):
    def __init__(self, openai_api_key=None):

        if not openai_api_key :
            openai_api_key = os.environ["OPENAI_API_KEY"]

        # Initiate Interractor dependencies e.g. openai client & youtube client
        self.dalle : DalleInteractor = DalleInteractor(openai_api_key)
    
    def interract(self, prompt : str):
        return self.dalle.generate_image_from_text(prompt)
    
    def extract_image(self, image, prompt):
        return extract_image(image, prompt)
    
    async def download_image(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                
    async def update_song_picture(self, prompt : str, bot_client):
        pp_url = self.dalle.generate_image_from_activity(prompt)
        image_bytes = await self.download_image(pp_url)
        
        if image_bytes:
            await bot_client.user.edit(avatar=image_bytes)
            print("FINISHED CHANGING PP")

    def exit(self):
        pass
