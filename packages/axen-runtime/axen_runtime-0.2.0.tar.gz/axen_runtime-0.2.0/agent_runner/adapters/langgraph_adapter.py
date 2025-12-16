"""Adapter for LangGraph agents."""

from typing import Callable, Generator, Any, AsyncGenerator, List
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


class LangGraphAdapter(BaseAdapter):
    """Adapter for LangGraph agents."""

    @property
    def name(self) -> str:
        return "langgraph"

    def detect(self, handler: Callable) -> bool:
        """
        Detect LangGraph by checking imports.

        Checks if the function uses 'langgraph' or 'StateGraph' in its source code.

        Args:
            handler: The user's agent function

        Returns:
            True if LangGraph is detected
        """
        try:
            import langgraph

            source = inspect.getsource(handler)
            return "langgraph" in source.lower() or "StateGraph" in source
        except ImportError:
            return False
        except Exception as e:
            logger.debug(f"LangGraph detection failed: {e}")
            return False

    def wrap(self, handler: Callable, **kwargs) -> Callable:
        """
        Wrap LangGraph handler.

        LangGraph's stream() returns state updates.
        Extract the output field from each state.

        Args:
            handler: The user's agent function
            **kwargs: Additional configuration

        Returns:
            A generator function that yields output from state
        """
        debug = kwargs.get("debug", False)

        # Check if async
        if inspect.iscoroutinefunction(handler) or inspect.isasyncgenfunction(handler):
            if debug:
                logger.debug(f"Wrapping LangGraph async handler: {handler.__name__}")

            async def wrapped_handler(messages: List[Message]) -> AsyncGenerator[str, None]:
                input_text = _extract_last_message(messages)
                result = await handler(input_text)

                if inspect.isasyncgen(result):
                    async for state in result:
                        # Extract output from state dict
                        output = self._extract_output(state, debug)
                        if output:
                            yield output
                else:
                    yield str(result)

            return wrapped_handler

        else:
            if debug:
                logger.debug(f"Wrapping LangGraph sync handler: {handler.__name__}")

            def wrapped_handler(messages: List[Message]) -> Generator[str, None, None]:
                input_text = _extract_last_message(messages)
                result = handler(input_text)

                if inspect.isgenerator(result):
                    for state in result:
                        # Extract output from state dict
                        output = self._extract_output(state, debug)
                        if output:
                            yield output
                else:
                    yield str(result)

            return wrapped_handler

    def _extract_output(self, state: Any, debug: bool = False) -> str:
        """
        Extract output from LangGraph state.

        LangGraph states are typically dicts with 'output' or 'messages' keys.

        Args:
            state: LangGraph state object
            debug: Enable debug logging

        Returns:
            Extracted output string
        """
        if isinstance(state, dict):
            # Try to get 'output' field
            output = state.get("output", state.get("messages", None))

            if output is None:
                # Fallback: use the entire state
                if debug:
                    logger.debug(f"State has no 'output' or 'messages', using full state: {list(state.keys())}")
                return str(state)

            if isinstance(output, list):
                # Multiple messages
                return "\n".join(str(msg) for msg in output)
            else:
                return str(output)
        else:
            return str(state)
