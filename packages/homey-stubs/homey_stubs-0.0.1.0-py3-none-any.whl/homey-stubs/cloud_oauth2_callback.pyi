from collections.abc import Callable
from typing import Literal, LiteralString, Self, TypeVar, final
from warnings import deprecated

from .simple_class import SimpleClass

ChildEvent = TypeVar("ChildEvent", bound=LiteralString)

class CloudOAuth2Callback(SimpleClass[Literal["code", "url"] | ChildEvent]):
    """
    An OAuth2 callback that can be used in log-in flows.
    """

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling ManagerCloud.create_oauth2_callback."
    )
    def __init__(self) -> None: ...
    def on_url(self, f: Callable[[str], None]) -> Self:
        """
        The `url` event is fired when a URL is received.
        The user must be redirected to this URL to complete the sign-in process.

        Args:
            f: Callback that receives an absolute URL to the sign-in page.
        """

    def on_code(
        self,
        f: Callable[[str | Exception], None],
    ) -> Self:
        """
        The `code` event is fired when an OAuth2 code is received.
        The code can usually be swapped by the app for an access token.

        Args:
            f: Callback that receives an OAuth2 code, or an Exception if something went wrong.
        """
