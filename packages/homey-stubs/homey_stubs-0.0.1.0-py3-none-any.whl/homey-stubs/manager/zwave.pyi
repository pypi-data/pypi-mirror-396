from typing import final

from ..device import Device
from ..zwave_node import ZWaveNode
from . import Manager

@final
class ManagerZWave(Manager):
    """
    Manage the Z-Wave communication of the Homey.
    You can access this manager through the Homey instance as `self.homey.zwave`.
    """
    async def get_node(self, device: Device) -> ZWaveNode:
        """
        Get a Z-Wave node instance for the given device.
        """
