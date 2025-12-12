from collections.abc import Callable
from typing import Final, Literal, final
from warnings import deprecated

from .ble_descriptor import BleDescriptor
from .simple_class import SimpleClass

type BleCharacteristicProperty = Literal[
    "broadcast",
    "read",
    "writeWithoutResponse",
    "write",
    "notify",
    "indicate",
    "authenticatedSignedWrites",
    "extendedProperties",
]

class BleCharacteristic(SimpleClass):
    """
    A BLE characteristic of a peripheral.
    """

    id: Final[str]
    """The ID of this characteristic assigned by Homey."""
    uuid: Final[str]
    value: bytes | None
    descriptors: Final[tuple[BleDescriptor, ...]]
    properties: Final[
        tuple[
            BleCharacteristicProperty,
            ...,
        ]
    ]

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved through BleService#characteristics or by calling"
        " BleService.discover_characteristics or BleService.get_characteristic."
    )
    def __init__(self) -> None: ...
    async def discover_descriptors(
        self, uuid_filter: list[str] | None = None
    ) -> tuple[BleDescriptor, ...]:
        """
        Discover the descriptors of this characteristic.

        Args:
            uuid_filter: A collection of descriptor UUIDs to limit the discovery to.

        Raises:
            NotConnected:
        """
    async def subscribe_to_notifications(
        self, callback: Callable[[bytes], None]
    ) -> None:
        """
        Subscribe to BLE notifications from the characteristic.
        The callback is called with the data of any notification that arrives.
        Only one callback can be active at a time.

        Raises:
            NotConnected:
        """
    async def unsubscribe_from_notification(self) -> None:
        """
        Unsubscribe from BLE notifications from the characteristic.

        Raises:
            NotConnected:
        """
    async def read(self) -> bytes:
        """
        Read the current value of this characteristic.

        Raises:
            NotConnected:
        """
    async def write(self, data: bytes) -> None:
        """
        Write the data to this characteristic.

        Raises:
            NotConnected:
        """
