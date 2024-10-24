"""Strings utility functions."""

__all__ = (
    'camel_case_to_snake_case',
    'cname_for',
    'convert_for_repr',
    'is_snake_case_iterable',
    'is_snake_case_string',
    'is_valid_datetime_str',
    'is_valid_number_str',
    'isCamelCaseIterable',
    'isCamelCaseString',
    'pluralize',
    'redact_key_value_pair',
    'redact_string',
    'snake_case_to_camel_case',
    'validate_casing',
    )

from .. import codecs

from . import cfg
from . import enm
from . import exc
from . import lib
from . import obj
from . import typ


class Constants(cfg.Constants):
    """Constants specific to this file."""

    CACHED_CNAMES: dict[tuple[typ.AnyString, tuple[typ.AnyString, ...]], typ.AnyString] = {}


def pluralize(string: str) -> str:
    """Pluralize a singular string."""

    if (
        string.endswith(suffix := 'y')
        and not string.endswith('ay')
        and not string.endswith('ey')
        ):
        return string.removesuffix(suffix) + 'ies'
    elif string[-1] in {'s', 'z'}:
        return string
    else:
        return string + 's'


def isCamelCaseString(
    string: str
    ) -> lib.t.TypeGuard[typ.string[typ.camelCase]]:
    """
    Check if `string` is valid `camelCase`.

    ---

    Checks for strict [lower] `camelCase` (i.e. `RESTful casing`) \
    according to the [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html#s5.3-camel-case).

    Unlike Google, does *NOT* allow for an optional uppercase character \
    at the end of the `string`.

    """

    return _isCamelCaseString(string)


@lib.functools.cache
def _isCamelCaseString(string: str) -> bool:
    return bool(obj.Pattern.camelCase.match(string))


def is_snake_case_string(
    string: typ.AnyString
    ) -> lib.t.TypeGuard[typ.string[typ.snake_case]]:
    """
    Check if `string` is valid `snake_case`.

    ---

    Checks for strict [lower] `snake_case` (i.e. \
    `python attribute casing`).

    """

    return _is_snake_case_string(string)


@lib.functools.cache
def _is_snake_case_string(string: str) -> bool:
    return bool(obj.Pattern.snake_case.match(string))


@lib.functools.cache
def validate_casing(
    value: lib.t.Any,
    casing: typ.Casing
    ) -> lib.t.Optional[lib.Never]:
    """
    Assert value is `str` and of correct `Casing`.

    ---

    Raises `TypeError` if not `str`.

    Raises `StringCasingError` if `str` of incorrect `Casing`.

    """

    if not isinstance(value, str):
        raise TypeError(
            f'{value!s} is not a valid `str`.'
            )
    elif (
        casing == enm.SupportedCasing.snake_case.value
        and not is_snake_case_string(value)
        ):
        raise exc.StringCasingError(value, casing)
    elif (
        casing == enm.SupportedCasing.camelCase.value
        and not isCamelCaseString(value)
        ):
        raise exc.StringCasingError(value, casing)
    else:
        return None


@lib.functools.cache
def snake_case_to_camel_case(
    snake_case_string: typ.string[typ.snake_case]
    ) -> typ.string[typ.camelCase]:
    """Convert a valid `str[snake_case]` to `str[camelCase]`."""

    camelCaseString: typ.string[typ.camelCase] = (
        obj.Pattern.SnakeToCamelReplacements.sub(
            lambda match: match.group()[-1].upper(),
            snake_case_string.strip('_')
            )
        )

    return camelCaseString


@lib.functools.cache
def camel_case_to_snake_case(
    camelCaseString: typ.string[typ.camelCase]
    ) -> typ.string[typ.snake_case]:
    """Convert a valid `str[camelCase]` to `str[snake_case]`."""

    snake_case_string: typ.string[typ.snake_case] = (
        obj.Pattern.CamelToSnakeReplacements.sub(
            lambda match: '_' + match.group().lower(),
            camelCaseString
            )
        )

    return snake_case_string


@lib.t.overload
def is_snake_case_iterable(
    strings: 'typ.Mapping[str, typ.AnyType]'
    ) -> lib.t.TypeGuard[
        'typ.Mapping[typ.string[typ.snake_case], typ.AnyType]'
        ]: ...
@lib.t.overload
def is_snake_case_iterable(
    strings: lib.t.Iterable[str]
    ) -> 'lib.t.TypeGuard[lib.t.Iterable[typ.string[typ.snake_case]]]': ...
def is_snake_case_iterable(
    strings: 'lib.t.Iterable[str] | typ.Mapping[str, typ.AnyType]'
    ) -> lib.t.TypeGuard[
        lib.t.Union[
            'lib.t.Iterable[typ.string[typ.snake_case]]',
            'typ.Mapping[typ.string[typ.snake_case], typ.AnyType]'
            ]
        ]:
    """
    Check if all `strings` are `str[snake_case]`.

    ---

    Ignores leading and / or trailing underscores.

    """

    return all(
        is_snake_case_string(string)
        for _string
        in strings
        if (string := _string.strip('_'))
        )


@lib.t.overload
def isCamelCaseIterable(
    strings: 'typ.Mapping[str, typ.AnyType]'
    ) -> lib.t.TypeGuard[
        'typ.Mapping[typ.string[typ.camelCase], typ.AnyType]'
        ]: ...
@lib.t.overload
def isCamelCaseIterable(
    strings: lib.t.Iterable[str]
    ) -> 'lib.t.TypeGuard[lib.t.Iterable[typ.string[typ.camelCase]]]': ...
def isCamelCaseIterable(
    strings: 'lib.t.Iterable[str] | typ.Mapping[str, typ.AnyType]'
    ) -> lib.t.TypeGuard[
        lib.t.Union[
            'lib.t.Iterable[typ.string[typ.camelCase]]',
            'typ.Mapping[typ.string[typ.camelCase], typ.AnyType]'
            ]
        ]:
    """
    Check if all `strings` are `str[camelCase]`.

    ---

    Ignores leading and / or trailing underscores.

    """

    return all(
        isCamelCaseString(string)
        for _string
        in strings
        if (string := _string.strip('_'))
        )


@lib.t.overload
def cname_for(
    string: 'typ.AnyString | str',
    container: tuple[typ.string[typ.StringType], ...]
    ) -> lib.t.Optional[typ.string[typ.StringType]]: ...
@lib.t.overload
def cname_for(
    string: 'typ.AnyString | str',
    container: tuple[str, ...]
    ) -> lib.t.Optional[str]: ...
def cname_for(
    string: 'typ.AnyString | str',
    container: tuple[typ.string[typ.StringType] | str, ...]
    ) -> lib.t.Optional[typ.string[typ.StringType] | str]:
    """
    Get the actual, canonical name for valid `string`, as contained in \
    an arbitrary, valid, immutable `Container[str]` (i.e. a \
    `tuple[str, ...]`), agnostic of `string` casing and / or underscores.

    ---

    ### Example Usage

    ```python
    d = {
        '_id': 123,
        '_meaning_of_life': 42
        }

    cname_for(d, 'id')
    '_id'

    cname_for(d, 'meaningOfLife')
    42

    ```

    """

    v: typ.string[typ.StringType]
    if (__key := (string, container)) in Constants.CACHED_CNAMES:
        v = Constants.CACHED_CNAMES[__key]
    elif (
        (
            (k := (__k := string.strip('_'))) in container
            or (k := '_' + __k) in container
            or (k := __k + '_') in container
            or (k := '_' + __k + '_') in container
            )
        or (
            isCamelCaseString(__k)
            and (
                (
                    k := (_k := camel_case_to_snake_case(__k))
                    ) in container
                or (k := '_' + _k) in container
                or (k := _k + '_') in container
                or (k := '_' + _k + '_') in container
                )
            )
        or (
            is_snake_case_string(__k)
            and (
                (
                    k := (_k := snake_case_to_camel_case(__k))
                    ) in container
                or (k := '_' + _k) in container
                or (k := _k + '_') in container
                or (k := '_' + _k + '_') in container
                )
            )
        ):
        v = k
        Constants.CACHED_CNAMES[__key] = v
    else:
        v = None
        Constants.CACHED_CNAMES[__key] = v

    return v


def is_valid_number_str(
    any_str: str
    ) -> lib.t.TypeGuard[typ.string[typ.numeric]]:
    """
    Return `True` if python `str` is parsable as a valid \
    `numbers.Number`.

    """

    return bool(obj.Pattern.Number.match(any_str))


def is_valid_datetime_str(
    any_str: str
    ) -> lib.t.TypeGuard[typ.string[typ.datetime]]:
    """
    Return `True` if python `str` is parsable as a valid \
    `datetime`.

    """

    return bool(obj.Pattern.DateTime.match(any_str))


def redact_key_value_pair(key: str, value: str) -> str:
    """
    Redact potentially sensitive key, value pairs.

    ---

    Returns only the value (or a redacted version).

    """

    for id_, pattern in obj.KeyValueRedactionPatterns.items():
        if pattern.search(key) is not None:
            return f'[ REDACTED :: {id_} ]'

    return value


def redact_string(string: str) -> str:
    """Redact potentially sensitive values."""

    for id_, pattern in obj.RedactionPatterns.items():
        string = pattern.sub(
            repl=f'[ REDACTED :: {id_} ]',
            string=string
            )

    return string


@lib.t.overload
def convert_for_repr(
    obj_: 'typ.Mapping[typ.Primitive, typ.Serial]'
    ) -> dict[typ.Primitive, typ.Serial]: ...
@lib.t.overload
def convert_for_repr(obj_: typ.Primitive) -> typ.Primitive: ...
@lib.t.overload
def convert_for_repr(obj_: typ.Serial | lib.t.Any) -> typ.Serial: ...
def convert_for_repr(obj_: lib.t.Any) -> typ.Serial:
    """Recursively prepare `obj_` for neat `__repr__`."""

    if isinstance(obj_, str):
        redacted = redact_string(obj_)
        if len(redacted) > Constants.MAX_CHARS:
            lines = obj.StringWrapper.wrap(redacted)
            if len(lines) >= Constants.CUTOFF_LEN:
                lines.insert(Constants.CUTOFF_LEN, '\n[[...]]')
            lines.insert(0, Constants.M_LINE_TOKEN + '\n')
            as_array: list[typ.Serial] = ''.join(
                lines[:Constants.CUTOFF_LEN + 2]
                ).split('\n')
            return as_array
        else:
            return redacted
    elif obj_ is None or typ.utl.check.is_primitive(obj_):
        return obj_
    elif typ.utl.check.is_field(obj_):
        from ... import objects
        return repr(objects.typ.Field(obj_, obj_.type_))  # type: ignore[call-overload]
    elif typ.utl.check.is_typed(obj_):
        return {
            convert_for_repr(k): (
                convert_for_repr(redact_key_value_pair(k, v))
                if (
                    isinstance(k, str)
                    and isinstance((v := getattr(obj_, k)), str)
                    )
                else convert_for_repr(v)
                )
            for k
            in typ.utl.hint.collect_annotations(obj_)
            }
    elif typ.utl.check.is_mapping(obj_):
        return {
            convert_for_repr(k): (
                convert_for_repr(redact_key_value_pair(k, v))
                if (isinstance(k, str) and isinstance(v, str))
                else convert_for_repr(v)
                )
            for k, v
            in obj_.items()
            }
    elif typ.utl.check.is_array(obj_):
        if len(obj_) >= 1 and not all(isinstance(v, str) for v in obj_):
            return [
                convert_for_repr(v)
                for v
                in obj_
                ][:Constants.CUTOFF_LEN]
        else:
            return list(obj_)[:Constants.CUTOFF_LEN]
    elif isinstance(obj_, (lib.types.FunctionType, lib.types.MethodType)):
        rtn_tp: typ.Serial | lib.t.Any = (
            obj_.__annotations__.get('return', codecs.utl.encode(obj_))
            )
        return convert_for_repr(rtn_tp)
    else:
        return convert_for_repr(codecs.utl.encode(obj_))
