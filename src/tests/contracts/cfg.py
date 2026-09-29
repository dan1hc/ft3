"""Constant values specific to contract tests."""

__all__ = ('Constants',)

from ft3 import core


class Constants(core.cfg.Constants):
	"""Constant values specific to contract tests."""

	CODE_PATTERN = r'^[a-z][a-z0-9_]*$'
	"""Every exception code is a snake_case identifier."""
