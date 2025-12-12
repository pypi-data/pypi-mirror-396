from typing import final
from warnings import deprecated

from .simple_class import SimpleClass
from .widget import SettingAutoCompleteListener

class WidgetSetting(SimpleClass):
    """
    A setting for a widget, as defined in `app.json`.
    """

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling Widget.get_setting."
    )
    def __init__(self) -> None: ...
    def register_autocomplete_listener(
        self, listener: SettingAutoCompleteListener
    ) -> None:
        """
        Register an autocomplete listener for this setting.

        Args:
            listener: An async listener for when an autocomplete value is requested for this setting.
                It receives the query typed by the user, as well as any settings in the widget, as currently selected by the user.

        Raises:
            AlreadyExists: Raised if a listener was already registered for this setting.
        """
