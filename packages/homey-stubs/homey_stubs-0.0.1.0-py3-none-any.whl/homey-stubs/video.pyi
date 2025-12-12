from abc import ABC
from typing import Literal
from warnings import deprecated

type VideoStreamType = Literal["dash", "hls", "other", "rtsp", "rtmp", "webrtc"]
type Demuxer = Literal["h264", "h265", "mpegts", "ts"]

class Video(ABC):
    """
    Base class for video streams.
    """

    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling"
        " ManagerVideos.create_video_web_rtc, ManagerVideos.create_video_rtsp, ManagerVideos.create_video_rtmp,"
        " ManagerVideos.create_video_hls, ManagerVideos.create_video_dash, or ManagerVideos.create_video_other."
    )
    def __init__(self) -> None: ...
    async def unregister(self) -> None:
        """
        Unregister the video.
        """
