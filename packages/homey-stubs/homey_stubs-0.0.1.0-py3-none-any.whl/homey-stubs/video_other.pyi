from warnings import deprecated

from .video_with_url import VideoWithURL

class VideoOther(VideoWithURL):
    """
    A video using a VLC supported URL.

    Example:
    ```python
    # In your device.py file
    async def on_init(self):
        await super().on_init()

        video = self.homey.videos.create_video_other()

        async def video_callback():
            return f"https://{self.get_setting('ip')}/stream.mp4"

        video.register_video_url_listener(video_callback)
        await self.set_camera_video('front_door', 'Front Door', video)
    ```
    """

    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling ManagerVideos#create_video_other."
    )
    def __init__(self) -> None: ...
