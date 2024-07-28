"""Strings exceptions."""

from .. import exc

__all__ = (
    'StringCasingError',
    *exc.__all__
    )

from .. exc import *

from . import typ


class StringCasingError(BasePackageException[str, typ.Casing]):
    """Exception raised on invalid string casing."""

    def __init__(self, string: str, valid_case: typ.Casing) -> None:
        super().__init__(
            ' '.join(
                (
                    string,
                    'is not a valid',
                    f'`{valid_case!s}` string.'
                    )
                ),
            string,
            valid_case
            )
