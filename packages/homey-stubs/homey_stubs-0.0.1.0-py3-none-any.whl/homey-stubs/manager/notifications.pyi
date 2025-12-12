from typing import final

from . import Manager

@final
class ManagerNotifications(Manager):
    """
    Manages notifications.
    You can access this manager through the Homey instance as `self.homey.notifications`.
    """
    async def create_notification(self, message: str) -> None:
        """
        Create a notification with the given message. Use `**double asterisks**` to make variables bold.
        """
