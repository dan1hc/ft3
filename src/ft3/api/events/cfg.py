"""Api events constants."""

__all__ = (
    'Constants',
    )

from .. import cfg


class Constants(cfg.Constants):
    """Constant values specific to api events modules."""

    PATH_ID = '[a-zA-Z0-9]{1,256}'
