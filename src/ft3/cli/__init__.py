"""
Overview
========

**Summary:** Primary command-line interface (CLI) to ft3.

---

Usage
-----

```sh
$ ft3 --help
```

"""

__all__ = (
    'cfg',
    'lib',
    'obj',
    'main',
    'utl',
    )

from . import cfg
from . import lib
from . import obj
from . import utl

from . utl import main
