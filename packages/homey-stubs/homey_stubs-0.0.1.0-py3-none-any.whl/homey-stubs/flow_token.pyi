from typing import TypeVar, final
from warnings import deprecated

from .image import Image

Value = TypeVar("Value", bound=str | float | bool | Image)

class FlowToken[Value]:
    """
    A token in the flow editor.
    """

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling ManagerFlows#create_token."
    )
    def __init__(self) -> None: ...
    def get_value(self) -> Value | None: ...
    async def set_value(self, value: Value | None) -> None:
        """
        Set the value of the token.
        """
    async def unregister(self) -> None:
        """
        Unregister this token.
        """
