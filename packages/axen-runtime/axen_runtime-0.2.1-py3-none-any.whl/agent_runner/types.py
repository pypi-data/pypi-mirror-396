"""Type definitions for the Agent Platform SDK."""

from typing import (
    Callable,
    AsyncGenerator,
    Generator,
    Union,
    Any,
    Dict,
    List,
    Optional,
    Protocol,
    Literal,
    TypedDict,
)
from typing_extensions import TypeAlias

# Type aliases for clarity
Token: TypeAlias = str
Input: TypeAlias = Union[str, Dict[str, Any], List[Dict[str, Any]]]


# Message type for OpenAI-format conversations
class Message(TypedDict):
    """OpenAI-format message."""
    role: Literal["system", "user", "assistant", "function"]
    content: str


# Message list type
MessageList: TypeAlias = List[Message]

# Handler can accept string or message list
StringHandler: TypeAlias = Callable[[str], Generator[Token, None, None]]
MessageHandler: TypeAlias = Callable[[MessageList], Generator[Token, None, None]]
AsyncStringHandler: TypeAlias = Callable[[str], AsyncGenerator[Token, None]]
AsyncMessageHandler: TypeAlias = Callable[[MessageList], AsyncGenerator[Token, None]]

# Handler function can accept either format
SyncHandler: TypeAlias = Union[StringHandler, MessageHandler]
AsyncHandler: TypeAlias = Union[AsyncStringHandler, AsyncMessageHandler]
HandlerFunction: TypeAlias = Union[SyncHandler, AsyncHandler]

# Streaming response
StreamingResponse: TypeAlias = AsyncGenerator[Token, None]


class BaseAdapter(Protocol):
    """Protocol for framework adapters."""

    def detect(self, handler: Callable) -> bool:
        """Detect if this adapter can handle the given function."""
        ...

    def wrap(self, handler: Callable, **kwargs) -> HandlerFunction:
        """Wrap the handler to normalize output."""
        ...

    @property
    def name(self) -> str:
        """Adapter name for logging."""
        ...
