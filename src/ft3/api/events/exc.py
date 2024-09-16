"""Api events exceptions module."""

from .. import exc

__all__ = (
    'HTTPError',
    'MethodNotAllowedError',
    'MethodNotImplementedError',
    'NotAuthenticatedError',
    'NotAuthorizedError',
    'RateLimitedError',
    'RequestError',
    'ResourceNotFoundError',
    'ResourceLockedError',
    'UnexpectedError',
    *exc.__all__
    )

from ..  exc import *


class HTTPError(BasePackageException[str]):
    """Base HTTP Error class."""

    def __init__(self, message: str):
        super().__init__(message, message)


class RequestError(HTTPError):
    """Operation could not be completed due to an error with the request."""


class NotAuthenticatedError(HTTPError):
    """Must be authenticated to complete the request."""


class NotAuthorizedError(HTTPError):
    """Not authorized to complete the request."""


class ResourceNotFoundError(HTTPError):
    """Requested resource could not be found at the specified location."""


class ResourceLockedError(HTTPError):
    """Requested resource is currently locked for modification."""


class RateLimitedError(HTTPError):
    """Too many requests."""


class MethodNotAllowedError(HTTPError):
    """Method not allowed for the requested resource."""


class MethodNotImplementedError(HTTPError):
    """Method not yet implemented for the requested resource."""


class UnexpectedError(HTTPError):
    """An unexpected error occurred."""
