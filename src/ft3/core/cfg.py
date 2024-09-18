"""Core constants."""

__all__ = (
    'Constants',
    )

from . import lib

if lib.t.TYPE_CHECKING:  # pragma: no cover
    from . import typ


class Constants:
    """Constant values shared across all of ft3."""

    PACAKGE = 'ft3'
    """Reference to package name."""

    CLASS_AS_DICT: 'typ.string[typ.snake_case]' = 'class_as_dict'
    """Common string reference."""

    DELIM = '-'
    """Common delimiter used throughout package."""

    INDENT = int(lib.os.getenv('INDENT', 2))
    """
    Default, package-wide indentation.

    ---

    Used for `__repr__`, log messages, etc.

    """

    UNDEFINED = f'[[{PACAKGE.upper()}_DEFAULT_PLACEHOLDER]]'
    """Placeholder for undefined values that should not be `None`."""

    ENV = lib.os.getenv('ENV', 'local').lower()
    """The lowered name of our runtime environment."""

    DEPLOY_ENVS = (
        'dev',
        'develop',
        'qa',
        'test',
        'testing',
        'stg',
        'stage',
        'staging',
        'uat',
        'prod',
        'production',
        )
    """Valid, non-local runtime environment names."""

    DELIM_REBASE = '_X_'

    __ANNOTATIONS__: 'typ.string[typ.snake_case]' = '__annotations__'
    __DATACLASS_FIELDS__: 'typ.string[typ.snake_case]' = '__dataclass_fields__'
    __HERITAGE__: 'typ.string[typ.snake_case]' = '__heritage__'
    __SLOTS__: 'typ.string[typ.snake_case]' = '__slots__'
    __MODULE__: 'typ.string[typ.snake_case]' = '__module__'
    __OPERATIONS__: 'typ.string[typ.snake_case]' = '__operations__'

    FIELDS: 'typ.string[typ.snake_case]' = 'fields'
    ENUMERATIONS: 'typ.string[typ.snake_case]' = 'enumerations'
    HASH_FIELDS: 'typ.string[typ.snake_case]' = 'hash_fields'

    DELETE: 'typ.string[typ.snake_case]'  = 'delete'
    GET: 'typ.string[typ.snake_case]'     = 'get'
    OPTIONS: 'typ.string[typ.snake_case]' = 'options'
    PATCH: 'typ.string[typ.snake_case]'   = 'patch'
    POST: 'typ.string[typ.snake_case]'    = 'post'
    PUT: 'typ.string[typ.snake_case]'     = 'put'
