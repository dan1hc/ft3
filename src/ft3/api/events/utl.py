"""Api event utility functions."""

__all__ = ('handle_request', 'paths_from_api')

from ... import objects

from .. import typ

from . import cfg
from . import enm
from . import exc
from . import lib
from . import obj


class Constants(cfg.Constants):
	"""Constants specific to this file."""

	ID = 'id'


PATHS: dict[int, tuple[obj.Api, list[str]]] = {}
"""
Sorted path names per `Api`, keyed by `id(api)` and holding the `Api` \
so the id stays unique for as long as the entry exists.

"""


def _uri_len(uri: str) -> tuple[int, int]:
	split_ = uri.split('/')
	count_ = len([e for e in split_ if bool(obj.Pattern.PathId.match(e))])
	return len(split_), -count_


def paths_from_api(api: obj.Api) -> list[str]:
	"""Cache and return the sorted path names of an OpenAPI spec."""

	if id(api) in PATHS:
		return PATHS[id(api)][1]
	if api.servers:
		server = api.servers[0]
		if server.variables is not None:
			path_root = server.url.replace(
				'{version}', server.variables['version'].default
			)
		else:
			path_root = server.url
		path_root = path_root.rstrip('/')
	else:  # pragma: no cover
		path_root = ''
	paths = sorted(
		[path_root + path for path in api.paths],
		key=_uri_len,
		reverse=True,
	)
	PATHS[id(api)] = (api, paths)
	return paths


def handle_request(request: obj.Request, api: obj.Api) -> obj.Response:
	"""Route an incoming request according to an OpenAPI spec."""

	path: lib.t.Optional[obj.Path] = None
	path_names = paths_from_api(api)
	request_path = lib.urllib.parse.urlsplit(request.path).path or '/'

	if api.servers:
		server = api.servers[0]
		if server.variables is not None:
			server_root = server.url.replace(
				'{version}', server.variables['version'].default
			)
		else:
			server_root = server.url
		server_root = server_root.rstrip('/') + '/'
	else:  # pragma: no cover
		server_root = Constants.API_PATH

	path_pattern = ''
	for path_name in path_names:
		path_pattern = '/'.join(
			(
				Constants.PATH_ID
				if bool(obj.Pattern.PathId.match(path_element))
				else path_element
				for path_element in path_name.split('/')
			)
		)
		if bool(lib.re.fullmatch(path_pattern + '/?', request_path)):
			path = api.paths[
				path_name.replace(server_root, Constants.API_PATH)
			]
			break

	status_code: typ.HttpStatusCode
	response_body: typ.CamelDict | list[typ.CamelDict] | str | bytes
	response_headers: dict[str, obj.Header] = {}
	override_headers: dict[str, str] = {}
	override_status: lib.t.Optional[typ.HttpStatusCode] = None

	default_response_headers: dict[str, obj.Header]
	if api.components is not None and (
		default_response_headers := api.components.get('headers')
	):
		response_headers.update(default_response_headers)

	from ... import log
	from .. import FILES

	if (file := FILES.get(request_path)) is not None:
		content_type = file.content_type
		status_code = 200
		response_body = file.content
	elif path is not None:
		method: typ.string[typ.snake_case] = request.method.lower()
		obj_ = path._resource_
		path_obj_names = '_'.join(
			[
				path_element.lstrip('{').replace('Id}', '').lower()
				for path_element in path_name.split('/')
				if bool(obj.Pattern.PathId.match(path_element))
			][-2:]
		)
		op_name: typ.string[typ.snake_case] = '_'.join(
			(path_obj_names, method)
		).lstrip('_')
		callback = obj_.__operations__.get(op_name)
		if callback is not None:
			operation: obj.Operation = path[method]
			parse_error: lib.t.Optional[Exception] = None
			try:
				if operation.parameters is not None:
					request.parse_path_params(
						'/'.join(
							(
								server_root.rstrip('/'),
								operation.path_uri.strip('/'),
							)
						),
						operation,
					)
					request.parse_query_params(method, operation, obj_)
				if operation.request_body is not None:
					request.parse_body(operation, obj_)
				request.validate_input(obj_, method)
			except Exception as exception:
				if Constants.LEGACY_WIRE:
					log.error({'request.error': repr(exception)})
				else:
					parse_error = exception
			else:
				log.info({'request.parsed': request})
			try:
				if parse_error is not None:
					raise parse_error
				response_obj = callback(request)
			except Exception as exception:
				if exception is parse_error:
					error = obj.Error.from_request_exception(exception)
				else:
					last_frame = lib.traceback.format_tb(
						exception.__traceback__
					)[-1]
					is_error_raised = 'raise ' in last_frame
					is_error_from_api = api.info.title in last_frame
					if (
						is_error_raised
						or is_error_from_api
						or isinstance(
							exception, objects.exc.TypeValidationError
						)
					):
						error = obj.Error.from_exception(exception)
					else:  # pragma: no cover
						error = obj.Error.from_exception(exc.UnexpectedError)
				log.error({'operation.error': error})
				content_type = enm.ContentType.json.value
				status_code = error.error_code
				response_body = error.as_response
			else:
				if isinstance(response_obj, obj.Response):
					override_headers = response_obj.headers.copy()
					override_status = response_obj.status_code
					response_obj = response_obj.body
				if response_obj is None:
					content_type = enm.ContentType.text.value
					status_code = 204 if method == Constants.DELETE else 200
					response_body = ''
				elif isinstance(response_obj, str):  # pragma: no cover
					content_type = enm.ContentType.text.value
					status_code = 200
					response_body = response_obj
				elif isinstance(response_obj, list):
					content_type = enm.ContentType.json.value
					status_code = 200
					response_body = [o.as_response for o in response_obj]
				else:
					content_type = enm.ContentType.json.value
					status_code = 201 if method == Constants.POST else 200
					response_body = response_obj.as_response
				if override_status is not None:
					status_code = override_status
			if operation.responses:
				for response_definition in operation.responses.values():
					response_headers.update(response_definition.headers or {})
		elif method == Constants.OPTIONS:
			content_type = enm.ContentType.text.value
			status_code = 204
			response_body = ''
			if path.options and path.options.responses:
				for response_definition in path.options.responses.values():
					response_headers.update(response_definition.headers or {})
		else:
			error = obj.Error.from_exception(exc.MethodNotImplementedError)
			content_type = enm.ContentType.json.value
			status_code = error.error_code
			response_body = error.as_response
	else:
		error = obj.Error.from_exception(exc.ResourceNotFoundError)
		content_type = enm.ContentType.json.value
		status_code = error.error_code
		response_body = error.as_response

	if isinstance(response_body, (bytes, str)):
		content_length = len(response_body)
	else:
		content_length = len(lib.json.dumps(response_body, default=str))

	headers = {
		header.value: enm.HeaderValue[header.name].value
		for header in enm.Header
		if header.value in response_headers
	}
	if enm.Header.contentLength.value in response_headers:
		headers[enm.Header.contentLength.value] = content_length
	if enm.Header.contentType.value in response_headers:
		headers[enm.Header.contentType.value] = content_type
	if enm.Header.date.value in response_headers:
		headers[enm.Header.date.value] = lib.datetime.datetime.now(
			lib.datetime.timezone.utc
		).isoformat()

	for name, header in response_headers.items():
		if name in request.headers:
			headers[name] = request.headers[name]
		elif name not in headers:
			headers[name] = header.description or ''
	headers.update(override_headers)

	return obj.Response(
		request_id=request.id_,
		status_code=status_code,
		headers=headers,
		body=response_body,
	)
