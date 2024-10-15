"""Api objects module."""

__all__ = (
    'Component',
    'Content',
    'File',
    'Header',
    'Healthz',
    'Info',
    'Operation',
    'Api',
    'Parameter',
    'Path',
    'RequestBody',
    'ResponseObject',
    'Schema',
    'SecurityScheme',
    'ServerVariable',
    'ServerObject',
    'Tag',
    'FILES',
    'OBJECTS',
    'RESPONSE_HEADERS'
    )

from .. import cli
from .. import core

from .. import Field, Object

from . import cfg
from . import enm
from . import lib
from . import typ


class Constants(cfg.Constants):
    """Constant values specific to this file."""


FILES: dict[str, 'File'] = {}
"""All `Files` served by the API."""

OBJECTS: dict[str, 'type[typ.Object]'] = {}
"""All `Objects` served by the API."""


class Component(Object):
    """
    [OpenAPI](https://swagger.io/docs/specification/components/) Component.

    """

    _ref_: Field[lib.t.Optional[typ.AnyString]] = None


class Schema(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#schema-object) Schema Object.

    """

    type_: Field[list[typ.ApiType]] = Field(
        default=[enm.Type.string.value],
        enum=enm.Type
        )
    format_: Field[lib.t.Optional[typ.ApiFormat]] = Field(
        default=None,
        enum=enm.Format
        )

    description: Field[lib.t.Optional[str]] = None

    default: Field[lib.t.Optional[typ.ApiTypeValue]] = None
    enum: Field[lib.t.Optional[typ.Enum]] = None

    required: Field[lib.t.Optional[list[typ.string[typ.camelCase]]]] = None

    min_length: Field[lib.t.Optional[int]] = None
    max_length: Field[lib.t.Optional[int]] = None
    pattern: Field[lib.t.Optional[str]] = None

    minimum: Field[lib.t.Optional[float]] = None
    exclusive_minimum: Field[lib.t.Optional[bool]] = None
    maximum: Field[lib.t.Optional[float]] = None
    exclusive_maximum: Field[lib.t.Optional[bool]] = None
    multiple_of: Field[lib.t.Optional[float]] = None

    min_items: Field[lib.t.Optional[int]] = None
    max_items: Field[lib.t.Optional[int]] = None
    unique_items: Field[lib.t.Optional[bool]] = None

    read_only: Field[lib.t.Optional[bool]] = None
    write_only: Field[lib.t.Optional[bool]] = None

    items_: Field[lib.t.Optional['Schema']] = None
    properties: Field[
        lib.t.Optional[dict[typ.string[typ.camelCase], 'Schema']]
        ] = None

    all_of: Field[lib.t.Optional[list['Schema']]] = None
    any_of: Field[lib.t.Optional[list['Schema']]] = None
    one_of: Field[lib.t.Optional[list['Schema']]] = None

    def __post_init__(self) -> None:
        if isinstance(self.enum, lib.enum.EnumMeta):  # pragma: no cover
            self.enum = sorted(self.enum._value2member_map_)
        return super().__post_init__()

    @classmethod
    def from_obj(
        cls,
        obj: type[Object],
        /,
        **kwargs: lib.t.Any
        ) -> 'Schema':
        """Parse Schema definition from `Object`."""

        oname: typ.string[typ.PascalCase] = kwargs.pop('name', obj.__name__)
        kwargs.setdefault('ref', oname)

        properties = {
            (
                fname := (
                    core
                    .strings
                    .utl
                    .snake_case_to_camel_case(field_name)
                    )
                ): cls.from_type(
                    ref=fname + oname,
                    default=field.factory(),
                    **{
                        k: v
                        for k, v
                        in field.items()
                        if k not in Constants.SKIP_FIELDS
                        }
                    )
            for field_name, field
            in obj.__dataclass_fields__.items()
            }

        requirements = [
            (
                core
                .strings
                .utl
                .snake_case_to_camel_case(field_name)
                )
            for field_name, field
            in obj.__dataclass_fields__.items()
            if field.required
            ]

        return cls(
            properties=properties,
            required=requirements or None,
            type_=[enm.Type.object.value],
            **kwargs
            )

    @classmethod
    def from_type(
        cls,
        /,
        *,
        type_: lib.t.Any = None,
        **kwargs: lib.t.Any
        ) -> 'Schema':
        """Parse Schema definition from python `type`."""

        typ_ = kwargs.pop('type', type_)
        types_: list[typ.ApiType] = []

        if (
            typ.utl.check.is_union(typ_)
            or typ.utl.check.is_wrapper_type(typ_)
            ):
            schemae = [
                cls.from_type(type_=tp)
                for tp
                in typ.utl.check.get_type_args(typ_)
                ]
            return cls(any_of=schemae, **kwargs)
        elif typ.utl.check.is_typevar(typ_):
            if typ_.__constraints__:
                schemae = [
                    cls.from_type(type_=tp)
                    for tp
                    in typ_.__constraints__
                    ]
                return cls(one_of=schemae, **kwargs)
            elif typ_.__bound__:
                return cls(
                    all_of=[cls.from_type(type_=typ_.__bound__)],
                    **kwargs
                    )
            else:  # pragma: no cover
                return cls(**kwargs)
        elif typ.utl.check.is_literal(typ_):
            literal_tp = typ.utl.check.get_type_args(typ_)[0]
            return cls.from_type(type_=literal_tp, **kwargs)
        elif typ.utl.check.is_object_type(typ_):
            return cls.from_obj(typ_, **kwargs)
        elif typ.utl.check.is_uuid_type(typ_):
            types_.append(enm.Type.string.value)
            return cls(
                type_=types_,
                format_=enm.Format.uuid.value,
                **kwargs
                )
        elif typ.utl.check.is_typed(typ_):
            types_.append(enm.Type.object.value)
            return cls(
                properties={
                    core.strings.utl.snake_case_to_camel_case(annotation): (
                        cls.from_type(type_=tp)
                        )
                    for annotation, tp
                    in typ_.__annotations__.items()
                    },
                type_=types_,
                **kwargs
                )
        elif typ.utl.check.is_array_type(typ_):
            types_.append(enm.Type.array.value)
            if (tps := typ.utl.check.get_args(typ_)):
                tp = tps[0]
            else:
                tp = str
            return cls(
                type_=types_,
                items_=cls.from_type(type_=tp),
                **kwargs
                )
        elif typ.utl.check.is_mapping_type(typ_):
            types_.append(enm.Type.object.value)
            return cls(type_=types_, **kwargs)
        elif typ.utl.check.is_bool_type(typ_):
            types_.append(enm.Type.boolean.value)
            return cls(
                type_=types_,
                format_=enm.Format.boolean.value,
                **kwargs
                )
        elif typ.utl.check.is_none_type(typ_):
            types_.append(enm.Type.null.value)
            return cls(type_=types_, **kwargs)
        elif typ.utl.check.is_number_type(typ_):
            otp = lib.t.get_origin(typ_) or typ_
            if issubclass(otp, lib.decimal.Decimal):
                types_.append(enm.Type.number.value)
                return cls(
                    type_=types_,
                    format_=enm.Format.double.value,
                    **kwargs
                    )
            elif issubclass(otp, int):
                types_.append(enm.Type.integer.value)
                return cls(
                    type_=types_,
                    format_=enm.Format.int32.value,
                    **kwargs
                    )
            elif issubclass(otp, float):
                types_.append(enm.Type.number.value)
                return cls(
                    type_=types_,
                    format_=enm.Format.float.value,
                    **kwargs
                    )
            else:  # pragma: no cover
                types_.append(enm.Type.number.value)
                return cls(type_=types_, **kwargs)
        elif typ.utl.check.is_datetime_type(typ_):
            types_.append(enm.Type.string.value)
            return cls(
                type_=types_,
                format_=enm.Format.datetime.value,
                **kwargs
                )
        elif typ.utl.check.is_date_type(typ_):
            types_.append(enm.Type.string.value)
            return cls(
                type_=types_,
                format_=enm.Format.date.value,
                **kwargs
                )
        else:
            return cls(**kwargs)


class Parameter(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#parameter-object) Parameter Object.

    """

    name: Field[typ.string[typ.camelCase]]

    in_: Field[str] = Field(
        default=enm.ParameterLocation.query.value,
        enum=enm.ParameterLocation
        )

    description: Field[lib.t.Optional[str]] = None

    required: Field[bool] = False
    deprecated: Field[lib.t.Optional[bool]] = None

    schema: Field[lib.t.Optional[Schema]] = None


class Header(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#header-object) Header Object.

    """

    description: Field[lib.t.Optional[str]] = None
    schema: Field[lib.t.Optional[Schema]] = None


class Content(Component):
    """OpenAPI content for ContentType."""

    schema: Field[lib.t.Optional[Schema]] = None


class RequestBody(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#request-body-object) Request Body Object.

    """

    description: Field[lib.t.Optional[str]] = None
    content: Field[dict[typ.ContentType, Content]] = {
        enm.ContentType.json.value: Content()
        }


class ResponseObject(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#response-object) Request Body Object.

    """

    description: Field[str]

    headers: Field[lib.t.Optional[dict[str, Header]]] = None
    content: Field[dict[typ.ContentType, lib.t.Optional[Content]]] = {
        enm.ContentType.text.value: None
        }


class Tag(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#tag-object) Tag Object.

    """

    name: Field[str]
    description: Field[lib.t.Optional[str]] = None


class Operation(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#operation-object) Operation Object.

    """

    description: Field[lib.t.Optional[str]] = None
    summary: Field[lib.t.Optional[str]] = None

    tags: Field[lib.t.Optional[list[str]]] = None

    parameters: Field[lib.t.Optional[list[Parameter]]] = None
    request_body: Field[lib.t.Optional[RequestBody]] = None

    responses: Field[lib.t.Optional[dict[str, ResponseObject]]] = None

    @property
    def path_uri(self) -> str:
        """Path URI."""

        path_params = [
            param._ref_
            for param
            in (self.parameters or ())
            if param.in_ == enm.ParameterLocation.path.value
            ]

        uri = ''
        for tag_ in (self.tags or ()):
            for tag in tag_.split(':'):
                name = tag[0].lower() + tag[1:]
                uri += ('/' + core.strings.utl.pluralize(name))
                if tag in path_params:
                    uri += ('/{' + name + 'Id}')

        return uri


class Path(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#path-item-object) Path Item Object.

    """

    _resource_: Field[type[Object]]

    summary: Field[str]

    description: Field[lib.t.Optional[str]] = None

    delete: Field[lib.t.Optional[Operation]] = None
    get_: Field[lib.t.Optional[Operation]] = None
    options: Field[lib.t.Optional[Operation]] = None
    patch: Field[lib.t.Optional[Operation]] = None
    post: Field[lib.t.Optional[Operation]] = None
    put: Field[lib.t.Optional[Operation]] = None

    def update_options(self) -> None:
        """Update options operation for the endpoint."""

        tags: list[str] = []
        path_params: dict[str, Parameter] = {}
        for method in Constants.METHODS:
            operation: lib.t.Optional[Operation] = self[method]
            if operation is not None:
                path_params |= {
                    param._ref_: param
                    for param
                    in (operation.parameters or ())
                    if param.in_ == enm.ParameterLocation.path.value
                    and param._ref_ is not None
                    }
                for tag in (operation.tags or ()):
                    if tag not in tags:
                        tags.append(tag)

        response_obj = ResponseObject(
            description='Empty response.',
            headers=RESPONSE_HEADERS
            )

        self.options = Operation(
            summary='Options for the endpoint.',
            tags=tags,
            parameters=list(path_params.values()) or None,
            responses={'204': response_obj}
            )

        return None


class ServerVariable(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#server-variable-object) Server Variable Object.

    """

    default: Field[str]
    description: Field[lib.t.Optional[str]] = None


class ServerObject(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#server-object) Server Object.

    """

    url: Field[str]
    description: Field[lib.t.Optional[str]] = None
    variables: Field[lib.t.Optional[dict[str, ServerVariable]]] = None


class Info(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#info-object) Info Object.

    """

    title: Field[str]
    version: Field[str]

    summary: Field[lib.t.Optional[str]] = None
    description: Field[lib.t.Optional[str]] = None
    terms_of_service: Field[lib.t.Optional[str]] = None


class File(Object):
    """A file object, useful for serving static files."""

    path: Field[str]
    """The path at which to serve the file."""

    content: Field[bytes | str]
    """File content."""

    content_type: Field[str] = enm.ContentType.text.value

    def __post_init__(self) -> None:
        FILES[self.path] = self
        return super().__post_init__()


class Api(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#openapi-object) OpenAPI Object.

    """

    info: Field[Info]
    openapi: Field[str] = Constants.VERSION

    paths: Field[dict[str, Path]] = {}
    tags: Field[list[Tag]] = []

    servers: Field[lib.t.Optional[list[ServerObject]]] = None

    @classmethod
    def register(cls, obj_: type[typ.ObjectType]) -> type[typ.ObjectType]:
        """Register an `Object` to be served from the API."""

        OBJECTS[obj_.__name__] = obj_

        return obj_


class SecurityScheme(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#security-scheme-object) Security Scheme Object.

    """

    type_: Field[str] = Field(
        default=enm.SecuritySchemeType.apiKey.value,
        enum=enm.SecuritySchemeType
        )

    name_: Field[lib.t.Optional[str]] = None
    in_: Field[lib.t.Optional[str]] = Field(
        default=None,
        enum=enm.ApiKeyLocation
        )

    scheme: Field[lib.t.Optional[str]] = Field(
        default=None,
        enum=enm.SecurityHTTPScheme
        )

    description: Field[lib.t.Optional[str]] = None
    content: Field[dict[typ.ContentType, Content]] = {
        enm.ContentType.json.value: Content()
        }


class Healthz(Object):
    """Default application heartbeat."""

    status: Field[str] = 'OK'
    """Application status."""


RESPONSE_HEADERS = {
    header.value: Header(
        description=(
            '\\' + value
            if (value := str(enm.HeaderValue[header.name].value)) == '*'
            else value
            ),
        schema=Schema.from_type(type_=dict[str, str])
        )
    for header
    in enm.Header
    }
"""Default response headers."""


api_parser = cli.obj.parsers.add_parser(  # type: ignore[has-type]
    'api',
    formatter_class=lib.argparse.ArgumentDefaultsHelpFormatter,
    )
api_parser.add_argument(
    'package',
    help='the name or path to the package to be served',
    )
api_parser.add_argument(
    '--port',
    '-p',
    default=Constants.DEFAULT_PORT,
    help='the port to serve on',
    dest='port',
    )
api_parser.add_argument(
    '--version',
    '-v',
    default=Constants.DEFAULT_VERSION,
    help='the version of the api',
    dest='version',
    )
api_parser.add_argument(
    '--api-path',
    default=Constants.API_PATH,
    help='the base path from which to serve the API',
    dest='api_path',
    )
api_parser.add_argument(
    '--no-heartbeat',
    action='store_false',
    help='set to disinclude /healthz endpoint',
    dest='include_heartbeat',
    )
api_parser.add_argument(
    '--include-version-prefix',
    action='store_true',
    help='set to include a version prefix (ex. /v1/healthz)',
    dest='include_version_prefix',
    )
