from typing import final

from ..cloud_oauth2_callback import CloudOAuth2Callback
from ..cloud_webhook import CloudWebhook
from . import Manager

@final
class ManagerCloud(Manager):
    """
    Manages interactions with the Homey cloud.
    This includes [OAuth2](https://apps.developer.homey.app/cloud/oauth2) and [Webhooks](https://apps.developer.homey.app/cloud/webhooks).
    You can access this manager through the Homey instance as `self.homey.cloud`.
    """
    async def create_oauth2_callback(self, url: str) -> CloudOAuth2Callback:
        """
        Generate an OAuth2 callback.

        Args:
            url: The API url for which to create a callback.
        """
    async def create_webhook(
        self, id: str, secret: str, data: dict = {}
    ) -> CloudWebhook:
        """
        Register a handler for a webhook [registered with Homey](https://tools.developer.homey.app/webhooks).

        Args:
            id: The ID given after registering the webhook.
            secret: The secret given after registering the webhook.
            data: Data used to identify this Homey in calls to the webhook.
        """
    async def unregister_webhook(self, webhook: CloudWebhook) -> None:
        """
        Unregister the given webhook handler.
        """
    async def get_homey_id(self) -> str:
        """
        Get the Homey's cloud ID.
        """
    async def get_local_address(self) -> str:
        """
        Get the Homey's local address and port.
        """
