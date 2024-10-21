"""Metaclass module utility functions."""

from .. import utl

__all__ = (
    'parse_new_annotations',
    'parse_new_namespace',
    *utl.__all__
    )

from ... import core

from .. import cfg
from .. import exc
from .. import lib
from .. import typ

from .. utl import *


class Constants(cfg.Constants):
    """Constant values specific to this file."""


def parse_new_annotations(
    __namespace: dict[typ.AnyString, lib.t.Any],
    __annotations: typ.SnakeDict,
    __module: str,
    __slots: list[typ.string[typ.snake_case]],
    __fields: typ.DataClassFields,
    __base_fields: set[typ.string[typ.snake_case]]
    ) -> tuple[
        list[typ.string[typ.snake_case]],
        typ.DataClassFields
        ] | lib.Never:
    """
    Parse passed `__annotations` for valid `Fields` not otherwise \
    explicitly mapped in `__namespace`.

    Returns updated `__slots` and `__fields`.

    ---

    Passed `__namespace` will be mutated inplace, removing all key, \
    value pairs where keys overlap with those in `__annotations`.

    ---

    Raises a corresponding exception if class definition invalid.

    """

    for name, dtype in __annotations.items():
        if (
            typ.utl.check.is_wrapper_type(dtype)
            or (
                name in __fields
                and (
                    name not in __namespace
                    or name not in __base_fields
                    )
                )
            ):
            continue
        elif (
            not utl.is_valid_keyword(name)
            and __module != Constants.FIELDS_MODULE
            ):
            raise exc.ReservedKeywordError(name)
        elif not typ.utl.check.is_field_type(dtype):
            raise exc.FieldAnnotationError(name, dtype)
        elif not core.strings.utl.is_snake_case_string(name):
            raise exc.IncorrectCasingError(tuple(__annotations))
        elif (
            (default := __namespace.pop(name, Constants.UNDEFINED))
            == Constants.UNDEFINED
            ):
            required = True
            default = None
        else:
            required = False

        if __module == Constants.FIELDS_MODULE:
            __fields[name] = {
                'name': name,
                'type': dtype,
                'default': default,
                'required': required
                }
        else:
            from .. import fields as fields_
            __fields[name] = fields_.Field(
                name=name,
                type=typ.utl.check.get_args(dtype)[0],
                default=default,
                required=required
                )
        __slots.append(name)

    return __slots, __fields


def parse_new_namespace(
    __namespace: dict[typ.AnyString, lib.t.Any],
    __annotations: typ.SnakeDict,
    __module: str,
    __slots: list[typ.string[typ.snake_case]],
    __fields: typ.DataClassFields,
    ) -> tuple[
        list[str],
        list[typ.string[typ.snake_case]],
        typ.DataClassFields
        ] | lib.Never:
    """
    Parse passed `__namespace` for valid `Fields`.

    Returns a `list[str]` of default values, as well as updated \
    `__slots` and `__fields`.

    ---

    Raises a corresponding exception if class definition invalid.

    """

    defaults: list[str] = []
    for name, default in __namespace.items():
        if (
            (is_snake_case := core.strings.utl.is_snake_case_string(name))
            and (
                utl.is_valid_keyword(name)
                or __module == Constants.FIELDS_MODULE
                )
            ):
            dtype = __annotations.get(name)
        elif not is_snake_case:
            raise exc.IncorrectCasingError(tuple(__namespace))
        else:
            raise exc.ReservedKeywordError(name)

        if typ.utl.check.is_wrapper_type(dtype):
            continue
        elif (
            (is_field := typ.utl.check.is_field(default))
            and typ.utl.check.is_field_type(dtype)
            ):
            default['name'] = name
            default['type'] = typ.utl.check.get_args(dtype)[0]
        elif (
            is_field_as_dict := (
                isinstance(default, dict)
                and len(default) > 0
                and all(
                    k in Constants.FIELD_KEYS
                    for k
                    in default
                    )
                and __module != Constants.FIELDS_MODULE
                )
            and typ.utl.check.is_field_type(dtype)
            ):
            default['name'] = name
            default['type'] = typ.utl.check.get_args(dtype)[0]
            from .. import fields as fields_
            __fields[name] = fields_.Field(default)
        elif (
            (is_field or is_field_as_dict)
            and dtype is None
            ):
            raise exc.MissingTypeAnnotation(name)
        elif (
            (is_field or is_field_as_dict)
            and not typ.utl.check.is_field_type(dtype)
            ):
            raise exc.FieldAnnotationError(name, dtype)

        if is_field:
            __fields[name] = default
            __slots.append(name)
            defaults.append(name)
        elif is_field_as_dict:
            from .. import fields as fields_
            __fields[name] = fields_.Field(default)
            __slots.append(name)
            defaults.append(name)

    return defaults, __slots, __fields
