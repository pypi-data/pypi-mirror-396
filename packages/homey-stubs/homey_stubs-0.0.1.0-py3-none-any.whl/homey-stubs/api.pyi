from collections.abc import Callable
from typing import Any, Literal, LiteralString, Self, TypedDict, TypeVar

from .homey import Homey
from .util.event_emitter import EventEmitter

ChildEvent = TypeVar("ChildEvent", bound=LiteralString)

class Api(EventEmitter[Literal["realtime"] | ChildEvent]):
    """
    A web API endpoint on Homey.
    When registered, realtime events sent to the endpoint are fired on the instance.
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
    def unregister(self) -> None:
        """
        Unregister this API instance.
        """

    def on_realtime(
        self,
        f: Callable[[str, Any], None],
    ) -> Self:
        """
        The `realtime` event is fired when such an event is received on this API endpoint.

        Args:
            f: A callback that receives the name of the event and its data.
        """

class ApiRequest(TypedDict):
    """
    An API request, as received in the `api.py` implementation of the app.

    - query: query parameters passed along with the request.
    - params: a set of parameters defined in the path of the endpoint.
    - body: the request body. JSON is automatically parsed.
    - homey: the Homey instance the app is running on. It can be used, for example, to access the App instance.
    """

    query: dict[str, str]
    params: dict[str, str]
    body: Any
    homey: Homey
