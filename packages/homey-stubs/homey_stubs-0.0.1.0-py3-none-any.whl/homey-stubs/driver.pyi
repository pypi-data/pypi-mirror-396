from asyncio import Future
from types import MappingProxyType
from typing import Any, Final, Required, TypedDict, final
from warnings import deprecated

from .device import Device
from .discovery_strategy import DiscoveryStrategy
from .homey import Homey
from .pair_session import PairSession
from .simple_class import SimpleClass

type Data = MappingProxyType[str, Any]

class Driver(SimpleClass):
    """
    The Driver class manages all Device instances, which represent all paired devices.
    This class should be extended and exported as homey_export from driver.py.

    Example:
        ```python
        from homey.driver import Driver, ListDeviceProperties

        class MyDriver(Driver):
            async def on_pair_list_devices(self):
                api_devices = await get_api_devices()
                pair_devices: list[ListDeviceProperties] = [
                    {"data": {"id": api_device.id}}
                    for api_device in api_devices
                    if api_device.type == 5
                ]
                return pair_devices

        homey_export = MyDriver
        ```
    """

    homey: Final[Homey]
    manifest: Final[Any]
    """The app.json manifest of this driver."""

    @final
    @deprecated(
        "This class must not be initialized by the developer, but is instantiated when starting the app."
    )
    def __init__(self) -> None: ...
    async def on_init(self) -> None:
        """
        This method is called when the driver is loaded,
        and properties such as its devices are available.
        It can be used for setup.

        This method is expected to be overridden.
        """
    async def on_uninit(self) -> None:
        """
        This method is called when unloading the driver.
        It can be used for cleanup.

        This method is expected to be overridden.
        """
    async def ready(self) -> Future:
        """
        Get an awaitable that is resolved when the driver is ready, meaning Driver#on_init has been run.
        """

    async def on_pair(self, session: PairSession) -> None:
        """
        This method is called when a pairing session is started.
        It can be used to hook into the pairing flow.

        This method can be overridden,
        with the default implementation supporting the standard pairing flow.
        """
    async def on_repair(self, session: PairSession, device: Device) -> None:
        """
        This method is called when a re-pairing session is started.
        It can be used to hook into the pairing flow.

        This method can be overridden,
        with the default implementation supporting the standard re-pairing flow.
        """
    async def on_unpair(self, session: PairSession, device: Device) -> None:
        """
        This method is called when an unpairing session is started.
        It can be used to hook into the pairing flow.

        This method can be overridden,
        with the default implementation supporting the standard unpairing flow.
        """
    async def on_pair_list_devices(self, view_data: dict) -> list[ListDeviceProperties]:
        """
        This method is called when a pairing session is started
        and the default `on_pair` implementation has not been overridden.
        It can be used to get a list of devices to pair the user can choose from.

        This method is expected to be overridden.

        Args:
            view_data: Data from the pairing view that requested the list of devices.

        Returns:
            A tuple with device descriptions, which are used in the rest of the default pairing flow.
        """
    async def on_map_device_class(self, device: Device) -> type[Device]:
        """
        This method is called when pairing a new device to determine which class to initialize it with.

        This method is expected to be overridden.

        Example:
        ```python
        from homey.driver import Driver
        from device import MyDevice, MyDimDevice

        class MyDriver(Driver):
            def on_map_device_class(self, device):
                return MyDimDevice if device.has_capability("dim") else MyDevice
        ```

        Args:
            device: A temporary Device instance which will be destroyed after this method returns,
                and which does not support async calls. Its data can be used to determine which class to use.
        """

    def get_device(self, device_data: dict[str, Any]) -> Device:
        """
        Get a device belonging to this driver that matches the given data.

        Raises:
            NotFound:
        """
    def get_device_by_id(self, device_id: str) -> Device:
        """
        Get a device belonging to this driver by the ID assigned by Homey.

        Raises:
            NotFound:
        """
    def get_devices(self) -> tuple[Device, ...]:
        """
        Get all devices belonging to this driver.
        """
    def get_discovery_strategy(self) -> DiscoveryStrategy | None:
        """
        Get the discovery strategy for this driver, as defined in app.json.
        """

class ListDeviceProperties(TypedDict, total=False):
    """
    The properties of a device shown in the pairing screen.
    Only the data object is required.
    """

    data: Required[dict[str, Any]]
    """
    The immutable data of this device.
    By default data.id is used to distinguish between devices.
    """
    store: dict[str, Any]
    """Mutable data of this device that should persist."""
    settings: dict[str, bool | float | str | None]
    """A mapping from setting IDs to the initial value of the setting for this particular device."""
    capabilities: list[str]
    """The capabilities of this particular device."""
    capabilitiesOptions: dict[str, dict[str, Any]]
    """A mapping from capability IDs to options for the capability of this particular device."""
    name: str
    """The name of the device to be used in the UI."""
    icon: str
    """The filename of the icon for the device to be used in the UI."""
