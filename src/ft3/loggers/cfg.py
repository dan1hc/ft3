"""Loggers constants."""

__all__ = ('Constants',)

from .. import core

from . import lib


class Constants(core.cfg.Constants):
	"""Constant values shared across log modules."""

	FTIME_LOG = '%Y-%m-%dT%H:%M:%S'
	FTIME_LOG_MSEC = '%s.%03dZ'

	LOG_LEVEL = lib.os.getenv(
		'LOG_LEVEL',
		'DEBUG'
		if core.cfg.Constants.ENV in {'dev', 'develop', 'local'}
		else 'INFO',
	).upper()
	LOG_TRACEBACK = lib.os.getenv('LOG_TRACEBACK', 'true').lower() == 'true'
	LOG_FORMAT = lib.os.getenv('LOG_FORMAT', 'json').lower()
	"""`json` (one line per record, default) or `pretty` (indented)."""
	INTERCEPT_PRINTS = lib.os.getenv(
		'LOG_PRINTS', 'false'
	).lower() != 'true' and lib.os.getenv(
		'INTERCEPT_PRINTS', 'true'
	).lower() in ('1', 'true', 'yes', 'on')
	"""
    Whether `print()` calls become INFO log records. `LOG_PRINTS=true` \
    (1.x) or `INTERCEPT_PRINTS=false` leaves `print()` untouched.

    """

	PRINT_MSG = ' '.join(
		(
			f'print() intercepted by {core.cfg.Constants.PACKAGE}',
			'and logged instead. FIX: use log.debug().',
		)
	)
