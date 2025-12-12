from types import MappingProxyType
from typing import Literal, final

from . import Manager

type AppSettingValue = bool | float | str | None | dict[str, AppSettingValue]

@final
class ManagerSettings(Manager[Literal["set", "unset"]]):
    """
    Manages settings for this app.
    You can access this manager through the Homey instance as `self.homey.settings`.
    """
    def get(self, key: str) -> AppSettingValue:
        """
        Get the value of the setting with the given key, or None if it does not exist.
        """
    async def set(self, key: str, value: AppSettingValue) -> None:
        """
        Set the setting with the given key to the given value.
        """
    async def unset(self, key: str) -> None:
        """
        Remove the setting with the given key.
        """
    def get_settings(self) -> MappingProxyType[str, AppSettingValue]:
        """
        Get all the app settings.
        """
