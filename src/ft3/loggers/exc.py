"""Loggers exceptions module."""

from .. import core

__all__ = (
    'InvalidLogMessageTypeError',
    *core.exc.__all__
    )

from .. core . exc import *

from . import cfg
from . import lib


class Constants(cfg.Constants):
    """Constant values specific to this file."""


class InvalidLogMessageTypeError(BasePackageException[lib.t.Any]):
    """
    Error raised when a log message of invalid data type is passed.

    """

    def __init__(self, message: lib.t.Any):
        super().__init__(
            ' '.join(
                (
                    'To avoid accidental log pollution,'
                    'ft3 can only log: `dict, list, str, Object` types.',
                    f"The following message of type: '{type(message)!s}'",
                    f'was passed.\nmessage: {message!s}'
                    )
                ),
            message
            )
