from collections.abc import Callable, Coroutine
from typing import Any, Self, final
from warnings import deprecated

class PairSession:
    """
    A pairing session, prompting users for information to add new devices.
    """

    @final
    @deprecated(
        "This class must not be initialized by the developer, but is passed to Driver.on_pair."
    )
    def __init__(self) -> None: ...
    async def done(self) -> None:
        """
        Close the pairing session.
        """
    async def emit(self, event: str, data: Any | None = None) -> None:
        """
        Emits an event with the given name, along with any data, to the pairing view.
        """
    async def show_view(self, id: str) -> None:
        """
        Show the view with the given id in the pairing flow, as defined in `app.json`.
        """
    async def next_view(self) -> None:
        """
        Go to the next pairing step.
        """
    async def prev_view(self) -> None:
        """
        Go to the previous pairing step.
        """
    def set_handler(
        self, event: str, listener: Callable[..., Coroutine[Any, Any, Any]]
    ) -> Self:
        """
        Register a listener for events of the given name emitted by the pairing view.
        Any data returned will be sent back to the view.

        Args:
            listener: An async listener that receives any data that is passed along with the event.

        Returns:
            This pairing session, for chained calls.
        """
