"""Template exceptions module."""

from ... import api

__all__ = (
    'CustomExampleError',
    *api.events.exc.__all__
    )

from ... api . events . exc import *


class CustomExampleError(RequestError):
    """Cannot redefine a pet called `Bark`."""
