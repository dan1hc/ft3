"""Objects imports."""

from .. import core

__all__ = (
    'copy',
    'dataclass_transform',
    'inspect',
    *core.lib.__all__
    )

import copy
import inspect

from .. core . lib import *

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import dataclass_transform  # noqa  # type: ignore
else:  # pragma: no cover
    from typing import dataclass_transform
