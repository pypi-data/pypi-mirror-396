"""Adapter for CrewAI agents."""

from typing import Callable, Generator, Any, List
import inspect
from .base import BaseAdapter
from ..logger import get_logger
from ..types import Message

logger = get_logger(__name__)


def _extract_last_message(messages: List[Message]) -> str:
    """Extract the last user message content."""
    if not messages:
        return ""
    for msg in reversed(messages):
        if msg.get("content"):
            return msg["content"]
    return ""


class CrewAIAdapter(BaseAdapter):
    """Adapter for CrewAI agents."""

    @property
    def name(self) -> str:
        return "crewai"

    def detect(self, handler: Callable) -> bool:
        """
        Detect CrewAI by checking imports or return type.

        Checks if the function uses 'crewai' or 'Crew' in its source code.

        Args:
            handler: The user's agent function

        Returns:
            True if CrewAI is detected
        """
        try:
            import crewai

            # Check if function returns Crew object or uses Crew in code
            source = inspect.getsource(handler)
            return "crewai" in source.lower() or "Crew" in source
        except ImportError:
            return False
        except Exception as e:
            logger.debug(f"CrewAI detection failed: {e}")
            return False

    def wrap(self, handler: Callable, **kwargs) -> Callable:
        """
        Wrap CrewAI handler to yield tokens.

        CrewAI's kickoff() can return:
        1. String output (non-streaming)
        2. StreamOutput object (streaming)

        Args:
            handler: The user's agent function
            **kwargs: Additional configuration

        Returns:
            A generator function that yields tokens
        """
        debug = kwargs.get("debug", False)

        if debug:
            logger.debug(f"Wrapping CrewAI handler: {handler.__name__}")

        def wrapped_handler(messages: List[Message]) -> Generator[str, None, None]:
            input_text = _extract_last_message(messages)
            result = handler(input_text)

            # Check if result is already a generator
            if inspect.isgenerator(result):
                if debug:
                    logger.debug("CrewAI result is generator (pass-through)")
                yield from result

            # CrewAI streaming output
            elif hasattr(result, "stream"):
                if debug:
                    logger.debug("CrewAI result has stream() method")
                for chunk in result.stream():
                    if hasattr(chunk, "content"):
                        yield chunk.content
                    else:
                        yield str(chunk)

            # Non-streaming output
            elif isinstance(result, str):
                if debug:
                    logger.debug("CrewAI result is string (splitting for streaming)")
                # Split into words for token-like streaming
                for word in result.split():
                    yield word + " "

            else:
                # Fallback: convert to string
                if debug:
                    logger.debug(f"CrewAI result type: {type(result)} (fallback to str)")
                yield str(result)

        return wrapped_handler
