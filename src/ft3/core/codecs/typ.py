"""Codecs types."""

from .. import typ

__all__ = (
    'ErrorRef',
    *typ.__all__
    )

from .. typ import *

from . import lib

ErrorRef = lib.t.NewType('ErrorRef', str)
