"""Loggers typing."""

from .. import core

__all__ = (
    'AnyLogRecord',
    'LogRecordType',
    'LogRecordWithPrint',
    'LogRecordWithPrintAndTraceBack',
    'LogRecordWithTraceBack',
    'SupportedLogObject',
    *core.typ.__all__
    )

from .. core . typ import *

from . import lib

AnyLogRecord: lib.t.TypeAlias = lib.t.Union[
    'LogRecord',
    'LogRecordWithPrint',
    'LogRecordWithPrintAndTraceBack',
    'LogRecordWithTraceBack',
    ]
SupportedLogObject: lib.t.TypeAlias = lib.t.Union[
    'Mapping[AnyString, SupportedLogObject]',
    Object,
    type[Object],
    AnyString,
    'Array[SupportedLogObject]'
    ]


class LogRecord(lib.t.TypedDict):
    """Basic log record."""

    content: SupportedLogObject


class LogRecordWithPrint(LogRecord):
    """Log record with print message included."""

    printed: str


class LogRecordWithTraceBack(LogRecord):
    """Log record with traceback included."""

    traceback: str


class LogRecordWithPrintAndTraceBack(LogRecord):
    """A fully populated log record."""

    printed: str
    traceback: str


LogRecordType = lib.t.TypeVar('LogRecordType', bound=AnyLogRecord)
