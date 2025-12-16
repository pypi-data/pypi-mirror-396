"""Normalize any handler (sync/async generator) to async generator."""

from typing import Callable, AsyncGenerator
import inspect
import asyncio
from ..types import Token
from ..logger import get_logger

logger = get_logger(__name__)


def normalize_generator(
    handler: Callable,
    chunk_size: int = 1
) -> Callable[[str], AsyncGenerator[Token, None]]:
    """
    Normalize any handler (sync/async generator) to async generator.

    This ensures the runtime server can always use async/await.

    Args:
        handler: Wrapped handler from adapter
        chunk_size: Tokens per chunk (for batching)

    Returns:
        Async generator function that yields tokens
    """

    if inspect.isasyncgenfunction(handler):
        # Already async generator - optionally add chunking
        async def normalized(input_text: str) -> AsyncGenerator[Token, None]:
            buffer = []
            async for token in handler(input_text):
                buffer.append(token)
                if len(buffer) >= chunk_size:
                    yield "".join(buffer)
                    buffer = []

            # Flush remaining
            if buffer:
                yield "".join(buffer)

        return normalized

    elif inspect.isgeneratorfunction(handler):
        # Sync generator - convert to async
        async def normalized(input_text: str) -> AsyncGenerator[Token, None]:
            buffer = []

            # Run sync generator in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            gen = handler(input_text)

            while True:
                try:
                    # Get next token in thread pool
                    token = await loop.run_in_executor(None, lambda: next(gen))
                    buffer.append(token)

                    if len(buffer) >= chunk_size:
                        yield "".join(buffer)
                        buffer = []
                except StopIteration:
                    break

            # Flush remaining
            if buffer:
                yield "".join(buffer)

        return normalized

    else:
        raise TypeError(f"Handler must be a generator function, got {type(handler)}")
