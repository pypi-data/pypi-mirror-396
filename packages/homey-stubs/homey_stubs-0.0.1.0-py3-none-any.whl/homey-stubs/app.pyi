from typing import Any, Final, final
from warnings import deprecated

from .homey import Homey
from .simple_class import SimpleClass

class App(SimpleClass):
    """
    The App class is your start point for any app.
    This class should be extended and exported as homey_export from app.py.

    Example:
        ```python
        from homey.app import App

        class MyApp(App):
            \"""My Homey app\"""

            async def on_init(self):
                self.log("MyApp has been initialized")

        homey_export = MyApp
        ```
    """

    homey: Final[Homey]
    """The Homey instance this app is running on."""
    id: Final[str]
    """The ID of this app."""
    manifest: Final[Any]
    """The app.json manifest of this app."""
    sdk: Final[int]
    """The SDK version this app is using."""

    @final
    @deprecated(
        "This class must not be initialized by the developer, but is instantiated when starting the app."
    )
    def __init__(self) -> None: ...
    async def on_init(self) -> None:
        """
        This method is called when initializing the app.
        It can be used for setup.

        This method is expected to be overridden.
        """
    async def on_uninit(self) -> None:
        """
        This method is called when unloading the app.
        It can be used for cleanup.

        This method is expected to be overridden.
        """
