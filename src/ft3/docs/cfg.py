"""Docs constants."""

__all__ = (
    'Constants',
    )

from .. import core

from . import lib


class Constants(core.cfg.Constants):
    """Constant values specific to docs modules."""

    BASE_VERSION    = '0.0.0'
    DOCS_STATIC_DIR = lib.os.path.join(
        lib.os.path.split(lib.os.path.dirname(__file__))[0],
        'docs',
        'static',
        )

    try:
        DEFAULT_USER = lib.os.getlogin()
    except OSError:  # pragma: no cover
        DEFAULT_USER = '<UNSPECIFIED>'
