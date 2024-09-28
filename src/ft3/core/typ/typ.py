"""Typing types."""

__all__ = (
    'camelCase',
    'datetime',
    'numeric',
    'snake_case',
    'string',
    'AnyDict',
    'AnyField',
    'AnyOrForwardRef',
    'AnyOtherType',
    'AnyOtherTypeCo',
    'AnyString',
    'AnyType',
    'AnyTypeCo',
    'ArgsType',
    'Array',
    'ArrayType',
    'CamelDict',
    'Casing',
    'DataClassFields',
    'Enum',
    'ExceptionType',
    'FieldsTuple',
    'Immutable',
    'Literal',
    'Mapping',
    'MappingType',
    'NoneType',
    'NumberType',
    'Object',
    'ObjectType',
    'OptionalAnyDict',
    'OptionalGenericAlias',
    'PackageExceptionType',
    'PascalCase',
    'Primitive',
    'Serial',
    'SnakeDict',
    'StrOrForwardRef',
    'StringFormat',
    'StringType',
    'Typed',
    'UnionGenericAlias',
    'VariadicArray',
    'VariadicArrayType',
    )

from . import lib
from . import obj

from . obj import (
    string,
    AnyType,
    AnyOtherType,
    AnyTypeCo,
    AnyOtherTypeCo,
    ArgsType,
    StringType
    )

if lib.t.TYPE_CHECKING:  # pragma: no cover
    from ... import objects  # noqa: F401
    from .. import exc  # noqa: F401

AnyOrForwardRef = lib.t.ForwardRef | lib.t.Any
StrOrForwardRef = lib.t.ForwardRef | str
OptionalGenericAlias = type(lib.t.Optional[str])
UnionGenericAlias = type(int | str)
Wrapper = obj.SupportsParams[lib.Unpack[ArgsType]]

PascalCase = lib.t.NewType('PascalCase', str)
camelCase = lib.t.NewType('camelCase', str)
snake_case = lib.t.NewType('snake_case', str)
datetime = lib.t.NewType('datetime', str)
numeric = lib.t.NewType('numeric', str)

AnyDict: lib.t.TypeAlias = dict['AnyString', lib.t.Any]
AnyField: lib.t.TypeAlias = 'objects.Field[AnyType]'
AnyString = str | string[StringType]
Array = obj.ArrayProto[AnyType]
CamelDict: lib.t.TypeAlias = dict[string[camelCase], lib.t.Any]
Casing = camelCase | snake_case
DataClassFields: lib.t.TypeAlias = 'dict[string[snake_case], AnyField[lib.t.Any]]'  # noqa
Enum: lib.t.TypeAlias = (
    frozenset['Immutable']
    | list['Immutable']
    | set['Immutable']
    | tuple['Immutable', ...]
    | lib.enum.EnumMeta
    )
FieldsTuple: lib.t.TypeAlias = tuple[string[snake_case], ...]
Immutable: lib.t.TypeAlias = (
    bool
    | bytes
    | complex
    | lib.decimal.Decimal
    | lib.enum.Enum
    | float
    | lib.fractions.Fraction
    | int
    | lib.types.NoneType  # type: ignore[valid-type]
    | range
    | AnyString
    | lib.enum.EnumMeta
    | frozenset['Immutable']
    | tuple['Immutable', ...]
    | lib.types.MappingProxyType['Immutable', 'Immutable']
    )
Literal = lib.t.Literal['*']
Mapping = obj.MappingProto[AnyType, AnyOtherType]
NoneType = lib.types.NoneType  # type: ignore[valid-type]
Object: lib.t.TypeAlias = 'objects.Object'
OptionalAnyDict = lib.t.Optional[dict[AnyString, lib.t.Any]]
Primitive: lib.t.TypeAlias = bool | float | int | NoneType | AnyString  # type: ignore[valid-type]
Serial: lib.t.TypeAlias = Primitive | dict[Primitive, 'Serial'] | list['Serial']  # noqa
SnakeDict: lib.t.TypeAlias = dict[string[snake_case], lib.t.Any]
StringFormat: lib.t.TypeAlias = (
    camelCase | snake_case | PascalCase | datetime | numeric
    )
Typed = obj.SupportsAnnotations
VariadicArray = obj.VariadicArrayProto[lib.Unpack[tuple[AnyType, ...]]]

ArrayType = lib.t.TypeVar('ArrayType', bound=Array)
ExceptionType = lib.t.TypeVar('ExceptionType', bound=Exception)
MappingType = lib.t.TypeVar('MappingType', bound=Mapping)
NumberType = lib.t.TypeVar('NumberType', bound=lib.numbers.Number)
ObjectType = lib.t.TypeVar('ObjectType', bound=Object)
PackageExceptionType = lib.t.TypeVar(
    'PackageExceptionType',
    bound='exc.BasePackageException',
    covariant=True,
    )
VariadicArrayType = lib.t.TypeVar('VariadicArrayType', bound=VariadicArray)
