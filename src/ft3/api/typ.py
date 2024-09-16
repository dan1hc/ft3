"""Api typing."""

from .. import core

__all__ = (
    'ApiFormat',
    'ApiMethod',
    'ApiResponseType',
    'ApiType',
    'ApiTypeValue',
    'ContentType',
    'HttpErrorCode',
    'HttpStatusCode',
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
    | lib.t.Literal['uuid']
    )
ApiMethod: lib.t.TypeAlias = (
    lib.t.Literal['delete']
    | lib.t.Literal['get']
    | lib.t.Literal['options']
    | lib.t.Literal['patch']
    | lib.t.Literal['post']
    | lib.t.Literal['put']
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
ApiResponseType: lib.t.TypeAlias = (
    lib.t.Literal['EMPTY']
    | lib.t.Literal['MANY']
    | lib.t.Literal['ONE']
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
ContentType: lib.t.TypeAlias = (
    lib.t.Literal['*/*']
    | lib.t.Literal['text/html']
    | lib.t.Literal['image/x-icon']
    | lib.t.Literal['application/json']
    | lib.t.Literal['image/png']
    | lib.t.Literal['text/plain']
    )
HttpErrorCode: lib.t.TypeAlias = (
    lib.t.Literal[400]
    | lib.t.Literal[401]
    | lib.t.Literal[403]
    | lib.t.Literal[404]
    | lib.t.Literal[405]
    | lib.t.Literal[423]
    | lib.t.Literal[429]
    | lib.t.Literal[500]
    | lib.t.Literal[501]
    )
HttpStatusCode: lib.t.TypeAlias = (
    lib.t.Literal[200]
    | lib.t.Literal[201]
    | lib.t.Literal[204]
    | lib.t.Literal[301]
    | HttpErrorCode
    )
