"""
Overview
========

**Author:** dan@1howardcapital.com

**Summary:** Zero-dependency python framework for object oriented development.
Implement _once_, document _once_, in _one_ place.

---

With ft3, you will quickly learn established best practice... \
or face the consequences of runtime errors that will break your code \
if you deviate from it.

Experienced python engineers will find a framework \
that expects and rewards intuitive magic method implementations, \
consistent type annotations, and robust docstrings.

Implement _pythonically_ with ft3 and you will only ever need to: \
implement _once_, document _once_, in _one_ place.

---

Getting Started
---------------

### Installation

Install from command line, with pip:

`$ pip install ft3`

"""

__all__ = (
	'api',
	'cli',
	'core',
	'docs',
	'log',
	'loggers',
	'objects',
	'configure',
	'Api',
	'Field',
	'File',
	'Object',
)

__version__ = '1.1.3'

from . import core
from . import cli
from . import docs
from . import loggers
from . import objects

from .loggers import log
from .objects import Field, Object

from . import api

from .api import Api, File


def configure(
	*,
	legacy_wire: 'bool | None' = None,
	redact_allow: 'tuple[str, ...] | list[str] | None' = None,
	log_format: 'str | None' = None,
	log_level: 'str | None' = None,
	log_traceback: 'bool | None' = None,
) -> None:
	"""
	Set ft3 settings from code, for applications that would rather \
	not depend on environment variables (or their deployment's \
	configuration) for a library setting.

	---

	Call it once, at import of your package, before serving:

	```python
	import ft3

	ft3.configure(legacy_wire=True, redact_allow=['arena_tokens'])
	```

	Each keyword overrides the matching environment variable \
	(`FT3_LEGACY_WIRE`, `LOG_REDACT_ALLOW`, `LOG_FORMAT`, `LOG_LEVEL`, \
	`LOG_TRACEBACK`); a keyword left `None` keeps the current value.

	"""

	if legacy_wire is not None:
		core.cfg.Constants.LEGACY_WIRE = legacy_wire
	if redact_allow is not None:
		core.strings.cfg.Constants.REDACT_ALLOW = tuple(redact_allow)
	if log_format is not None:
		loggers.cfg.Constants.LOG_FORMAT = log_format.lower()
	if log_level is not None:
		log.setLevel(loggers.obj.level_for(log_level))
	if log_traceback is not None:
		loggers.cfg.Constants.LOG_TRACEBACK = log_traceback
	return None
