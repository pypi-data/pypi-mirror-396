from typing import Any, Self, override

from .flow_card import FlowCard, RunListener

class FlowCardTrigger(FlowCard):
    """
    A flow card with type `trigger`, as defined in the app's `app.json`.
    """
    @override
    def register_run_listener(self, listener: RunListener[None]) -> Self: ...
    async def trigger(self, tokens: dict[str, Any], **trigger_kwargs) -> None:
        """
        Activate the flow card, and thereby any flows it is used in.

        Args:
            tokens: A mapping from tokens to their values in the flow, as defined in `app.json`.
            trigger_kwargs: Arguments that will be passed to the card's run listener.
        """
