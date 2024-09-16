"""Template enumerations."""

__all__ = (
    'PetLocation',
    'PetType',
    )

from . import lib


class PetLocation(lib.enum.Enum):
    """Valid Pet locations."""

    inside  = 'inside'
    outside = 'outside'
    timeout = 'timeout'


class PetType(lib.enum.Enum):
    """Valid Pet types."""

    cat = 'cat'
    dog = 'dog'
