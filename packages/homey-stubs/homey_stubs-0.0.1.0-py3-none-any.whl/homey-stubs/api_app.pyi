from collections.abc import Callable
from typing import Literal, LiteralString, Self, TypeVar

from .api import Api

ChildEvent = TypeVar("ChildEvent", bound=LiteralString)

class ApiApp(Api[Literal["install", "uninstall"] | ChildEvent]):
    """
    The API of another App on Homey.
    When registered, realtime events sent to this app are fired on the instance.
    """
    async def get_installed(self) -> bool:
        """
        Check whether the app is installed, enabled and running.
        """
    async def get_version(self) -> str:
        """
        Get the app's installed version.
        """
    def on_install(self, f: Callable[[], None]) -> Self:
        """
        The `install` event is fired when the other app is installed.

        Args:
            f: A callback that receives no data.
        """
    def on_uninstall(self, f: Callable[[], None]) -> Self:
        """
        The `uninstall` event is fired when the other app is uninstalled.

        Args:
            f: A callback that receives no data.
        """
