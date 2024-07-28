"""Objects enumerations."""

from .. import core

__all__ = (
    'MatchThreshold',
    'SortDirection',
    *core.enm.__all__,
    )

from .. core . enm import *

from . import lib


class MatchThreshold(lib.enum.Enum):
    """Minimum Query Similarity Enumeration."""

    default = 0.85


class SortDirection(lib.enum.Enum):
    """Sort Direction Enumeration."""

    asc  = 'asc'
    desc = 'desc'
