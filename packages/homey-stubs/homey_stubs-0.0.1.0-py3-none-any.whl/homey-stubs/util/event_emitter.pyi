from collections.abc import Callable, Set
from typing import Any, Generic, LiteralString, Self, TypeVar

Event = TypeVar("Event", bound=LiteralString)

class EventEmitter(Generic[Event]):
    def on(self, event: Event, f: Callable[..., None]) -> Self:
        """
        Register the function `f` to the event name `event`:

        ```python
        def data_handler(data):
            print(data)

        handler = ee.on("event", data_handler)
        ```
        """
    def once(
        self,
        event: Event,
        f: Callable[..., None],
    ) -> Self:
        """
        Register the function `f` to the event name `event`.
        The listener is automatically removed after being called.
        """
    def emit(
        self,
        event: Event,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """
        Emit `event`, passing `*args` and `**kwargs` to each attached
        function. Returns `True` if any functions are attached to `event`;
        otherwise returns `False`.

        Example:

        ```python
        ee.emit('data', '00101001')
        ```

        Assuming `on_data` is an attached function, this will call
        `on_data('00101001')'`.
        """
    def remove_listener(self, event: Event, f: Callable[..., None]) -> Self:
        """
        Unregister the function `f` from the event name `event`:
        """
    def remove_all_listeners(self, event: Event | None = None) -> Self:
        """
        Remove all listeners attached to `event`.
        If `event` is `None`, remove all listeners on all events.
        """
    def event_names(self) -> Set[Event]:
        """
        Get a set of events that this emitter is listening to.
        """

class EventException(Exception):
    """An uncaught error event."""
