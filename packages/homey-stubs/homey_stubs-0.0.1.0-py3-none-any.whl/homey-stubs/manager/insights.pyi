from typing import Literal, final, overload

from ..insights_log import InsightsLog
from . import Manager

@final
class ManagerInsights(Manager):
    """
    Manages logs in the app's insights.
    You can access this manager through the Homey instance as `self.homey.insights`.
    """
    @overload
    async def create_log(
        self,
        id: str,
        title: str,
        type: Literal["number"],
        units: str | None = None,
        decimals: int | None = None,
    ) -> InsightsLog[float]:
        """
        Create a log.

        Args:
            id: ID of the log, lowercase and alphanumeric.
            title: Title of the log.
            type: Type of the logged values.
            units: Units of the logged values.
            decimals: Visible number of decimals.
        """
    @overload
    async def create_log(
        self,
        id: str,
        title: str,
        type: Literal["boolean"],
        units: str | None = None,
        decimals: int | None = None,
    ) -> InsightsLog[bool]:
        """
        Create an insights log.

        Args:
            id: ID of the log, lowercase and alphanumeric.
            title: Title of the log.
            type: Type of the logged values.
            units: Units of the logged values.
            decimals: Visible number of decimals.

        Raises:
            AlreadyExists: Raised if the log ID is already in use.
        """
    async def delete_log(self, log: InsightsLog) -> None:
        """
        Delete the given log.

        Raises:
            NotFound: Raised if no log with the given ID is found.
        """
    async def get_log(self, id: str) -> InsightsLog:
        """
        Get the log with given ID.

        Raises:
            NotFound: Raised if no log with the given ID is found.
        """
    async def get_logs(self) -> tuple[InsightsLog, ...]:
        """
        Get all logs belonging to this app.
        """
