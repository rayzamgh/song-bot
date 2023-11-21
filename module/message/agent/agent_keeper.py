import asyncio
import copy
from datetime import datetime, timedelta
from utils import get_current_datetime, get_current_formatted_datetime, get_current_weather
import random

class SongKeeper:
    """This class represents SongBot's status, 
    including the current condition and environment.
    """

    def __init__(self):
        """Initializes the SongKeeper's condition and environment."""

        current_formatted_time = get_current_formatted_datetime()
        current_weather = asyncio.run(get_current_weather("Jakarta"))

        self.condition = {
            "mood": "chill",
            "busyness": "not busy",
            "current_activity": "working from home",
        }

        self.environment = {
            "place": "Jakarta",
            "current_time": current_formatted_time,
            "weather": {
                "forecast": current_weather.description,
                "last_update": current_formatted_time
            }
        }

        self.activity_log = ["Baru aja jalan-jalan keluar"]
        self.hunger = 50
        self.boredom = 50
        self.mood_swing = 50

        # Get the current time
        self.last_hit = get_current_datetime()

    @property
    def status(self):
        """Returns a dictionary that represents Song's current status."""

        # Calculate the difference between the two times
        current_datetime = get_current_datetime()
        time_difference = current_datetime - self.last_hit

        # Compare the difference to one hour
        if time_difference > timedelta(minutes=15):
            self.last_hit = current_datetime

        current_condition = copy.copy(self.condition)
        current_environment = copy.copy(self.environment)

        current_environment["weather"] = current_environment["weather"]["forecast"]

        activities = {
            'activities' : self.activity_log[-1]
        }

        return current_condition | current_environment | activities

    async def advance_clock(self):
        """
        Updates Song's status and activities periodically.
        """

        # Update current time
        self.environment["current_time"] = get_current_formatted_datetime()

        # Update current weather
        self.environment["weather"]["forecast"] = await get_current_weather(self.environment["place"])
        self.environment["weather"]["last_update"] = self.environment["current_time"]

        # Increase hunger and boredom based on elapsed time
        self.hunger += 15
        self.boredom += 20
        self.mood_swing += 20
        
        self.hunger = min(100, self.hunger)
        self.boredom = min(100, self.boredom)

        if self.hunger > 90:
            self.feed()

        if self.boredom > 90:
            self.play()

        if self.mood_swing > 90:
            self.swing_mood()

        print("Song clock advanced!")

    def feed(self):

        CHOICE_OF_FOOD = {
            "wafer beng beng": {
                "description": "buat ganjel perut aja",
                "satisfy": 20,
            },
            "nasi padang": {
                "description": "deket benhill, kenyang banget gue",
                "satisfy": 60,
            },
            "nasi goreng": {
                "description": "spesial pake telur mata sapi di atasnya",
                "satisfy": 50,
            },
            "es krim": {
                "description": "seger bener, wkwkwk",
                "satisfy": 35,
            },
            "rendang": {
                "description": "Empuknya rendang ini, lumer di mulut gue!",
                "satisfy": 65,
            },
            "sate ayam": {
                "description": "gosong anjir wkwkwk",
                "satisfy": 55,
            },
            "gado-gado": {
                "description": "Saus kacangnya mantul banget",
                "satisfy": 40,
            },
            "klepon": {
                "description": "Manisnya keluar pas digigit",
                "satisfy": 25,
            },
            "pisang goreng": {
                "description": "guilty pleasure favorit gw wkwkwk",
                "satisfy": 30,
            }
        }

        selected_food, details = random.choice(list(CHOICE_OF_FOOD.items()))

        time_now = get_current_formatted_datetime()

        self.activity_log.append(f"Di jam {time_now}, gue makan {selected_food}, {details['description']}")

        self.hunger -= details['satisfy']
        self.hunger = max(0, self.hunger)
        
        
    def play(self):

        CHOICE_OF_ACTIVITY = {
            "jalan-jalan keluar": {
                "description": "iseng aja gue muter daerah senopati, gk tau mau ngapain wkwk",
                "satisfy": 20,
            },
            "main video game gta 5": {
                "description": "free roam aja gangguin warga lokal sama polisi di game",
                "satisfy": 60,
            },
            "main video game dragon ball": {
                "description": f"tadi diajakin main sama Rayza, gue {'menang' if random.choice([True, False]) else 'kalah'} donggggg",
                "satisfy": 60,
            },
            "rewatch inuyasha": {
                "description": "kangen aja gw sama inuyasha pengen nonton, haha",
                "satisfy": 40,
            },
        }

        selected_activity, details = random.choice(list(CHOICE_OF_ACTIVITY.items()))

        time_now = get_current_formatted_datetime()

        self.activity_log.append(f"Di jam {time_now}, gue {selected_activity}, {details['description']}")

        self.hunger -= details['satisfy']
        self.boredom = max(0, self.boredom)
        
        
    def swing_mood(self):

        CHOICE_OF_MOOD = [
            "normal",
            "chill",
            "angsty",
            "angry",
            "super angry",
            "tired",
            "happy",
            "lovely",
        ]

        self.condition["mood"] = random.choice(CHOICE_OF_MOOD)

        self.boredom = 0