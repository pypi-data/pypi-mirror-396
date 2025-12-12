from collections.abc import Callable
from types import MappingProxyType
from typing import Final, Literal, LiteralString, Self, TypeVar, final
from warnings import deprecated

from .simple_class import SimpleClass
from .zwave_command_class import ZWaveCommandClass

ChildEvent = TypeVar("ChildEvent", bound=LiteralString)

class ZWaveNode(SimpleClass[Literal["online", "nif", "unknownReport"] | ChildEvent]):
    """
    A Z-Wave Device in Homey.
    """

    battery: Final[bool]
    device_class_basic: Final[str]
    device_class_generic: Final[str]
    device_class_specific: Final[str]
    firmware_id: Final[int]
    multi_channel_node: Final[bool]
    manufacturer_id: Final[int]
    multi_channel_node_id: Final[int | None]
    multi_channel_nodes: Final[MappingProxyType[str, ZWaveNode]]
    node_id: Final[int]
    product_id: Final[int]
    product_type_id: Final[int]

    online: Final[bool]
    command_classes: Final[MappingProxyType[str, ZWaveCommandClass]]

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling ManagerZWave.get_node."
    )
    def __init__(self) -> None: ...
    async def send_command(
        self, command_class_id: int, command_id: int, params: bytes | None = None
    ) -> None:
        """
        Send a raw command from the given command class with the given parameters.
        """

    def on_online(
        self,
        f: Callable[[bool], None],
    ) -> Self:
        """
        This event is fired when a battery node changes its online status.

        Args:
            f: A callback that receives the new online status.
        """

    def on_nif(
        self,
        f: Callable[[str, str, list[bytes]], None],
    ) -> Self:
        """
        This event is fired when a Node Information Frame is received.

        Args:
            f: A callback that receives the NIF event, node token, and a list of any arguments.
        """

    def on_unknown_report(
        self,
        f: Callable[[bytes], None],
    ) -> Self:
        """
        This event is fired when an unknown command is received.

        Args:
            f: A callback that receives the report frame.
        """
