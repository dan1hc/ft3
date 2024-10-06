"""Typing objects."""

__all__ = (
    'string',
    'ArrayProto',
    'FieldPattern',
    'ForwardPattern',
    'MappingProto',
    'MetaLike',
    'ObjectLike',
    'SupportsAnnotations',
    'SupportsParams',
    'VariadicArrayProto',
    'WrapperPattern',
    )

from . import cfg
from . import lib

if lib.t.TYPE_CHECKING:  # pragma: no cover
    from ... import api
    from . import typ  # noqa: F401


class Constants(cfg.Constants):
    """Constant values specific to this file."""


# Note: these need to be here to avoid circular import.
# They are however imported by adjacent typ and injected
# to typ's __all__ for consistency.
AnyType = lib.t.TypeVar('AnyType')
AnyOtherType = lib.t.TypeVar('AnyOtherType')
AnyTypeCo = lib.t.TypeVar('AnyTypeCo', covariant=True)
AnyOtherTypeCo = lib.t.TypeVar('AnyOtherTypeCo', covariant=True)
ArgsType = lib.TypeVarTuple('ArgsType')
StringType = lib.t.TypeVar('StringType', bound='typ.StringFormat')


class ArrayProto(lib.t.Protocol, lib.t.Collection[AnyTypeCo]):
    """Protocol for a generic, single-parameter array."""

    def __init__(
        self,
        iterable: lib.t.Iterable[AnyTypeCo],
        /
        ) -> None: ...

    def __iter__(self) -> lib.t.Iterator[AnyTypeCo]: ...


class VariadicArrayProto(
    ArrayProto[tuple[lib.Unpack[ArgsType]]],
    lib.t.Protocol
    ):
    """Protocol for a generic, any-parameter array."""

    def __hash__(self) -> int: ...


class MappingProto(
    lib.t.Protocol,
    lib.t.Generic[AnyTypeCo, AnyOtherTypeCo]
    ):
    """Protocol for a generic, double-parameter mapping."""

    def __init__(self, *args: lib.t.Any, **kwargs: lib.t.Any) -> None: ...

    def __iter__(self) -> lib.t.Iterator[AnyTypeCo]: ...

    def __getitem__(
        self,
        __name: str,
        __default: lib.t.Optional[AnyType] = None
        ) -> AnyTypeCo | AnyType: ...

    def items(self) -> lib.t.ItemsView[AnyTypeCo, AnyOtherTypeCo]: ...

    def keys(self) -> lib.t.KeysView[AnyTypeCo]: ...

    def values(self) -> lib.t.ValuesView[AnyOtherTypeCo]: ...


class SupportsAnnotations(lib.t.Protocol):
    """
    Protocol for a typed object.

    ---

    Typed objects include `dataclass`, `TypedDict`, `pydantic.Model`, \
    and both `ft3.Field` and `ft3.Object` amongst others.

    """

    __annotations__: dict[str, lib.t.Any]
    __bases__: tuple[type, ...]

    def __init__(self, *args: lib.t.Any, **kwargs: lib.t.Any) -> None: ...


class SupportsParams(lib.t.Protocol, lib.t.Generic[lib.Unpack[ArgsType]]):
    """Protocol for a generic with any number of parameters."""

    if lib.sys.version_info >= (3, 9):
        def __class_getitem__(
            cls,
            item: tuple[lib.Unpack[ArgsType]],
            /
            ) -> lib.types.GenericAlias: ...

    __args__: tuple[lib.Unpack[ArgsType]]

    def __hash__(self) -> int: ...


class MetaLike(lib.t.Protocol):
    """Meta protocol."""

    __annotations__: 'typ.SnakeDict'
    __dataclass_fields__: 'lib.t.ClassVar[typ.DataClassFields]'


class ObjectLike(lib.t.Protocol):
    """Object protocol."""

    __annotations__: 'typ.SnakeDict'
    __bases__: tuple[type, ...]
    __dataclass_fields__: 'lib.t.ClassVar[typ.DataClassFields]'
    __operations__: lib.t.ClassVar[
        dict[
            'typ.string[typ.snake_case]',
            lib.t.Callable[
                ['api.events.obj.Request', ],
                lib.t.Optional['typ.Object']
                | lib.t.Optional[list['typ.Object']]
                | str
                ]
            ]
        ]

    def __contains__(self, __key: lib.t.Any, /) -> bool: ...

    def __getitem__(self, __key: lib.t.Any, /) -> lib.t.Any: ...

    def __setitem__(
        self,
        __key: str,
        __value: lib.t.Any
        ) -> lib.t.Optional[lib.Never]: ...

    def __ior__(self, other: 'ObjectLike', /) -> lib.Self: ...

    def get(
        self,
        __key: 'typ.AnyString',
        __default: AnyType = None
        ) -> lib.t.Any | AnyType: ...

    def items(
        self
        ) -> 'lib.t.ItemsView[typ.string[typ.snake_case], lib.t.Any]': ...

    @classmethod
    def keys(cls) -> 'lib.t.KeysView[typ.string[typ.snake_case]]': ...

    def pop(
        self,
        __key: str,
        /,
        __default: AnyType = Constants.UNDEFINED
        ) -> AnyType | lib.t.Any | lib.Never: ...

    def setdefault(
        self,
        __key: str,
        __value: lib.t.Any
        ) -> lib.t.Optional[lib.Never]: ...

    def update(self, other: 'ObjectLike', /) -> None: ...

    def values(self) -> lib.t.ValuesView[lib.t.Any]: ...

    @lib.t.overload
    def to_dict(
        self,
        camel_case: lib.t.Literal[False] = False,
        include_null: bool = True
        ) -> 'typ.SnakeDict': ...
    @lib.t.overload
    def to_dict(
        self,
        camel_case: lib.t.Literal[True],
        include_null: bool
        ) -> 'typ.CamelDict': ...
    @lib.t.overload
    def to_dict(
        self,
        camel_case: bool,
        include_null: bool
        ) -> 'typ.SnakeDict | typ.CamelDict': ...
    def to_dict(
        self,
        camel_case: bool = False,
        include_null: bool = True
        ) -> 'typ.SnakeDict | typ.CamelDict': ...


FieldPattern = lib.re.compile(
    r'(ft3(\.[a-zA-Z]{1,32}){0,32}\.)?Field'
    r'\[((\[)?[\.\|\,a-zA-Z0-9_ ]{1,64}(\])?){1,64}\]'
    )

ForwardPattern = lib.re.compile(r'ForwardRef|\(|\)|\'|\"|~')

WrapperPattern = lib.re.compile(
    r'([a-zA-Z]{1,64}\.?)?(Annotated|ClassVar|Final|InitVar)'
    r'\[((\[)?[\.\|\,a-zA-Z0-9_ ]{1,64}(\])?){1,64}\]'
    )


class string(str, lib.t.Generic[StringType]):  # pragma: no cover
    """Generic `str` protocol."""

    @lib.t.overload
    def __new__(cls, object: object = ...) -> lib.Self: ...
    @lib.t.overload
    def __new__(
        cls,
        object: 'lib.builtins.ReadableBuffer',  # type: ignore[name-defined]
        encoding: str = ...,
        errors: str = ...
        ) -> lib.Self: ...
    def __new__(
        cls,
        object: object = ...,
        encoding: str = ...,
        errors: str = ...
        ) -> lib.Self:
        return super().__new__(cls, object)
    @lib.t.overload
    def capitalize(self: lib.LiteralString) -> lib.LiteralString: ...
    @lib.t.overload
    def capitalize(self) -> 'string[StringType] | string[lib.t.Any]': ...  # type: ignore[misc]
    def capitalize(
        self
        ) -> 'string[StringType] | string[lib.t.Any] | lib.LiteralString':
        return super().capitalize()
    @lib.t.overload
    def casefold(self: lib.LiteralString) -> lib.LiteralString: ...
    @lib.t.overload
    def casefold(self) -> 'string[StringType] | string[lib.t.Any]': ...  # type: ignore[misc]
    def casefold(
        self
        ) -> 'string[StringType] | string[lib.t.Any] | lib.LiteralString':
        return super().casefold()
    @lib.t.overload
    def center(
        self: lib.LiteralString,
        width: lib.t.SupportsIndex,
        fillchar: lib.LiteralString = " ",
        /
        ) -> lib.LiteralString: ...
    @lib.t.overload
    def center(  # type: ignore[misc]
        self,
        width: lib.t.SupportsIndex,
        fillchar: str = " ",
        /
        ) -> 'string[StringType] | string[lib.t.Any]': ...
    def center(  # type: ignore[misc]
        self,
        width: lib.t.SupportsIndex,
        fillchar: lib.LiteralString | str = " ",
        /
        ) -> 'string[StringType] | string[lib.t.Any] | lib.LiteralString':
        return super().center(width, fillchar)
    @lib.t.overload
    def expandtabs(
        self: lib.LiteralString,
        tabsize: lib.t.SupportsIndex = 8
        ) -> lib.LiteralString: ...
    @lib.t.overload
    def expandtabs(  # type: ignore[misc]
        self,
        tabsize: lib.t.SupportsIndex = 8
        ) -> 'string[StringType] | string[lib.t.Any]': ...
    def expandtabs(
        self,
        tabsize: lib.t.SupportsIndex = 8
        ) -> 'string[StringType] | string[lib.t.Any] | lib.LiteralString':
        return super().expandtabs(tabsize)
    def format(
        self,
        *args: object,
        **kwargs: object
        ) -> 'string[StringType] | string[lib.t.Any]':
        formatted: 'string[StringType] | string[lib.t.Any]' = (
            super().format(*args, **kwargs)
            )
        return formatted
    def format_map(
        self,
        mapping: 'lib.builtins._FormatMapMapping',
        /
        ) -> 'string[StringType] | string[lib.t.Any]':
        formatted: 'string[StringType] | string[lib.t.Any]' = (
            super().format_map(mapping)
            )
        return formatted
    @lib.t.overload  # type: ignore[no-overload-impl]
    def join(
        self: lib.LiteralString,
        iterable: lib.t.Iterable[lib.LiteralString],
        /
        ) -> lib.LiteralString: ...
    @lib.t.overload
    def join(  # type: ignore[misc]
        self,
        iterable: 'lib.t.Iterable[string[StringType]]',
        /
        ) -> 'string[StringType]': ...
    @lib.t.overload
    def join(  # type: ignore[misc]
        self,
        iterable: str,
        /
        ) -> 'string[lib.t.Any]': ...
    def join(
        self,
        iterable: lib.t.Union[
            lib.t.Iterable[lib.LiteralString],
            'lib.t.Iterable[string[StringType]]',
            str
            ],
        /
        ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
        return super().join(iterable)
    @lib.t.overload
    def ljust(
        self: lib.LiteralString,
        width: lib.t.SupportsIndex,
        fillchar: lib.LiteralString = " ",
        /
        ) -> lib.LiteralString: ...
    @lib.t.overload
    def ljust(  # type: ignore[misc]
        self,
        width: lib.t.SupportsIndex,
        fillchar: str = " ",
        /
        ) -> 'string[StringType] | string[lib.t.Any]': ...
    def ljust(
        self,
        width: lib.t.SupportsIndex,
        fillchar: lib.LiteralString | str = " ",
        /
        ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
        return super().ljust(width, fillchar)
    @lib.t.overload
    def lower(self: lib.LiteralString) -> lib.LiteralString: ...
    @lib.t.overload
    def lower(self) -> 'string[StringType] | string[lib.t.Any]': ...  # type: ignore[misc]
    def lower(
        self
        ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
        return super().lower()
    @lib.t.overload
    def lstrip(
        self: lib.LiteralString,
        chars: lib.LiteralString | None = None,
        /
        ) -> lib.LiteralString: ...
    @lib.t.overload
    def lstrip(  # type: ignore[misc]
        self,
        chars: str | None = None,
        /
        ) -> 'string[StringType] | string[lib.t.Any]': ...
    def lstrip(
        self,
        chars: lib.LiteralString | str | None = None,
        /
        ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
        return super().lstrip(chars)
    @lib.t.overload
    def partition(
        self: lib.LiteralString,
        sep: lib.LiteralString,
        /
        ) -> tuple[
            lib.LiteralString,
            lib.LiteralString,
            lib.LiteralString
            ]: ...
    @lib.t.overload
    def partition(self, sep: str, /) -> tuple[  # type: ignore[misc]
        'string[StringType] | string[lib.t.Any]', 
        'string[StringType] | string[lib.t.Any]', 
        'string[StringType] | string[lib.t.Any]'
        ]: ...
    def partition(
        self,
        sep: lib.LiteralString | str,
        /
        ) -> (
            tuple[
                lib.LiteralString,
                lib.LiteralString,
                lib.LiteralString
                ]
            | tuple[
                'string[StringType] | string[lib.t.Any]', 
                'string[StringType] | string[lib.t.Any]', 
                'string[StringType] | string[lib.t.Any]'
                ]
            ):
        return super().partition(sep)
    if lib.sys.version_info >= (3, 13):  # pragma: no cover
        @lib.t.overload
        def replace(
            self: lib.LiteralString,
            old: lib.LiteralString,
            new: lib.LiteralString,
            /,
            count: lib.t.SupportsIndex = -1
        ) -> lib.LiteralString: ...
        @lib.t.overload
        def replace(  # type: ignore[misc]
            self,
            old: str,
            new: str,
            /,
            count: lib.t.SupportsIndex = -1
            ) -> 'string[StringType] | string[lib.t.Any]': ...
        def replace(
            self,
            old: lib.LiteralString | str,
            new: lib.LiteralString | str,
            /,
            count: lib.t.SupportsIndex = -1
            ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
            return super().replace(old, new, count)
    else:  # pragma: no cover
        @lib.t.overload  # type: ignore[no-redef]
        def replace(
            self: lib.LiteralString,
            old: lib.LiteralString,
            new: lib.LiteralString,
            count: lib.t.SupportsIndex = -1,
            /
        ) -> lib.LiteralString: ...
        @lib.t.overload
        def replace(  # type: ignore[misc]
            self,
            old: str,
            new: str,
            count: lib.t.SupportsIndex = -1,
            /
            ) -> 'string[StringType] | string[lib.t.Any]': ...
        def replace(
            self,
            old: lib.LiteralString | str,
            new: lib.LiteralString | str,
            count: lib.t.SupportsIndex = -1,
            /
            ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
            return super().replace(old, new, count)
    if lib.sys.version_info >= (3, 9):
        @lib.t.overload
        def removeprefix(
            self: lib.LiteralString,
            prefix: lib.LiteralString,
            /
            ) -> lib.LiteralString: ...
        @lib.t.overload
        def removeprefix(  # type: ignore[misc]
            self,
            prefix: str,
            /
            ) -> 'string[StringType] | string[lib.t.Any]': ...
        def removeprefix(
            self,
            prefix: lib.LiteralString | str,
            /
            ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
            return super().removeprefix(prefix)
        @lib.t.overload
        def removesuffix(
            self: lib.LiteralString,
            suffix: lib.LiteralString,
            /
            ) -> lib.LiteralString: ...
        @lib.t.overload
        def removesuffix(  # type: ignore[misc]
            self,
            suffix: str,
            /
            ) -> 'string[StringType] | string[lib.t.Any]': ...
        def removesuffix(
            self,
            suffix: lib.LiteralString | str,
            /
            ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
            return super().removesuffix(suffix)

    @lib.t.overload
    def rjust(
        self: lib.LiteralString,
        width: lib.t.SupportsIndex,
        fillchar: lib.LiteralString = " ",
        /
        ) -> lib.LiteralString: ...
    @lib.t.overload
    def rjust(  # type: ignore[misc]
        self,
        width: lib.t.SupportsIndex,
        fillchar: str = " ",
        /
        ) -> 'string[StringType] | string[lib.t.Any]': ...
    def rjust(
        self,
        width: lib.t.SupportsIndex,
        fillchar: lib.LiteralString | str = " ",
        /
        ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
        return super().rjust(width, fillchar)
    @lib.t.overload
    def rpartition(
        self: lib.LiteralString,
        sep: lib.LiteralString,
        /
        ) -> tuple[
            lib.LiteralString,
            lib.LiteralString,
            lib.LiteralString
            ]: ...
    @lib.t.overload
    def rpartition(  # type: ignore[misc]
        self,
        sep: str,
        /
        ) -> tuple[
            'string[StringType] | string[lib.t.Any]', 
            'string[StringType] | string[lib.t.Any]', 
            'string[StringType] | string[lib.t.Any]'
            ]: ...
    def rpartition(
        self,
        sep: lib.LiteralString | str,
        /
        ) -> (
            tuple[
                lib.LiteralString,
                lib.LiteralString,
                lib.LiteralString
                ]
            | tuple[
                'string[StringType] | string[lib.t.Any]', 
                'string[StringType] | string[lib.t.Any]', 
                'string[StringType] | string[lib.t.Any]'
                ]
            ):
        return super().rpartition(sep)
    @lib.t.overload
    def rsplit(
        self: lib.LiteralString,
        sep: lib.LiteralString | None = None,
        maxsplit: lib.t.SupportsIndex = -1
        ) -> list[lib.LiteralString]: ...
    @lib.t.overload
    def rsplit(  # type: ignore[misc]
        self,
        sep: str | None = None,
        maxsplit: lib.t.SupportsIndex = -1
        ) -> 'list[string[StringType] | string[lib.t.Any]]': ...
    def rsplit(
        self,
        sep: lib.LiteralString | str | None = None,
        maxsplit: lib.t.SupportsIndex = -1
        ) -> lib.t.Union[
            list[lib.LiteralString],
            'list[string[StringType] | string[lib.t.Any]]'
            ]:
        return super().rsplit(sep, maxsplit)
    @lib.t.overload
    def rstrip(
        self: lib.LiteralString,
        chars: lib.LiteralString | None = None,
        /
        ) -> lib.LiteralString: ...
    @lib.t.overload
    def rstrip(  # type: ignore[misc]
        self,
        chars: str | None = None,
        /
        ) -> 'string[StringType] | string[lib.t.Any]': ...
    def rstrip(
        self,
        chars: lib.LiteralString | str | None = None,
        /
        ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
        return super().rstrip(chars)
    @lib.t.overload
    def split(
        self: lib.LiteralString,
        sep: lib.LiteralString | None = None,
        maxsplit: lib.t.SupportsIndex = -1
        ) -> list[lib.LiteralString]: ...
    @lib.t.overload
    def split(  # type: ignore[misc]
        self,
        sep: str | None = None,
        maxsplit: lib.t.SupportsIndex = -1
        ) -> 'list[string[StringType] | string[lib.t.Any]]': ...
    def split(
        self,
        sep: lib.LiteralString | str | None = None,
        maxsplit: lib.t.SupportsIndex = -1
        ) -> lib.t.Union[
            list[lib.LiteralString],
            'list[string[StringType] | string[lib.t.Any]]'
            ]:
        return super().split(sep, maxsplit)
    @lib.t.overload
    def splitlines(
        self: lib.LiteralString,
        keepends: bool = False
        ) -> list[lib.LiteralString]: ...
    @lib.t.overload
    def splitlines(  # type: ignore[misc]
        self,
        keepends: bool = False
        ) -> 'list[string[StringType] | string[lib.t.Any]]': ...
    def splitlines(
        self,
        keepends: bool = False
        ) -> lib.t.Union[
            list[lib.LiteralString],
            'list[string[StringType] | string[lib.t.Any]]'
            ]:
        return super().splitlines(keepends)
    @lib.t.overload
    def strip(
        self: lib.LiteralString,
        chars: lib.LiteralString | None = None,
        /
        ) -> lib.LiteralString: ...
    @lib.t.overload
    def strip(  # type: ignore[misc]
        self,
        chars: str | None = None,
        /
        ) -> 'string[StringType] | string[lib.t.Any]': ...
    def strip(
        self,
        chars: lib.LiteralString | str | None = None,
        /
        ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
        return super().strip(chars)
    @lib.t.overload
    def swapcase(self: lib.LiteralString) -> lib.LiteralString: ...
    @lib.t.overload
    def swapcase(self) -> 'string[StringType] | string[lib.t.Any]': ...  # type: ignore[misc]
    def swapcase(
        self
        ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
        return super().swapcase()
    @lib.t.overload
    def title(self: lib.LiteralString) -> lib.LiteralString: ...
    @lib.t.overload
    def title(self) -> 'string[StringType] | string[lib.t.Any]': ...  # type: ignore[misc]
    def title(
        self
        ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
        return super().title()
    def translate(
        self,
        table: 'lib.builtins._TranslateTable',
        /
        ) -> 'string[StringType] | string[lib.t.Any]':
        translated: 'string[StringType] | string[lib.t.Any]' = (
            super().translate(table)
            )
        return translated
    @lib.t.overload
    def upper(self: lib.LiteralString) -> lib.LiteralString: ...
    @lib.t.overload
    def upper(self) -> 'string[StringType] | string[lib.t.Any]': ...  # type: ignore[misc]
    def upper(
        self
        ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
        return super().upper()
    def zfill(
        self,
        width: lib.t.SupportsIndex,
        /
        ) -> 'string[StringType] | string[lib.t.Any]':
        zfilled: 'string[StringType] | string[lib.t.Any]' = (
            super().zfill(width)
            )
        return zfilled
    def __add__(
        self,
        value: str,
        /
        ) -> 'string[StringType] | string[lib.t.Any]':
        added: 'string[StringType] | string[lib.t.Any]' = self + value
        return added
    def __getitem__(
        self,
        key: lib.t.SupportsIndex | slice,
        /
        ) -> 'string[StringType] | string[lib.t.Any]':
        item: 'string[StringType] | string[lib.t.Any]' = (
            super().__getitem__(key)
            )
        return item
    @lib.t.overload
    def __iter__(
        self: lib.LiteralString
        ) -> lib.t.Iterator[lib.LiteralString]: ...
    @lib.t.overload
    def __iter__(  # type: ignore[misc]
        self
        ) -> 'lib.t.Iterator[string[StringType] | string[lib.t.Any]]': ...
    def __iter__(
        self
        ) -> lib.t.Union[
            lib.t.Iterator[lib.LiteralString],
            'lib.t.Iterator[string[StringType] | string[lib.t.Any]]'
            ]:
        iterator: lib.t.Union[
            lib.t.Iterator[lib.LiteralString],
            'lib.t.Iterator[string[StringType] | string[lib.t.Any]]'
            ] = super().__iter__()
        return iterator
    @lib.t.overload
    def __mod__(
        self: lib.LiteralString,
        value: lib.t.Union[
            lib.LiteralString,
            tuple[lib.LiteralString, ...]
            ],
        /
        ) -> lib.LiteralString: ...
    @lib.t.overload
    def __mod__(
        self,
        value: lib.t.Any,
        /
        ) -> 'string[StringType] | string[lib.t.Any]': ...
    def __mod__(
        self,
        value: lib.t.Any,
        /
        ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
        return super().__mod__(value)
    @lib.t.overload
    def __mul__(
        self: lib.LiteralString,
        value: lib.t.SupportsIndex,
        /
        ) -> lib.LiteralString: ...
    @lib.t.overload
    def __mul__(  # type: ignore[misc]
        self,
        value: lib.t.SupportsIndex,
        /
        ) -> 'string[StringType] | string[lib.t.Any]': ...
    def __mul__(
        self,
        value: lib.t.SupportsIndex,
        /
        ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
        return super().__mul__(value)
    @lib.t.overload
    def __rmul__(
        self: lib.LiteralString,
        value: lib.t.SupportsIndex,
        /
        ) -> lib.LiteralString: ...
    @lib.t.overload
    def __rmul__(  # type: ignore[misc]
        self,
        value: lib.t.SupportsIndex,
        /
        ) -> 'string[StringType] | string[lib.t.Any]': ...
    def __rmul__(
        self,
        value: lib.t.SupportsIndex,
        /
        ) -> 'lib.LiteralString | string[StringType] | string[lib.t.Any]':
        return super().__rmul__(value)
    def __getnewargs__(
        self
        ) -> 'tuple[string[StringType] | string[lib.t.Any]]':
        new_args: 'tuple[string[StringType] | string[lib.t.Any]]' = (
            super().__getnewargs__()
            )
        return new_args
