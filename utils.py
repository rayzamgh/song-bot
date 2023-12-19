
from datetime import datetime, time
from discord import Message
import pytz
import python_weather
from bs4 import BeautifulSoup
from langchain.schema import (
    AIMessage,
    BaseChatMessageHistory,
    SystemMessage,
    ChatMessage,
    FunctionMessage,
    BaseMessage,
    HumanMessage,
)
from typing import Sequence

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

    print(text_only)


async def get_current_weather(city):
    """Fetches the current weather for the city specified in the environment."""

    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        weather = await client.get(city)
        return weather.current

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
        if isinstance(m, HumanMessage):
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
            raise ValueError(f"Got unsupported message type {m.type} : {m}")
        message = f"{role}: {m.content}"
        if isinstance(m, AIMessage) and "function_call" in m.additional_kwargs:
            message += f"{m.additional_kwargs['function_call']}"
        string_messages.append(message)

    return "\n".join(string_messages)
