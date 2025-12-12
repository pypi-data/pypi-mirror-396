from typing import Any, Literal, final, overload

from ..flow_card_action import FlowCardAction
from ..flow_card_condition import FlowCardCondition
from ..flow_card_trigger import FlowCardTrigger
from ..flow_card_trigger_device import FlowCardTriggerDevice
from ..flow_token import FlowToken
from ..image import Image
from . import Manager

@final
class ManagerFlow(Manager):
    """
    Manages flows in this app.
    You can access this manager through the Homey instance as `self.homey.flow`.
    """
    def get_action_card(self, id: str) -> FlowCardAction:
        """
        Get the action flow card with the given ID, as defined in app.json.
        """
    def get_condition_card(self, id: str) -> FlowCardCondition:
        """
        Get the condition flow card with the given ID, as defined in app.json.
        """
    def get_trigger_card(self, id: str) -> FlowCardTrigger:
        """
        Get the trigger flow card with the given ID, as defined in app.json.
        """
    def get_device_trigger_card(self, id: str) -> FlowCardTriggerDevice:
        """
        Get the device trigger flow card with the given ID, as defined in app.json.
        """

    @overload
    async def create_token(
        self,
        id: str,
        type: Literal["string"],
        title: str,
        value: Any | None = None,
    ) -> FlowToken[str]:
        """
        Create a flow token, which can be used to create a tag in the flow editor.
        """
    @overload
    async def create_token(
        self,
        id: str,
        type: Literal["number"],
        title: str,
        value: Any | None = None,
    ) -> FlowToken[float]:
        """
        Create a flow token, which can be used to create a tag in the flow editor.
        """
    @overload
    async def create_token(
        self,
        id: str,
        type: Literal["boolean"],
        title: str,
        value: Any | None = None,
    ) -> FlowToken[bool]:
        """
        Create a flow token, which can be used to create a tag in the flow editor.
        """
    @overload
    async def create_token(
        self,
        id: str,
        type: Literal["image"],
        title: str,
        value: Any | None = None,
    ) -> FlowToken[Image]:
        """
        Create a flow token, which can be used to create a tag in the flow editor.
        """
    def get_token(self, id: str) -> FlowToken:
        """
        Get the token with the given ID, as set in `create_token`.
        """
    async def unregister_token(self, token: FlowToken) -> None:
        """
        Unregister the given token.
        """
