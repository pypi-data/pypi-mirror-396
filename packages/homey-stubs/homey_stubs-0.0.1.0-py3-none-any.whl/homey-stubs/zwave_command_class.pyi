from collections.abc import Callable
from typing import (
    Any,
    Literal,
    LiteralString,
    Self,
    TypedDict,
    TypeVar,
    final,
)
from warnings import deprecated

from .simple_class import SimpleClass

ChildEvent = TypeVar("ChildEvent", bound=LiteralString)

class ZWaveCommandClass(SimpleClass[Literal["report"] | ChildEvent]):
    """
    A Z-Wave Command Class for a ZWaveNode in Homey.
    At runtime this class is populated with static methods corresponding to the commands of the command class.

    Example:
        ```python
        from homey.device import Device
        from homey.zwave_node import ZWaveNode


        class MyDevice(Device):
            node: ZWaveNode

            async def on_init(self):
                self.node = await self.homey.zwave.get_node(self)
                command_class = self.node.command_classes["COMMAND_CLASS_BASIC"]
                if command_class is not None:
                    command_class.on("report", self.handle_report)
                    self.log("Device state:", await command_class.send_command("BASIC_GET"))

            def handle_report(self, command, report):
                self.log(command.name, "report:", report)


        homey_export = MyDevice
        ```
    """

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved from ZWaveNode.command_classes."
    )
    async def send_command(
        self, command: str, arguments: dict[str, Any] | None = None
    ) -> Any:
        """
        Send the given command with the given arguments.

        Returns:
            The response from the Z-Wave device.
        """

    def on_report(
        self,
        f: Callable[[Command, dict, int], None],
    ) -> Self:
        """
        This event is fired when a report has been received from this command class.

        Args:
            f: A callback that receives the command object, the report, and the ID of the node.
        """

class Command(TypedDict):
    name: str
    value: int
