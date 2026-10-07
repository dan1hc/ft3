"""
Overview
========

**Author:** dan@1howardcapital.com

**Summary:** Zero-dependency Python framework for object-oriented \
services, built for agents as its only users.

---

Declare an `Object` once; ft3 derives validation, JSON serialization, \
a REST API with an OpenAPI document, and structured logging from it. \
Every rule ft3 enforces is written down in `AGENTS.md`, every error \
names the fix, and `ft3 check` reports whether a package is correct \
before it is served.

---

Getting Started
---------------

```sh
pip install ft3
ft3 check my_pkg      # validate: routes, errors, per-field notices
ft3 openapi my_pkg    # write openapi.json as a build artifact
ft3 api my_pkg        # serve locally
```

Settings come from environment variables or `ft3.configure(...)`.

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

__version__ = '2.0.1'

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
