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

LOG_PRINTS = os.getenv('LOG_PRINTS', 'false').lower() == 'true'
# Whether or not print() statements may be logged.

LOG_TRACEBACK = os.getenv('LOG_TRACEBACK', 'false').lower() == 'true'
# Whether or not error tracebacks may be logged.

```

"""

__all__ = (
    'cfg',
    'exc',
    'lib',
    'log',
    'obj',
    'typ',
    'utl',
    )

from . import cfg
from . import exc
from . import lib
from . import obj
from . import typ
from . import utl

from . obj import log
