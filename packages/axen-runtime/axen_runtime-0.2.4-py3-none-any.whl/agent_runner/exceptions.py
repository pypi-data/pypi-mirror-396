"""Custom exceptions for the Agent Platform SDK."""


class AgentPlatformError(Exception):
    """Base exception for all Agent Platform SDK errors."""

    pass


class HandlerNotRegisteredError(AgentPlatformError):
    """Raised when attempting to execute without registering a handler."""

    def __init__(self):
        super().__init__(
            "No handler registered. Call serve(your_handler) before executing."
        )


class AdapterDetectionError(AgentPlatformError):
    """Raised when no suitable adapter can be found for a handler."""

    def __init__(self, handler_name: str):
        super().__init__(
            f"Could not find a suitable adapter for handler '{handler_name}'. "
            f"Ensure your handler is a generator function or async generator."
        )


class StreamingError(AgentPlatformError):
    """Raised when streaming fails."""

    pass


class TimeoutError(AgentPlatformError):
    """Raised when agent execution times out."""

    def __init__(self, timeout: int):
        super().__init__(f"Agent execution timed out after {timeout} seconds")


class InvalidFrameworkError(AgentPlatformError):
    """Raised when an unsupported framework is specified."""

    def __init__(self, framework: str):
        super().__init__(
            f"Unsupported framework: '{framework}'. "
            f"Supported frameworks: 'crewai', 'langgraph', 'openai', 'auto'"
        )
