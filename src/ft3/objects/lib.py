"""Objects imports."""

from .. import core

__all__ = (
	'ast',
	'copy',
	'dataclass_transform',
	'inspect',
	'numbers',
	*core.lib.__all__,
)

import ast
import copy
import inspect
import numbers

from ..core.lib import *

from typing import dataclass_transform
