from collections.abc import Callable
from typing import Final, Literal, LiteralString, Self, TypeVar, final
from warnings import deprecated

from .ble_service import BleService
from .simple_class import SimpleClass

type BlePeripheralState = Literal[
    "error",
    "connecting",
    "connected",
    "disconnecting",
    "disconnected",
]

ChildEvent = TypeVar("ChildEvent", bound=LiteralString)

class BlePeripheral(SimpleClass[Literal["disconnect"] | ChildEvent]):
    """
    A BLE peripheral.
    """

    id: Final[str]
    """The ID of the peripheral assigned by Homey."""
    uuid: Final[str]
    address: Final[str]
    """The MAC address of the peripheral."""
    address_type: Final[Literal["random", "public", "unknown"]]
    """The type of address used by the peripheral."""
    connectable: Final[bool]
    """Whether the peripheral allows connections."""
    state: Final[BlePeripheralState]
    connected: Final[bool]
    """Whether the peripheral is currently connected to the Homey."""
    rssi: Final[int]
    """Received signal strength indicator of the peripheral."""
    services: Final[tuple[BleService, ...]]
    """
    Services on the peripheral.
    
    Note that this is only filled with services that have been discovered by
    BlePeripheral.discover_services or BlePeripheral.discover_all
    """

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling BleAdvertisement.connect."
    )
    def __init__(self) -> None: ...
    async def connect(self) -> Self:
        """
        Raises:
            NotConnected: Raised if the connection attempt failed.
        """
    async def disconnect(self) -> None: ...
    async def get_service(self, uuid) -> BleService:
        """
        Get the service with the given UUID.

        Raises:
            NotConnected:
            NotFound:
        """
    async def discover_services(
        self, uuid_filter: list[str] | None = None
    ) -> tuple[BleService, ...]:
        """
        Discover the services of this peripheral.

        Args:
            uuid_filter: A collection of peripheral UUIDs to limit the discovery to.

        Raises:
            NotConnected:
        """

    async def discover_all(self) -> tuple[BleService, ...]:
        """
        Discover all services and characteristics of this peripheral.

        Raises:
            NotConnected:
        """
    async def update_rssi(self) -> int: ...
    async def read(self, service_uuid: str, characteristic_uuid: str) -> bytes:
        """
        Read the current value of the characteristic of the service with the given UUIDs.

        Raises:
            NotConnected:
            NotFound:
        """
    async def write(
        self, service_uuid: str, characteristic_uuid: str, data: bytes
    ) -> None:
        """
        Write the data to the characteristic of the service with the given UUIDs.

        Raises:
            NotConnected:
            NotFound:
        """
    def on_disconnect(self, f: Callable[[], None]) -> Self:
        """
        The `disconnect` event is fired when the peripheral is disconnected.

        Args:
            f: A callback that receives no data.
        """
