from typing import final

from ..widget import Widget
from . import Manager

@final
class ManagerDashboards(Manager):
    """
    Manages user dashboards.
    You can access this manager through the Homey instance as `self.homey.dashboards`.
    """

    def get_widget(self, id: str) -> Widget:
        """
        Get the widget with the given ID, as defined in `app.json`.


        Raises:
            NotFound:
        """
