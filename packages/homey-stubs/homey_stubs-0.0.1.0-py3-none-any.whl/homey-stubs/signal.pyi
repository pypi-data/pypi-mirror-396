from abc import ABC
from collections.abc import Callable
from typing import Literal, LiteralString, Self, TypeVar, final
from warnings import deprecated

from .device import Device
from .simple_class import SimpleClass

ChildEvent = TypeVar("ChildEvent", bound=LiteralString)

class Signal(SimpleClass[Literal["cmd", "payload"] | ChildEvent], ABC):
    """
    Base class for signals.
    """

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling"
        "ManagerRF#get_signal_433, ManagerRF#get_signal_868, or ManagerRF#get_signal_infrared."
    )
    def __init__(self) -> None: ...
    async def cmd(
        self,
        command_id: str,
        repetitions: int | None = None,
        device: Device | None = None,
    ) -> None:
        """
        Send a predefined command using this signal.

        Requires the `homey:wireless:433`, `homey:wireless:868`, or `homey:wireless:ir` permissions.
        For more information about permissions read the [Permissions tutorial](https://apps.developer.homey.app/the-basics/app/permissions).

        Args:
            command_id: The ID of the command, as defined in `app.json`.
            repetitions: How often the signal gets transmitted.
            device: The device to send the signal to.
        """
    async def tx(
        self,
        frame: list[int] | bytes | bytearray,
        repetitions: int | None = None,
        device: Device | None = None,
    ) -> None:
        """
        Transmit a raw frame using this signal.

        Args:
            frame: The data to be transmitted.
            repetitions: How often the signal gets transmitted.
            device: The device to send the signal to.
        """
    async def disable_rx(self) -> None:
        """
        Disable receiving commands for this signal.

        Requires the `homey:wireless:433`, `homey:wireless:868`, or `homey:wireless:ir` permissions.
        For more information about permissions read the [Permissions tutorial](https://apps.developer.homey.app/the-basics/app/permissions).
        """
    async def enable_rx(self) -> None:
        """
        Enable receiving commands for this signal.

        Requires the `homey:wireless:433`, `homey:wireless:868`, or `homey:wireless:ir` permissions.
        For more information about permissions read the [Permissions tutorial](https://apps.developer.homey.app/the-basics/app/permissions).
        """

    def on_cmd(
        self,
        f: Callable[[str], None],
    ) -> Self:
        """
        This event is fired when a signal command has been received.

        Args:
            f: A callback that receives the ID of the command, as defined in `app.json`.
        """
    def on_payload(
        self,
        f: Callable[[tuple[int, ...], bool], None],
    ) -> Self:
        """
        This event is fired when a signal payload has been received.

        Args:
            f: A callback that receives an array of word indices, as well as whether this is the first detected repetition of the signal.
        """
