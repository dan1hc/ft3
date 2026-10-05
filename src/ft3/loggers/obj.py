"""Loggers objects."""

__all__ = ('log', 'Formatter')

from .. import core

from . import cfg
from . import lib
from . import typ
from . import utl


class Constants(cfg.Constants):
	"""Constant values specific to this file."""

	FT3_MESSAGE = 'ft3_message'
	"""`LogRecord` attribute carrying the structured message."""

	CAPTURED_WARNING = lib.re.compile(r'^.+?:\d+: \w*Warning: ')
	"""Matches text produced by `warnings.formatwarning`."""


def level_for(name: str) -> int:
	"""Numeric level for a `LOG_LEVEL` name, `INFO` if unknown."""

	return lib.logging._nameToLevel.get(name.upper(), lib.logging.INFO)


def is_pretty() -> bool:
	"""Whether records are indented rather than single-line."""

	return Constants.LOG_FORMAT == 'pretty'


class Formatter(lib.logging.Formatter):
	"""
	Emits one valid JSON document per record.

	---

	```json
	{"level": "INFO", "timestamp": "2026-09-29T15:26:20.083Z", \
	"logger": "ft3", "message": {"content": "example"}}
	```

	Records produced by other libraries are wrapped the same way, \
	with their formatted text as `content`.

	"""

	converter = lib.time.gmtime
	default_time_format = Constants.FTIME_LOG
	default_msec_format = Constants.FTIME_LOG_MSEC

	def __init__(self, pretty: lib.t.Optional[bool] = None) -> None:
		super().__init__()
		self.pretty = pretty

	def format(self, record: lib.logging.LogRecord) -> str:
		"""Render the record as JSON."""

		message = getattr(record, Constants.FT3_MESSAGE, None)
		if message is None:
			message = {'content': record.getMessage()}
		envelope = {
			'level': record.levelname,
			'timestamp': self.formatTime(record),
			'logger': record.name,
			'message': message,
		}
		pretty = is_pretty() if self.pretty is None else self.pretty
		return lib.json.dumps(
			envelope,
			indent=Constants.INDENT if pretty else None,
			default=core.strings.utl.convert_for_repr,
		)


log = lib.logging.getLogger(Constants.PACKAGE)
"""
Centralized application log.

Pre-configured so you do not need to. This logger keeps the log \
stream machine-readable and free from pollution.

* emits one valid JSON document per record (single-line by default, \
indented with `LOG_FORMAT=pretty`)
* turns forgotten `print()` calls into INFO records that carry the \
printed text (disable with `INTERCEPT_PRINTS=false`)
* captures `warnings` and displays each once as a WARNING record
* attaches the full, untruncated traceback to ERROR and CRITICAL \
records logged while an exception is active (`LOG_TRACEBACK`)
* redacts values that should never be logged (api keys, tokens, \
passwords, connection-string passwords, card and social security \
numbers, and more)

---

Usage
-----

The expectation is this will be the only log used across an \
application.

* Set logging level through the `LOG_LEVEL` environment variable.
    \
    * Defaults to 'DEBUG' if `Constants.ENV` is either `local` (default) \
    or `dev`, otherwise 'INFO'.

---

Special Rules
-------------

* Can only log `str`, `dict`, `list`, and `Object` types.

* A `dict` shaped like a record (`{'content': ...}`) is logged as-is; \
any other mapping becomes the record's `content`.

---

Usage Examples
--------------

```python
import ft3

ft3.log.debug('example')
# >>>
# {"level": "DEBUG", "timestamp": "2026-09-29T15:30:01.061Z", \
# "logger": "ft3", "message": {"content": "example"}}

ft3.log.info({'str': 'example', 'a': 2})
# >>>
# {"level": "INFO", "timestamp": "2026-09-29T15:31:11.118Z", \
# "logger": "ft3", "message": {"content": {"a": 2, "str": "example"}}}

```

"""

log.setLevel(level_for(Constants.LOG_LEVEL))

lib.logging.basicConfig(handlers=[lib.logging.StreamHandler()])
for _handler in lib.logging.getLogger().handlers:
	if isinstance(_handler.formatter, (type(None), lib.logging.Formatter)):
		_handler.setFormatter(Formatter())

lib.warnings.simplefilter('once')
lib.logging.captureWarnings(True)
lib.logging.Logger.manager.loggerDict['py.warnings'] = log

if Constants.INTERCEPT_PRINTS:
	_print = lib.builtins.print

	def _reprint(
		*args: lib.t.Any,
		sep: lib.t.Optional[str] = ' ',
		end: lib.t.Optional[str] = '\n',
		file: lib.t.Any = None,
		flush: bool = False,
	) -> None:
		"""Route `print()` into the log unless it targets a file."""

		if file is not None and file not in (lib.sys.stdout, lib.sys.stderr):
			_print(*args, sep=sep, end=end, file=file, flush=flush)
			return None
		log.info(
			typ.LogRecordWithPrint(
				content=Constants.PRINT_MSG,
				printed=(sep or ' ').join(str(a) for a in args),
			),
			stacklevel=2,
		)
		return None

	lib.builtins.print = _reprint


def _monkey_log(
	level: (
		lib.t.Literal[0]
		| lib.t.Literal[10]
		| lib.t.Literal[20]
		| lib.t.Literal[30]
		| lib.t.Literal[40]
		| lib.t.Literal[50]
	),
	msg: lib.t.Any,
	args: 'lib.logging._ArgsType',
	exc_info: 'lib.logging._ExcInfoType' = None,
	extra: lib.t.Union[lib.t.Mapping[str, object], None] = None,
	stack_info: bool = False,
	stacklevel: int = 1,
	**kwargs: lib.t.Any,
) -> None:
	"""
	Replacement for `Logger._log` that builds structured records.

	---

	`record.msg` is the JSON-serialized message, so any foreign \
	formatter (a Lambda runtime's, say) still prints valid JSON; \
	`record.ft3_message` carries the structured form for `Formatter`.

	"""

	sinfo = None
	try:
		fn, lno, func, sinfo = log.findCaller(stack_info, stacklevel + 1)
	except ValueError:  # pragma: no cover
		fn, lno, func = '(unknown file)', 0, '(unknown function)'

	if isinstance(msg, str) and args:
		msg_ = msg % args
	else:
		msg_ = msg
	captured_warning = (
		level == lib.logging.WARNING
		and isinstance(msg_, str)
		and Constants.CAPTURED_WARNING.match(msg_) is not None
	)

	msg_dict = utl.parse_incoming_log_message(
		msg_, level, captured_warning=captured_warning
	)

	if isinstance(exc_info, BaseException):
		exc_tuple: lib.t.Any = (
			type(exc_info),
			exc_info,
			exc_info.__traceback__,
		)
	elif isinstance(exc_info, tuple):
		exc_tuple = exc_info
	elif exc_info is None or exc_info is True:
		exc_tuple = lib.sys.exc_info()
	else:
		exc_tuple = (None, None, None)

	converted: dict[str, lib.t.Any] = core.strings.utl.convert_for_repr(
		msg_dict
	)
	if (
		Constants.LOG_TRACEBACK
		and level >= lib.logging.ERROR
		and exc_tuple[1] is not None
		and not isinstance(exc_tuple[1], KeyboardInterrupt)
	):
		converted['traceback'] = [
			core.strings.utl.redact_string(line)
			for line in ''.join(
				lib.traceback.format_exception(*exc_tuple)
			).splitlines()
		]

	record = log.makeRecord(
		log.name,
		level,
		fn,
		lno,
		lib.json.dumps(
			converted,
			indent=Constants.INDENT if is_pretty() else None,
			sort_keys=True,
			default=core.strings.utl.convert_for_repr,
		),
		tuple(),
		None,
		func,
		{**(extra or {}), Constants.FT3_MESSAGE: converted},
		sinfo,
	)
	log.handle(record)


log._log = _monkey_log
