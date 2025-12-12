from typing import Generic, TypeVar, final
from warnings import deprecated

Type = TypeVar("Type", bound=float | bool)

class InsightsLog(Generic[Type]):
    """
    The log of a value in Homey insights.
    """
    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling ManagerInsights.create_log."
    )
    def __init__(self) -> None: ...
    async def create_entry(self, value: Type) -> None:
        """
        Create a new insights log entry with the given value.
        """
