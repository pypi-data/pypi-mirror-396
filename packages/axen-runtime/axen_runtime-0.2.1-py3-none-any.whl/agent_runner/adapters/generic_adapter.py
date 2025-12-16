"""Generic adapter for plain Python generators."""

from typing import Callable, Generator, AsyncGenerator, Any, List
import inspect
from .base import BaseAdapter
from ..logger import get_logger
from ..types import Message

logger = get_logger(__name__)


def _extract_last_message(messages: List[Message]) -> str:
    """Extract the last user message content from messages array."""
    if not messages:
        return ""
    # Find the last message (preferably user message)
    for msg in reversed(messages):
        if msg.get("content"):
            return msg["content"]
    return ""


def _expects_messages(handler: Callable) -> bool:
    """Check if handler expects messages array or string."""
    try:
        sig = inspect.signature(handler)
        params = list(sig.parameters.values())

        if not params:
            return False

        first_param = params[0]
        param_name = first_param.name

        # Check parameter name
        if param_name in ("messages", "message_list", "conversation"):
            return True

        # Check type annotation if available
        if first_param.annotation != inspect.Parameter.empty:
            annotation_str = str(first_param.annotation)
            if "List" in annotation_str or "list" in annotation_str:
                return True

        return False
    except Exception as e:
        logger.debug(f"Could not inspect handler signature: {e}")
        return False


class GenericAdapter(BaseAdapter):
    """Fallback adapter for plain Python generators."""

    @property
    def name(self) -> str:
        return "generic"

    def detect(self, handler: Callable) -> bool:
        """
        Always returns True (fallback adapter).

        This adapter handles plain Python generators and regular functions.
        It's the last adapter tried, so it should always match.
        """
        return True

    def wrap(self, handler: Callable, **kwargs) -> Callable:
        """
        Wrap generic handler to accept messages array.

        Handles both old format (str) and new format (List[Message]).
        Provides backward compatibility by extracting last message.

        Args:
            handler: The user's agent function
            **kwargs: Additional configuration

        Returns:
            A generator function that accepts messages and yields tokens
        """
        debug = kwargs.get("debug", False)
        expects_msg_array = _expects_messages(handler)

        if debug:
            logger.debug(
                f"Handler {handler.__name__} expects "
                f"{'message array' if expects_msg_array else 'string'}"
            )

        # Async generator function
        if inspect.isasyncgenfunction(handler):
            if expects_msg_array:
                # Handler already expects messages - pass through
                return handler
            else:
                # Handler expects string - extract last message
                async def wrapped_handler(messages: List[Message]) -> AsyncGenerator[str, None]:
                    input_text = _extract_last_message(messages)
                    async for token in handler(input_text):
                        yield str(token)
                return wrapped_handler

        # Sync generator function
        elif inspect.isgeneratorfunction(handler):
            if expects_msg_array:
                # Handler already expects messages - pass through
                return handler
            else:
                # Handler expects string - extract last message
                def wrapped_handler(messages: List[Message]) -> Generator[str, None, None]:
                    input_text = _extract_last_message(messages)
                    for token in handler(input_text):
                        yield str(token)
                return wrapped_handler

        # Async function (not generator)
        elif inspect.iscoroutinefunction(handler):
            if expects_msg_array:
                async def wrapped_handler(messages: List[Message]) -> AsyncGenerator[str, None]:
                    result = await handler(messages)
                    if inspect.isasyncgen(result):
                        async for item in result:
                            yield str(item)
                    elif inspect.isgenerator(result):
                        for item in result:
                            yield str(item)
                    else:
                        # Single value - split for streaming
                        for word in str(result).split():
                            yield word + " "
                return wrapped_handler
            else:
                async def wrapped_handler(messages: List[Message]) -> AsyncGenerator[str, None]:
                    input_text = _extract_last_message(messages)
                    result = await handler(input_text)
                    if inspect.isasyncgen(result):
                        async for item in result:
                            yield str(item)
                    elif inspect.isgenerator(result):
                        for item in result:
                            yield str(item)
                    else:
                        # Single value - split for streaming
                        for word in str(result).split():
                            yield word + " "
                return wrapped_handler

        # Sync function (not generator)
        else:
            if expects_msg_array:
                def wrapped_handler(messages: List[Message]) -> Generator[str, None, None]:
                    result = handler(messages)
                    if inspect.isgenerator(result):
                        for item in result:
                            yield str(item)
                    elif inspect.isasyncgen(result):
                        raise TypeError(
                            f"Handler {handler.__name__} returned async generator "
                            "but is not an async function. Use 'async def' instead."
                        )
                    else:
                        # Single value - split for streaming
                        for word in str(result).split():
                            yield word + " "
                return wrapped_handler
            else:
                def wrapped_handler(messages: List[Message]) -> Generator[str, None, None]:
                    input_text = _extract_last_message(messages)
                    result = handler(input_text)
                    if inspect.isgenerator(result):
                        for item in result:
                            yield str(item)
                    elif inspect.isasyncgen(result):
                        raise TypeError(
                            f"Handler {handler.__name__} returned async generator "
                            "but is not an async function. Use 'async def' instead."
                        )
                    else:
                        # Single value - split for streaming
                        for word in str(result).split():
                            yield word + " "
                return wrapped_handler
