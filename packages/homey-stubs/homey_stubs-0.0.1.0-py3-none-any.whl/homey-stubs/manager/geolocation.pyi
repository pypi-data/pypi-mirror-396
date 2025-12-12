from typing import Literal, final

from . import Manager

@final
class ManagerGeolocation(Manager[Literal["location"]]):
    """
    Manages the location information of the Homey.
    You can access this manager through the Homey instance as `self.homey.geolocation`.
    """
    def get_latitude(self) -> float | None:
        """
        Get the Homey's physical location's latitude.

        Requires the `homey:manager:geolocation` permission.
        For more information about permissions read the [Permissions tutorial](https://apps.developer.homey.app/the-basics/app/permissions).
        """
    def get_longitude(self) -> float | None:
        """
        Get the Homey's physical location's longitude.

        Requires the `homey:manager:geolocation` permission.
        For more information about permissions read the [Permissions tutorial](https://apps.developer.homey.app/the-basics/app/permissions).
        """
    def get_accuracy(self) -> float | None:
        """
        Get the Homey's physical location's accuracy in meters.

        Requires the `homey:manager:geolocation` permission.
        For more information about permissions read the [Permissions tutorial](https://apps.developer.homey.app/the-basics/app/permissions).
        """
    def get_mode(self) -> Literal["auto", "manual"] | None:
        """
        Get the Homey's location mode.
        """
