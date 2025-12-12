from types import MappingProxyType
from typing import Generic, Literal, LiteralString, TypeVar, final
from warnings import deprecated

from .discovery_result import DiscoveryResult
from .simple_class import SimpleClass

Result = TypeVar("Result", bound=DiscoveryResult, default=DiscoveryResult)
ChildEvent = TypeVar("ChildEvent", bound=LiteralString, default=LiteralString)

class DiscoveryStrategy(
    SimpleClass[Literal["result"] | ChildEvent],
    Generic[Result, ChildEvent],
):
    """
    A strategy for discovering new devices.
    """

    @final
    @deprecated(
        "This class must not be initialized by the developer, but created by calling ManagerDiscovery#get_strategy instead."
    )
    def __init__(self) -> None: ...
    def get_discovery_results(self) -> MappingProxyType[str, Result]:
        """
        Get all discovered devices.

        Returns:
            A mapping from IDs to discovery results.
        """
