from collections.abc import Callable, Coroutine
from typing import Any, Self
from warnings import deprecated

from .video_with_url import VideoWithURL

class VideoWebRTC(VideoWithURL):
    """
    A video using a WebRTC stream.

    Example:
    ```python
    # In your device.py file
    async def on_init(self):
        await super().on_init()

        video = self.homey.videos.create_video_web_rtc()

        video.register_offer_listener(self.handle_web_rtc_offer)
        video.register_keep_alive_listener(self.refresh_stream)

        await self.set_camera_video('front_door', 'Front Door', video)
    ```
    """

    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling ManagerVideos.create_video_web_rtc."
    )
    def __init__(self) -> None: ...
    def register_offer_listener(
        self, listener: Callable[[str], Coroutine[Any, Any, str]]
    ) -> Self:
        """
        Register a listener for WebRTC offer events.
        This is invoked when Homey requests an SDP answer for a WebRTC offer.
        Args:
            listener: An async listener that receives an SDP string and returns an answer.
        """
    def register_keep_alive_listener(
        self, listener: Callable[[str], Coroutine[Any, Any, None]]
    ) -> Self:
        """
        Register a listener for WebRTC keep alive events.
        This is invoked when Homey sends keep alive signals for active WebRTC streams.
        Args:
            listener: An async listener that receives a stream ID.
        """
