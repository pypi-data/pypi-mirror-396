from warnings import deprecated

from .video_with_url import VideoWithURL

class VideoRTMP(VideoWithURL):
    """
    A video using an RTMP stream.

    Example:
    ```python
    # In your device.py file
    async def on_init(self):
        await super().on_init()

        video = self.homey.videos.create_video_rtmp()

        async def video_callback():
            return f"rtmp://{self.get_setting('ip')}:1935/stream"

        video.register_video_url_listener(video_callback)
        await self.set_camera_video('front_door', 'Front Door', video)
    ```
    """

    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling ManagerVideos.create_video_rtmp."
    )
    def __init__(self) -> None: ...
