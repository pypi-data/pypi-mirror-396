from typing import Final, final
from warnings import deprecated

from .ble_characteristic import BleCharacteristic
from .simple_class import SimpleClass

class BleService(SimpleClass):
    """
    A BLE service of a peripheral.
    """

    id: Final[str]
    """The ID of the service assigned by Homey."""
    uuid: Final[str]
    characteristics: Final[tuple[BleCharacteristic, ...]]

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved through BlePeripheral.services"
        " or by calling BlePeripheral.discover_services or BlePeripheral.get_service."
    )
    def __init__(self) -> None: ...
    async def get_characteristic(self, uuid: str) -> BleCharacteristic:
        """
        Get the characteristic with the given UUID.

        Raises:
            NotConnected:
            NotFound:
        """
    async def discover_characteristics(
        self, uuid_filter: list[str] | None = None
    ) -> tuple[BleCharacteristic, ...]:
        """
        Discover the characteristics of this service.

        Args:
            uuid_filter: A collection of characteristic UUIDs to limit the discovery to.

        Raises:
            NotConnected:
        """

    async def read(self, characteristic_uuid: str) -> bytes:
        """
        Read the current value of the characteristic with the given UUID.

        Raises:
            NotConnected:
            NotFound:
        """
    async def write(self, characteristic_uuid: str, data: bytes) -> None:
        """
        Write the data to the characteristic with the given UUID.

        Raises:
            NotConnected:
            NotFound:
        """
