"""Api utility functions."""

__all__ = (
	'api_from_package',
	'check',
	'check_package',
	'openapi',
	'openapi_document',
	'openapi_from_package',
	'unregistered_handlers',
	'filter_to_unique_params',
	'operation_from_object',
	'parameters_from_object',
	'paths_from_object',
	'response_type_from_object',
	'runtime_api_from_package',
	'serve',
)

from .. import core
from .. import objects

from .. import Object

from . import cfg
from . import enm
from . import lib
from . import obj
from . import typ

from .obj import FILES, OBJECTS, REQUEST_HEADERS, RESPONSE_HEADERS, SECURITY

if lib.t.TYPE_CHECKING:  # pragma: no cover
	from . import events


class Constants(cfg.Constants):
	"""Constants specific to this file."""

	ID = 'id'

	IN = 'in'
	REQUIRED = 'required'
	SCHEMA: typ.string[lib.t.Any] = 'schema'

	ONE: lib.t.Literal['ONE'] = 'ONE'
	MANY: lib.t.Literal['MANY'] = 'MANY'
	EMPTY: lib.t.Literal['EMPTY'] = 'EMPTY'


def _join_root(api_path: str, *segments: str) -> str:
	"""Join an api path and segments into an absolute, slash-led url."""

	parts = [p for p in (api_path.strip('/'), *segments) if p]
	return '/' + '/'.join(parts)


def unregistered_handlers(paths: list[obj.Path]) -> list[str]:
	"""
    Qualified names of Objects that have HTTP handlers but are served \
    by no path, the usual sign of a missing `@Api.register`.

    """

	served = {path._resource_ for path in paths}
	template = '.'.join((Constants.PACKAGE, 'template'))
	return [
		qualname
		for qualname, handled in objects.objs.obj.Constants.HANDLED.items()
		if handled not in served
		and handled.__name__ not in OBJECTS
		and not handled.__module__.startswith(template)
	]


def _warn_unregistered_handlers(paths: list[obj.Path]) -> None:
	"""Warn once per unregistered handler class."""

	from .. import loggers

	for qualname in unregistered_handlers(paths):
		loggers.utl.warn_once(
			('api', 'unregistered_handlers', qualname),
			{
				'unregistered.handlers': {
					'object': qualname,
					'outcome': 'its routes are not served',
					'fix': 'decorate the class with @Api.register',
				}
			},
		)
	return None


def _runtime_schema_from_field(field: lib.t.Any) -> obj.Schema:
	"""Return the schema details needed by request dispatch."""

	return obj.Schema(
		read_only=field.get('read_only'),
		write_only=field.get('write_only'),
	)


def _runtime_schema_from_object(cls: type[Object]) -> obj.Schema:
	"""Return the object schema details needed by request dispatch."""

	oname: typ.string[typ.PascalCase] = cls.__name__
	properties = {
		(
			fname := core.strings.utl.snake_case_to_camel_case(field_name)
		): obj.Schema(
			_ref_=fname + oname,
			read_only=field.get('read_only'),
			write_only=field.get('write_only'),
		)
		for field_name, field in cls.__dataclass_fields__.items()
	}

	return obj.Schema(properties=properties, type_=[enm.Type.object.value])


def _discard_generated_doc_files(path_root: str) -> None:
	"""Remove generated docs files from the API file registry."""

	for file_path in (
		Constants.SWAGGER_PATH,
		'/'.join((path_root, 'openapi.json')),
		'/favicon.ico',
	):
		obj.FILES.pop(file_path, None)

	return None


def parameters_from_object(
	cls: type[Object],
	include_schema_details: bool = True,
) -> list[obj.Parameter]:
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
			schema=(
				obj.Schema.from_type(
					**{
						k: v
						for k, v in field.items()
						if k not in Constants.SKIP_FIELDS
					}
				)
				if include_schema_details
				else _runtime_schema_from_field(field)
			),
			required=required or field.required,
		)
		parameters.append(parameter)

	return parameters


def response_type_from_object(
	cls: type[Object],
	method: typ.ApiMethod,
	operation_key: lib.t.Optional[str] = None,
) -> typ.ApiResponseType:
	"""
	Calculate response type from an `Object`.

	---

	Handlers are keyed by `operation_key` (`pet_get` for a GET by id,
	`get` for a list), which defaults to the bare `method`.

	"""

	callback = cls.__operations__.get(operation_key or method)  # type: ignore[call-overload]
	if callback is None:  # pragma: no cover
		return Constants.EMPTY

	tp = callback.__annotations__.get('return')

	if typ.utl.check.is_array_of_obj_type(tp):
		return Constants.MANY
	elif typ.utl.check.is_object_type(tp):
		return Constants.ONE
	else:
		return Constants.EMPTY  # pragma: no cover


def filter_to_unique_params(
	parameters: list[obj.Parameter],
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
	include_docs: bool = True,
	operation_key: lib.t.Optional[str] = None,
) -> lib.t.Optional[obj.Operation]:
	"""Generate RESTful API `Operation` from an `Object`."""

	parameters = parameters_from_object(cls, include_docs)

	response_headers: dict[str, obj.Header] = {}
	if include_default_response_headers:
		response_headers.update(obj.DEFAULT_RESPONSE_HEADERS)

	response_headers_by_method = RESPONSE_HEADERS.get(cls.__name__)
	if response_headers_by_method is not None:
		response_headers.update(response_headers_by_method[method])

	security: list[dict[str, list[str]]] = []
	if security_schemes := SECURITY.get(cls.__name__):
		security.extend(
			[{scheme.name_: []} for scheme in security_schemes[method]]
		)

	tags: list[str] = []
	if parent_tags is not None:
		tags.extend(parent_tags)
	tags.append(core.strings.utl.snake_case_to_camel_case(cls.__name__))

	if not cls.hash_fields:
		parameters.clear()

	if request_headers := REQUEST_HEADERS.get(cls.__name__):
		parameters.extend(request_headers[method])

	response_type = response_type_from_object(cls, method, operation_key)

	if include_docs:
		match response_type:
			case Constants.MANY:
				response_obj = obj.ResponseObject(
					description='Success response.',
					headers=response_headers,
					content={
						enm.ContentType.json.value: obj.Content(
							schema=obj.Schema.from_type(type_=list[cls])  # type: ignore[valid-type]
						)
					},
				)
			case Constants.ONE:
				response_obj = obj.ResponseObject(
					description='Success response.',
					headers=response_headers,
					content={
						enm.ContentType.json.value: obj.Content(
							schema=obj.Schema.from_obj(cls)
						)
					},
				)
			case _:
				response_obj = obj.ResponseObject(
					description='Empty response.', headers=response_headers
				)
	else:
		response_obj = obj.ResponseObject(
			description=(
				'Empty response.'
				if response_type == Constants.EMPTY
				else 'Success response.'
			),
			headers=response_headers,
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
						for param in parameters
						if param.in_ != enm.ParameterLocation.query.value
					]
				)
				or None,
				security=security,
				responses={'204': response_obj},
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
								for k, v in parameter.items()
								if k != Constants.REQUIRED
								and (
									k != Constants.IN
									or v != enm.ParameterLocation.path.value
								)
							}
						)
						for parameter in parameters
					]
				)
				or None,
				security=security,
				responses={'200': response_obj},
			)
		case Constants.GET:
			operation = obj.Operation(
				summary=f'Fetch one {cls.__name__}.',
				tags=tags,
				parameters=filter_to_unique_params(
					(parent_path_parameters or [])
					+ [
						parameter
						for parameter in parameters
						if parameter.in_ != enm.ParameterLocation.query.value
					]
				)
				or None,
				security=security,
				responses={'200': response_obj},
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
								for k, v in parameter.items()
								if k != Constants.REQUIRED
							}
						)
						if parameter.in_ != enm.ParameterLocation.path.value
						else parameter
						for parameter in parameters
					]
				)
				or None,
				security=security,
				responses={'200': response_obj},
			)
		case Constants.POST:
			operation = obj.Operation(
				summary=f'Create one {cls.__name__}.',
				tags=tags,
				request_body=obj.RequestBody(
					content={
						enm.ContentType.json.value: obj.Content(
							schema=(
								obj.Schema.from_obj(cls)
								if include_docs
								else _runtime_schema_from_object(cls)
							)
						)
					}
				),
				parameters=filter_to_unique_params(
					(parent_path_parameters or [])
					+ [
						parameter
						for parameter in parameters
						if parameter.in_ == enm.ParameterLocation.header.value
					]
				)
				or None,
				security=security,
				responses={'201': response_obj},
			)
		case Constants.PUT:
			operation = obj.Operation(
				summary=f'Replace one {cls.__name__}.',
				tags=tags,
				request_body=obj.RequestBody(
					content={
						enm.ContentType.json.value: obj.Content(
							schema=(
								obj.Schema.from_obj(cls)
								if include_docs
								else _runtime_schema_from_object(cls)
							)
						)
					}
				),
				parameters=filter_to_unique_params(
					(parent_path_parameters or [])
					+ [
						parameter
						for parameter in parameters
						if parameter.in_ != enm.ParameterLocation.query.value
					]
				)
				or None,
				security=security,
				responses={'200': response_obj},
			)
		case _:  # pragma: no cover
			operation = None

	return operation


def _is_operation_config_valid(
	cls: type[Object],
	callback: lib.t.Callable[
		[
			'events.obj.Request',
		],
		lib.t.Optional[typ.Object] | lib.t.Optional[list[typ.Object]] | str,
	],
	method: typ.ApiMethod,
	prefix: typ.string[typ.snake_case] | typ.AnyString,
	parent_tags: list[str] | None,
) -> bool:
	return callback is not None and (
		(
			parent_tags is None
			and (
				(
					(len_ := len(prefix.split('_'))) == 1
					and method != Constants.POST
					and (
						method != Constants.GET
						or not any(
							issubclass(tp, list)
							for tp in typ.utl.check.get_checkable_types(
								callback.__annotations__['return']
							)
						)
						or bool(cls.hash_fields)
					)
				)
				or (
					not bool(prefix)
					and (
						method == Constants.POST
						or (
							method == Constants.GET
							and (
								any(
									issubclass(tp, list)
									for tp in typ.utl.check.get_checkable_types(
										callback.__annotations__['return']
									)
								)
								or not bool(cls.hash_fields)
							)
						)
					)
				)
			)
		)
		or (
			parent_tags is not None
			and bool(prefix)
			and (
				(
					(len_ := len(prefix.split('_'))) == 2
					and method != Constants.POST
					and (
						method != Constants.GET
						or not any(
							issubclass(tp, list)
							for tp in typ.utl.check.get_checkable_types(
								callback.__annotations__['return']
							)
						)
						or bool(cls.hash_fields)
					)
				)
				or (
					len_ == 1
					and (
						method == Constants.POST
						or (
							method == Constants.GET
							and (
								any(
									issubclass(tp, list)
									for tp in typ.utl.check.get_checkable_types(
										callback.__annotations__['return']
									)
								)
								or not bool(cls.hash_fields)
							)
						)
					)
				)
			)
		)
	)


def paths_from_object(
	cls: type[Object],
	parent_tags: lib.t.Optional[list[str]] = None,
	parent_path_parameters: lib.t.Optional[list[obj.Parameter]] = None,
	include_default_response_headers: bool = True,
	include_docs: bool = True,
) -> list[obj.Path]:
	"""Generate RESTful API `Path` Objects from an `Object`."""

	paths: list[obj.Path] = []

	operations_by_uri: dict[str, dict[typ.ApiMethod, obj.Operation]] = {}
	method: typ.ApiMethod
	for method_, callback in cls.__operations__.items():
		prefix, _, method = method_.rpartition('_')
		if _is_operation_config_valid(
			cls, callback, method, prefix, parent_tags
		):
			operation = operation_from_object(
				cls,
				method,
				parent_tags,
				parent_path_parameters,
				include_default_response_headers,
				include_docs,
				method_,
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
			description=(
				lib.textwrap.dedent(cls.__doc__)
				if include_docs and cls.__doc__
				else None
			),
			**operations,  # type: ignore[arg-type]
		)

		for method, operation in operations.items():
			for parameter in operation.parameters or ():
				if (
					parameter.in_ == enm.ParameterLocation.path.value
					and parameter._ref_ is not None
					and parameter._ref_ not in path_parameter_names
				):
					path_parameter_names.append(parameter._ref_)
					path_parameters.append(parameter)
			for tag in operation.tags or ():
				if tag not in tags:
					tags.append(tag)

		path.update_options(cls, include_default_response_headers)
		paths.append(path)

	child_objs: list[type[Object]] = []
	for field in cls.__dataclass_fields__.values():
		obj_or_none = objects.utl.get_obj_from_type(field.type_)
		if obj_or_none is not None:
			child_objs.append(obj_or_none)

	for child_obj in child_objs:
		if (
			child_obj.hash_fields
			and (name := child_obj.__name__)  # not in OBJECTS
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
					include_default_response_headers,
					include_docs,
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
	lazy_docs: bool = True,
) -> obj.Api:
	"""Generate a RESTful API from passed python package name."""

	include_docs = not lazy_docs
	package = lib.importlib.import_module(name)

	if include_heartbeat:
		from . import Request

		obj.Api.register(obj.Healthz)

		@obj.Healthz.GET
		def respond(request: Request) -> obj.Healthz:
			"""Application status check."""

			return obj.Healthz()  # pragma: no cover

	if not name.startswith(
		'.'.join((Constants.PACKAGE, 'template'))
	):  # pragma: no cover
		OBJECTS.pop('PetWithPet', None)
		REQUEST_HEADERS.pop('PetWithPet', None)
		RESPONSE_HEADERS.pop('PetWithPet', None)
		SECURITY.pop('PetWithPet', None)
		SECURITY.pop('Pet', None)

	paths: list[obj.Path] = []
	for obj_ in OBJECTS.values():
		paths.extend(
			paths_from_object(
				obj_,
				include_default_response_headers=(
					include_default_response_headers
				),
				include_docs=include_docs,
			)
		)

	_warn_unregistered_handlers(paths)

	tags: list[obj.Tag] = []
	tagged: list[str] = []
	for path in paths:
		for method in Constants.METHODS:
			operation: lib.t.Optional[obj.Operation] = path[method]
			if operation is not None:
				if operation.tags is not None:
					operation.tags = [':'.join(operation.tags)]
					if include_docs:
						for tag in operation.tags:
							if tag not in tagged:
								_, _, obj_tag = tag.rpartition(':')
								pascal_tag = obj_tag[0].upper() + obj_tag[1:]
								if obj_ := OBJECTS.get(pascal_tag):
									tagged.append(tag)
									tags.append(
										obj.Tag(
											name=tag,
											description=(
												lib.textwrap.dedent(
													obj_.__doc__
												)
												if obj_.__doc__
												else None
											),
										)
									)

	info = obj.Info(
		title=name,
		version=version,
		summary='API created with ft3.',
		description=(
			lib.textwrap.dedent(package.__doc__)
			if include_docs and package.__doc__
			else None
		),
	)

	if include_version_prefix:
		server = obj.ServerObject(
			url=_join_root(api_path, '{version}'),
			variables={'version': obj.ServerVariable(default=version)},
		)
	else:
		server = obj.ServerObject(url=_join_root(api_path))

	security: dict[str, obj.SecurityScheme] = {}
	for obj_security_requirements in SECURITY.values():
		for security_requirements in obj_security_requirements.values():
			for security_scheme in security_requirements:
				security[security_scheme.name_] = security_scheme.to_dict(
					camel_case=True,
					include_null=False,
					include_private=False,
					include_write_only=True,
					include_read_only=False,
				)

	components: dict[str, dict[str, lib.t.Any]] = {'securitySchemes': security}
	if include_default_response_headers:
		components['headers'] = {
			name: header.to_dict(
				camel_case=True,
				include_null=False,
				include_private=False,
				include_write_only=True,
				include_read_only=False,
			)
			for name, header in obj.DEFAULT_RESPONSE_HEADERS.items()
		}

	api = obj.Api(
		info=info,
		paths={path.pop('ref'): path for path in paths},
		tags=tags,
		servers=[server],
		components=components,
	)

	path_root = _join_root(api_path, version)
	if lazy_docs:
		_discard_generated_doc_files(path_root)
		return api

	from . import static

	swagger_path = Constants.SWAGGER_PATH

	obj.File(
		path=swagger_path,
		content=(
			lib.string.Template(static.swagger_template).safe_substitute(
				{'TITLE': name, 'PATH': '/'.join((path_root, 'openapi.json'))}
			)
		),
		content_type=enm.ContentType.html.value,
	)

	obj.File(
		path='/'.join((path_root, 'openapi.json')),
		content=lib.json.dumps(
			openapi_document(api), indent=Constants.INDENT, default=repr
		),
		content_type=enm.ContentType.json.value,
	)
	obj.File(
		path='/favicon.ico',
		content=static.favicon,
		content_type=enm.ContentType.icon.value,
	)

	return api


def runtime_api_from_package(
	name: str,
	version: str,
	api_path: str,
	include_heartbeat: bool = True,
	include_version_prefix: bool = False,
	include_default_response_headers: bool = True,
) -> obj.Api:
	"""Generate a RESTful API with only runtime dispatch metadata."""

	return api_from_package(
		name,
		version,
		api_path,
		include_heartbeat,
		include_version_prefix,
		include_default_response_headers,
		lazy_docs=True,
	)


def openapi_document(api: obj.Api) -> typ.AnyDict:
	"""The OpenAPI document for `api`, as a JSON-ready dict."""

	api_as_dict: dict[str, typ.AnyDict] = api.to_dict(
		camel_case=True,
		include_null=False,
		include_private=False,
		include_write_only=False,
		include_read_only=True,
	)
	path_dict: typ.AnyDict
	param_dict: typ.AnyDict
	operation_dict: typ.AnyDict
	for path_dict in api_as_dict['paths'].values():
		for method in Constants.METHODS:
			params_list: list[typ.AnyDict] = []
			if operation_dict := path_dict.get(method):
				if 'parameters' not in operation_dict:
					continue
				for param_dict in operation_dict['parameters']:
					if param_dict['in'] == enm.ParameterLocation.path.value:
						del param_dict[Constants.SCHEMA]
					params_list.append(param_dict)
				operation_dict['parameters'] = params_list
	return api_as_dict


def _build_for_tooling(
	package: str,
	version: str,
	api_path: str,
	include_heartbeat: bool,
	include_version_prefix: bool,
) -> obj.Api:
	"""Build a fully documented API without leaving doc files registered."""

	files = dict(FILES)
	try:
		return api_from_package(
			package,
			version,
			api_path,
			include_heartbeat=include_heartbeat,
			include_version_prefix=include_version_prefix,
			lazy_docs=False,
		)
	finally:
		FILES.clear()
		FILES.update(files)


def openapi_from_package(
	package: str,
	version: str = Constants.DEFAULT_VERSION,
	api_path: str = Constants.API_PATH,
	include_heartbeat: bool = True,
	include_version_prefix: bool = False,
) -> typ.AnyDict:
	"""
    Generate the OpenAPI document for a package at build time, the \
    way `ft3 openapi` does. Nothing runs at import time in the served \
    application.

    """

	api = _build_for_tooling(
		package, version, api_path, include_heartbeat, include_version_prefix
	)
	return openapi_document(api)


def _objects_reachable(paths: list[obj.Path]) -> list[type[Object]]:
	"""Served Objects plus every Object type nested in their fields."""

	found: list[type[Object]] = []
	pending = [path._resource_ for path in paths]
	while pending:
		cls = pending.pop()
		if cls in found:
			continue
		found.append(cls)
		for field in cls.__dataclass_fields__.values():
			nested = objects.utl.get_obj_from_type(field.type_)
			if nested is not None and nested not in found:
				pending.append(nested)
	return found


def _field_notices(cls: type[Object]) -> list[typ.AnyDict]:
	"""Every Field of `cls` whose behavior changed in ft3 2.0."""

	notices: list[typ.AnyDict] = []
	for name, field in cls.__dataclass_fields__.items():
		checkable = typ.utl.check.get_checkable_types(field.type_)
		item_types = typ.utl.check.get_type_args(field.type_)
		found: list[tuple[str, str]] = []
		if name.startswith('_'):
			found.append(
				(
					'private_field',
					'rejected on request input (400); accepted with a'
					' warning under FT3_LEGACY_WIRE',
				)
			)
		if field.required and field.default is None:
			found.append(
				(
					'required_field',
					'must be present and non-null on POST and PUT bodies'
					' (400); warning under FT3_LEGACY_WIRE',
				)
			)
		if field.constraints:
			found.append(
				(
					'constraints_enforced',
					'enum/bounds/length/pattern now return 400 on request'
					' input: ' + ', '.join(field.constraints),
				)
			)
		if (
			any(issubclass(tp, lib.t.Mapping) for tp in checkable)
			and field.get('camel_case_keys') is None
		):
			found.append(
				(
					'dict_keys_default',
					'dict keys are no longer camelCased on the wire; set'
					' camel_case_keys=True to keep 1.x behavior',
				)
			)
		if (
			typ.utl.check.is_array_type(field.type_)
			and item_types
			and any(
				typ.utl.check.is_none_type(tp)
				for tp in typ.utl.check.get_checkable_types(item_types[0])
			)
			and field.get('drop_null_items') is None
		):
			found.append(
				(
					'list_nulls_default',
					'None items now keep their position on the wire; set'
					' drop_null_items=True to keep 1.x behavior',
				)
			)
		for notice, detail in found:
			notices.append(
				{
					'object': cls.__name__,
					'field': name,
					'notice': notice,
					'detail': detail,
				}
			)
	return notices


def check_package(
	package: str,
	version: str = Constants.DEFAULT_VERSION,
	api_path: str = Constants.API_PATH,
	include_heartbeat: bool = True,
	include_version_prefix: bool = False,
) -> typ.AnyDict:
	"""
    Validate a package the way `ft3 check` does and return the report.

    ---

    The report lists `errors` (the package cannot be served correctly), \
    `routes` (every served path, its methods, and its resource), and \
    `notices` (every Field whose behavior changed in ft3 2.0, which is \
    the migration list for a package upgrading from 1.x). `ok` is \
    `True` when there are no errors.

    """

	report: typ.AnyDict = {
		'package': package,
		'ok': False,
		'errors': [],
		'routes': [],
		'notices': [],
	}
	try:
		api = _build_for_tooling(
			package,
			version,
			api_path,
			include_heartbeat,
			include_version_prefix,
		)
	except Exception as exception:
		report['errors'].append(
			{
				'code': 'build_failed',
				'ref': core.exc.code_for(type(exception)),
				'detail': str(exception),
				'fix': 'import the package in python and read the traceback',
			}
		)
		return report

	paths = list(api.paths.values())
	for qualname in unregistered_handlers(paths):
		report['errors'].append(
			{
				'code': 'unregistered_handlers',
				'object': qualname,
				'detail': 'has HTTP handlers but is served by no path',
				'fix': 'decorate the class with @Api.register',
			}
		)

	root = api.servers[0].url if api.servers else api_path
	if api.servers and api.servers[0].variables is not None:
		root = root.replace('{version}', version)
	for ref, path in api.paths.items():
		methods = [m for m in Constants.METHODS if path[m] is not None]
		if not methods:  # pragma: no cover
			report['errors'].append(
				{
					'code': 'path_without_operations',
					'object': ref,
					'detail': 'no method is served at this path',
					'fix': 'attach at least one handler or unregister',
				}
			)
		report['routes'].append(
			{
				'path': root.rstrip('/') + ref,
				'methods': methods,
				'resource': path._resource_.__name__,
			}
		)

	try:
		lib.json.dumps(openapi_document(api), default=repr)
	except Exception as exception:  # pragma: no cover
		report['errors'].append(
			{
				'code': 'openapi_failed',
				'ref': core.exc.code_for(type(exception)),
				'detail': str(exception),
				'fix': 'read the traceback from `ft3 openapi`',
			}
		)

	for cls in _objects_reachable(paths):
		report['notices'].extend(_field_notices(cls))

	report['ok'] = not report['errors']
	return report


def _emit(text: str) -> None:
	"""Write CLI output to stdout, bypassing print() interception."""

	lib.sys.stdout.write(text)
	if not text.endswith('\n'):
		lib.sys.stdout.write('\n')


def check(
	package: str,
	version: str,
	api_path: str,
	include_heartbeat: bool,
	include_version_prefix: bool,
	output_format: str,
) -> None:
	"""
    CLI entrypoint validating a package without serving it.

    ---

    `$ ft3 check my_pkg`

    Prints a JSON report (or `--format text`) and exits non-zero when \
    the package cannot be served correctly. Run it after every edit.

    """

	report = check_package(
		package, version, api_path, include_heartbeat, include_version_prefix
	)
	if output_format == 'json':
		_emit(lib.json.dumps(report, indent=Constants.INDENT, default=repr))
	else:
		lines = [f'{package}: {"ok" if report["ok"] else "FAILED"}']
		for error in report['errors']:
			lines.append(
				f'  error {error["code"]}: {error.get("object", "")}'
				f' {error["detail"]}. FIX: {error["fix"]}'
			)
		for route in report['routes']:
			lines.append(
				f'  route {route["path"]} [{", ".join(route["methods"])}]'
				f' -> {route["resource"]}'
			)
		for notice in report['notices']:
			lines.append(
				f'  notice {notice["object"]}.{notice["field"]}'
				f' {notice["notice"]}: {notice["detail"]}'
			)
		_emit('\n'.join(lines))
	lib.sys.exit(0 if report['ok'] else 1)


def openapi(
	package: str,
	version: str,
	api_path: str,
	include_heartbeat: bool,
	include_version_prefix: bool,
	output: str,
) -> None:
	"""
    CLI entrypoint writing a package's OpenAPI document.

    ---

    `$ ft3 openapi my_pkg --output openapi.json`

    This is a build-time artifact: generate it in CI and ship it \
    beside the package or import it into your gateway. `-` writes to \
    stdout.

    """

	document = lib.json.dumps(
		openapi_from_package(
			package,
			version,
			api_path,
			include_heartbeat,
			include_version_prefix,
		),
		indent=Constants.INDENT,
		default=repr,
	)
	if output == '-':
		_emit(document)
	else:
		with open(output, 'w') as file:
			file.write(document + '\n')
		_emit(f'wrote {output}')
	return None


def serve(
	package: str,
	port: int,
	version: str,
	api_path: str,
	include_heartbeat: bool,
	include_version_prefix: bool,
	include_default_response_headers: bool,
	lazy_docs: bool = True,
) -> None:  # pragma: no cover
	"""
    CLI entrypoint serving a package with the stdlib HTTP server, \
    for local development.

    ---

    `$ ft3 api my_pkg --port 8080`

    Serves on port 80 by default with no generated docs, so startup \
    costs no more than importing the package. `--generate-docs` also \
    serves Swagger at `/swagger` and the OpenAPI document; for a build \
    artifact use `ft3 openapi` instead.

    Deploy behind a gateway, not this server: pass the gateway event \
    to `ft3.api.Handler(api=api)(request)`.
	"""

	from .. import log
	from .events import Handler
	from .server import Server

	Server.handler = Handler(
		api=api_from_package(
			package,
			version,
			api_path,
			include_heartbeat,
			include_version_prefix,
			include_default_response_headers,
			lazy_docs,
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
obj.check_parser.set_defaults(func=check)  # type: ignore[has-type]
obj.openapi_parser.set_defaults(func=openapi)  # type: ignore[has-type]
