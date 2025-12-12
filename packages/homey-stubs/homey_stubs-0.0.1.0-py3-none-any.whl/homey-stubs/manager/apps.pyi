from typing import final

from ..api_app import ApiApp
from . import Manager

@final
class ManagerApps(Manager):
    """
    Manages other apps installed on the Homey.
    You can access this manager through the Homey instance as `self.homey.apps`.
    """
    async def get_installed(self, app: ApiApp) -> bool:
        """
        Check whether the app is installed, enabled and running.
        """
    async def get_version(self, app: ApiApp) -> str:
        """
        Get the app's installed version.
        """
