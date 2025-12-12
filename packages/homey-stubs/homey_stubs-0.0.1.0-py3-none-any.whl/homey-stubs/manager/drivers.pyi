from types import MappingProxyType
from typing import final

from ..driver import Driver
from . import Manager

@final
class ManagerDrivers(Manager):
    """
    Manages drivers in this app.
    You can access this manager through the Homey instance as `self.homey.drivers`.
    """
    def get_driver(self, id: str) -> Driver:
        """
        Get a driver instance by its ID.
        """
    def get_drivers(self) -> MappingProxyType[str, Driver]:
        """
        Get all driver instances.

        Returns:
            A mapping from IDs to drivers.
        """
