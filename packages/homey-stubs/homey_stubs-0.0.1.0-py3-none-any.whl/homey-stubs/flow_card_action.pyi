from typing import Self, override

from .flow_card import FlowCard, RunListener

class FlowCardAction(FlowCard):
    """
    A flow card with type `action`, as defined in the app's `app.json`.
    """
    @override
    def register_run_listener(self, listener: RunListener[None]) -> Self: ...
