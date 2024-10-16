"""Loggers utility functions."""

__all__ = (
    'parse_incoming_log_message',
    )

from .. import core

from . import cfg
from . import exc
from . import lib
from . import typ


class Constants(cfg.Constants):
    """Constant values specific to this file."""


@lib.t.overload
def parse_incoming_log_message(
    msg: str,
    level: lib.t.Literal[30]
    ) -> typ.LogRecord | typ.LogRecordWithPrint: ...
@lib.t.overload
def parse_incoming_log_message(
    msg: str,
    level: (
        lib.t.Literal[0]
        | lib.t.Literal[10]
        | lib.t.Literal[20]
        | lib.t.Literal[40]
        | lib.t.Literal[50]
        )
    ) -> typ.LogRecord: ...
@lib.t.overload
def parse_incoming_log_message(
    msg: lib.t.Any,
    level: lib.t.Literal[30]
    ) -> typ.LogRecord | typ.LogRecordWithPrint | lib.Never: ...
@lib.t.overload
def parse_incoming_log_message(
    msg: lib.t.Any,
    level: (
        lib.t.Literal[0]
        | lib.t.Literal[10]
        | lib.t.Literal[20]
        | lib.t.Literal[40]
        | lib.t.Literal[50]
        )
    ) -> typ.LogRecord | lib.Never: ...
def parse_incoming_log_message(
    msg: lib.t.Any,
    level: (
        lib.t.Literal[0]
        | lib.t.Literal[10]
        | lib.t.Literal[20]
        | lib.t.Literal[30]
        | lib.t.Literal[40]
        | lib.t.Literal[50]
        )
    ) -> typ.LogRecord | typ.LogRecordWithPrint | lib.Never:
    """
    Parse incoming log message or warning to dict format.

    ---

    Raises an exception if msg type cannot be parsed.

    Automatically redacts common, sensitive data.

    """

    if isinstance(msg, str):
        if level != lib.logging.WARNING:
            return typ.LogRecord(content=msg)
        else:
            original_msg, _, warn_msg = msg.partition('.py')
            if warn_msg:
                warn_msg = ':'.join(warn_msg.split(':')[3:]).strip()
                warn_msg, *_ = warn_msg.rpartition('\n')
                if Constants.SILENCE_MSG in warn_msg:
                    warn_msg, _, printed = warn_msg.partition('\n')
                    return typ.LogRecordWithPrint(
                        content=warn_msg,
                        printed=printed
                        )
                else:
                    return typ.LogRecord(content=warn_msg)
            else:
                return typ.LogRecord(content=original_msg)
    elif core.typ.utl.check.is_object(msg):
        if isinstance(msg, type):
            return typ.LogRecord(content={msg.__name__: msg})
        else:
            return typ.LogRecord(content={msg.__class__.__name__: msg})
    elif core.typ.utl.check.is_array(msg):
        return typ.LogRecord(content=msg)
    elif core.typ.utl.check.is_mapping(msg):
        if (
            (dict_keys := sorted(msg.keys())) == ['content']
            or dict_keys == ['content', 'printed']
            ):
            msg_: typ.LogRecord | typ.LogRecordWithPrint = msg
            return msg_
        else:
            return typ.LogRecord(content=msg)
    else:
        raise exc.InvalidLogMessageTypeError(msg)
