from typing import Any, final

from ..api import Api
from ..api_app import ApiApp
from . import Manager

@final
class ManagerApi(Manager):
    """
    Manages web API access and realtime events to this app, as well as communication with other apps.
    You can access this manager through the Homey instance as `self.homey.api`.
    """
    async def get(self, uri: str) -> Any:
        """
        Perform a GET request.

        Args:
            uri: The path to request, relative to /api.

        Returns:
            The response from the endpoint.
        """
    async def post(self, uri: str, body: Any) -> Any:
        """
        Perform a POST request.

        Args:
            uri: The path to request, relative to /api.
            body: A body to send with the request.

        Returns:
            The response from the endpoint.
        """
    async def put(self, uri: str, body: Any) -> Any:
        """
        Perform a PUT request.

        Args:
            uri: The path to request, relative to /api.
            body: A body to send with the request.

        Returns:
            The response from the endpoint.
        """
    async def delete(self, uri: str) -> Any:
        """
        Perform a DELETE request.

        Args:
            uri: The path to request, relative to /api.

        Returns:
            The response from the endpoint.
        """
    async def realtime(self, event: str, data: Any) -> None:
        """
        Emit a realtime event.

        Args:
            event: The name of the event.
            data: The data to send.
        """

    def get_api(self, uri: str) -> Api:
        """
        Create an API instance, to receive realtime events.

        Args:
            uri: The URI of the endpoint, e.g. `homey:manager:webserver`.

        Returns:
            An API instance registered to the given uri.
        """
    def get_api_app(self, app_id: str) -> ApiApp:
        """
        Create an app API instance, to receive realtime events.

        Args:
            app_id:

        Returns:
            An ApiApp instance registered to the given app.
        """
    def unregister_api(self, api: Api) -> None:
        """
        Unregister an API instance.

        Args:
            api: Api instance.
        """
    async def get_local_url(self) -> str:
        """
        Get a url for local access.
        """
    async def get_owner_api_token(self) -> str:
        """
        Start a new API session on behalf of the homey owner and return the API token.
        The API Token expires after not being used for two weeks.

        Requires the `homey:manager:api` permission.
        For more information about permissions read the [Permissions tutorial](https://apps.developer.homey.app/the-basics/app/permissions).

        Returns:
            An API token.
        """
