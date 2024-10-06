"""Codecs utility functions."""

__all__ = (
    'encode',
    'parse',
    'serialize',
    'try_decode',
    'try_parse_json',
    )

from .. import strings

from . import cfg
from . import enm
from . import lib
from . import typ


class Constants(cfg.Constants):
    """Constant values specific to this file."""


def serialize(value: lib.t.Any) -> str:
    """Convert value to string."""

    return lib.json.dumps(
        value,
        indent=Constants.INDENT,
        sort_keys=True,
        default=strings.utl.convert_for_repr
        )


def encode(value: lib.t.Any) -> typ.Serial:
    """
    JSON encode `value` using a corresponding encoder, otherwise returns \
    `repr(value)`.

    """

    if (encoder := Constants.ENCODERS.get(value.__class__)) is not None:
        return encoder(value)

    for _base in reversed(value.__class__.__bases__):
        for __base in reversed(_base.__mro__):
            if (encoder := Constants.ENCODERS.get(__base)) is not None:
                return encoder(value)

    return repr(value)


def try_decode(
    value: lib.t.Any,
    tp: type[typ.AnyType],
    ) -> typ.AnyType | enm.ParseErrorRef:
    """
    Attempt to parse value, returning `enm.ParseErrorRef` if error.

    """

    try:
        if tp is lib.t.Any:
            as_tp: typ.AnyType = value
            return as_tp
        elif typ.utl.check.is_literal(tp):
            literals = typ.utl.check.get_args(tp)
            literal: typ.AnyType
            if value in literals:
                literal = value
                return literal
            literal_tps = (type(literal) for literal in literals)
            for literal_tp in literal_tps:
                literal = try_decode(value, literal_tp)
                if literal in literals:
                    return literal
            return enm.ParseErrorRef.literal_decode
        elif isinstance(value, typ.utl.check.get_checkable_types(tp)):
            tp_value: typ.AnyType = value
            return tp_value
        elif isinstance(value, str):
            if typ.utl.check.is_bool_type(tp):
                if value.lower() in enm.Boolean._member_names_:
                    boolean: typ.AnyType = (
                        value.lower() == enm.Boolean.true.name
                        )
                    return boolean
                else:
                    return enm.ParseErrorRef.bool_decode
            elif typ.utl.check.is_number_type(tp):
                if strings.utl.is_valid_number_str(value):
                    num_tp: type[typ.AnyType] = tp
                    return num_tp(value)  # type: ignore[call-arg]
                else:
                    return enm.ParseErrorRef.number_decode
            elif (
                (is_datetime_tp := typ.utl.check.is_datetime_type(tp))
                or typ.utl.check.is_date_type(tp)
                ):
                if strings.utl.is_valid_datetime_str(value):
                    dt = (
                        lib.datetime.datetime.fromisoformat(value)
                        .replace(tzinfo=lib.datetime.timezone.utc)
                        )
                    if is_datetime_tp:
                        dt_value: typ.AnyType = dt
                        return dt_value
                    else:
                        date_value: typ.AnyType = dt.date()
                        return date_value
                else:
                    return enm.ParseErrorRef.datetime_decode
            elif typ.utl.check.is_none_type(tp):
                if value.lower() in enm.NoneAlias._member_names_:
                    none: typ.AnyType = None
                    return none
                else:
                    return enm.ParseErrorRef.null_decode
            else:  # pragma: no cover
                return tp(value)  # type: ignore[call-arg]
        elif value is None:
            return enm.ParseErrorRef.null_decode
        else:
            return tp(value)  # type: ignore[call-arg]
    except:  # noqa: E722
        return enm.ParseErrorRef.value_decode


def try_parse_json(
    json_string: str
    ) -> typ.Serial | enm.ParseErrorRef:
    """
    Attempt to parse valid JSON string, returning \
    `enm.ParseErrorRef` if error.

    """

    try:
        deserialized: typ.Serial = lib.json.loads(json_string)
        return deserialized
    except:  # noqa: E722
        return enm.ParseErrorRef.invalid_json


@lib.t.overload
def parse(
    value: lib.t.Any,
    tp: type[typ.VariadicArrayType],
    ) -> typ.VariadicArrayType | enm.ParseErrorRef: ...
@lib.t.overload
def parse(
    value: lib.t.Any,
    tp: type[typ.ArrayType],
    ) -> typ.ArrayType | enm.ParseErrorRef: ...
@lib.t.overload
def parse(
    value: lib.t.Any,
    tp: type[typ.MappingType],
    ) -> typ.MappingType | enm.ParseErrorRef: ...
@lib.t.overload
def parse(
    value: lib.t.Any,
    tp: type[typ.Typed],
    ) -> typ.Typed | enm.ParseErrorRef: ...
@lib.t.overload
def parse(
    value: lib.t.Any,
    tp: type[typ.AnyType],
    ) -> typ.AnyType | enm.ParseErrorRef: ...
def parse(
    value: typ.AnyType,
    tp: (
        type[typ.VariadicArrayType]
        | type[typ.ArrayType]
        | type[typ.MappingType]
        | type[typ.Typed]
        | type[typ.AnyType]
        ),
    ) -> (
        typ.VariadicArrayType
        | typ.ArrayType
        | typ.MappingType
        | typ.Typed
        | typ.AnyType
        | enm.ParseErrorRef
        ):
    """
    Try to recursively parse python `tp` from `value`.

    ---

    Value should either be an instance of `tp` or a valid, serialized \
    representation of that `tp` (JSON string or otherwise).

    Returns `enm.ParseErrorRef` if no valid type could be parsed, \
    allowing for downstream validation instead of immediately raising \
    an exception within this function.

    """

    valid_types = typ.utl.check.expand_types(tp)
    if len(valid_types) > 1:
        parsed_value_or_err_ref = parse(value, valid_types[0])
        for dtype_candidate in valid_types[1:]:
            if not isinstance(parsed_value_or_err_ref, enm.ParseErrorRef):
                break
            else:  # pragma: no cover
                parsed_value_or_err_ref = parse(value, dtype_candidate)
        return parsed_value_or_err_ref
    elif isinstance(value, str):
        if (
            typ.utl.check.is_array_type(tp)
            or typ.utl.check.is_variadic_array_type(tp)
            ):
            deserialized_as_list = try_parse_json(value)
            if not isinstance(deserialized_as_list, enm.ParseErrorRef):
                return parse(deserialized_as_list, tp)
            else:
                return deserialized_as_list
        elif typ.utl.check.is_mapping_type(tp):
            deserialized_as_dict = try_parse_json(value)
            if not isinstance(deserialized_as_dict, enm.ParseErrorRef):
                return parse(deserialized_as_dict, tp)
            else:
                return deserialized_as_dict
        else:
            return try_decode(value, tp)
    elif typ.utl.check.is_typed(tp):
        if typ.utl.check.is_object(tp):
            tp_annotations = {
                k: typ.utl.hint.finalize_type(typ.utl.check.get_args(v)[0])  # Expand Field[Any] --> Any
                for k, v
                in typ.utl.hint.collect_annotations(tp).items()
                }
        else:
            tp_annotations = {
                k: typ.utl.hint.finalize_type(v)
                for k, v
                in typ.utl.hint.collect_annotations(tp).items()
                }
        if typ.utl.check.is_serialized_mapping(value):
            tp_dict: dict[str, lib.t.Any] = {}
            for k, val in value.items():
                if (
                    isinstance(k, str)
                    and (
                        ckey := strings.utl.cname_for(
                            k,
                            tuple(tp_annotations)
                            )
                        )
                    ):
                    tp_val = parse(val, tp_annotations[ckey])
                    if isinstance(tp_val, enm.ParseErrorRef):
                        return enm.ParseErrorRef.invalid_map_decode
                    tp_dict[ckey] = tp_val
                else:
                    return enm.ParseErrorRef.invalid_keys_decode
            return tp(**tp_dict)
        else:  # pragma: no cover
            return try_decode(value, tp)
    elif (generics := typ.utl.check.get_type_args(tp)):
        if (typ.utl.check.is_variadic_array_type(tp)):
            if not typ.utl.check.is_array(value):
                return enm.ParseErrorRef.value_decode
            elif typ.utl.check.is_ellipsis(generics[-1]):
                parsed_variadic_unknown_len = [
                    parse(v, generics[0])
                    for v
                    in value
                    ]
                if any(
                    (
                        isinstance(p, enm.ParseErrorRef)
                        or not isinstance(
                            p,
                            typ.utl.check.get_checkable_types(generics[0])
                            )
                        )
                    for p
                    in parsed_variadic_unknown_len
                    ):
                    return enm.ParseErrorRef.invalid_arr_decode
                else:
                    return try_decode(parsed_variadic_unknown_len, tp)
            elif len(value) == len(generics):
                parsed_variadic_known_len = [
                    parse(v, generics[i])
                    for i, v
                    in enumerate(value)
                    ]
                if any(
                    (
                        isinstance(p, enm.ParseErrorRef)
                        or not isinstance(
                            p,
                            typ.utl.check.get_checkable_types(generics[i])
                            )
                        )
                    for i, p
                    in enumerate(parsed_variadic_known_len)
                    ):
                    return enm.ParseErrorRef.invalid_arr_decode
                else:
                    return try_decode(parsed_variadic_known_len, tp)
            else:
                return enm.ParseErrorRef.invalid_arr_len
        elif typ.utl.check.is_array_type(tp):
            if typ.utl.check.is_array(value):
                parsed_array = [
                    parse(v, generics[0])
                    for v
                    in value
                    ]
                if any(
                    (
                        isinstance(p, enm.ParseErrorRef)
                        or not isinstance(
                            p,
                            typ.utl.check.get_checkable_types(generics[0])
                            )
                        )
                    for p
                    in parsed_array
                    ):
                    return enm.ParseErrorRef.invalid_arr_decode
                else:
                    return try_decode(parsed_array, tp)
            else:
                return try_decode(value, tp)
        elif typ.utl.check.is_mapping_type(tp):
            if (
                typ.utl.check.is_serialized_mapping(value)
                or typ.utl.check.is_mapping(value)
                ):
                if len(generics) == 2:
                    key_type, value_type = generics
                    parsed_map = {
                        parse(k, key_type): parse(v, value_type)
                        for k, v
                        in value.items()
                        }
                    if any(
                        isinstance(k, enm.ParseErrorRef)
                        for k
                        in parsed_map.keys()
                        ):
                        return enm.ParseErrorRef.invalid_keys_decode
                    elif any(
                        isinstance(v, enm.ParseErrorRef)
                        for v
                        in parsed_map.values()
                        ):
                        return enm.ParseErrorRef.invalid_values_decode
                    else:
                        return try_decode(parsed_map, tp)
                else:
                    return enm.ParseErrorRef.invalid_map_decode
            else:
                return try_decode(value, tp)
        else:  # pragma: no cover
            return try_decode(value, tp)
    else:
        return try_decode(value, tp)
