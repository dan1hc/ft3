"""Constant values specific to module unit tests."""

__all__ = (
    'Constants',
    )

from ft3 . core import strings

from .. import cfg


class Constants(cfg.Constants, strings.cfg.Constants):
    """Constant values specific to unit tests in this module."""

    INVALID_STRING_CASING_EXAMPLE = 'WRONG_cASasdfING9000man'
