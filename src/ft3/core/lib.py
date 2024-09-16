"""Core imports."""

__all__ = (
    'argparse',
    'dataclasses',
    'datetime',
    'decimal',
    'enum',
    'functools',
    'itertools',
    'json',
    'os',
    're',
    'sys',
    't',
    'textwrap',
    'types',
    'urllib',
    'uuid',
    'LiteralString',
    'Never',
    'Self',
    'TypeVarTuple',
    'Unpack',
    )

import argparse
import dataclasses
import datetime
import decimal
import enum
import functools
import itertools
import json
import os
import re
import sys
import typing as t
import textwrap
import types
import urllib.parse
import uuid

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import (  # noqa  # type: ignore
        LiteralString,
        Never,
        Self,
        TypeVarTuple,
        Unpack
        )
else:  # pragma: no cover
    from typing import (
        LiteralString,
        Never,
        Self,
        TypeVarTuple,
        Unpack
        )
