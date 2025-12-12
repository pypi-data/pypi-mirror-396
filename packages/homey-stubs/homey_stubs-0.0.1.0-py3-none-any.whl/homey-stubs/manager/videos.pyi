from typing import final

from ..video import Demuxer, Video
from ..video_dash import VideoDASH
from ..video_hls import VideoHLS
from ..video_other import VideoOther
from ..video_rtmp import VideoRTMP
from ..video_rtsp import VideoRTSP
from ..video_web_rtc import VideoWebRTC
from . import Manager

@final
class ManagerVideos(Manager):
    """
    Manages video streams used by the App.
    You can access this manager through the Homey instance as `self.homey.videos`.
    """

    def get_video(self, id: str) -> Video:
        """
        Get the video with the given ID.

        Raises:
            NotFound: Raised if no video with the given ID is found.
        """
    async def unregister_video(self, video: Video):
        """
        Unregisters the given video.
        """
    async def create_video_web_rtc(self, data_channel=True) -> VideoWebRTC:
        """
        Create a WebRTC video instance for video streaming.
        The video must be associated with a device using `Device.set_camera_video` to enable streaming functionality.

        Args:
            data_channel: Whether the frontend should set up a WebRTC data channel for bidirectional communication.
                Some video streams don't work with a data channel and some don't work without it.
        """
    async def create_video_rtsp(
        self, allow_invalid_certificates=False, demuxer: Demuxer | None = None
    ) -> VideoRTSP:
        """
        Create an RTSP video instance for video streaming.
        The video must be associated with a device using `Device.set_camera_video` to enable streaming functionality.
        """
    async def create_video_rtmp(
        self, allow_invalid_certificates=False, demuxer: Demuxer | None = None
    ) -> VideoRTMP:
        """
        Create an RTMP video instance for video streaming.
        The video must be associated with a device using `Device.set_camera_video` to enable streaming functionality.
        """
    async def create_video_hls(
        self, allow_invalid_certificates=False, demuxer: Demuxer | None = None
    ) -> VideoHLS:
        """
        Create a HLS video instance for video streaming.
        The video must be associated with a device using `Device.set_camera_video` to enable streaming functionality.
        """
    async def create_video_dash(
        self, allow_invalid_certificates=False, demuxer: Demuxer | None = None
    ) -> VideoDASH:
        """
        Create a DASH video instance for video streaming.
        The video must be associated with a device using `Device.set_camera_video` to enable streaming functionality.
        """
    async def create_video_other(
        self, allow_invalid_certificates=False, demuxer: Demuxer | None = None
    ) -> VideoOther:
        """
        Create a video instance for video streaming.
        This video can contain any VLC-supported URL, and the front-end will try to play it.
        The video must be associated with a device using `Device.set_camera_video` to enable streaming functionality.
        """
