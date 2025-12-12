from collections.abc import Callable
from typing import Any, Literal, LiteralString, Self, TypeVar

from .util.event_emitter import EventEmitter

ChildEvent = TypeVar("ChildEvent", bound=LiteralString)

class SimpleClass(EventEmitter[Literal["__log", "__error", "__debug"] | ChildEvent]):
    """
    This is a simple class with log functions.
    """
    def log(self, *args: Any) -> None:
        """
        Log the given arguments, emitting a __log event.
        """
    def error(self, *args: Any) -> None:
        """
        Log the given arguments, emitting an __error event.
        """
    def debug(self, *args: Any) -> None:
        """
        Log the given arguments, emitting a __debug event.
        """
    def on_log(self, f: Callable[..., None]) -> Self:
        """
        The `__log` event is fired when the `SimpleClass.log` method is called.

        Args:
            f: A callback that receives the positional arguments passed to `SimpleClass.log`
        """
    def on_error(self, f: Callable[..., None]) -> Self:
        """
        The `__error` event is fired when the `SimpleClass.error` method is called.

        Args:
            f: A callback that receives the positional arguments passed to `SimpleClass.error`
        """
    def on_debug(self, f: Callable[..., None]) -> Self:
        """
        The `__debug` event is fired when the `SimpleClass.debug` method is called.

        Args:
            f: A callback that receives the positional arguments passed to `SimpleClass.debug`
        """
