"""Type hinting utility functions."""

__all__ = (
    'collect_annotations',
    'resolve_type',
    )

from .. import cfg
from .. import lib

from . import check

if lib.t.TYPE_CHECKING:  # pragma: no cover
    from .. import obj
    from .. import typ


class Constants(cfg.Constants):
    """Constant values specific to this file."""

    CACHED_ANNOTATIONS: 'dict[str, typ.AnyDict]' = {}
    """Local cache for typed object annotations."""


eval_type: lib.t.Callable[
    [
        'typ.AnyOrForwardRef',
        lib.t.Any,
        lib.t.Any,
        lib.t.Optional[frozenset]
        ],
    lib.t.Any
    ] = lib.t._eval_type  # type: ignore[attr-defined]
"""
Evaluate all `ForwardRef` in the given `type`.

---

For use of globalns and localns see the docstring for `get_type_hints()`.

`recursive_guard` is used to prevent infinite recursion with a recursive
`ForwardRef`.

"""


@lib.t.overload
def parse_ref_to_typ(
    ref: lib.t.ForwardRef,
    globalns: None,
    localns: 'typ.OptionalAnyDict'
    ) -> lib.t.ForwardRef: ...
@lib.t.overload
def parse_ref_to_typ(
    ref: lib.t.ForwardRef,
    globalns: 'typ.OptionalAnyDict',
    localns: 'typ.OptionalAnyDict'
    ) -> 'typ.AnyOrForwardRef': ...
def parse_ref_to_typ(
    ref: lib.t.ForwardRef,
    globalns: 'typ.OptionalAnyDict' = None,
    localns: 'typ.OptionalAnyDict' = None
    ) -> 'typ.AnyOrForwardRef':
    """Attempt to cast `ForwardRef` to `type`."""

    try:
        tp = eval_type(
            ref,
            globalns,
            localns,
            frozenset()
            )
    except NameError:
        return ref
    else:
        return tp


def parse_str_to_ref(
    typ_as_str: str,
    is_argument: bool,
    ) -> lib.t.ForwardRef:
    """Cast `str` to `ForwardRef`."""

    return lib.t.ForwardRef(
        typ_as_str,
        is_argument=is_argument,
        is_class=True
        )


@lib.t.overload
def resolve_type(
    typ_ref_or_str: 'typ.AnyType | typ.StrOrForwardRef',
    globalns: 'typ.AnyDict',
    localns: 'typ.AnyDict',
    is_argument: bool
    ) -> 'typ.AnyType | lib.t.Any': ...
@lib.t.overload
def resolve_type(
    typ_ref_or_str: 'typ.AnyType | typ.StrOrForwardRef',
    globalns: 'typ.OptionalAnyDict',
    localns: 'typ.OptionalAnyDict',
    is_argument: bool
    ) -> 'typ.AnyType | typ.AnyOrForwardRef': ...
@lib.t.overload
def resolve_type(
    typ_ref_or_str: 'typ.StrOrForwardRef',
    globalns: 'typ.OptionalAnyDict' = None,
    localns: 'typ.OptionalAnyDict' = None,
    is_argument: bool = False
    ) -> 'typ.AnyOrForwardRef': ...
def resolve_type(
    typ_ref_or_str: 'typ.AnyType | typ.StrOrForwardRef',
    globalns: 'typ.OptionalAnyDict' = None,
    localns: 'typ.OptionalAnyDict' = None,
    is_argument: bool = False
    ) -> 'typ.AnyType | typ.AnyOrForwardRef':
    """
    Attempt to resolve `str` or `ForwardRef` to `type`.

    ---

    Recursively resolves parameterized generics.

    """

    if isinstance(typ_ref_or_str, str):
        ref = parse_str_to_ref(typ_ref_or_str, is_argument)
        return resolve_type(ref, globalns, localns, is_argument)
    elif check.is_params_type(typ_ref_or_str):
        args = check.get_type_args(typ_ref_or_str)
        for arg in args:
            resolve_type(arg, globalns, localns, True)
        return typ_ref_or_str
    elif isinstance(typ_ref_or_str, lib.t.ForwardRef):
        typ_or_ref = parse_ref_to_typ(typ_ref_or_str, globalns, localns)
        if check.is_params_type(typ_or_ref):
            return resolve_type(typ_or_ref, globalns, localns, is_argument)
        else:
            return typ_or_ref
    else:
        return typ_ref_or_str


def _collect_annotations(
    __name: str,
    __annotations: 'typ.AnyDict',
    __bases: tuple[type, ...]
    ) -> 'typ.AnyDict':
    annotations: 'typ.AnyDict' = {}
    for _base in reversed(__bases):
        for __base in reversed(_base.__mro__):
            annotations |= getattr(__base, Constants.__ANNOTATIONS__, {})
    annotations |= __annotations
    # Ensure any annotations hinted for TYPE_CHECKING removed.
    annotations.pop(Constants.__ANNOTATIONS__, None)
    annotations.pop(Constants.__DATACLASS_FIELDS__, None)
    annotations.pop(Constants.__HERITAGE__, None)
    annotations.pop(Constants.__OPERATIONS__, None)
    annotations.pop(Constants.FIELDS, None)
    annotations.pop(Constants.ENUMERATIONS, None)
    annotations.pop(Constants.HASH_FIELDS, None)
    Constants.CACHED_ANNOTATIONS[__name] = annotations
    return annotations


def collect_annotations(
    typed_obj: 'obj.SupportsAnnotations | type[obj.SupportsAnnotations]'
    ) -> 'typ.AnyDict':
    """
    Get all type annotations for `typed_obj`.

    ---

    Walks `__bases__` to collect all annotations.

    """

    obj_tp = typed_obj if isinstance(typed_obj, type) else type(typed_obj)

    if obj_tp.__name__ in Constants.CACHED_ANNOTATIONS:
        return Constants.CACHED_ANNOTATIONS[obj_tp.__name__]

    return _collect_annotations(
        obj_tp.__name__,
        getattr(obj_tp, Constants.__ANNOTATIONS__, {}),
        obj_tp.__bases__
        )
