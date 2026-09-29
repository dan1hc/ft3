"""Core exceptions."""

__all__ = ('BasePackageException',)

from . import lib
from . import typ

_CODE_PATTERN = lib.re.compile(r'(?<!^)(?=[A-Z])')
"""Splits a PascalCase class name ahead of each capital letter."""


class BasePackageException(Exception, lib.t.Generic[lib.Unpack[typ.ArgsType]]):
	"""
	Exception common to the entire package.

	---

	Subclasses `Exception`, so an ordinary `except Exception` \
	handler catches every ft3 error.

	Every subclass carries a stable, machine-readable `code` \
	(the snake_case form of its class name unless set explicitly) \
	that error responses and calling agents can key on without \
	parsing message text.

	Automatically handles serialization.

	"""

	code: lib.t.ClassVar[str] = 'base_package_exception'
	"""Stable, machine-readable identifier for this error."""

	def __init_subclass__(cls, **kwargs: lib.t.Any) -> None:
		super().__init_subclass__(**kwargs)
		if 'code' not in cls.__dict__:
			cls.code = _CODE_PATTERN.sub('_', cls.__name__).lower()

	def __init__(self, msg: str, *args: lib.Unpack[typ.ArgsType]) -> None:
		"""Instantiate `ft3` exception."""

		self._args = args
		super().__init__(msg)

	def __reduce__(
		self: typ.PackageExceptionType,
	) -> tuple[
		type[typ.PackageExceptionType], tuple[lib.Unpack[typ.ArgsType]]
	]:
		return (self.__class__, self._args)
