"""Type hinting utility functions."""

__all__ = (
    'collect_annotations',
    'finalize_type',
    'reference_and_expand_types',
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

    MAX_RECURSIONS = 4


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


def reference_and_expand_types(tp_or_ref: lib.t.Any) -> list[lib.t.Any]:
    """
    Recursively expand all `types` (and `type` args) into flat list of \
    `types` and / or `ForwardRefs`.

    """

    from .. import obj

    all_tps: list[lib.t.Any] = []
    tps: list[tuple[lib.t.Any, bool]] = [
        (tp_, False)
        for tp_
        in check.expand_types(tp_or_ref)
        ]

    recursion_count = 0

    while tps and recursion_count < Constants.MAX_RECURSIONS:
        tp, is_arg_tp = tps.pop()
        if isinstance(tp, str):
            all_tps.append(parse_str_to_ref(tp, is_arg_tp))
        elif check.is_params_type(tp):
            arg_tps = check.get_type_args(tp)
            recursion_count += 1
            tps.extend(
                [
                    (tp_, True)
                    for tp_
                    in arg_tps
                    ]
                )
            if any(isinstance(arg_tp, str) for arg_tp in arg_tps):
                tps.append(
                    (
                        obj.ForwardPattern.sub('', str(tp)),
                        False
                        )
                    )
            else:
                all_tps.append(tp)
        else:
            all_tps.append(tp)

    return all_tps


@lib.functools.cache
def finalize_type(tp_or_ref_or_str: lib.t.Any) -> lib.t.Any:
    """Recursively resolve any remaining `ForwardRefs`."""

    from .. import obj

    if isinstance(tp_or_ref_or_str, str):
        ref_tps = [parse_str_to_ref(tp_or_ref_or_str, False)]
    elif isinstance(tp_or_ref_or_str, lib.t.ForwardRef):  # pragma: no cover
        ref_tps = [tp_or_ref_or_str]
    else:
        ref_tps = [
            tp
            for tp
            in reference_and_expand_types(tp_or_ref_or_str)
            if isinstance(tp, lib.t.ForwardRef)
            ]

    has_unresolved_refs = bool(ref_tps)

    if has_unresolved_refs:
        ref_tps = list(set(ref_tps))
        tp_as_ref = parse_str_to_ref(
            obj.ForwardPattern.sub('', str(tp_or_ref_or_str)),
            False
            )
        ref_tps.append(tp_as_ref)

        modules: dict[str, lib.types.ModuleType] = {}

        for name, module in lib.sys.modules.items():
            if isinstance(module.__dict__, dict):
                for ref_tp in ref_tps:
                    *module_info, tp_info = ref_tp.__forward_arg__.split('.')
                    if (
                        name in '.'.join(module_info)
                        or tp_info in module.__dict__
                        ):
                        modules[name] = module

        namespace = {**modules}
        for ref_tp in ref_tps:
            parse_ref_to_typ(ref_tp, namespace, {})
            for name, module in modules.items():
                tp = parse_ref_to_typ(ref_tp, namespace, module.__dict__)
                if not isinstance(tp, lib.t.ForwardRef):
                    break

        return ref_tps[-1].__forward_value__ or tp_or_ref_or_str
    else:
        return tp_or_ref_or_str
