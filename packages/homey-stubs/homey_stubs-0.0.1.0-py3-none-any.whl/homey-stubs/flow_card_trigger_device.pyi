from typing import Any, Self, override

from .device import Device
from .flow_card import FlowCard, RunListener

class FlowCardTriggerDevice(FlowCard):
    """
    A flow card with type trigger and an argument with type `device` with a filter with `driver_id`, as defined in an app's `app.json`.
    """
    @override
    def register_run_listener(self, listener: RunListener[None]) -> Self: ...
    async def trigger(
        self, tokens: dict[str, Any], device: Device, **trigger_kwargs
    ) -> None:
        """
        Activate the flow card, and thereby any flows it is used in.

        Args:
            tokens: A mapping from tokens to their values in the flow, as defined in `app.json`.
            device: The device to trigger the flow card for.
            trigger_kwargs: Arguments that will be passed to the card's run listener.
        """
