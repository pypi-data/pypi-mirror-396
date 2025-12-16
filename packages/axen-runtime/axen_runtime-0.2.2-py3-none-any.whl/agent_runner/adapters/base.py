"""Base adapter interface for framework adapters."""

from typing import Callable
from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    """Base class for all framework adapters."""

    @abstractmethod
    def detect(self, handler: Callable) -> bool:
        """
        Detect if this adapter can handle the given function.

        Args:
            handler: The user's agent function

        Returns:
            True if the function/object is compatible with this adapter
        """
        pass

    @abstractmethod
    def wrap(self, handler: Callable, **kwargs) -> Callable:
        """
        Wrap the handler to produce a consistent generator output.

        Args:
            handler: The user's agent function
            **kwargs: Additional configuration (timeout, debug, etc.)

        Returns:
            A function that yields tokens (str)
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Adapter name for logging.

        Returns:
            The name of this adapter (e.g., "crewai", "langgraph")
        """
        pass
