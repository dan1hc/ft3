"""Static files for docs gen."""

__all__ = (
    'config_template',
    )

from .. import lib

ROOT = lib.os.path.dirname(__file__)

with open(lib.os.path.join(ROOT, 'conf.tpl'), 'r') as f:
    config_template = f.read()
