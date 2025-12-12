from types import MappingProxyType
from typing import Final

from .discovery_result import DiscoveryResult

class DiscoveryResultSSDP(DiscoveryResult):
    """
    A result of an SSDP discovery strategy.
    """

    port: Final[int]
    headers: Final[MappingProxyType[str, str]]
    """The headers in the SSDP response of the device."""
