from typing import final
from warnings import deprecated

from .flow_card import ArgumentAutoCompleteListener
from .simple_class import SimpleClass

class FlowArgument(SimpleClass):
    """
    An argument for a flow card as defined in the app's app.json.
    """

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling FlowCard.get_argument."
    )
    def __init__(self) -> None: ...
    def register_autocomplete_listener(
        self, listener: ArgumentAutoCompleteListener
    ) -> None:
        """
        Register an autocomplete listener for this argument.

        Args:
            listener: An async listener for when an autocomplete value is requested for this argument.
                It receives the query typed by the user, as well as any arguments in the flow card, as currently selected by the user, serialized as json.

        Raises:
            AlreadyExists: Raised if a listener was already registered for this argument.
        """
