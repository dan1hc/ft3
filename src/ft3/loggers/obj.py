"""Loggers objects."""

__all__ = (
    'log',
    )

from .. import core

from . import cfg
from . import lib
from . import typ
from . import utl


class Constants(cfg.Constants):
    """Constant values specific to this file."""


lib.logging.Formatter.converter = lib.time.gmtime
lib.logging.Formatter.default_time_format = Constants.FTIME_LOG
lib.logging.Formatter.default_msec_format = Constants.FTIME_LOG_MSEC
lib.logging.basicConfig(
    format=(' ' * Constants.INDENT).join(
        (
            '{\n',
            '"level": %(levelname)s,\n',
            '"timestamp": %(asctime)s,\n',
            '"logger": ft3,\n',
            '"message": %(message)s\n}',
            )
        ),
    )

log = lib.logging.getLogger(__name__)
"""
Centralized application log.

Pre-configured so you do not need to. By default, this loggger \
will do everything it can to keep your log stream as actionable \
and free from pollution as possible.

* emits neatly formatted JSON log messages
* intercepts forgotten print statements
    \
    * silences them in all deployed environments
* intercepts forgotten debug-level logs
    \
    * silences them in deployed environments > dev
* intercepts irritating warnings, displaying them once as \
neatly formatted warning level log messages
* automatically redacts things that should never be logged \
in the first place (like API Keys, credentials, SSN's, etc.)

---

Usage
-----

The expectation is this will be the only log used across \
an application.

* Set logging level through the `LOG_LEVEL` environment variable.
    \
    * Defaults to 'DEBUG' if `Constants.ENV` is either `local` (default) \
    or `dev`, otherwise 'INFO'.

---

Special Rules
-------------

* Can only log `str`, `dict`, and `Object` types.

* Automatically redacts almost all sensitive data, including \
api keys, tokens, credit card numbers, connection strings, \
and secrets.

* All `warnings` will be filtered through this log and \
displayed only once.

* All `print` statements will be silenced *except* when \
`Constants.ENV` is set to 'local' (its default if `ENV` \
is unavailable in `os.environ` at runtime).
    \
    * Best practice is to set log level to 'DEBUG' and \
    use the `log.debug` method in place of `print` statements.
    \
    * `warnings` will be displayed once for all `print` \
    statements that would otherwise be silenced in any \
    non-local development environment.

---

Usage Examples
--------------

```python
import ft3

ft3.log.debug('example')
# >>>
# {
#   "level": DEBUG,
#   "timestamp": 2024-02-25T15:30:01.061Z,
#   "logger": ft3,
#   "message": {
#     "content": "example"
#   }
# }

ft3.log.info({'str': 'example', 'a': 2})
# >>>
# {
#   "level": INFO,
#   "timestamp": 2024-02-25T15:31:11.118Z,
#   "logger": ft3,
#   "message": {
#     "a": 2,
#     "str": "example"
#   }
# }


class Pet(ft3.Object):
    \"""A pet.\"""

    id_: ft3.Field[str]
    _alternate_id: ft3.Field[str]

    name: ft3.Field[str]
    type: ft3.Field[str]
    in_: ft3.Field[str]
    is_tail_wagging: ft3.Field[bool] = True


ft3.log.debug(Pet)
# >>>
# {
#   "level": DEBUG,
#   "timestamp": 2024-02-25T15:30:01.339Z,
#   "logger": ft3,
#   "message": {
#     "Pet": {
#       "_alternate_id": "Field[str]",
#       "id": "Field[str]",
#       "in": "Field[str]",
#       "is_tail_wagging": "Field[bool]",
#       "name": "Field[str]",
#       "type": "Field[str]"
#     }
#   }
# }

ft3.log.debug(
    Pet(
        id_='abc1234',
        name='Fido',
        type='dog',
        )
    )
# >>>
# {
#   "level": DEBUG,
#   "timestamp": 2024-02-25T15:30:01.450Z,
#   "logger": ft3,
#   "message": {
#     "Pet": {
#       "_alternate_id": null,
#       "id": "abc1234",
#       "in": null,
#       "is_tail_wagging": true,
#       "name": "Fido",
#       "type": "dog"
#     }
#   }
# }

```

"""

log.setLevel(lib.logging._nameToLevel[Constants.LOG_LEVEL])

lib.warnings.simplefilter('once')
lib.logging.captureWarnings(True)
lib.logging.Logger.manager.loggerDict['py.warnings'] = log

if not Constants.LOG_PRINTS:

    _print = __builtins__['print']  # type: ignore[index]

    def _reprint(*args: lib.t.Any, **kwargs: lib.t.Any) -> None:
        if Constants.ENV in Constants.DEPLOY_ENVS:  # pragma: no cover (still covered)
            lib.warnings.warn(
                '\n'.join(
                    (
                        Constants.SILENCE_MSG,
                        *[str(a) for a in args],
                        )
                    )
                )
        else:
            lib.warnings.warn(Constants.WARN_MSG, stacklevel=1)
            _print(*args, **kwargs)

    __builtins__['print'] = _reprint


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
    exc_info: 'lib.logging._ExcInfoType' = True,
    extra: lib.t.Union[lib.t.Mapping[str, object], None] = None,
    stack_info: bool = False,
    stacklevel: int = 1,
    **kwargs: lib.t.Any
    ) -> None:
    """Monkey patch for `logger._log`."""

    sinfo = None
    if lib.logging._srcfile:  # pragma: no cover
        try:
            fn, lno, func, sinfo = log.findCaller(stack_info, stacklevel)
        except ValueError:
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
    else:  # pragma: no cover
        fn, lno, func = "(unknown file)", 0, "(unknown function)"

    if msg == '%s' and args and isinstance(args, tuple):  # pragma: no cover
        msg_ = args[0]
    else:
        msg_ = msg

    msg_dict = utl.parse_incoming_log_message(msg_, level)

    if isinstance(exc_info, BaseException):
        exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
    elif not isinstance(exc_info, tuple):
        exc_info = lib.sys.exc_info()
    if (
        Constants.LOG_TRACEBACK
        and level >= lib.logging.ERROR
        and any(exc_info)
        and not isinstance(exc_info[1], KeyboardInterrupt)
        ):
        if 'printed' in msg_dict:  # pragma: no cover (still covered)
            msg_final = typ.LogRecordWithPrintAndTraceBack(
                content=msg_dict['content'],
                printed=msg_dict['printed'],  # type: ignore[typeddict-item]
                traceback=''.join(lib.traceback.format_exception(*exc_info))
                )
        else:  # pragma: no cover (still covered)
            msg_final = typ.LogRecordWithTraceBack(
                content=msg_dict['content'],
                traceback=''.join(lib.traceback.format_exception(*exc_info))
                )
    else:
        msg_final = msg_dict

    record = log.makeRecord(
        log.name,
        level,
        fn,
        lno,
        lib.textwrap.indent(
            lib.json.dumps(
                core.strings.utl.convert_for_repr(msg_final),
                default=core.strings.utl.convert_for_repr,
                indent=Constants.INDENT,
                sort_keys=True
                ),
            Constants.INDENT * ' '
            ).lstrip(),
        tuple(),
        None,
        func,
        extra,
        sinfo
        )
    log.handle(record)


log._log = _monkey_log
