from typing import final

from ..discovery_strategy import DiscoveryStrategy
from . import Manager

@final
class ManagerDiscovery(Manager):
    """
    Manages discovery of new devices.
    You can access this manager through the Homey instance as `self.homey.discovery`.
    """
    def get_strategy(self, id: str) -> DiscoveryStrategy:
        """
        Get the strategy with the given ID, as defined in app.json.


        Raises:
            NotFound: Raised if no strategy with the given ID is found.
        """
