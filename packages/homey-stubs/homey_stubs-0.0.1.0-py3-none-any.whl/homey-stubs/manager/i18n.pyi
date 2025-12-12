from typing import Literal, final

from . import Manager

type Translations = dict[str, str | Translations]

@final
class ManagerI18n(Manager):
    """
    Manages [internationalization](https://apps.developer.homey.app/the-basics/app/internationalization) in the app.
    You can access this manager through the Homey instance as `self.homey.i18n`.
    """
    def get_strings(self) -> Translations:
        """Get the locale file for the language the Homey uses."""
    def translate(self, key: str, tags: dict[str, str] | None = None) -> str | None:
        """
        Translate a string, as defined in the app's `/locales/<language>.json` file.

        Example:

        /locales/en.json
        ```json
        { "welcome": "Welcome, __name__!" }
        ```

        /app.py
        ```python
        welcome_message = self.homey.translate("welcome", { "name": "Dave" })
        self.log(welcome_message)
        ```

        Args:
            key: The key in the `<language.json>` file, with dots separating nesting. For example `"errors.missing"`.
            tags: A mapping of tags in the string to replace. For example, for `Hello, __name__!` you could pass `{"name":"Dave"}`.

        Returns:
            The translated string, or None if the key was not found.
        """

    def get_language(self) -> str:
        """
        Get the language the Homey uses.

        Returns:
            A 2-character language code.
        """
    def get_units(self) -> Literal["metric", "imperial"]:
        """
        Get the units the Homey uses.
        """
