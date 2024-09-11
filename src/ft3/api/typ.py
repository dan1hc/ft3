"""Api typing."""

from .. import core

__all__ = (
    'ApiFormat',
    'ApiType',
    'ApiTypeValue',
    *core.typ.__all__
    )

from .. core . typ import *

from . import lib

ApiFormat: lib.t.TypeAlias = (
    lib.t.Literal['boolean']
    | lib.t.Literal['byte']
    | lib.t.Literal['date']
    | lib.t.Literal['datetime']
    | lib.t.Literal['double']
    | lib.t.Literal['float']
    | lib.t.Literal['int32']
    )
ApiType: lib.t.TypeAlias = (
    lib.t.Literal['array']
    | lib.t.Literal['boolean']
    | lib.t.Literal['integer']
    | lib.t.Literal['null']
    | lib.t.Literal['number']
    | lib.t.Literal['object']
    | lib.t.Literal['string']
    )
ApiTypeValue: lib.t.TypeAlias = (
    list['ApiTypeValue']
    | bool
    | int
    | NoneType  # type: ignore[valid-type]
    | float
    | dict[str, 'ApiTypeValue']
    | str
    )
