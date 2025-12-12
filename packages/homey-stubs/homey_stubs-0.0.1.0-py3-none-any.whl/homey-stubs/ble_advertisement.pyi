from typing import Final, Literal, LiteralString, NamedTuple, final
from warnings import deprecated

from .ble_peripheral import BlePeripheral
from .simple_class import SimpleClass

class BleAdvertisement(SimpleClass):
    """
    A BLE advertisement for a peripheral.
    """

    id: Final[str]
    """The ID of the peripheral assigned by Homey."""
    uuid: Final[str]
    """The UUID of the peripheral."""
    local_name: Final[str]
    """The local name advertised by the peripheral."""
    address: Final[str]
    """The MAC address of the peripheral."""
    address_type: Final[Literal["random", "public"]]
    """The type of address used by the peripheral."""
    connectable: Final[bool]
    """Whether the peripheral allows connections."""
    manufacturer_data: Final[bytes]
    """Manufacturer specific data for the peripheral."""
    service_data: Final[tuple[ServiceData, ...]]
    """Data of the services advertised by the peripheral."""
    service_uuids: Final[tuple[str, ...]]
    """UUIDs of the services advertised by the peripheral."""
    rssi: Final[int]
    """Received signal strength indicator of the peripheral."""
    timestamp: Final[int]
    """Unix epoch timestamp of when this advertisement was discovered, in ms."""

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling"
        " ManagerBLE.discover or ManagerBLE.find."
    )
    def __init__(self) -> None: ...
    async def connect(self) -> BlePeripheral:
        """
        Connect to the peripheral referenced by this advertisement.
        """

class ServiceData(NamedTuple):
    uuid: LiteralString
    """The UUID of the service."""
    data: bytes
