"""Core exceptions."""

__all__ = (
    'BasePackageException',
    )

from . import lib
from . import typ


class BasePackageException(
    BaseException,
    lib.t.Generic[lib.Unpack[typ.ArgsType]]
    ):
    """
    Exception common to the entire package.

    ---

    Automatically handles serialization.

    """

    def __init__(self, msg: str, *args: lib.Unpack[typ.ArgsType]) -> None:
        """Instantiate `ft3` exception."""

        self._args = args
        super().__init__(msg)

    def __reduce__(
        self: typ.PackageExceptionType
        ) -> tuple[
            type[typ.PackageExceptionType],
            tuple[lib.Unpack[typ.ArgsType]]
            ]:
        return (
            self.__class__,
            self._args
            )
