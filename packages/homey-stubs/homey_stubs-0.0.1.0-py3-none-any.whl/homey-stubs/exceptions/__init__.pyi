class NotFound(Exception):
    """The resource could not be found."""

class AlreadyExists(Exception):
    """The given ID is already in use."""

class NotConnected(Exception):
    """The device is not connected."""
