from typing import final

from ..image import Image
from . import Manager

@final
class ManagerImages(Manager):
    """
    Manages images used by the app.
    You can access this manager through the Homey instance as `self.homey.images`.
    """
    async def create_image(self) -> Image:
        """
        Create an image instance.
        """
    def get_image(self, id: str) -> Image:
        """
        Get the image with the given ID.


        Raises:
            NotFound: Raised if no image with the given ID is found.
        """
    async def unregister_image(self, image: Image) -> None:
        """
        Unregister the given image.
        """
