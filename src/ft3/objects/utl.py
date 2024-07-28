"""Objects utility functions."""

__all__ = (
    'get_enumerations_from_fields',
    'get_fields_for_hash',
    'is_public_field',
    'is_valid_keyword',
    )

from . import cfg
from . import lib
from . import typ


class Constants(cfg.Constants):
    """Constant values specific to this file."""


@lib.functools.cache
def is_public_field(f: str) -> bool:
    """Return if field name is public."""

    return not (
        (f in Constants.FORBIDDEN_KEYWORDS)
        or f.startswith('_')
        )


@lib.functools.cache
def is_valid_keyword(f: str) -> bool:
    """Return if field name is allowed."""

    return f not in (
        set(Constants.FORBIDDEN_KEYWORDS)
        | set(Constants.BASE_ATTRS)
        )


def get_enumerations_from_fields(
    fields: typ.DataClassFields,
    ) -> dict[typ.string[typ.snake_case], tuple[typ.Primitive, ...]]:
    """
    Return dict containing all enums for object.

    ---

    Automatically appends `None` to any enums for an `Optional` type.

    """

    d: dict[typ.string[typ.snake_case], tuple[typ.Primitive, ...]] = {}
    for k, field in fields.items():
        if isinstance((enum_ := field.get('enum')), lib.enum.EnumMeta):
            d[k] = tuple([e.value for e in enum_._member_map_.values()])
        elif typ.utl.check.is_array(enum_):
            d[k] = tuple(enum_)
        if (
            k in d
            and isinstance(
                None,
                typ.utl.check.get_checkable_types(field.type_)
                )
            and None not in d[k]
            ):
            d[k] = (*d[k], None)

    return d


def get_fields_for_hash(
    __fields: typ.DataClassFields
    ) -> tuple[typ.string[typ.snake_case], ...]:
    """
    Filter to set of minimum fields required to compute a unique hash \
    for their owner object.

    ---

    Fields used must be of primitive types, for these purposes: \
    `bool | float | int | None | str`.

    Fields ending in the following will be used [in the following \
    order of precedence]:

    1. `'*id' | '*key'`
    2. `'*name'`

    For example, for an object with fields `'id_'` and \
    `'_common_name_'`, this function would return `('id_', )`, as \
    `'id_'` takes precedence over `'_common_name_'`.

    If no fields are named in ways that suggest they can be used to \
    determine the uniqueness of the object, all fields will instead be \
    returned.

    """

    id_fields: list[typ.string[typ.snake_case]] = []
    name_fields: list[typ.string[typ.snake_case]] = []
    primitive_fields: list[typ.string[typ.snake_case]] = []

    for f, field in __fields.items():
        if (
            isinstance(field.type_, (lib.t.ForwardRef, str))
            or not all(
                typ.utl.check.is_primitive(sub_tp)
                for sub_tp
                in typ.utl.check.get_checkable_types(field)
                )
            ):  # pragma: no cover
            continue
        elif (s := f.strip('_').lower()).endswith('id'):
            id_fields.append(f)
        elif s.endswith('key'):
            id_fields.append(f)
        elif s.startswith('name') or s.endswith('name'):
            name_fields.append(f)
        else:
            primitive_fields.append(f)

    if id_fields:
        fields_for_hash = tuple(id_fields)
    elif name_fields:
        fields_for_hash = tuple(name_fields)
    elif primitive_fields:
        fields_for_hash = tuple(primitive_fields)
    else:
        fields_for_hash = tuple(__fields)

    return fields_for_hash
