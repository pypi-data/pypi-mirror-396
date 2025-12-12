from asyncio import Future
from collections.abc import Callable, Coroutine
from io import BytesIO
from typing import Any, NotRequired, TypedDict, final
from warnings import deprecated

class Image:
    """
    An image, which can be used as token values in the flow editor, device album art, or camera images.
    An image must be registered, and the contents will be retrieved when needed.
    """

    @final
    @deprecated(
        "This class must not be initialized by the developer, but retrieved by calling ManagerImages.create_image."
    )
    def __init__(self) -> None: ...
    async def get_stream(self) -> StreamReturn:
        """
        Get a stream containing the image data.
        """
    async def pipe(self, stream: Writable) -> ImageStreamMetadata:
        """
        Pipe the image data into the stream.

        Returns:
            The metadata of the image file.
        """
    def set_path(self, path: str) -> None:
        """
        Set the image file path.
        Args:
            path: A relative path to the image, e.g. `/userdata/kitten.jpg`
        """
    def set_stream(
        self, source: Callable[[BytesIO], Coroutine[Any, Any, None]]
    ) -> None:
        """
        Set a function that writes the image data to streams if requested.
        This is mostly useful for external image sources.
        """
    def set_url(self, url: str) -> None:
        """
        Set the image file URL.
        This URL must be publicly accessible.

        Args:
            url: An absolute URL of the image file, starting with `https://`
        """
    async def unregister(self) -> None:
        """
        Unregister the image.
        """
    async def update(self) -> None:
        """
        Notify users that the image contents have been updated.
        """

class ImageStreamMetadata(TypedDict):
    filename: str
    """The filename of the image file."""
    content_type: str
    """The MIME type of the image file."""
    content_length: NotRequired[int]
    """The size of the image file in bytes."""

class Writable:
    buffer: BytesIO
    done: Future
    def __init__(self, buffer: BytesIO): ...

class StreamReturn(TypedDict):
    data: Writable
    meta: ImageStreamMetadata
