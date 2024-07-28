"""Strings constants."""

__all__ = (
    'Constants',
    )

from .. import cfg

from . import lib


class Constants(cfg.Constants):
    """Constant values shared across core strings modules."""

    MAX_CHARS = int(lib.os.getenv('MAX_CHARS', 384))
    """
    Default, package-wide maximum string length [before it is wrapped \
    into a multi-line string].

    ---

    Used for `__repr__`, log messages, etc.

    """

    CUTOFF_LEN = int(lib.os.getenv('CUTOFF_LEN', 12))
    """
    Default, package-wide maximum multi-line string line count [before \
    `list[str]` is trimmed and an ellipsis (...) is appended as its \
    final item].

    ---

    Used for `__repr__`, log messages, etc.

    """

    WRAP_WIDTH = int(lib.os.getenv('WRAP_WIDTH', 64))
    """
    Default, package-wide maximum multi-line string line count [before \
    `list[str]` is trimmed and an ellipsis (...) is appended as its \
    final item].

    ---

    Used for `__repr__`, log messages, etc.

    """

    M_LINE_TOKEN = '[[MULTI_LINE_STRING_AS_ARRAY]]'
    """
    Token pre-pended to a wrapped, multi-line string to indicate that \
    the value was originally a string.

    """
