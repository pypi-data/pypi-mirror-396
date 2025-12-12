from typing import final

from ..device import Device
from ..signal import Signal
from ..signal_433 import Signal433
from ..signal_868 import Signal868
from ..signal_infrared import SignalInfrared
from . import Manager

@final
class ManagerRF(Manager):
    """
    Manages radio frequency communication on the Homey.
    You can access this manager through the Homey instance as `self.homey.rf`.
    """
    async def cmd(
        self,
        signal: Signal,
        command_id: str,
        repetitions: int | None = None,
        device: Device | None = None,
    ) -> None:
        """
        Send a predefined command using the given signal.

        Requires the `homey:wireless:433`, `homey:wireless:868`, or `homey:wireless:ir` permissions.
        For more information about permissions read the [Permissions tutorial](https://apps.developer.homey.app/the-basics/app/permissions).

        Args:
            signal: The signal used to transmit the data.
            command_id: The ID of the command, as defined in app.json.
            repetitions: How often the signal gets transmitted.
            device: The device to send the signal to.
        """
    async def tx(
        self,
        signal: Signal,
        frame: list[int] | bytes | bytearray,
        repetitions: int | None = None,
        device: Device | None = None,
    ) -> None:
        """
        Transmit a raw frame using the given signal.

        Args:
            signal: The signal used to transmit the data.
            frame: The data to be transmitted.
            repetitions: How often the signal gets transmitted.
            device: The device to send the signal to.
        """
    async def disable_signal_rx(self, signal: Signal) -> None:
        """
        Disable receiving commands for the given signal.

        Requires the `homey:wireless:433`, `homey:wireless:868`, or `homey:wireless:ir` permissions.
        For more information about permissions read the [Permissions tutorial](https://apps.developer.homey.app/the-basics/app/permissions).
        """
    async def enable_signal_rx(self, signal: Signal) -> None:
        """
        Enable receiving commands for the given signal.

        Requires the `homey:wireless:433`, `homey:wireless:868`, or `homey:wireless:ir` permissions.
        For more information about permissions read the [Permissions tutorial](https://apps.developer.homey.app/the-basics/app/permissions).
        """

    def get_signal_433(self, id: str) -> Signal433:
        """
        Get the 433 MHz signal with the given ID, as defined in app.json.
        """
    def get_signal_868(self, id: str) -> Signal868:
        """
        Get the 868 MHz signal with the given ID, as defined in app.json.
        """
    def get_signal_infrared(self, id: str) -> SignalInfrared:
        """
        Get the infrared signal with the given ID, as defined in app.json.
        """
