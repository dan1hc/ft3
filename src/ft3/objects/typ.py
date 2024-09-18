"""Objects typing."""

from .. import core

__all__ = (
    'Field',
    'MetaType',
    'SortDirection',
    'Type',
    *core.typ.__all__,
    )

from .. core . typ import *

from . import cfg
from . import lib

if lib.t.TYPE_CHECKING:  # pragma: no cover
    from . import metas  # noqa: F401


class Constants(cfg.Constants):
    """Constant values specific to this file."""


SortDirection = lib.t.Literal['asc'] | lib.t.Literal['desc']

MetaType = lib.t.TypeVar('MetaType', bound='metas.Meta')
Type = lib.t.TypeVar('Type', bound=type)


class Field(lib.types.GenericAlias, lib.t.Generic[AnyTypeCo]):
    """Single Generic alias type."""

    @lib.t.overload
    def __new__(cls, origin: type, args: type[AnyTypeCo]) -> lib.Self: ...
    @lib.t.overload
    def __new__(cls, origin: type, args: AnyTypeCo) -> lib.Self: ...
    def __new__(
        cls,
        origin: type,
        args: lib.t.Union[type[AnyTypeCo], AnyTypeCo]
        ) -> lib.Self:
        return super().__new__(cls, origin, args)

    def __repr__(self) -> str:
        ftypes = utl.check.expand_types(self.__args__[0])
        _delim = (
            ' | '
            if core.typ.utl.check.is_union(self)
            else ', '
            )
        _ftypes = _delim.join(
            (
                getattr(t, '__name__', 'Any')
                if isinstance(t, type)
                else str(t)
                for t
                in ftypes
                )
            )
        return f'Field[{_ftypes}]'
