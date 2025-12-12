from abc import ABC
from collections.abc import Callable, Coroutine
from typing import Any, Self
from warnings import deprecated

from .video import Video

class VideoWithURL(Video, ABC):
    """
    A base class for various video streaming protocols, such as RTSP, RTMP, HLS, and DASH.
    """

    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling ManagerVideos.create_video_rtsp,"
        "ManagerVideos.create_video_rtmp, ManagerVideos.create_video_hls, ManagerVideos.create_video_dash,"
        "or ManagerVideos.create_video_other."
    )
    def __init__(self) -> None: ...
    def register_video_url_listener(
        self, listener: Callable[[], Coroutine[Any, Any, str]]
    ) -> Self:
        """
        Register a listener for video URL requests.
        This is invoked when Homey requests the video stream URL.
        Args:
            listener: An async listener that returns the video URL.
        """
