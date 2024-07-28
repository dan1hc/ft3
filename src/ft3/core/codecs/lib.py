"""Codecs imports."""

from .. import lib

__all__ = (
    'collections',
    'ipaddress',
    'numbers',
    'pathlib',
    'uuid',
    *lib.__all__
    )

import collections.abc
import ipaddress
import numbers
import pathlib
import uuid

from .. lib import *
