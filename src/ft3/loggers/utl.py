"""Loggers utility functions."""

__all__ = ('parse_captured_warning', 'parse_incoming_log_message', 'warn_once')

from .. import core

from . import cfg
from . import exc
from . import lib
from . import typ


class Constants(cfg.Constants):
	"""Constant values specific to this file."""

	WARNED: set[tuple[str, ...]] = set()
	"""Keys already warned about by `warn_once`."""


def warn_once(key: tuple[str, ...], content: dict[str, lib.t.Any]) -> bool:
	"""
	Log `content` at WARNING the first time `key` is seen in this \
	process, returning whether anything was logged.

	---

	Used for lenient-mode notices so a hot path never floods the log.

	"""

	if key in Constants.WARNED:
		return False
	Constants.WARNED.add(key)
	from . import obj

	obj.log.warning(content)
	return True


def parse_captured_warning(formatted: str) -> str:
	"""
	Reduce `warnings.formatwarning` output (`file.py:12: Category: \\
	message\\n  source`) to the warning message itself.

	"""

	first_line, _, _ = formatted.partition('\n')
	_, _, after_location = first_line.partition(': ')
	_, _, message = after_location.partition(': ')
	return message.strip() or first_line.strip()


@lib.t.overload
def parse_incoming_log_message(
	msg: str,
	level: lib.t.Literal[30],
	*,
	captured_warning: bool = False,
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
	),
	*,
	captured_warning: bool = False,
) -> typ.LogRecord: ...
@lib.t.overload
def parse_incoming_log_message(
	msg: lib.t.Any,
	level: lib.t.Literal[30],
	*,
	captured_warning: bool = False,
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
	),
	*,
	captured_warning: bool = False,
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
	),
	*,
	captured_warning: bool = False,
) -> typ.LogRecord | typ.LogRecordWithPrint | lib.Never:
	"""
	Parse incoming log message or warning to dict format.

	---

	Raises an exception if msg type cannot be parsed.

	With `captured_warning`, `msg` is the text produced by \
	`warnings.formatwarning` and only the warning message is kept.

	"""

	if isinstance(msg, str):
		if captured_warning:
			return typ.LogRecord(content=parse_captured_warning(msg))
		return typ.LogRecord(content=msg)
	elif core.typ.utl.check.is_object(msg):
		if isinstance(msg, type):
			return typ.LogRecord(content={msg.__name__: msg})
		else:
			return typ.LogRecord(content={msg.__class__.__name__: msg})
	elif core.typ.utl.check.is_array(msg):
		return typ.LogRecord(content=msg)
	elif core.typ.utl.check.is_mapping(msg):
		if (dict_keys := sorted(msg.keys())) == ['content'] or dict_keys == [
			'content',
			'printed',
		]:
			msg_: typ.LogRecord | typ.LogRecordWithPrint = msg
			return msg_
		else:
			return typ.LogRecord(content=msg)
	else:
		raise exc.InvalidLogMessageTypeError(msg)
