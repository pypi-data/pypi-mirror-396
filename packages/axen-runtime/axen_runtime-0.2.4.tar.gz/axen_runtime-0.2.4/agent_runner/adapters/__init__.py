"""Framework adapters for auto-detection and wrapping."""

from typing import Callable, List
from .base import BaseAdapter
from .crewai_adapter import CrewAIAdapter
from .langgraph_adapter import LangGraphAdapter
from .openai_adapter import OpenAIAdapter
from .generic_adapter import GenericAdapter
from ..logger import get_logger

logger = get_logger(__name__)

# Ordered list of adapters (most specific first, generic last)
ADAPTERS: List[BaseAdapter] = [
    CrewAIAdapter(),
    LangGraphAdapter(),
    OpenAIAdapter(),
    GenericAdapter(),  # Always matches (fallback)
]


def detect_and_wrap_adapter(
    handler: Callable,
    framework: str = None,
    **kwargs
) -> Callable:
    """
    Auto-detect the appropriate adapter and wrap the handler.

    This function tries adapters in order until one matches.
    If a framework is specified, it uses that adapter directly.

    Args:
        handler: The user's agent function
        framework: Optional framework hint ("crewai", "langgraph", "openai", "auto")
        **kwargs: Additional config passed to adapter (timeout, debug, etc.)

    Returns:
        Wrapped handler that yields tokens

    Raises:
        ValueError: If specified framework is not found
    """

    # If framework is specified, use that adapter
    if framework and framework != "auto":
        for adapter in ADAPTERS:
            if adapter.name == framework.lower():
                logger.info(f"Using specified adapter: {adapter.name}")
                return adapter.wrap(handler, **kwargs)

        logger.warning(f"Unknown framework '{framework}', falling back to auto-detection")

    # Auto-detect
    for adapter in ADAPTERS:
        if adapter.detect(handler):
            logger.info(f"Auto-detected framework: {adapter.name}")
            return adapter.wrap(handler, **kwargs)

    # Should never reach here (GenericAdapter always matches)
    raise RuntimeError("No compatible adapter found (this should never happen)")
