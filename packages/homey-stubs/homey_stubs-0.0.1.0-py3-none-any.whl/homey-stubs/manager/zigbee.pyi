from typing import final

from ..device import Device
from ..zigbee_node import ZigbeeNode
from . import Manager

@final
class ManagerZigbee(Manager):
    """
    Manage the Zigbee communication of the Homey.
    You can access this manager through the Homey instance as `self.homey.zigbee`.
    """
    async def get_node(self, device: Device) -> ZigbeeNode:
        """
        Get a Zigbee node instance for the given device.
        """
