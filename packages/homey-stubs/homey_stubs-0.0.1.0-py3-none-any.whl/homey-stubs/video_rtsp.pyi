from warnings import deprecated

from .video_with_url import VideoWithURL

class VideoRTSP(VideoWithURL):
    """
    A video using an RTSP stream.

    Example:
    ```python
    # In your device.py file
    async def on_init(self):
        await super().on_init()

        video = self.homey.videos.create_video_rtsp()

        async def video_callback():
            return f"rtsp://{self.get_setting('ip')}:554/stream"

        video.register_video_url_listener(video_callback)
        await self.set_camera_video('front_door', 'Front Door', video)
    ```
    """

    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling ManagerVideos.create_video_rtsp."
    )
    def __init__(self) -> None: ...
