from collections.abc import Callable
from typing import Any, Literal, LiteralString, Self, TypedDict, TypeVar, final
from warnings import deprecated

from .simple_class import SimpleClass

ChildEvent = TypeVar("ChildEvent", bound=LiteralString)

class CloudWebhook(SimpleClass[Literal["message"] | ChildEvent]):
    """
    A webhook that can receive incoming messages.
    """

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling ManagerCloud#create_webhook."
    )
    def __init__(self) -> None: ...
    async def unregister(self) -> None:
        """
        Unregister this webhook handler.
        """
    def on_message(
        self,
        f: Callable[[WebhookMessage], None],
    ) -> Self:
        """
        The `message` event is fired when a webhook message is received.

        Args:
            f: A callback that receives a dict containing the headers, query, and body of the message.
        """

class WebhookMessage(TypedDict):
    body: Any
    headers: dict[str, str]
    query: dict[str, str]
