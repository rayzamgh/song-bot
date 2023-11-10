import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from enum import Enum

class GameSpotAPI:
    BASE_URL = "http://www.gamespot.com/api/"

    # Enum class for possible topics
    class Topics(Enum):
        ARTICLES = "articles"
        GAMES = "games"
        RELEASES = "releases"
        
    # Define the structure for each topic
    TOPIC_STRUCTURES = {
        Topics.ARTICLES: {
            "raw": ["title", "deck"],
            "html": ["body"],
            "skip" : ["site_detail_url"], 
        },
        Topics.GAMES: {
            "raw": ["name", "description"]
        },
        Topics.RELEASES: {
            "raw": ["name", "description"]
        }
    }

    def __init__(self, api_key):
        self.api_key = api_key

    def _get(self, endpoint, params=None):
        if params is None:
            params = {}
        headers = {
            "User-Agent": "PostmanRuntime/7.28.4",
            "Accept": "application/json",
            "Referer": "https://www.gamespot.com/"
        }
        params["api_key"] = self.api_key
        params["format"] = "json"
        response = requests.get(f"{self.BASE_URL}{endpoint}/", params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_latest_games(self, limit=10):
        today = datetime.today().strftime('%Y-%m-%d')
        return self._get("games", {
            "limit": limit,
            "sort": "release_date:desc",
            "filter": f"release_date:{today}"
        })

    def get_latest_releases(self, limit=10):
        today = datetime.today().strftime('%Y-%m-%d')
        return self._get("releases", {
            "limit": limit,
            "sort": "release_date:desc",
            "filter": f"release_date:{today}"
        })

    def get_latest_articles(self, limit=10):
        today = datetime.today().strftime('%Y-%m-%d')
        yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        return self._get("articles", {
            "limit": limit,
            "sort": "publish_date:desc",
            "filter": f"publish_date:{yesterday} 00:00:00|{today} 23:59:59"
        })

    def get_song_babble(self, topic: Topics):
        def format_html(html_text):
            soup = BeautifulSoup(html_text, 'html.parser')
            return soup.get_text(separator=' ', strip=True)

        def construct_text(response, topic_structure):
            raw_text = ""
            extra_info = {}
            for part_of_text in topic_structure.get("raw", []):
                raw_text += f"""{part_of_text}, {response["results"][0][part_of_text]}\n"""

            for part_of_text in topic_structure.get("html", []):
                raw_text += f"""{part_of_text}, {format_html(response["results"][0][part_of_text])}\n"""

            for part_of_text in topic_structure.get("skip", []):
                extra_info[part_of_text] = response["results"][0][part_of_text]
 
            return raw_text, extra_info

        if topic == self.Topics.ARTICLES:
            response = self.get_latest_articles()
        elif topic == self.Topics.GAMES:
            response = self.get_latest_games()
        else:
            response = self.get_latest_releases()

        return construct_text(response, self.TOPIC_STRUCTURES[topic])