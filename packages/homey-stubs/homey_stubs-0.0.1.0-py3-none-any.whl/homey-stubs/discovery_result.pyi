from abc import ABC
from collections.abc import Callable
from datetime import datetime
from typing import Final, Literal, LiteralString, Self, TypeVar, final
from warnings import deprecated

from .simple_class import SimpleClass

ChildEvent = TypeVar("ChildEvent", bound=LiteralString)

class DiscoveryResult(
    SimpleClass[Literal["addressChanged", "lastSeenChanged"] | ChildEvent],
    ABC,
):
    """
    Base class for the results of discovery strategies.
    """

    address: Final[str | None]
    """The IP address of the device."""
    id: Final[str]
    """The ID of the device assigned by Homey."""
    last_seen: Final[datetime]
    """When the device has last been discovered."""

    @final
    @deprecated(
        "This class must not be initialized by the developer, but is instantiated by Homey when a device is discovered."
    )
    def __init__(self) -> None: ...
    def on_address_changed(self, f: Callable[[Self], None]) -> Self: ...
    def on_last_seen_changed(self, f: Callable[[Self], None]) -> Self: ...
