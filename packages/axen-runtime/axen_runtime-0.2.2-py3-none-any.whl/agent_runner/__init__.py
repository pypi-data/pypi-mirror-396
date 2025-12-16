"""Agent Platform SDK - Universal wrapper for AI agents."""

from .sdk import serve, test_agent, AgentRuntime
from .exceptions import (
    AgentPlatformError,
    HandlerNotRegisteredError,
    AdapterDetectionError,
    StreamingError,
    TimeoutError,
    InvalidFrameworkError,
)

__version__ = "0.1.0"

__all__ = [
    "serve",
    "test_agent",
    "AgentRuntime",
    "AgentPlatformError",
    "HandlerNotRegisteredError",
    "AdapterDetectionError",
    "StreamingError",
    "TimeoutError",
    "InvalidFrameworkError",
]
