from typing import final

from ..ble_advertisement import BleAdvertisement
from . import Manager

@final
class ManagerBLE(Manager):
    """
    Manages Bluetooth Low Energy communication.
    You can access this manager through the Homey instance as `self.homey.ble`.
    """
    async def discover(
        self, service_filter: list[str] | None = None
    ) -> tuple[BleAdvertisement, ...]:
        """
        Discover BLE peripherals for a certain time.

        Requires the `homey:wireless:ble` permission.
        For more information about permissions read the [Permissions tutorial](https://apps.developer.homey.app/the-basics/app/permissions).

        Args:
            service_filter: A collection of service UUIDs the peripheral should expose.

        Returns:
            A tuple of BLE advertisements, filtered by the service filter if given.
        """
    async def find(self, peripheral_uuid: str) -> BleAdvertisement:
        """
        Find a BLE peripheral with the given UUID.

        Requires the `homey:wireless:ble` permission.
        For more information about permissions read the [Permissions tutorial](https://apps.developer.homey.app/the-basics/app/permissions).

        Args:
            peripheral_uuid:

        Returns:
            The BLE advertisement of the peripheral.

        Raises:
            NotFound: Raised if no peripheral with the given UUID is found.
        """
