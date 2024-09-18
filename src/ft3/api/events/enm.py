"""Api events enumerations."""

from .. import enm

__all__ = (
    'ErrorCode',
    'ErrorMap',
    'ErrorMessage',
    *enm.__all__
    )

from .. enm import *

from . import cfg
from . import lib


class Constants(cfg.Constants):
    """Modules specific to Api events Enums."""


class ErrorCode(lib.enum.Enum):
    """Common HTTP error codes."""

    RequestError              = 400
    NotAuthenticatedError     = 401
    NotAuthorizedError        = 403
    ResourceNotFoundError     = 404
    MethodNotAllowedError     = 405
    ResourceLockedError       = 423
    RateLimitedError          = 429
    UnexpectedError           = 500
    MethodNotImplementedError = 501


class ErrorMap(lib.enum.Enum):
    """Map of python exceptions to common HTTP errors."""

    SyntaxError            = 'RequestError'
    ConnectionRefusedError = 'NotAuthenticatedError'
    PermissionError        = 'NotAuthorizedError'
    FileNotFoundError      = 'ResourceNotFoundError'
    ModuleNotFoundError    = 'MethodNotAllowedError'
    OverflowError          = 'RateLimitedError'
    Exception              = 'UnexpectedError'
    NotImplementedError    = 'MethodNotImplementedError'

    TypeValidationError    = 'RequestError'


class ErrorMessage(lib.enum.Enum):
    """Common HTTP error messages by code."""

    _400 = 'Operation could not be completed due to an error with the request.'  # noqa
    _401 = 'Must be authenticated to complete the request.'
    _403 = 'Not authorized to complete the request.'
    _404 = 'Requested resource could not be found at the specified location.'
    _405 = 'Method not allowed for the requested resource.'
    _423 = 'Requested resource is currently locked for modification.'
    _429 = 'Too many requests.'
    _500 = 'An unexpected error occurred'
    _501 = 'Method not yet implemented for the requested resource.'
