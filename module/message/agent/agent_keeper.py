import asyncio
import python_weather
import copy
from datetime import datetime, timedelta

class SongKeeper:
    """This class represents a SongBot's status, 
    including the current condition and environment.
    """

    def __init__(self):
        """Initializes the SongKeeper's condition and environment."""

        current_formatted_time = self.get_current_formatted_datetime()
        current_weather = asyncio.run(self.get_current_weather("Jakarta"))

        self.condition = {
            "mood": "chill", 
            "busyness": "not busy", 
            "current_activity": "working from home"
        }

        self.environment = {    
            "place" : "Jakarta",
            "time" : current_formatted_time,
            "weather" : {
                "forecast" : current_weather.description,
                "last_update" : current_formatted_time
            }
        }

        # Get the current time
        self.last_hit = datetime.now()

    @property
    def status(self):
        """Returns a dictionary that represents Song's current status."""

        # Calculate the difference between the two times
        time_difference = self.last_hit - self.last_hit

        # Compare the difference to one hour
        if time_difference > timedelta(hours=1):
            self.advance_clock()
        
        current_condition = copy.copy(self.condition)
        current_environment = copy.copy(self.environment)

        current_environment["weather"] = self.environment["weather"]["forecast"]

        self.last_hit = datetime.now()

        return current_condition | current_environment
    
    def get_current_formatted_datetime(self) -> str:
        """Returns the current date and time in a human-readable format."""
        
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime('%B %d, %Y, %I:%M %p')

        return formatted_datetime
    
    async def get_current_weather(self, city):
        """Fetches the current weather for the city specified in the environment."""

        async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
            weather = await client.get(city)
            return weather.current
        
    async def advance_clock(self):
        """Updates Song's status and activities periodically.
        TODO:
        This method is intended to be called every hour and updates the 
        current time and weather in Song's environment.
        """
        
        # Update current time
        self.environment["time"] = self.get_current_datetime()

        # Update current weather
        self.environment["weather"]["forecast"] = asyncio.run(self.get_current_weather(self.environment["place"]))
        self.environment["weather"]["last_update"] = self.environment["time"]
