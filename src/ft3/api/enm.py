"""API enumerations."""

from .. import core

__all__ = (
    'Component',
    'Format',
    'Type',
    *core.enm.__all__
    )

from .. core . enm import *

from . import cfg
from . import lib
from . import typ


class Constants(cfg.Constants):
    """Modules specific to REST Enums."""


class Component(lib.enum.Enum):
    """
    [OpenAPI](https://swagger.io/docs/specification/components/) Components Enumeration.

    ---

    #### YAML Definition

    ```yaml
    components:
        # Reusable schemas (data models)
        schemas:
            ...
        # Reusable path, query, header and cookie parameters
        parameters:
            ...
        # Security scheme definitions (see Authentication)
        securitySchemes:
            ...
        # Reusable request bodies
        requestBodies:
            ...
        # Reusable responses, such as 401 Unauthorized or 400 Bad Request
        responses:
            ...
        # Reusable response headers
        headers:
            ...
        # Reusable examples
        examples:
            ...
        # Reusable links
        links:
            ...
        # Reusable callbacks
        callbacks:
            ...

    ```

    """

    callbacks       = 'callbacks'
    examples        = 'examples'
    headers         = 'headers'
    links           = 'links'
    parameters      = 'parameters'
    requestBodies   = 'requestBodies'
    responses       = 'responses'
    schemas         = 'schemas'
    securitySchemes = 'securitySchemes'


class Format(lib.enum.Enum):
    """
    [OpenAPI](https://swagger.io/docs/specification/data-models/data-types/#format) Type Formats Enumeration.

    ---

    Maps to python types.

    """

    boolean  = bool
    byte     = bytes
    date     = lib.datetime.date
    datetime = lib.datetime.datetime
    double   = lib.decimal.Decimal
    float    = float
    int32    = int


class Type(lib.enum.Enum):
    """
    [OpenAPI](https://swagger.io/docs/specification/data-models/data-types/) Types Enumeration.

    ---

    Maps to python types.

    """

    array   = list
    boolean = bool
    integer = int
    null    = typ.NoneType  # type: ignore[valid-type]
    number  = float
    object  = dict
    string  = str
