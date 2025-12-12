from types import MappingProxyType
from typing import Final

from .discovery_result import DiscoveryResult

class DiscoveryResultMDNSSD(DiscoveryResult):
    """
    A result of an mDNS-SD discovery strategy.
    """

    full_name: Final[str | None]
    name: Final[str | None]
    host: Final[str | None]
    """The hostname of the device."""
    port: Final[int | None]
    txt: Final[MappingProxyType[str, str]]
    """The TXT records of the device"""
