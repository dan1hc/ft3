"""
Summary
-------

A simple python API and package that can be copy / pasted / replaced.

"""

__all__ = (
    'api',
    'pkg'
    )

from .. import log

from . import api
from . import pkg

print('SOMEONE LEFT THIS PRINT STATEMENT AND FORGOT ABOUT IT')
print('GOOD THING THIS PACKAGE AUTOMATICALLY SILENCES PRINT STATEMENTS')
print('IF IT DETECTS AN ENV >= DEV.')
print('...')
print('THIS HELPS PREVENT LOG POLLUTION')

log.debug('BEST PRACTICE IS TO USE A DEBUG LEVEL LOG MESSAGE INSTEAD')