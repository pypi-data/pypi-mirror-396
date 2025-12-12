from typing import Self, override

from .flow_card import FlowCard, RunListener

class FlowCardCondition(FlowCard):
    """
    A flow card with type `condition`, as defined in the app's `app.json`.
    """
    @override
    def register_run_listener(self, listener: RunListener[bool]) -> Self:
        """
        Register a listener for when this flow card is activated.
        Raising an exception in the listener will make the flow fail with the exception's message.

        Args:
            listener: An async listener ran when the flow card is activated, which returns whether the condition is met.
                It receives the arguments of the flow card, and arguments passed when triggering the flow card.

        Returns:
            This flow card, for chained calls.

        Raises:
            AlreadyExists: Raised if a listener was already registered for this flow card.
        """
