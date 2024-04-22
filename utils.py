

import pytz
import python_weather
import threading
import gc
import time
from datetime import datetime
from discord import Message, VoiceClient
from bs4 import BeautifulSoup
from pydub import AudioSegment
from langchain.schema import (
    AIMessage,
    SystemMessage,
    ChatMessage,
    FunctionMessage,
    BaseMessage,
    HumanMessage,
)
from typing_extensions import Literal
from typing import Sequence

class SongMessage(AIMessage):
    """A Message from Song."""

    example: bool = False
    """Whether this Message is being passed in to the model as part of an example 
        conversation.
    """

    type: Literal["song"] = "song"


class DiscordMessage(HumanMessage):
    """A Message from a human."""

    example: bool = False
    """Whether this Message is being passed in to the model as part of an example 
        conversation.
    """
    user: str = "rayza"
    type: str = "human"

def get_current_datetime() -> datetime:
    # Get the current time in UTC
    current_datetime = datetime.now(pytz.utc)

    # Define a fixed offset time zone with +7 hours
    offset_timezone = pytz.timezone('Asia/Bangkok')

    # Convert the current time to the desired offset time zone
    return current_datetime.astimezone(offset_timezone)

def get_day_state() -> str:
    # Get the current time in the specified timezone
    current_datetime : datetime = get_current_datetime()

    # Get the current hour
    current_hour = current_datetime.hour

    # Determine the day state based on the current hour
    if 0 <= current_hour < 10:
        day_state = "morning"
    elif 10 <= current_hour < 14:
        day_state = "day"
    elif 14 <= current_hour < 18:
        day_state = "evening"
    else:  # 18 <= current_hour < 24
        day_state = "night"

    return day_state


def get_current_formatted_datetime() -> str:
    """Returns the current date and time in a human-readable format, adjusted by +7 hours."""

    # Get the current time in UTC
    current_datetime = datetime.now(pytz.utc)

    # Define a fixed offset time zone with +7 hours
    offset_timezone = pytz.timezone('Asia/Bangkok')

    # Convert the current time to the desired offset time zone
    adjusted_datetime = current_datetime.astimezone(offset_timezone)

    # Format the adjusted time
    formatted_datetime = adjusted_datetime.strftime('%B %d, %Y, %I:%M %p')

    return formatted_datetime

async def get_original_message(message : Message):
    original_message_id = message.reference.message_id
    original_message_channel = message.channel
    original_message = await original_message_channel.fetch_message(original_message_id)
    return original_message

def format_html(html_message):

    soup = BeautifulSoup(html_message, 'html.parser')

    # Extracting text from the parsed HTML
    text_only = soup.get_text(separator=' ', strip=True)


async def get_current_weather(city):
    """Fetches the current weather for the city specified in the environment."""

    try:
        async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
            weather = await client.get(city)
            return weather.current.description
    except:
        return "Gloomy"

def get_buffer_string(
    messages: Sequence[BaseMessage], human_prefix: str = "Human", ai_prefix: str = "AI"
) -> str:
    """Convert sequence of Messages to strings and concatenate them into one string.

    Args:
        messages: Messages to be converted to strings.
        human_prefix: The prefix to prepend to contents of HumanMessages.
        ai_prefix: THe prefix to prepend to contents of AIMessages.

    Returns:
        A single string concatenation of all input messages.

    Example:
        .. code-block:: python

            from langchain.schema import AIMessage, HumanMessage

            messages = [
                HumanMessage(content="Hi, how are you?"),
                AIMessage(content="Good, how are you?"),
            ]
            get_buffer_string(messages)
            # -> "Human: Hi, how are you?\nAI: Good, how are you?"
    """
    string_messages = []
    for m in messages:
        if isinstance(m, DiscordMessage):
            role = m.user
        elif isinstance(m, HumanMessage):
            role = human_prefix
        elif isinstance(m, AIMessage):
            role = ai_prefix
        elif isinstance(m, SystemMessage):
            role = "System"
        elif isinstance(m, FunctionMessage):
            role = "Function"
        elif isinstance(m, ChatMessage):
            role = m.role
        else:
            raise ValueError(f"Got unsupported message type {m.__class__.__name__} {isinstance(m, HumanMessage)}: {m}")
        message = f"{role}: {m.content}"
        if isinstance(m, AIMessage) and "function_call" in m.additional_kwargs:
            message += f"{m.additional_kwargs['function_call']}"
        string_messages.append(message)

    return "\n".join(string_messages)


def join_mp3s(mp3_buffers, new_mp3_filename):
    combined = AudioSegment.empty()
    for mp3_buffer in mp3_buffers:
        # Load the MP3 file from the io.BytesIO object
        audio = AudioSegment.from_file(mp3_buffer, format="mp3")
        combined += audio
    
    # Export the combined audio to a new MP3 file
    combined.export(new_mp3_filename, format="mp3")

    # Open the saved file, read it as bytes, and return the bytes
    with open(new_mp3_filename, 'rb') as file:
        file_bytes = file.read()

    return file_bytes
