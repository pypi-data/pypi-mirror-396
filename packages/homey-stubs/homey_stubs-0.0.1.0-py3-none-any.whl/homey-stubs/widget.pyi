from typing import Any, Protocol, Required, Self, TypedDict

from .device import SettingValue
from .simple_class import SimpleClass
from .widget_setting import WidgetSetting

class Widget(SimpleClass):
    """
    A widget, as defined in `app.json`.
    """
    def register_argument_autocomplete_listener(
        self, id: str, listener: SettingAutoCompleteListener
    ) -> Self:
        """
        Register an autocomplete listener for the setting with the given id.

        Args:
            listener: An async listener for when an autocomplete value is requested for the setting.
                It receives the query typed by the user, as well as any settings in the widget, as currently selected by the user.

        Returns:
            This widget, for chained calls.

        Raises:
            AlreadyExists: Raised if a listener was already registered for the setting.
            NotFound: Raised if no setting with the given id is found.
        """
    def get_setting(self, id: str) -> WidgetSetting:
        """
        Get the setting with the given id.

        Raises:
            NotFound: Raised if a setting with the given id is not found.:
        """

class SettingAutoCompleteResult(TypedDict, total=False):
    name: Required[str]
    """The autocomplete value that will be shown to the user and used in the widget."""
    description: str
    """A short description of the result that will be shown below the name."""
    icon: str
    """A path to an `.svg` file to show as icon for the result."""
    image: str
    """A path to an image that is not an `.svg` file to show as icon for the result."""
    data: Any
    """Any additional data you wild like to pass to the widget for this autocomplete value."""

class SettingAutoCompleteListener(Protocol):
    """
    A listener for when an autocomplete value is requested in a widget.
    It receives the query typed by the user, as well as the values of any settings in the widget,
    as currently selected by the user.
    """
    async def __call__(
        self, query: str, settings: dict[str, SettingValue | SettingAutoCompleteResult]
    ) -> list[SettingAutoCompleteResult]:
        """
        Args:
            query: The query typed by the user.
            settings: The values of any settings in the widget, as currently selected by the user.
        """
