"""Core SDK with the serve() function."""

from typing import Callable, Union, Any, Optional, AsyncGenerator, List
import asyncio
import inspect
from .adapters import detect_and_wrap_adapter
from .streaming import normalize_generator
from .types import HandlerFunction, Token, Message, MessageList
from .logger import get_logger
from .exceptions import HandlerNotRegisteredError

logger = get_logger(__name__)


class AgentRuntime:
    """
    Internal runtime singleton that holds the user's handler.

    The FastAPI server accesses this to execute the agent.
    """

    _instance = None

    def __init__(self):
        self.handler: Optional[Callable[[MessageList], AsyncGenerator[Token, None]]] = None
        self.config: dict = {}

    @classmethod
    def get_instance(cls):
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_handler(
        self,
        handler: Callable[[MessageList], AsyncGenerator[Token, None]],
        config: dict = None
    ):
        """
        Register the user's agent handler.

        Args:
            handler: Normalized async generator handler that accepts messages
            config: Configuration dict (timeout, chunk_size, etc.)
        """
        self.handler = handler
        self.config = config or {}
        logger.info(f"Registered handler with config: {self.config}")


def serve(
    handler: Union[Callable, Any],
    *,
    framework: Optional[str] = None,
    config: Optional[dict] = None,
    timeout: int = 300,
    chunk_size: int = 1,
    debug: bool = False
):
    """
    Universal serve function for AI agents.

    This is the main entry point for developers. Just call serve(your_agent)
    and the SDK will handle the rest.

    Usage Examples:

    1. Plain Generator (backward compatible):
        def my_agent(input_text: str):
            for word in input_text.split():
                yield word
        serve(my_agent)

    1b. Plain Generator (new format with messages):
        def my_agent(messages: List[Message]):
            latest = messages[-1]["content"]
            for word in latest.split():
                yield word
        serve(my_agent)

    2. CrewAI:
        from crewai import Agent, Task, Crew

        def my_crew_agent(input_text: str):
            crew = Crew(agents=[...], tasks=[...])
            for chunk in crew.kickoff(input_text):
                yield chunk
        serve(my_crew_agent, framework="crewai")

    3. LangGraph:
        from langgraph.graph import StateGraph

        def my_graph_agent(input_text: str):
            graph = StateGraph(...)
            for state in graph.stream({"input": input_text}):
                yield state["output"]
        serve(my_graph_agent, framework="langgraph")

    4. OpenAI (with streaming - new format with full messages):
        from openai import OpenAI

        def my_openai_agent(messages: List[Message]):
            client = OpenAI()
            stream = client.chat.completions.create(
                model="gpt-4",
                messages=messages,  # Pass full conversation history
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        serve(my_openai_agent, framework="openai")

    Args:
        handler: The agent function (can be sync/async generator or regular function)
        framework: Framework hint for auto-detection ("auto", "crewai", "langgraph", "openai")
        config: Additional configuration (e.g., model params, API keys)
        timeout: Maximum execution time in seconds (default: 300)
        chunk_size: Tokens per chunk for streaming (default: 1)
        debug: Enable debug logging (default: False)
    """

    # Auto-detect framework and wrap with appropriate adapter
    adapted_handler = detect_and_wrap_adapter(
        handler=handler,
        framework=framework,
        timeout=timeout,
        debug=debug
    )

    # Normalize to async generator for consistent runtime handling
    normalized_handler = normalize_generator(adapted_handler, chunk_size=chunk_size)

    # Register with runtime
    runtime = AgentRuntime.get_instance()
    runtime.register_handler(
        handler=normalized_handler,
        config={
            "timeout": timeout,
            "chunk_size": chunk_size,
            "debug": debug,
            "framework": framework or "auto",
            **(config or {})
        }
    )

    logger.info(f"Agent '{handler.__name__}' is ready to serve")


def test_agent(input_text: str, handler: Callable = None):
    """
    Test the agent locally without running the server.

    This is a convenience function for developers to test their agents
    before deploying.

    Usage:
        from agent_runner import serve, test_agent

        def my_agent(input_text: str):
            yield f"Echo: {input_text}"

        serve(my_agent)

        # Test it
        for token in test_agent("Hello World"):
            print(token, end="", flush=True)

    Args:
        input_text: Input text to test with
        handler: Optional handler to use (if not registered via serve())

    Yields:
        Tokens from the agent

    Raises:
        HandlerNotRegisteredError: If no handler is registered
    """
    runtime = AgentRuntime.get_instance()
    handler = handler or runtime.handler

    if handler is None:
        raise HandlerNotRegisteredError()

    # Execute the handler
    if inspect.isasyncgenfunction(handler) or inspect.iscoroutinefunction(handler):
        # Async generator
        async def run():
            async for token in handler(input_text):
                yield token

        loop = asyncio.get_event_loop()
        async_gen = run()

        while True:
            try:
                yield loop.run_until_complete(async_gen.__anext__())
            except StopAsyncIteration:
                break
    else:
        # Sync generator
        yield from handler(input_text)
