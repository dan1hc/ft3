"""Api enumerations."""

from .. import core

__all__ = (
    'ApiKeyLocation',
    'Component',
    'ContentType',
    'Format',
    'Header',
    'HeaderValue',
    'ParameterLocation',
    'SecurityHTTPScheme',
    'SecuritySchemeType',
    'Type',
    *core.enm.__all__
    )

from .. core . enm import *

from . import cfg
from . import lib


class Constants(cfg.Constants):
    """Modules specific to Api Enums."""


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

    boolean  = 'boolean'
    byte     = 'byte'
    date     = 'date'
    datetime = 'datetime'
    double   = 'double'
    float    = 'float'
    int32    = 'int32'
    uuid     = 'uuid'


class Type(lib.enum.Enum):
    """
    [OpenAPI](https://swagger.io/docs/specification/data-models/data-types/) Types Enumeration.

    ---

    Maps to python types.

    """

    array   = 'array'
    boolean = 'boolean'
    integer = 'integer'
    null    = 'null'
    number  = 'number'
    object  = 'object'
    string  = 'string'


class SecurityHTTPScheme(lib.enum.Enum):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#security-scheme-object) Security HTTP Scheme Enumeration.

    """

    basic  = 'basic'
    bearer = 'bearer'


class SecuritySchemeType(lib.enum.Enum):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#security-scheme-object) Security Types Enumeration.

    """

    http          = 'http'
    apiKey        = 'apiKey'
    oauth2        = 'oauth2'
    openIdConnect = 'openIdConnect'


class ApiKeyLocation(lib.enum.Enum):
    """
    ApiKey In Enumeration.

    ---

    There are three possible locations specified by the in field:

    1. `header`
    2. `query`
    3. `cookie`

    """

    header = 'header'
    query  = 'query'
    cookie = 'cookie'


class ParameterLocation(lib.enum.Enum):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#parameter-object) Paramater In Enumeration.

    ---

    There are four possible parameter locations specified by the in field:

    1. `path` Used together with Path Templating, where the parameter value is actually part of the operation's URL. This does not include the host or base path of the API. For example, in /items/{itemId}, the path parameter is itemId.
    2. `query` Parameters that are appended to the URL. For example, in /items?id=###, the query parameter is id.
    3. `header` Custom headers that are expected as part of the request. Note that RFC7230 states header names are case insensitive.
    4. `cookie` Used to pass a specific cookie value to the API.

    """

    path   = 'path'
    query  = 'query'
    header = 'header'
    cookie = 'cookie'


class ContentType(lib.enum.Enum):
    """Common content types."""

    any_ = '*/*'
    html = 'text/html'
    icon = 'image/x-icon'
    json = 'application/json'
    png  = 'image/png'
    text = 'text/plain'


class Header(lib.enum.Enum):
    """Default headers."""

    accessControlAllowCredentials = 'Access-Control-Allow-Credentials'
    accessControlAllowHeaders     = 'Access-Control-Allow-Headers'
    accessControlMaxAge           = 'Access-Control-Max-Age'
    accessControlAllowMethods     = 'Access-Control-Allow-Methods'
    accessControlAllowOrigin      = 'Access-Control-Allow-Origin'
    connection                    = 'Connection'
    contentLength                 = 'Content-Length'
    contentType                   = 'Content-Type'
    date                          = 'Date'


class HeaderValue(lib.enum.Enum):
    """Default headers."""

    accessControlAllowCredentials = True
    accessControlAllowHeaders     = '*'
    accessControlMaxAge           = 86400
    accessControlAllowMethods     = '*'
    accessControlAllowOrigin      = '*'
    connection                    = 'keep-alive'
    contentLength                 = '*'
    contentType                   = ContentType.json.value
    date                          = "'%Y-%m-%dT%H:%M:%S.%f%z'"
