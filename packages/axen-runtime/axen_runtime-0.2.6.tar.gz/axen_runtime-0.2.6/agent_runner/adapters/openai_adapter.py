"""Adapter for OpenAI API (native streaming)."""

from typing import Callable, AsyncGenerator, Generator, Any, List
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


def _expects_messages(handler: Callable) -> bool:
    """Check if handler expects messages array."""
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
        # Check type annotation
        if first_param.annotation != inspect.Parameter.empty:
            annotation_str = str(first_param.annotation)
            if "List" in annotation_str or "list" in annotation_str:
                return True
        return False
    except Exception:
        return False


class OpenAIAdapter(BaseAdapter):
    """Adapter for OpenAI API (native streaming)."""

    @property
    def name(self) -> str:
        return "openai"

    def detect(self, handler: Callable) -> bool:
        """
        Detect OpenAI usage.

        Checks if the function uses 'openai' in its source code.
        """
        try:
            import openai

            source = inspect.getsource(handler)
            return "openai" in source.lower() or "OpenAI()" in source
        except ImportError:
            return False
        except Exception as e:
            logger.debug(f"OpenAI detection failed: {e}")
            return False

    def wrap(self, handler: Callable, **kwargs) -> Callable:
        """
        Wrap OpenAI handler to accept messages array.

        OpenAI handlers ideally receive full messages array.
        Provides backward compatibility for string-based handlers.

        Args:
            handler: The user's agent function
            **kwargs: Additional configuration

        Returns:
            A generator function that accepts messages and yields content tokens
        """
        debug = kwargs.get("debug", False)
        expects_msg_array = _expects_messages(handler)

        if debug:
            logger.debug(
                f"Wrapping OpenAI handler {handler.__name__} "
                f"(expects {'messages' if expects_msg_array else 'string'})"
            )

        if inspect.iscoroutinefunction(handler) or inspect.isasyncgenfunction(handler):
            # Async handler
            if expects_msg_array:
                # Pass full messages array
                async def wrapped_handler(messages: List[Message]) -> AsyncGenerator[str, None]:
                    result = await handler(messages)
                    if inspect.isasyncgen(result):
                        async for chunk in result:
                            content = self._extract_content(chunk)
                            if content:
                                yield content
                    else:
                        yield str(result)
                return wrapped_handler
            else:
                # Extract last message (backward compatible)
                async def wrapped_handler(messages: List[Message]) -> AsyncGenerator[str, None]:
                    input_text = _extract_last_message(messages)
                    result = await handler(input_text)
                    if inspect.isasyncgen(result):
                        async for chunk in result:
                            content = self._extract_content(chunk)
                            if content:
                                yield content
                    else:
                        yield str(result)
                return wrapped_handler

        else:
            # Sync handler
            if expects_msg_array:
                # Pass full messages array
                def wrapped_handler(messages: List[Message]) -> Generator[str, None, None]:
                    result = handler(messages)
                    if inspect.isgenerator(result):
                        for chunk in result:
                            content = self._extract_content(chunk)
                            if content:
                                yield content
                    else:
                        yield str(result)
                return wrapped_handler
            else:
                # Extract last message (backward compatible)
                def wrapped_handler(messages: List[Message]) -> Generator[str, None, None]:
                    input_text = _extract_last_message(messages)
                    result = handler(input_text)
                    if inspect.isgenerator(result):
                        for chunk in result:
                            content = self._extract_content(chunk)
                            if content:
                                yield content
                    else:
                        yield str(result)
                return wrapped_handler

    def _extract_content(self, chunk: Any) -> str:
        """
        Extract content from OpenAI chunk.

        OpenAI chunk structure: chunk.choices[0].delta.content

        Args:
            chunk: OpenAI streaming chunk

        Returns:
            Extracted content string or empty string
        """
        try:
            if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    return delta.content
        except Exception as e:
            logger.debug(f"Failed to extract content from chunk: {e}")

        return ""
