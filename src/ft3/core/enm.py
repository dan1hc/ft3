"""Core enumerations."""

__all__ = (
    'Boolean',
    'NoneAlias',
    )

from . import lib


class Boolean(lib.enum.Enum):
    """Boolean Enumeration."""

    true  = True
    false = False


class NoneAlias(lib.enum.Enum):
    """Nones Enumeration."""

    null = None
    none = None
    nan  = None
