from collections.abc import Callable
from typing import (
    Any,
    Final,
    Literal,
    LiteralString,
    Self,
    TypeVar,
    final,
)
from warnings import deprecated

from .app import App
from .manager.api import ManagerApi
from .manager.apps import ManagerApps
from .manager.arp import ManagerArp
from .manager.ble import ManagerBLE
from .manager.clock import ManagerClock
from .manager.cloud import ManagerCloud
from .manager.dashboards import ManagerDashboards
from .manager.discovery import ManagerDiscovery
from .manager.drivers import ManagerDrivers
from .manager.flow import ManagerFlow
from .manager.geolocation import ManagerGeolocation
from .manager.i18n import ManagerI18n
from .manager.images import ManagerImages
from .manager.insights import ManagerInsights
from .manager.notifications import ManagerNotifications
from .manager.rf import ManagerRF
from .manager.settings import ManagerSettings
from .manager.videos import ManagerVideos
from .manager.zigbee import ManagerZigbee
from .manager.zwave import ManagerZWave
from .simple_class import SimpleClass

ChildEvent = TypeVar("ChildEvent", bound=LiteralString)

class Homey(SimpleClass[Literal["cpuwarn", "memwarn", "unload"] | ChildEvent]):
    """
    The Homey instance holds all the Managers, System Events and generic properties.
    You can access the Homey instance through `self.homey` on App, Driver and Device,
    and it is also passed into your api handlers.

    By reading Homey#platform and Homey#platformVersion, your app can determine which product your app is running on.
     * Product                  platform 	platform_version
     * Homey Cloud              cloud 	    1
     * Homey Pro (Early 2023)   local       2
    """

    api: Final[ManagerApi]
    apps: Final[ManagerApps]
    arp: Final[ManagerArp]
    ble: Final[ManagerBLE]
    clock: Final[ManagerClock]
    cloud: Final[ManagerCloud]
    dashboards: Final[ManagerDashboards]
    discovery: Final[ManagerDiscovery]
    drivers: Final[ManagerDrivers]
    flow: Final[ManagerFlow]
    geolocation: Final[ManagerGeolocation]
    i18n: Final[ManagerI18n]
    images: Final[ManagerImages]
    insights: Final[ManagerInsights]
    notifications: Final[ManagerNotifications]
    rf: Final[ManagerRF]
    settings: Final[ManagerSettings]
    videos: Final[ManagerVideos]
    zigbee: Final[ManagerZigbee]
    zwave: Final[ManagerZWave]

    app: Final[App]
    """This app."""
    env: Final[Any]
    """The environment variables from `env.json`."""
    manifest: Final[Any]
    """The app manifest from `app.json`."""
    platform: Final[Literal["local", "cloud"]]
    """The platform that the Homey is running on."""
    platform_version: Final[Literal[1, 2]]
    """The platform version the Homey is running on."""
    version: Final[str]

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved through App#homey, Driver#homey, or Device#homey."
    )
    def __init__(self) -> None: ...
    async def ready(self) -> None:
        """
        Get an awaitable that is resolved when the Homey is ready, meaning App.on_init has been run.
        """
    def translate(self, key: str, tags: dict[str, str] | None = None) -> str | None:
        """
        Translate a string, as defined in the app's `/locales/<language>.json` file.

        Example:

        /locales/en.json
        ```json
        { "welcome": "Welcome, __name__!" }
        ```

        /app.py
        ```python
        welcome_message = self.homey.translate("welcome", { "name": "Dave" })
        self.log(welcome_message)
        ```

        Args:
            key: The key in the `<language.json>` file, with dots separating nesting. For example `"errors.missing"`.
            tags: A mapping of tags in the string to replace. For example, for `Hello, __name__!` you could pass `{"name":"Dave"}`.

        Returns:
            The translated string, or None if the key was not found.
        """
    def set_interval(self, callback: Callable, ms: int, *args, **kwargs) -> int:
        """
        Set an interval that calls the given callback every `ms` milliseconds, with any given arguments.
        This interval is automatically cleared when the Homey instance gets destroyed.

        Returns:
            The ID of the created interval.
        """
    def clear_interval(self, id: int | None) -> None:
        """
        Clear the interval with the given ID.
        """
    def set_timeout(self, callback: Callable, ms: int, *args, **kwargs) -> int:
        """
        Set a timeout that calls the given callback after `ms` milliseconds, with any given arguments.
        This timeout is automatically cleared when the Homey instance gets destroyed.

        Returns:
            The ID of the created timout.
        """
    def clear_timeout(self, id: int | None) -> None:
        """
        Clear the timeout with the given ID.
        """
    def has_permission(self, permission: str) -> bool:
        """
        Get whether the app has the given permission.
        """

    def on_cpuwarn(
        self,
        f: Callable[[int, int], None],
    ) -> Self:
        """
        This event is fired when the app is using too much CPU.
        If the app does not behave within a reasonable amount of time, the app is killed.

        Args:
            f: Callback that receives the number of warnings already sent and the maximum number of warnings until the app is killed.
        """
    def on_memwarn(
        self,
        f: Callable[[int, int], None],
    ) -> Self:
        """
        This event is fired when the app is using too much memory.
        If the app does not behave within a reasonable amount of time, the app is killed.

        Args:
            f: Callback that receives the number of warnings already sent and the maximum number of warnings until the app is killed.
        """
    def on_unload(
        self,
        f: Callable[[], None],
    ) -> Self:
        """
        This event is fired when the app is stopped.

        Args:
            f: Callback that receives no arguments.
        """
