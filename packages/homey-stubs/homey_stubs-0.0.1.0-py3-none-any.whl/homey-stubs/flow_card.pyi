from abc import ABC
from collections.abc import Callable
from types import MappingProxyType
from typing import (
    Any,
    Literal,
    LiteralString,
    Protocol,
    Required,
    Self,
    TypedDict,
    TypeVar,
    final,
)
from warnings import deprecated

from .flow_argument import FlowArgument
from .simple_class import SimpleClass

ChildEvent = TypeVar("ChildEvent", bound=LiteralString)

class FlowCard(SimpleClass[Literal["update"] | ChildEvent], ABC):
    """
    Base class for flow cards.
    """

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling"
        "ManagerFlows.get_action_card, ManagerFlows.get_condition_card, ManagerFlows.get_trigger_card, or ManagerFlows.get_device_trigger_card."
    )
    def __init__(self) -> None: ...
    def get_argument(self, name: str) -> FlowArgument:
        """
        Get the argument with the given name from this flow card.

        Raises:
            NotFound:
        """
    async def get_argument_values(self) -> tuple[MappingProxyType[str, Any], ...]:
        """
        Get the values of any arguments in instances of the flow card, as currently selected by the user.
        """
    def register_argument_autocomplete_listener(
        self, name: str, listener: ArgumentAutoCompleteListener
    ) -> Self:
        """
        Register an autocomplete listener for the argument with the given name.

        Args:
            listener: An async listener for when an autocomplete value is requested for the argument.
                It receives the query typed by the user, as well as any arguments in the flow card, as currently selected by the user, serialized as json.

        Returns:
            This flow card, for chained calls.

        Raises:
            AlreadyExists: Raised if a listener was already registered for the argument.
            NotFound: Raised if no argument with the given name is found.
        """
    def register_run_listener(self, listener: RunListener) -> Self:
        """
        Register a listener for when this flow card is activated.
        Raising an exception in the listener will make the flow fail with the exception's message.

        Args:
            listener: An async listener ran when the flow card is activated.
                It receives the arguments of the flow card, and arguments passed when triggering the flow card.

        Returns:
            This flow card, for chained calls.

        Raises:
            AlreadyExists: Raised if a listener was already registered for this flow card.
        """
    def on_update(self, f: Callable[[], None]) -> Self:
        """
        The `update` event is fired when the flow card is updated by the user, e.g. when a flow has been saved.

        Args:
            f: A callback that receives no arguments.
        """

class ArgumentAutoCompleteResult(TypedDict, total=False):
    name: Required[str]
    """The autocomplete value that will be shown to the user and used in the flow."""
    description: str
    """A short description of the result that will be shown below the name."""
    icon: str
    """A path to an `.svg` file to show as icon for the result."""
    image: str
    """A path to an image that is not an `.svg` file to show as icon for the result."""
    data: Any
    """Any additional data you wild like to pass to the flow run listener for this autocomplete value."""

class ArgumentAutoCompleteListener(Protocol):
    """
    A listener for when an autocomplete value is requested in a flow card.
    It receives the query typed by the user, as well as the values of any arguments in the flow card,
    as currently selected by the user, serialized as json.
    """
    async def __call__(
        self, query: str, **kwargs: str
    ) -> list[ArgumentAutoCompleteResult]:
        """
        Args:
            query: The query typed by the user.
            kwargs: The values of any arguments in the flow card, as currently selected by the user, serialized as json.
        """

class RunListener[RunListener](Protocol):
    """
    A listener ran when a flow card is activated.
    It receives the arguments of the flow card, and arguments passed when triggering the flow card.

    If an exception is raised, the flow will fail and the error message will be shown to the user.
    """
    async def __call__(
        self, card_arguments: dict[str, Any], **trigger_kwargs: Any
    ) -> RunListener:
        """
        Args:
            card_arguments: Arguments in the flow card, as currently selected by the user.
            trigger_kwargs: Arguments passed when triggering the flow card.
        """
