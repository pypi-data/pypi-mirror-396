from collections.abc import Callable
from typing import Literal, Self, final

from . import Manager

@final
class ManagerClock(Manager[Literal["timezoneChange"]]):
    """
    Manages the time information of the Homey.
    You can access this manager through the Homey instance as `self.homey.clock`.
    """
    def get_timezone(self) -> str:
        """
        Get the current timezone of the Homey.
        """

    def on_timezone_change(self, f: Callable[[str], None]) -> Self:
        """
        The `timezoneChange` event is fired when the timezone of the Homey is changed.

        Args:
            f: A callback that receives the new timezone.
        """
