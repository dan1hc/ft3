"""
Overview
========

**Summary:** ft3 extension for logging.

---

Usage
-----

##### Controlled by the following environment variables / defaults.

```python
ENV = os.getenv('ENV', 'local').lower()
LOG_LEVEL = (
    os.getenv(
        'LOG_LEVEL',
        (
            'DEBUG'
            if ENV in {'dev', 'develop', 'local'}
            else 'INFO'
            )
        )
    ).upper()
# The default level for the logger.

LOG_TRACEBACK = os.getenv('LOG_TRACEBACK', 'true').lower() == 'true'
# Whether error tracebacks are attached to ERROR+ records.

LOG_FORMAT = os.getenv('LOG_FORMAT', 'json').lower()
# 'json' emits one line per record; 'pretty' indents each record.

INTERCEPT_PRINTS = os.getenv('INTERCEPT_PRINTS', 'true').lower() == 'true'
# Whether print() calls become INFO records carrying the printed text.
# LOG_PRINTS=true (the 1.x name) also disables interception.

```

"""

__all__ = (
	'cfg',
	'exc',
	'lib',
	'log',
	'obj',
	'Formatter',
	'typ',
	'utl',
)

from . import cfg
from . import exc
from . import lib
from . import obj
from . import typ
from . import utl

from .obj import log, Formatter
