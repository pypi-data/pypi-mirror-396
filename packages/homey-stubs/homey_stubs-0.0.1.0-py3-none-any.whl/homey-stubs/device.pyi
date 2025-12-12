from types import MappingProxyType
from typing import Any, Final, Protocol, final
from warnings import deprecated

from .discovery_result import DiscoveryResult
from .driver import Driver
from .homey import Homey
from .image import Image
from .simple_class import SimpleClass
from .video import Video

type CapabilityValue = bool | float | str | None
type SettingValue = bool | float | str | None

type Data = MappingProxyType[str, Any]
type Store = MappingProxyType[str, Any]
type Energy = Any

class Device(SimpleClass):
    """
    A device paired in Homey.
    It should be extended and exported from device.py as homey_export, or any custom class as returned in Driver#on_map_device_class.

    Example:
        ```python
        from homey.device import Device

        class MyDevice(Device):
            \"""My Homey device\"""

            async def on_init(self):
                self.register_capability_listener("onoff", self.on_onoff)

            async def on_onoff(self, value: bool, **kwargs):
                \"""Turn the device on or off.\"""

        homey_export = MyDevice
        ```
    """

    driver: Final[Driver]
    homey: Final[Homey]

    @final
    @deprecated(
        "This class must not be initialized by the developer, but is instantiated by Homey after being added by a user."
    )
    def __init__(self) -> None: ...

    ### Lifecycle ###
    async def on_init(self) -> None:
        """
        This method is called when the device is loaded,
        and properties such as data, settings, and capabilities are available.
        It can be used for setup.

        This method is expected to be overridden.
        """
    async def on_uninit(self) -> None:
        """
        This method is called when the device is unloaded.
        It can be used for cleanup.

        This method is expected to be overridden.
        """
    async def ready(self) -> None:
        """
        Get an awaitable that is resolved when the device is ready, meaning Device#on_init has been run.
        """
    async def on_added(self) -> None:
        """
        This method is called when the device is added by a user.

        This method is expected to be overridden.
        """
    async def on_deleted(self) -> None:
        """
        This method is called when the device is removed by a user.

        This method is expected to be overridden.
        """

    ### Capabilities ###
    def get_capability_value(self, id: str) -> CapabilityValue:
        """
        Get the current value of the capability with the given ID.

        Raises:
            NotFound:
        """
    async def set_capability_value(self, id: str, value: CapabilityValue) -> None:
        """
        Set the value of the capability with the given ID.

        Raises:
            NotFound:
        """
    def get_state(self) -> MappingProxyType[str, CapabilityValue]:
        """
        Get the state of all capabilities of this device.
        """
    def has_capability(self, id: str) -> bool:
        """
        Get whether the device has the capability with the given ID.
        """
    async def register_capability_listener(
        self, capability_id: str, listener: CapabilityListener
    ) -> None:
        """
        Register a listener for when the value of a capability is changed.

        Args:
            listener: An async listener for when a capability value is changed.
                It receives the new value, as well as any optional arguments, such as duration.
        """
    async def register_multiple_capability_listener(
        self,
        capability_ids: list[str],
        listener: MultipleCapabilityListener,
        debounce_timeout: int = 250,
    ) -> None:
        """
        Register a listener for multiple capabilities, that is called when the value of any of them is changed.

        Args:
            listener: An async listener for multiple capabilities at once.
                It receives a mapping containing from each capability to its new value,
                as well as a mappings containing any optional arguments, such as duration, for each capability.
            debounce_timeout: For how many milliseconds value changes are debounced before calling the listener.
        """
    async def trigger_capability_listener(
        self, capability_id: str, value: CapabilityValue, **kwargs
    ) -> None:
        """
        Trigger the capability listener registered to the given capability with the given value and any keyword arguments.
        """
    async def add_capability(self, id: str) -> None:
        """
        Add a capability to this device.

        Note: this is an expensive method so use it only when needed.
        """
    async def remove_capability(self, id: str) -> None:
        """
        Remove the capability with the given ID from this device.

        Note:
        Any flow that depends on this capability will become broken.
        This is an expensive method so use it only when needed.
        """
    def get_capabilities(self) -> tuple[str, ...]: ...
    def get_capability_options(self, id: str) -> MappingProxyType[str, Any]:
        """
        Get the current options configuration of the capability with the given ID.

        Raises:
            NotFound:
        """
    async def set_capability_options(self, id, options: dict[str, Any]) -> None:
        """
        Set the options configuration of the capability with the given ID.

        Note: this is an expensive method so use it only when needed.

        Raises:
            NotFound:
        """

    ### Settings ###
    async def on_settings(
        self,
        old_settings: dict[str, SettingValue],
        new_settings: dict[str, SettingValue],
        changed_keys: tuple[str, ...],
    ) -> str | None:
        """
        This method is called when the settings of the device are change in Homey by a user,
        so that they can be synchronized with the device or a bridge.

        This method is expected to be overridden.

        Args:
            old_settings: The settings object before the changes.
            new_settings: The settings object after the changes.
            changed_keys: The keys of the settings that were changed.

        Returns:
            A custom message that will be displayed to the user, or None if no message should be shown.
        """
    def get_setting(self, key: str) -> SettingValue:
        """
        Get the value of the setting with the given key.
        """
    def get_settings(self) -> MappingProxyType[str, SettingValue]:
        """
        Get the settings object of this device.
        """
    async def set_settings(self, settings: dict[str, SettingValue]) -> None:
        """
        Update the settings object of the device.
        The given settings may be a subset of the settings defined for the device.

        Note: the `Device.on_settings` method will not be called when the settings are changed programmatically.
        """

    ### Device data ###
    def get_id(self) -> str:
        """
        Get the ID assigned to this device by Homey.
        """
    def get_data(self) -> Data:
        """
        Get the data object of this device.
        """
    def get_store(self) -> Store:
        """
        Get the store object of this device.
        """
    async def set_store_value(self, key: str, value: Any) -> None:
        """
        Set the value for the given key in the store object of the device.
        """
    async def unset_store_value(self, key: str) -> None:
        """
        Remove the given key from the store object of the device.
        """

    async def set_album_art_image(self, image: Image) -> None:
        """
        Set the album art used for this device.
        """
    async def set_camera_image(self, id: str, title: str, image: Image) -> None:
        """
        Set the camera image for this device.

        Args:
            id: Unique identifier of the image, e.g. `front`.
            title: Title of the image used in the UI, e.g. `Front Camera`.
        """
    async def set_camera_video(self, id: str, title: str, video: Video) -> None:
        """
        Set the camera video for this device.

        Args:
            id: Unique identifier of the video, e.g. `front`.
            title: Title of the video used in the UI, e.g. `Front Camera`.
        """

    def get_energy(self) -> MappingProxyType[str, Any]:
        """
        Get the energy configuration of this device.
        """
    async def set_energy(self, energy: dict[str, Any]) -> None:
        """
        Set the energy configuration of this device.
        """

    def get_available(self) -> bool:
        """
        Get whether the device is marked as available.
        """
    async def set_unavailable(self, message: str | None = None) -> None:
        """
        Mark the device as unavailable.

        Args:
            message: A message to display to the user, or None if the default message should be shown.
        """
    async def set_available(self) -> None:
        """
        Mark this device as available.
        """

    async def set_warning(self, message: str | None = None) -> None:
        """
        Set a warning message for this device, to be shown to the user.
        This message is persistent, so make sure to unset it when necessary.

        Args:
            message: The message to display to the user, or None to show no message.
        """
    async def unset_warning(self) -> None:
        """
        Remove the warning message for this device.
        """

    def get_class(self) -> str:
        """
        Get the Homey device class of this device.
        """
    async def set_class(self, device_class: str) -> None:
        """
        Set the Homey device class of this device.
        """

    def get_name(self) -> str:
        """
        Get the name of the device in Homey.
        """
    async def on_renamed(self, name: str) -> None:
        """
        This method is called when the device is renamed in Homey by a user,
        so that the name can be synchronized with the device or a bridge.

        This method is expected to be overridden.
        """
    async def set_last_seen_at(self) -> None:
        """
        Set when the device has last been seen.
        This method should be called if the device is known to be alive and responding.
        """

    ### Discovery ###
    async def on_discovery_result(self, discovery_result: DiscoveryResult) -> bool:
        """
        This method is called when a device has been discovered to check whether it is this device.
        By default, the method will compare this and the discovered device's data.id property.

        This method is expected to be overridden.

        Returns:
            Whether the discovery result is for this device.
        """
    async def on_discovery_available(self, discovery_result: DiscoveryResult) -> None:
        """
        This method is called when a discovery result matching this device is found,
        in order to set up a connection with the device.
        Raising an exception here will make the device unavailable with the exception's message.

        This method is expected to be overridden.
        """
    async def on_discovery_last_seen_changed(
        self, discovery_result: DiscoveryResult
    ) -> None:
        """
        This method is called when the device has been found again.

        This method is expected to be overridden.
        """
    async def on_discovery_address_changed(
        self, discovery_result: DiscoveryResult
    ) -> None:
        """
        This method is called when the device was found again at a different address.

        This method is expected to be overridden.
        """

class CapabilityListener[Value](Protocol):
    """
    A listener for when a capability value is changed.
    It receives the new value, as well as any optional arguments, such as duration.

    If an exception is raised, the capability value will not be changed and the error message will be shown to the user.

    For example:
    ```python
    listener(0.8, duration=300)
    ```
    """
    async def __call__(self, value: Value, **kwargs: Any) -> None: ...

class MultipleCapabilityListener[MultipleValues](Protocol):
    """
    A listener for multiple capabilities at once.
    It receives a mapping from each capability to its new value,
    as well as a mappings containing any optional arguments, such as duration, for each capability.

    If an exception is raised, the capability values will not be changed and the error message will be shown to the user.

    For example:
    ```python
    listener({"onoff": True, "dim": 0.8}, dim={"duration": 300})
    ```
    """
    async def __call__(
        self, values: MultipleValues, **kwargs: dict[str, Any]
    ) -> None: ...
