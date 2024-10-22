"""Api utility functions."""

__all__ = (
    'api_from_package',
    'filter_to_unique_params',
    'operation_from_object',
    'parameters_from_object',
    'paths_from_object',
    'response_type_from_object',
    'serve'
    )

from .. import core

from .. import Object

from . import cfg
from . import enm
from . import lib
from . import obj
from . import typ

from . obj import OBJECTS, REQUEST_HEADERS, RESPONSE_HEADERS, SECURITY


class Constants(cfg.Constants):
    """Constants specific to this file."""

    ID = 'id'

    IN = 'in'
    REQUIRED = 'required'
    SCHEMA: typ.string[lib.t.Any] = 'schema'

    ONE: lib.t.Literal['ONE'] = 'ONE'
    MANY: lib.t.Literal['MANY'] = 'MANY'
    EMPTY: lib.t.Literal['EMPTY'] = 'EMPTY'


def parameters_from_object(cls: type[Object]) -> list[obj.Parameter]:
    """Generate RESTful API `Paremeter` Objects from an `Object`."""

    parameters: list[obj.Parameter] = []
    for name, field in cls.__dataclass_fields__.items():
        if name in cls.hash_fields:
            paramater_location = enm.ParameterLocation.path.value
            required = True
        else:
            paramater_location = enm.ParameterLocation.query.value
            required = False
        if name.strip('_') == Constants.ID:
            name_: typ.string[typ.camelCase] = (
                core.strings.utl.snake_case_to_camel_case(
                    core.strings.utl.camel_case_to_snake_case(cls.__name__)
                    )
                + 'Id'
                )
        else:
            name_ = core.strings.utl.snake_case_to_camel_case(name)
        parameter = obj.Parameter(
            _ref_=cls.__name__,
            name=name_,
            description=field.description,
            in_=paramater_location,
            schema=obj.Schema.from_type(
                **{
                    k: v
                    for k, v
                    in field.items()
                    if k not in Constants.SKIP_FIELDS
                    }
                ),
            required=required or field.required
            )
        parameters.append(parameter)

    return parameters


def response_type_from_object(
    cls: type[Object],
    method: typ.ApiMethod
    ) -> typ.ApiResponseType:
    """Calculate response type from an `Object`."""

    callback = cls.__operations__.get(method)  # type: ignore[call-overload]
    if callback is None:  # pragma: no cover
        return Constants.EMPTY

    tp = callback.__annotations__.get('return')

    if typ.utl.check.is_array_of_obj_type(tp):
        return Constants.MANY
    elif typ.utl.check.is_object_type(tp):
        return Constants.ONE
    else:
        return Constants.EMPTY


def filter_to_unique_params(
    parameters: list[obj.Parameter]
    ) -> list[obj.Parameter]:
    """Filters to a unique parameter set."""

    params: list[obj.Parameter] = []
    param_refs: list[str] = []

    for parameter in parameters:
        if parameter.name not in param_refs:
            param_refs.append(parameter.name)
            params.append(parameter)

    return params


def operation_from_object(
    cls: type[Object],
    method: typ.ApiMethod,
    parent_tags: lib.t.Optional[list[str]] = None,
    parent_path_parameters: lib.t.Optional[list[obj.Parameter]] = None,
    include_default_response_headers: bool = True,
    ) -> lib.t.Optional[obj.Operation]:
    """Generate RESTful API `Operation` from an `Object`."""

    parameters = parameters_from_object(cls)

    if (request_headers := REQUEST_HEADERS.get(cls.__name__)):
        parameters.extend(request_headers[method])

    response_headers: dict[str, obj.Header] = {}
    if include_default_response_headers:
        response_headers.update(obj.DEFAULT_RESPONSE_HEADERS)

    response_headers_by_method = RESPONSE_HEADERS.get(cls.__name__)
    if response_headers_by_method is not None:
        response_headers.update(response_headers_by_method[method])

    security: list[dict[str, list[str]]] = []
    if (security_schemes := SECURITY.get(cls.__name__)):
        security.extend(
            [
                {scheme.name_: []}
                for scheme
                in security_schemes[method]
                ]
            )

    tags: list[str] = []
    if parent_tags is not None:
        tags.extend(parent_tags)
    tags.append(core.strings.utl.snake_case_to_camel_case(cls.__name__))

    if not cls.hash_fields:
        parameters.clear()

    response_type = response_type_from_object(cls, method)

    match response_type:
        case Constants.MANY:
            response_obj = obj.ResponseObject(
                description='Success response.',
                headers=response_headers,
                content={
                    enm.ContentType.json.value: obj.Content(
                        schema=obj.Schema.from_type(type_=list[cls])  # type: ignore[valid-type]
                        )
                    }
                )
        case Constants.ONE:
            response_obj = obj.ResponseObject(
                description='Success response.',
                headers=response_headers,
                content={
                    enm.ContentType.json.value: obj.Content(
                        schema=obj.Schema.from_obj(cls)
                        )
                    }
                )
        case _:
            response_obj = obj.ResponseObject(
                description='Empty response.',
                headers=response_headers
                )

    match method:
        case Constants.DELETE:
            operation = obj.Operation(
                summary=f'Delete one {cls.__name__}.',
                tags=tags,
                parameters=filter_to_unique_params(
                    (parent_path_parameters or [])
                    + [
                        param
                        for param
                        in parameters
                        if param.in_ != enm.ParameterLocation.query.value
                        ]
                    ) or None,
                security=security,
                responses={'204': response_obj}
                )
        case Constants.GET if response_type == Constants.MANY:
            operation = obj.Operation(
                summary=f'Fetch many {cls.__name__}.',
                tags=tags,
                parameters=filter_to_unique_params(
                    (parent_path_parameters or [])
                    + [
                        obj.Parameter(  # type: ignore[misc]
                            **{
                                k: v
                                for k, v
                                in parameter.items()
                                if k != Constants.REQUIRED
                                and k != Constants.IN
                                }
                            )
                        for parameter
                        in parameters
                        ]
                    ) or None,
                security=security,
                responses={'200': response_obj}
                )
        case Constants.GET:
            operation = obj.Operation(
                summary=f'Fetch one {cls.__name__}.',
                tags=tags,
                parameters=filter_to_unique_params(
                    (parent_path_parameters or [])
                    + [
                        parameter
                        for parameter
                        in parameters
                        if parameter.in_ != enm.ParameterLocation.query.value
                        ]
                    ) or None,
                security=security,
                responses={'200': response_obj}
                )
        case Constants.PATCH:
            operation = obj.Operation(
                summary=f'Update one {cls.__name__}.',
                tags=tags,
                parameters=filter_to_unique_params(
                    (parent_path_parameters or [])
                    + [
                        obj.Parameter(  # type: ignore[misc]
                            **{
                                k: v
                                for k, v
                                in parameter.items()
                                if k != Constants.REQUIRED
                                }
                            )
                        if parameter.in_ != enm.ParameterLocation.path.value
                        else parameter
                        for parameter
                        in parameters
                        ]
                    ) or None,
                security=security,
                responses={'200': response_obj}
                )
        case Constants.POST:
            operation = obj.Operation(
                summary=f'Create one {cls.__name__}.',
                tags=tags,
                request_body=obj.RequestBody(
                    content={
                        enm.ContentType.json.value: obj.Content(
                            schema=obj.Schema.from_obj(cls)
                            )
                        }
                    ),
                parameters=filter_to_unique_params(
                    (parent_path_parameters or [])
                    + [
                        parameter
                        for parameter
                        in parameters
                        if parameter.in_ == enm.ParameterLocation.header.value
                        ]
                    ) or None,
                security=security,
                responses={'201': response_obj}
                )
        case Constants.PUT:
            operation = obj.Operation(
                summary=f'Replace one {cls.__name__}.',
                tags=tags,
                request_body=obj.RequestBody(
                    content={
                        enm.ContentType.json.value: obj.Content(
                            schema=obj.Schema.from_obj(cls)
                            )
                        }
                    ),
                parameters=filter_to_unique_params(
                    (parent_path_parameters or [])
                    + [
                        parameter
                        for parameter
                        in parameters
                        if parameter.in_ != enm.ParameterLocation.query.value
                        ]
                    ) or None,
                security=security,
                responses={'200': response_obj}
                )
        case _:  # pragma: no cover
            operation = None

    return operation


def paths_from_object(
    cls: type[Object],
    parent_tags: lib.t.Optional[list[str]] = None,
    parent_path_parameters: lib.t.Optional[list[obj.Parameter]] = None,
    include_default_response_headers: bool = True,
    ) -> list[obj.Path]:
    """Generate RESTful API `Path` Objects from an `Object`."""

    paths: list[obj.Path] = []

    operations_by_uri: dict[str, dict[typ.ApiMethod, obj.Operation]] = {}
    method: typ.ApiMethod
    for method, callback in cls.__operations__.items():
        if callback is not None:
            operation = operation_from_object(
                cls,
                method,
                parent_tags,
                parent_path_parameters,
                include_default_response_headers
                )
            if operation is not None:
                operations_by_uri.setdefault(operation.path_uri, {})
                operations_by_uri[operation.path_uri][method] = operation

    tags: list[str] = []
    path_parameter_names: list[str] = []
    path_parameters: list[obj.Parameter] = []

    for path_uri, operations in operations_by_uri.items():
        path = obj.Path(  # type: ignore[misc]
            _ref_=path_uri,
            _resource_=cls,
            summary=cls.__name__,
            description=lib.textwrap.dedent(cls.__doc__) if cls.__doc__ else None,
            **operations  # type: ignore[arg-type]
            )

        for method, operation in operations.items():
            for parameter in (operation.parameters or ()):
                if (
                    parameter.in_ == enm.ParameterLocation.path.value
                    and parameter._ref_ is not None
                    and parameter._ref_ not in path_parameter_names
                    ):
                    path_parameter_names.append(parameter._ref_)
                    path_parameters.append(parameter)
            for tag in (operation.tags or ()):
                if tag not in tags:
                    tags.append(tag)

        path.update_options(cls, include_default_response_headers)
        paths.append(path)

    child_objs: list[type[Object]] = []
    for field in cls.__dataclass_fields__.values():
        if typ.utl.check.is_object_type(field.type_):
            child_objs.append(field.type_)
        elif typ.utl.check.is_array_of_obj_type(field.type_):
            tps: tuple[type[Object], ...] = (
                typ.utl.check.get_type_args(field.type_)
                )
            child_objs.append(tps[0])

    for child_obj in child_objs:
        if (
            child_obj.hash_fields
            and (name := child_obj.__name__) not in OBJECTS
            and (
                name.lower() in cls
                or core.strings.utl.pluralize(name).lower() in cls
                )
            ):
            paths.extend(
                paths_from_object(
                    child_obj,
                    tags,
                    path_parameters or None,
                    include_default_response_headers
                    )
                )

    return paths


def api_from_package(
    name: str,
    version: str,
    api_path: str,
    include_heartbeat: bool = True,
    include_version_prefix: bool = False,
    include_default_response_headers: bool = True,
    ) -> obj.Api:
    """Generate a RESTful API from passed python package name."""

    package = lib.importlib.import_module(name)

    if include_heartbeat:
        from . import Request

        obj.Api.register(obj.Healthz)

        @obj.Healthz.GET
        def respond(request: Request) -> obj.Healthz:
            """Application status check."""

            return obj.Healthz()  # pragma: no cover

    if not name.startswith('.'.join((Constants.PACAKGE, 'template'))):  # pragma: no cover
        from .. template . pkg . obj import Pet, PetWithPet
        OBJECTS.pop(PetWithPet.__name__, None)
        REQUEST_HEADERS.pop(PetWithPet.__name__, None)
        RESPONSE_HEADERS.pop(PetWithPet.__name__, None)
        SECURITY.pop(PetWithPet.__name__, None)
        SECURITY.pop(Pet.__name__, None)

    paths: list[obj.Path] = []
    for obj_ in OBJECTS.values():
        paths.extend(
            paths_from_object(
                obj_,
                include_default_response_headers=(
                    include_default_response_headers
                    )
                )
            )

    tags: list[obj.Tag] = []
    tagged: list[str] = []
    for path in paths:
        for method in Constants.METHODS:
            operation: lib.t.Optional[obj.Operation] = path[method]
            if operation is not None:
                if operation.tags is not None:
                    operation.tags = [':'.join(operation.tags)]
                    for tag in operation.tags:
                        if tag not in tagged:
                            _, _, obj_tag = tag.rpartition(':')
                            pascal_tag = obj_tag[0].upper() + obj_tag[1:]
                            if (obj_ := OBJECTS.get(pascal_tag)):
                                tagged.append(tag)
                                tags.append(
                                    obj.Tag(
                                        name=tag,
                                        description=(
                                            lib.textwrap.dedent(obj_.__doc__)
                                            if obj_.__doc__
                                            else None
                                            )
                                        )
                                    )

    info = obj.Info(
        title=name,
        version=version,
        summary='API created with ft3.',
        description=(
            lib.textwrap.dedent(package.__doc__)
            if package.__doc__
            else None
            )
        )

    if include_version_prefix:
        server = obj.ServerObject(
            url='/'.join((api_path.strip('/'), '{version}')),
            variables={'version': obj.ServerVariable(default=version)}
            )
    else:  # pragma: no cover
        server = obj.ServerObject(url=api_path)

    security: dict[str, obj.SecurityScheme] = {}
    for obj_security_requirements in SECURITY.values():
        for security_requirements in obj_security_requirements.values():
            for security_scheme in security_requirements:
                security[security_scheme.name_] = security_scheme.to_dict(
                    camel_case=True,
                    include_null=False,
                    include_private=False,
                    include_write_only=True,
                    include_read_only=False
                    )

    components: dict[str, dict[str, lib.t.Any]] = {
        'securitySchemes': security
        }
    if include_default_response_headers:
        components['headers'] = {
            name: header.to_dict(
                camel_case=True,
                include_null=False,
                include_private=False,
                include_write_only=True,
                include_read_only=False
                )
            for name, header
            in obj.DEFAULT_RESPONSE_HEADERS.items()
            }

    api = obj.Api(
        info=info,
        paths={path.pop('ref'): path for path in paths},
        tags=tags,
        servers=[server],
        components=components
        )

    from . import static

    path_root = '/'.join((api_path.strip('/'), version))

    obj.File(
        path=path_root if include_version_prefix else api_path,
        content=(
            lib
            .string
            .Template(static.swagger_template)
            .safe_substitute(
                {
                    'TITLE': name,
                    'PATH': '/'.join((path_root, 'openapi.json'))
                    }
                )
            ),
        content_type=enm.ContentType.html.value
        )

    api_as_dict: dict[str, typ.AnyDict] = api.to_dict(
        camel_case=True,
        include_null=False,
        include_private=False,
        include_write_only=False,
        include_read_only=True
        )
    path_dict: typ.AnyDict
    param_dict: typ.AnyDict
    operation_dict: typ.AnyDict
    for path_dict in api_as_dict['paths'].values():
        for method in Constants.METHODS:
            params_list: list[typ.AnyDict] = []
            if (operation_dict := path_dict.get(method)):
                if 'parameters' not in operation_dict:
                    continue
                for param_dict in operation_dict['parameters']:
                    if param_dict['in'] == enm.ParameterLocation.path.value:
                        del param_dict[Constants.SCHEMA]
                    params_list.append(param_dict)
                operation_dict['parameters'] = params_list

    obj.File(
        path='/'.join((path_root, 'openapi.json')),
        content=lib.json.dumps(
            api_as_dict,
            indent=Constants.INDENT,
            default=repr
            ),
        content_type=enm.ContentType.json.value
        )
    obj.File(
        path='/favicon.ico',
        content=static.favicon,
        content_type=enm.ContentType.icon.value
        )

    return api


def serve(
    package: str,
    port: int,
    version: str,
    api_path: str,
    include_heartbeat: bool,
    include_version_prefix: bool,
    include_default_response_headers: bool
    ) -> None:  # pragma: no cover
    """
    CLI entrypoint for serving an application.

    ---

    Specify the name of your API package to serve it via simple http \
    server.

    ### Example

    `$ ft3 api ft3.template`

    ---

    You may specify a port as a positional argument following \
    the package name. By default, your application will be served \
    on port 80, accessible at http://localhost in your browser.

    ---

    ### DISCLAIMER

    `$ ft3 api serve` is highly insecure and should NOT be used \
    in any production environment.

    This _may_ change in the future.

    """

    from .. import log
    from . events import Handler
    from . server import Server

    Server.handler = Handler(
        api=api_from_package(
            package,
            version,
            api_path,
            include_heartbeat,
            include_version_prefix,
            include_default_response_headers
            )
        )

    lib.socketserver.ThreadingTCPServer.allow_reuse_address = True
    lib.socketserver.ThreadingTCPServer.block_on_close = False
    lib.socketserver.ThreadingTCPServer.daemon_threads = True

    with lib.socketserver.ThreadingTCPServer(('', port), Server) as httpd:
        try:
            log.info(f'SERVING PORT: {port} (Press CTRL+C to quit)')
            httpd.serve_forever()
        except KeyboardInterrupt:
            log.warning('Keyboard interrupt received, exiting.')

    return None


obj.api_parser.set_defaults(func=serve)  # type: ignore[has-type]
