"""Codecs enumerations."""

from .. import enm

__all__ = (
    'ParseErrorRef',
    *enm.__all__
    )

from .. enm import *

from . import lib
from . import typ


class ParseErrorRef(lib.enum.Enum):
    """
    Valid ErrorRef Enumeration.

    """

    bool_decode           = typ.ErrorRef(
        'Could not decode valid JSON string to python `bool`.'
        )
    invalid_arr_decode    = typ.ErrorRef(
        'Could not decode valid JSON array to python: `invalid item type(s)`.'
        )
    invalid_arr_len       = typ.ErrorRef(
        'Could not decode valid JSON array to python: `invalid array length`.'
        )
    invalid_json          = typ.ErrorRef(
        'Could not deserialize string as valid JSON.'
        )
    invalid_keys_decode   = typ.ErrorRef(
        'Could not decode valid JSON object to python: `invalid keys`.'
        )
    invalid_map_decode    = typ.ErrorRef(
        ' '.join(
            (
                'Could not decode valid JSON object to python:',
                '`invalid item type(s)`.'
                )
            )
        )
    invalid_values_decode = typ.ErrorRef(
        'Could not decode valid JSON object to python: `invalid values`.'
        )
    number_decode         = typ.ErrorRef(
        ' '.join(
            (
                'Could not decode valid JSON string to python',
                '`numbers.Number`.'
                )
            )
        )
    null_decode           = typ.ErrorRef(
        'Could not decode valid JSON string to python `None`.'
        )
    datetime_decode       = typ.ErrorRef(
        'Could not decode value to valid `datetime`.'
        )
    literal_decode        = typ.ErrorRef(
        'Could not decode value to valid `Literal`.'
        )
    value_decode          = typ.ErrorRef('Could not decode invalid value.')
