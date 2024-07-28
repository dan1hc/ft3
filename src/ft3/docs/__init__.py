"""
Overview
========

**Summary:** ft3 extension for generating wiki documentation with [Sphinx](https://www.sphinx-doc.org).

---

Usage
-----

##### Document a package as follows.

```sh
$ pip install ft3[docs]
$ ft3 docs package_name
```

"""

__all__ = (
    'cfg',
    'enm',
    'lib',
    'obj',
    'utl',
    )

from . import cfg
from . import enm
from . import lib
from . import obj
from . import utl
