"""Typing objects."""

__all__ = (
    'string',
    'ArrayProto',
    'FieldPattern',
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

WrapperPattern = lib.re.compile(
    r'([a-zA-Z]{1,64}\.?)?(Annotated|ClassVar|Final|InitVar)'
    r'\[((\[)?[\.\|\,a-zA-Z0-9_ ]{1,64}(\])?){1,64}\]'
    )


class string(str, lib.t.Generic[StringType]):
    """Generic `str` protocol."""

    @lib.t.overload  # type: ignore[no-overload-impl]
    def __new__(cls, object: object = ...) -> lib.Self: ...
    @lib.t.overload
    def __new__(
        cls,
        object: 'lib.builtins.ReadableBuffer',  # type: ignore[name-defined]
        encoding: str = ...,
        errors: str = ...
        ) -> lib.Self: ...
    @lib.t.overload  # type: ignore[no-overload-impl]
    def capitalize(self: lib.LiteralString) -> lib.LiteralString: ...
    @lib.t.overload
    def capitalize(self) -> 'string[StringType] | string[lib.t.Any]': ...  # type: ignore[misc]
    @lib.t.overload  # type: ignore[no-overload-impl]
    def casefold(self: lib.LiteralString) -> lib.LiteralString: ...
    @lib.t.overload
    def casefold(self) -> 'string[StringType] | string[lib.t.Any]': ...  # type: ignore[misc]
    @lib.t.overload  # type: ignore[no-overload-impl]
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
    @lib.t.overload  # type: ignore[no-overload-impl]
    def expandtabs(
        self: lib.LiteralString,
        tabsize: lib.t.SupportsIndex = 8
        ) -> lib.LiteralString: ...
    @lib.t.overload
    def expandtabs(  # type: ignore[misc]
        self,
        tabsize: lib.t.SupportsIndex = 8
        ) -> 'string[StringType] | string[lib.t.Any]': ...
    @lib.t.overload  # type: ignore[misc, no-overload-impl]
    def format(  # type: ignore[empty-body]
        self,
        *args: object,
        **kwargs: object
        ) -> 'string[StringType] | string[lib.t.Any]': ...
    def format_map(  # type: ignore[empty-body]
        self,
        mapping: 'lib.builtins._FormatMapMapping',
        /
        ) -> 'string[StringType] | string[lib.t.Any]': ...
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
    @lib.t.overload  # type: ignore[no-overload-impl]
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
    @lib.t.overload  # type: ignore[no-overload-impl]
    def lower(self: lib.LiteralString) -> lib.LiteralString: ...
    @lib.t.overload
    def lower(self) -> 'string[StringType] | string[lib.t.Any]': ...  # type: ignore[misc]
    @lib.t.overload  # type: ignore[no-overload-impl]
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
    @lib.t.overload  # type: ignore[no-overload-impl]
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
    if lib.sys.version_info >= (3, 13):  # pragma: no cover
        @lib.t.overload  # type: ignore[no-overload-impl]
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
    else:  # pragma: no cover
        @lib.t.overload  # type: ignore[no-redef, no-overload-impl]
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
    if lib.sys.version_info >= (3, 9):
        @lib.t.overload  # type: ignore[no-overload-impl]
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
        @lib.t.overload  # type: ignore[no-overload-impl]
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

    @lib.t.overload  # type: ignore[no-overload-impl]
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
    @lib.t.overload  # type: ignore[no-overload-impl]
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
    @lib.t.overload  # type: ignore[no-overload-impl]
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
    @lib.t.overload  # type: ignore[no-overload-impl]
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
    @lib.t.overload  # type: ignore[no-overload-impl]
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
    @lib.t.overload  # type: ignore[no-overload-impl]
    def splitlines(
        self: lib.LiteralString,
        keepends: bool = False
        ) -> list[lib.LiteralString]: ...
    @lib.t.overload
    def splitlines(  # type: ignore[misc]
        self,
        keepends: bool = False
        ) -> 'list[string[StringType] | string[lib.t.Any]]': ...
    @lib.t.overload  # type: ignore[no-overload-impl]
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
    @lib.t.overload  # type: ignore[no-overload-impl]
    def swapcase(self: lib.LiteralString) -> lib.LiteralString: ...
    @lib.t.overload
    def swapcase(self) -> 'string[StringType] | string[lib.t.Any]': ...  # type: ignore[misc]
    @lib.t.overload  # type: ignore[no-overload-impl]
    def title(self: lib.LiteralString) -> lib.LiteralString: ...
    @lib.t.overload
    def title(self) -> 'string[StringType] | string[lib.t.Any]': ...  # type: ignore[misc]
    def translate(  # type: ignore[empty-body]
        self,
        table: 'lib.builtins._TranslateTable',
        /
        ) -> 'string[StringType] | string[lib.t.Any]': ...
    @lib.t.overload  # type: ignore[no-overload-impl]
    def upper(self: lib.LiteralString) -> lib.LiteralString: ...
    @lib.t.overload
    def upper(self) -> 'string[StringType] | string[lib.t.Any]': ...  # type: ignore[misc]
    @lib.t.overload  # type: ignore[misc, no-overload-impl]
    def zfill(  # type: ignore[empty-body]
        self,
        width: lib.t.SupportsIndex,
        /
        ) -> 'string[StringType] | string[lib.t.Any]': ...  # type: ignore[misc]
    @lib.t.overload  # type: ignore[misc, no-overload-impl]
    def __add__(  # type: ignore[empty-body]
        self,
        value: str,
        /
        ) -> 'string[StringType] | string[lib.t.Any]': ...  # type: ignore[misc]
    def __getitem__(  # type: ignore[empty-body]
        self,
        key: lib.t.SupportsIndex | slice,
        /
        ) -> 'string[StringType] | string[lib.t.Any]': ...
    @lib.t.overload  # type: ignore[no-overload-impl]
    def __iter__(
        self: lib.LiteralString
        ) -> 'lib.t.Iterator[lib.LiteralString]': ...
    @lib.t.overload
    def __iter__(  # type: ignore[misc]
        self
        ) -> 'lib.t.Iterator[string[StringType] | string[lib.t.Any]]': ...
    @lib.t.overload  # type: ignore[no-overload-impl]
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
    @lib.t.overload  # type: ignore[no-overload-impl]
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
    @lib.t.overload  # type: ignore[no-overload-impl]
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
    def __getnewargs__(  # type: ignore[empty-body]
        self
        ) -> 'tuple[string[StringType] | string[lib.t.Any]]': ...
