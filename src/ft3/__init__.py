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
    'Api',
    'Field',
    'File',
    'Object'
    )

__version__ = '0.1.6'

from . import core
from . import cli
from . import docs
from . import loggers
from . import objects

from . loggers import log
from . objects import Field, Object

from . import api

from . api import Api, File
