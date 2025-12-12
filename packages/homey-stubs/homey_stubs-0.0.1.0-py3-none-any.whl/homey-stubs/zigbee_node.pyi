from typing import Final, final
from warnings import deprecated

from .simple_class import SimpleClass

class ZigbeeNode(SimpleClass):
    """
    A Zigbee device in Homey.
    """

    ieee_address: Final[str]
    manufacturer_name: Final[str]
    product_id: Final[str]

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling ManagerZigbee.get_node."
    )
    def __init__(self) -> None: ...
    async def handle_frame(
        self, endpoint_id: int, cluster_id: int, frame: bytes, meta: dict
    ) -> None:
        """
        This method is called when a frame is received from this Zigbee node.
        It must be overridden.
        """
    async def send_frame(self, endpoint_id: int, cluster_id: int, frame: bytes) -> None:
        """
        Send the frame to the given cluster on the given endpoint.
        """
