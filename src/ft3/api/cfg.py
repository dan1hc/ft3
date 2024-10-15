"""Api constants."""

__all__ = (
    'Constants',
    )

from .. import core


class Constants(core.cfg.Constants):
    """Constant values specific to Api modules."""

    DEFAULT_VERSION = 'v1'
    VERSION = '3.1.0'
    API_PATH = '/'
    DEFAULT_PORT = 80
    METHODS = (
        'delete',
        'get',
        'options',
        'patch',
        'post',
        'put',
        )
    SKIP_FIELDS = (
        'default',
        'required',
        )
