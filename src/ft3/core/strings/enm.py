"""Strings enumerations."""

from .. import enm

__all__ = (
    'SupportedCasing',
    *enm.__all__
    )

from .. enm import *

from . import lib
from . import typ


class SupportedCasing(lib.enum.Enum):
    """Valid string casings."""

    camelCase  = typ.camelCase
    snake_case = typ.snake_case
