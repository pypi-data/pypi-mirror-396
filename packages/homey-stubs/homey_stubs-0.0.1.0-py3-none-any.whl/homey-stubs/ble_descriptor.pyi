from typing import Final, final
from warnings import deprecated

from .simple_class import SimpleClass

class BleDescriptor(SimpleClass):
    """
    A BLE descriptor of a characteristic.
    """

    id: Final[str]
    """The ID of the descriptor assigned by Homey."""
    uuid: Final[str]
    value: bytes | None

    @final
    @deprecated(
        "This class must not be initialized by the developer,"
        " but retrieved through BleCharacteristic.descriptors"
        " or by calling BleCharacteristic#discover_descriptors."
    )
    def __init__(self) -> None: ...
    async def read(self) -> bytes:
        """
        Read the current value of this descriptor.

        Raises:
            NotConnected:
        """
    async def write(self, data: bytes) -> None:
        """
        Write the data to this descriptor.

        Raises:
            NotConnected:
        """
