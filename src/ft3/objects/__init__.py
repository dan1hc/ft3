"""
Objects Overview
================

**Author:** dan@1howardcapital.com

**Summary:** `Object` and `Field`, the declaration everything else \
derives from.

---

Usage
-----

```python
import ft3


class Pet(ft3.Object):
    \"""A pet.\"""

    id_: ft3.Field[str]
    name: ft3.Field[str] = 'Fido'

```

See `AGENTS.md` for the rules and `Object` / `Field` for the options.

"""

__all__ = (
	'cfg',
	'enm',
	'exc',
	'fields',
	'lib',
	'metas',
	'objs',
	'queries',
	'typ',
	'utl',
	'Field',
	'Object',
)

from . import cfg
from . import enm
from . import exc
from . import fields
from . import lib
from . import metas
from . import objs
from . import queries
from . import typ
from . import utl

from .fields import Field
from .objs import Object
