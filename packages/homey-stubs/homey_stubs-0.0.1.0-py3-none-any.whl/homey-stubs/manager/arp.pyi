from typing import final

from . import Manager

@final
class ManagerArp(Manager):
    """
    Manages the Address Resolution Protocol.
    You can access this manager through the Homey instance as `self.homey.arp`.
    """
    async def get_mac(self, ip: str) -> str:
        """
        Get the ip's MAC address.
        """
