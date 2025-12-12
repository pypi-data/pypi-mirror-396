from typing import Final

from .discovery_result import DiscoveryResult

class DiscoveryResultMAC(DiscoveryResult):
    """
    A result of a MAC discovery strategy.
    """

    mac: Final[str]
    """The MAC address of the device."""
