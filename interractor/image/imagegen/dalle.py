from openai import OpenAI

class DalleInteractor:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def generate_image_from_text(self, prompt, size="1024x1024", quality="hd", n=1):
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            n=n,
        )
        return response.data[0].url

    def generate_image_from_activity(self, activity, size="1024x1024", quality="hd", n=1):
        # Assuming activity is a string describing the bot's current activity.
        # You might need to adjust this depending on how the activity data is structured.
        prompt = self._convert_activity_to_prompt(activity)
        return self.generate_image_from_text(prompt, size, quality, n)

    def _convert_activity_to_prompt(self, activity):
        # This method should convert the bot's activity into a text prompt suitable for DALL-E.
        # This is a placeholder function; you'll need to implement the actual conversion logic.
        return f"A depiction of a playful black haired young adult asian girl, with glasses, doing : {activity}"

