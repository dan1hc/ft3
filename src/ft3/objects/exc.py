"""Objects exceptions module."""

from .. import core

__all__ = (
    'FieldAnnotationError',
    'IncorrectCasingError',
    'IncorrectDefaultTypeError',
    'IncorrectTypeError',
    'InvalidComparisonTypeError',
    'InvalidContainerComparisonTypeError',
    'InvalidFieldAdditionError',
    'InvalidFieldRedefinitionError',
    'InvalidObjectComparisonError',
    'MissingTypeAnnotation',
    'ReservedKeywordError',
    'TypeValidationError',
    *core.exc.__all__
    )

from .. core . exc import *

from . import cfg
from . import lib


class Constants(cfg.Constants):
    """Constant values specific to this file."""


class InvalidFieldAdditionError(BasePackageException[str]):
    """Cannot add new fields after a class has already been defined."""

    def __init__(self, name: str):
        super().__init__(
            ' '.join(
                (
                    'Cannot add fields after a class has already',
                    'been defined.',
                    f'\nFIELD: {name}'
                    )
                ),
            name
            )


class InvalidFieldRedefinitionError(BasePackageException[str]):
    """Cannot redefine field for the same key with a different name."""

    def __init__(self, name: str):
        super().__init__(
            ' '.join(
                (
                    'Cannot redefine field for the same key',
                    'with a different name.',
                    f'\nFIELD: {name}'
                    )
                ),
            name
            )


class IncorrectCasingError(BasePackageException[lib.t.Iterable[str]]):
    """Incorrect field casing."""

    def __init__(self, fields: lib.t.Iterable[str]):
        super().__init__(
            ' '.join(
                (
                    'All fields for all Object derivatives',
                    'must be `string[snake_case]`.',
                    f'\nFIELDS: {sorted(fields)!s}',
                    )
                ),
            fields
            )


class IncorrectDefaultTypeError(
    BasePackageException[str, type[lib.t.Any], lib.t.Any]
    ):
    """
    Error raised when a field's default value is not of an allowed type.

    """

    def __init__(
        self,
        name: str,
        dtype: type[lib.t.Any],
        value: lib.t.Any
        ) -> None:
        super().__init__(
            ' '.join(
                (
                    f"Field: '{name}',",
                    f"only supports type: '{dtype!s}',",
                    f'Default supplied: {value!s}',
                    f"is of type: '{type(value)!s}'",
                    )
                ),
            *(name, dtype, value)
            )


class IncorrectTypeError(
    BasePackageException[str, lib.t.Any, lib.t.Any]
    ):
    """Error raised when a field value is not of an allowed type."""

    def __init__(
        self,
        name: str,
        dtype: lib.t.Any,
        value: lib.t.Any
        ) -> None:
        super().__init__(
            ' '.join(
                (
                    f"Field: '{name}',",
                    f"only supports type: '{dtype!s}',",
                    f'Value supplied: {value!s}',
                    f"is of type: '{type(value)!s}'",
                    )
                ),
            *(name, dtype, value)
            )


class InvalidComparisonTypeError(
    BasePackageException[str, lib.t.Any, lib.t.Any]
    ):
    """
    Error raised when comparing a field with a value of a different \
    type.

    """

    def __init__(
        self,
        name: str,
        dtype: lib.t.Any,
        value: lib.t.Any
        ) -> None:
        super().__init__(
            ' '.join(
                (
                    f"Cannot compare field: '{name}',",
                    f"of type: '{dtype!s}',",
                    f'with the value supplied: {value!s}',
                    f"of type: '{type(value)!s}'",
                    )
                ),
            *(name, dtype, value)
            )


class InvalidContainerComparisonTypeError(
    BasePackageException[str, lib.t.Any, lib.t.Any]
    ):
    """
    Error raised when checking for membership or similarity against a \
    non-Iterable field.

    """

    def __init__(
        self,
        name: str,
        dtype: lib.t.Any,
        value: lib.t.Any
        ) -> None:
        super().__init__(
            ' '.join(
                (
                    f"Field: '{name}',",
                    f"of type: '{dtype!s}',",
                    f'cannot contain or be similar to: {value!s},',
                    'as this field is not an iterable.'
                    )
                ),
            *(name, dtype, value)
            )


class InvalidObjectComparisonError(
    BasePackageException[lib.t.Any, lib.t.Any]
    ):
    """
    Error raised when comparing an object with another with differing \
    fields.

    """

    def __init__(
        self,
        obj: lib.t.Any,
        other: lib.t.Any
        ) -> None:
        super().__init__(
            ' '.join(
                (
                    f"Cannot compare object: '{obj!s}',",
                    f"of type: '{obj.__class__.__name__}',",
                    f'with object: {other!s}',
                    f"of type: '{other.__class__.__name__}'",
                    )
                ),
            *(obj, other)
            )


class FieldAnnotationError(
    BasePackageException[
        str,
        lib.t.Optional[lib.t.Union[type[lib.t.Any], lib.t.ForwardRef]]
        ]
    ):
    """Incomplete type annotation."""

    def __init__(
        self,
        name: str,
        dtype: lib.t.Optional[
            lib.t.Union[
                type[lib.t.Any],
                lib.t.ForwardRef
                ]
            ]
        ):
        stype: str = getattr(dtype, '__name__', str(dtype))
        super().__init__(
            ' '.join(
                (
                    'All type annotations for Object derivatives',
                    'must be of a generic Field type such as',
                    '`Field[int] or Field[str]`.',
                    f'\nFIELD: {name}, TYPE: {stype}',
                    f'\nSUGGESTION: Field[{stype}]',
                    )
                ),
            *(name, dtype)
            )


class MissingTypeAnnotation(BasePackageException[str]):
    """Incomplete type annotation."""

    def __init__(self, name: str):
        super().__init__(
            ' '.join(
                (
                    'Type for all Fields must be annotated.',
                    f'\nFIELD: {name}',
                    )
                ),
            name
            )


class ReservedKeywordError(BasePackageException[str]):
    """Invalid keyword."""

    def __init__(self, name: str):
        super().__init__(
            ' '.join(
                (
                    'The following keyword is reserved for special',
                    f'purposes within {Constants.PACAKGE} and may',
                    'not be used / overwritten in class definitions.',
                    f'\nKEYWORD: {name}',
                    f'\nSUGGESTION: {name}_',
                    )
                ),
            name
            )


class TypeValidationError(
    BasePackageException[str, lib.t.Any, core.codecs.enm.ParseErrorRef]
    ):
    """Error raised when a field value could not be parsed as valid type."""

    def __init__(
        self,
        name: str,
        dtype: lib.t.Any,
        error_ref: core.codecs.enm.ParseErrorRef
        ) -> None:
        super().__init__(
            ' '.join(
                (
                    error_ref.value,
                    f"Field: '{name}',",
                    f"only supports type: '{dtype!s}',"
                    )
                ),
            *(name, dtype, error_ref)
            )
