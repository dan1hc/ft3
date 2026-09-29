"""Objects module."""

from .. import obj

__all__ = (
	'Client',
	'Error',
	'Handler',
	'Pattern',
	'Request',
	'Response',
	*obj.__all__,
)

from ... import core
from ... import objects

from ... import log, Field, Object

from .. import typ

from ..obj import *

from . import cfg
from . import enm
from . import exc
from . import lib


class Constants(cfg.Constants):
	"""Constant values specific to this file."""


class Pattern:
	"""Compiled regex patterns."""

	PathId = lib.re.compile('({' + Constants.PATH_ID + '})')
	"""Matches resource ids within a path uri."""


class Error(Object):
	"""A stimple error message object."""

	error_message: Field[str]
	error_code: Field[typ.HttpErrorCode]
	error_ref: Field[lib.t.Optional[str]] = None
	"""
    Stable identifier of the underlying error: an ft3 exception's \
    `code`, otherwise the exception class name in snake_case.

    """

	@classmethod
	def from_exception(
		cls, exception: typ.ExceptionType | type[typ.ExceptionType]
	) -> lib.Self:
		"""
        Populate error object from an exception instance or class.

        ---

        The HTTP code comes from the first class in the exception's \
        MRO that is a known HTTP error or is mapped to one, so \
        subclasses inherit their parent's status.

        """

		exc_tp: type[BaseException]
		msg: lib.t.Optional[str] = None
		if isinstance(exception, type):
			exc_tp = exception
		else:
			exc_tp = type(exception)
			if exception.args:
				msg = str(exception.args[0])

		error_code: typ.HttpErrorCode = 500
		for klass in exc_tp.__mro__:
			name_ = klass.__name__
			if name_ in enm.ErrorCode.__members__:
				error_code = enm.ErrorCode.__members__[name_].value
				break
			elif name_ in enm.ErrorMap.__members__:
				mapped = enm.ErrorMap.__members__[name_].value
				error_code = enm.ErrorCode.__members__[mapped].value
				break

		if msg is None:
			msg = enm.ErrorMessage['_' + str(error_code)].value

		return cls(
			error_message=msg,
			error_code=error_code,
			error_ref=core.exc.code_for(exc_tp),
		)

	@classmethod
	def from_request_exception(cls, exception: Exception) -> lib.Self:
		"""
        Like `from_exception`, for failures while parsing a request: \
        anything not already mapped is the request's fault (400).

        """

		error = cls.from_exception(exception)
		if error.error_code == 500:
			error.error_code = 400
			error.error_message = str(exception) or enm.ErrorMessage._400.value
		return error


class Request(Object):
	"""A simple request object."""

	id_: Field[str] = lambda: lib.uuid.uuid4().hex

	url: Field[str]
	path: Field[str]
	method: Field[str]

	headers: Field[dict[str, str]] = {}

	body: Field[lib.t.Any] = None

	path_params: Field[dict[typ.AnyString, str]] = {}
	query_params: Field[dict[typ.AnyString, lib.t.Any]] = {}

	def parse_body(
		self,
		operation: 'Operation',
		obj_: lib.t.Optional[type[typ.Object]] = None,
	) -> lib.t.Optional[lib.Never]:
		"""
        Parse JSON body from url string and optionally an `Object`.

        ---

        Automatically handles translation and injection of `id` params \
        for `PUT` requests.

        """

		deserialized: (
			dict[typ.string[lib.t.Any], lib.t.Any]
			| list[dict[typ.string[lib.t.Any], lib.t.Any]]
			| str
			| bool
			| int
			| float
			| typ.NoneType  # type: ignore[valid-type]
		)
		if operation.request_body is not None:
			content = operation.request_body.content.get(
				enm.ContentType.json.value
			)
		else:  # pragma: no cover
			content = None

		if (
			isinstance(self.body, str)
			and operation.request_body is not None
			and content is not None
			and (self.method == Constants.POST or self.method == Constants.PUT)
		):
			str_body: str = self.body
			deserialized = lib.json.loads(str_body)
		elif operation.request_body is not None and content is not None:
			deserialized = self.body
		else:  # pragma: no cover
			deserialized = None

		id_params: dict[typ.string[typ.camelCase], str] = {}
		if (
			self.method == Constants.PUT
			and self.path_params
			and content is not None
			and content.schema is not None
			and content.schema.properties is not None
		):
			ref_map: typ.AnyDict = {
				name_: schema._ref_
				for name_, schema in content.schema.properties.items()
				if schema._ref_ is not None
			}
			for path_param, value in self.path_params.items():
				if id_name := ref_map.get(path_param):
					id_params[id_name] = value

		if isinstance(deserialized, dict) and obj_ is not None:
			body = {
				k: obj_.__dataclass_fields__[cname].parse(
					v, strict=not Constants.LEGACY_WIRE
				)
				for k, v in deserialized.items()
				if core.strings.utl.isCamelCaseString(k)
				and isinstance(content, Content)
				and content.schema is not None
				and content.schema.properties is not None
				and k in content.schema.properties
				and (cname := core.strings.utl.cname_for(k, obj_.fields))
				is not None
			}
			body.update(id_params)
			self.body = body
		elif isinstance(deserialized, list) and obj_ is not None:
			body = [
				{
					**id_params,
					**{
						k: obj_.__dataclass_fields__[cname].parse(
							v, strict=not Constants.LEGACY_WIRE
						)
						for k, v in d.items()
						if core.strings.utl.isCamelCaseString(k)
						and isinstance(content, Content)
						and content.schema is not None
						and content.schema.properties is not None
						and k in content.schema.properties
						and (
							cname := core.strings.utl.cname_for(k, obj_.fields)
						)
						is not None
					},
				}
				for d in deserialized
			]
			self.body = body

		return None

	def parse_query_params(
		self,
		method: typ.string[typ.snake_case],
		operation: 'Operation',
		obj_: lib.t.Optional[type[typ.Object]] = None,
	) -> None:
		"""
        Parse query parameters from url string and optionally an \
        `Object`.

        """

		parsed = lib.urllib.parse.urlparse(self.url)
		if not self.query_params:
			self.query_params = {
				k: lib.urllib.parse.unquote(s[1])
				for _s in parsed.query.split('&')
				if (s := _s.split('='))
				and len(s) == 2
				and (
					(k := lib.urllib.parse.unquote(s[0]))
					and core.strings.utl.isCamelCaseString(k)
				)
			}
		if obj_ is not None:
			self.query_params = {
				param.name: field.parse(
					query_param, strict=not Constants.LEGACY_WIRE
				)
				for param in (operation.parameters or ())
				if param.name
				and (
					query_param := (
						self.query_params.get(param.name, Constants.UNDEFINED)
					)
				)
				!= Constants.UNDEFINED
				and param.schema is not None
				and (
					(
						cname := core.strings.utl.cname_for(
							param.name, obj_.fields
						)
					)
					is not None
					or (
						obj_.__name__.lower() + 'Id' == param.name
						and (
							cname := core.strings.utl.cname_for(
								'id', obj_.fields
							)
						)
						is not None
					)
				)
				and param.in_ == enm.ParameterLocation.query.value
				and (
					method == Constants.PATCH or not param.schema['write_only']
				)
				and (method == Constants.GET or not param.schema['read_only'])
				and (field := obj_.__dataclass_fields__.get(cname))
			}

		return None

	def validate_input(
		self, obj_: type[typ.Object], method: typ.string[typ.snake_case]
	) -> lib.t.Optional[lib.Never]:
		"""
        Apply the input policy to the parsed body and query params.

        ---

        * Private (`_x`) fields may not be supplied: 400, or accepted \
        with a one-time WARNING under `FT3_LEGACY_WIRE`.
        * `read_only` fields are dropped with a one-time WARNING.
        * On `POST` and `PUT`, every `required` field must be present \
        and non-null in the body: 400, or a one-time WARNING under \
        `FT3_LEGACY_WIRE`.

        """

		bodies: list[dict[typ.AnyString, lib.t.Any]] = []
		if isinstance(self.body, dict):
			bodies.append(self.body)
		elif isinstance(self.body, list):
			bodies.extend(b for b in self.body if isinstance(b, dict))
		require = method in (Constants.POST, Constants.PUT)
		for body in bodies:
			self._apply_input_policy(obj_, body, require)
		self._apply_input_policy(obj_, self.query_params, False)
		return None

	@staticmethod
	def _apply_input_policy(
		obj_: type[typ.Object],
		mapping: dict[typ.AnyString, lib.t.Any],
		require: bool,
	) -> lib.t.Optional[lib.Never]:
		from ... import loggers

		legacy = Constants.LEGACY_WIRE
		present: dict[str, lib.t.Any] = {}
		for key in list(mapping):
			cname = core.strings.utl.cname_for(str(key), obj_.fields)
			if cname is None:
				continue
			field = obj_.__dataclass_fields__[cname]
			if cname.startswith('_'):
				if not legacy:
					raise exc.RequestError(
						' '.join(
							(
								f"Field: '{key}' is private and may not be",
								f"supplied. FIX: remove '{key}' from the",
								'request.',
							)
						)
					)
				loggers.utl.warn_once(
					(obj_.__name__, 'private_input', cname),
					{
						'legacy.private_input': {
							'object': obj_.__name__,
							'field': cname,
							'outcome': 'accepted',
							'fix': 'stop sending private fields',
						}
					},
				)
			elif field.read_only:
				mapping.pop(key)
				loggers.utl.warn_once(
					(obj_.__name__, 'read_only_input', cname),
					{
						'read_only.input': {
							'object': obj_.__name__,
							'field': cname,
							'outcome': 'dropped',
							'fix': 'stop sending read_only fields',
						}
					},
				)
				continue
			present[cname] = mapping[key]
		if not require:
			return None
		for fname, field in obj_.__dataclass_fields__.items():
			if not field.required or field.read_only:
				continue
			if present.get(fname) is not None:
				continue
			if not legacy:
				raise objects.exc.MissingRequiredFieldError(
					obj_.__name__, fname
				)
			loggers.utl.warn_once(
				(obj_.__name__, 'missing_required', fname),
				{
					'legacy.missing_required': {
						'object': obj_.__name__,
						'field': fname,
						'outcome': 'accepted',
						'fix': 'supply every required field',
					}
				},
			)
		return None

	def parse_path_params(self, uri: str, operation: 'Operation') -> None:
		"""Parse path parameters from a matched path uri."""

		parsed = lib.urllib.parse.urlparse(self.url)
		path_components = uri.strip('/').split('/')
		if not self.path_params:
			self.path_params = {
				s: lib.urllib.parse.unquote(v)
				for i, v in enumerate(parsed.path.strip('/').split('/'))
				if bool(Pattern.PathId.match(k := path_components[i]))
				and (
					(s := lib.urllib.parse.unquote(k[1:-1]))
					and core.strings.utl.isCamelCaseString(s)
				)
			}
		self.path_params = {
			param.name: path_param
			for param in (operation.parameters or ())
			if (
				path_param := (
					self.path_params.get(param.name, Constants.UNDEFINED)
				)
			)
			!= Constants.UNDEFINED
			and param.schema is not None
			and param.in_ == enm.ParameterLocation.path.value
		}

		return None


class Response(Object):
	"""A simple response object."""

	request_id: Field[str]

	status_code: Field[typ.HttpStatusCode] = 200

	headers: Field[dict[str, str]] = {}

	body: Field[lib.t.Any]

	def serialize(self) -> bytes | str:
		"""JSON serialize body if not already a string."""

		if not isinstance(self.body, (bytes, str)):
			return lib.json.dumps(self.body, default=str)
		else:
			return self.body


class Client:
	"""
	In-process API client for tests and agents.

	---

	Builds a `Request` the way the HTTP server would and returns the \
	`Response` the API would send, without sockets or threads.

	```python
	client = ft3.api.Client(ft3.api.api_from_package('my_pkg', 'v1', '/'))
	response = client.get('/v1/pets', query={'type': 'dog'})
	assert response.status_code == 200
	```

	"""

	def __init__(self, api: Api) -> None:
		self.handler = Handler(api=api)

	def request(
		self,
		method: str,
		path: str,
		*,
		body: lib.t.Any = None,
		headers: lib.t.Optional[dict[str, str]] = None,
		query: lib.t.Optional[dict[str, lib.t.Any]] = None,
	) -> 'Response':
		"""Send one request and return the response."""

		url = path
		if query:
			url += '?' + lib.urllib.parse.urlencode(query)
		return self.handler(
			Request(
				url=url,
				path=path,
				method=method.lower(),
				body=body,
				headers=headers or {},
			)
		)

	def get(self, path: str, **kwargs: lib.t.Any) -> 'Response':
		"""Send a GET request."""

		return self.request('get', path, **kwargs)

	def post(self, path: str, **kwargs: lib.t.Any) -> 'Response':
		"""Send a POST request."""

		return self.request('post', path, **kwargs)

	def put(self, path: str, **kwargs: lib.t.Any) -> 'Response':
		"""Send a PUT request."""

		return self.request('put', path, **kwargs)

	def patch(self, path: str, **kwargs: lib.t.Any) -> 'Response':
		"""Send a PATCH request."""

		return self.request('patch', path, **kwargs)

	def delete(self, path: str, **kwargs: lib.t.Any) -> 'Response':
		"""Send a DELETE request."""

		return self.request('delete', path, **kwargs)

	def options(self, path: str, **kwargs: lib.t.Any) -> 'Response':
		"""Send an OPTIONS request."""

		return self.request('options', path, **kwargs)


class Handler(Object):
	"""A simple request handler."""

	api: Field[Api]
	file_paths: Field[list[str]] = []

	def __call__(self, request: Request) -> Response:
		"""Call on a request to receive a response."""

		from . import utl

		log.info({'request.raw': request})

		response = utl.handle_request(request, self.api)

		if response.status_code < 400:
			log.info({'response.success': response})
		else:
			log.warning({'response.error': response})

		return response
