"""Static files for docs gen."""

__all__ = (
    'config_template',
    )

import os

_root = __file__.removesuffix('__init__.py')

with open(os.path.join(_root, 'conf.tpl'), 'r') as f:
    config_template = f.read()
