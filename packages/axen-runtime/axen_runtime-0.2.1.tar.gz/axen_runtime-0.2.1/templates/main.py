"""
Sample AI Agent - Echo Agent
This is a simple agent that echoes back user messages.
"""

from agent_runner import serve
from typing import List
from agent_runner.types import Message


def my_agent(messages: List[Message]):
    """
    Simple echo agent that returns the user's message.

    Args:
        messages: List of conversation messages in OpenAI format

    Yields:
        Tokens to stream back to the user
    """
    # Get the latest user message
    latest_message = messages[-1]["content"]

    # Stream the response word by word
    response = f"Echo: {latest_message}"

    for word in response.split():
        yield word + " "


# Register the agent with the SDK
serve(my_agent, framework="auto")
