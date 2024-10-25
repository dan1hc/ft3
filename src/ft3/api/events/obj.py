"""Objects module."""

from .. import obj

__all__ = (
    'Error',
    'Handler',
    'Pattern',
    'Request',
    'Response',
    *obj.__all__
    )

from ... import core

from ... import log, Field, Object

from .. import typ

from .. obj import *

from . import cfg
from . import enm
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

    @classmethod
    def from_exception(
        cls,
        exception: typ.ExceptionType | type[typ.ExceptionType]
        ) -> lib.Self:
        """Populate error object from an exception."""

        name_ = exception.__class__.__name__
        exc_tp: type[typ.ExceptionType] = exception.__class__

        msg: lib.t.Optional[str]
        if isinstance(exception.args, tuple) and exception.args:
            msg = str(exception.args[0])
        else:
            msg = None

        error_code: typ.HttpErrorCode = 500
        while issubclass(exc_tp, Exception):
            if name_ in enm.ErrorCode._member_names_:
                error_code = enm.ErrorCode[name_].value
                break
            elif name_ in enm.ErrorMap._member_names_:
                error_code = enm.ErrorCode[enm.ErrorMap[name_].value].value
                break
            else:
                name_ = exc_tp.__name__
            exc_tp = exc_tp.__class__

        if msg is None:
            msg = enm.ErrorMessage['_' + str(error_code)].value

        return cls(
            error_message=msg,
            error_code=error_code
            )


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
            | str | bool | int | float | typ.NoneType  # type: ignore[valid-type]
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
            and (
                self.method == Constants.POST
                or self.method == Constants.PUT
                )
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
                for name_, schema
                in content.schema.properties.items()
                if schema._ref_ is not None
                }
            for path_param, value in self.path_params.items():
                if (id_name := ref_map.get(path_param)):
                    id_params[id_name] = value

        if isinstance(deserialized, dict) and obj_ is not None:
            body = {
                k: obj_.__dataclass_fields__[cname].parse(v)
                for k, v
                in deserialized.items()
                if core.strings.utl.isCamelCaseString(k)
                and isinstance(content, Content)
                and content.schema is not None
                and content.schema.properties is not None
                and k in content.schema.properties
                and (
                    cname := core.strings.utl.cname_for(k, obj_.fields)
                    ) is not None
                }
            body.update(id_params)
            self.body = body
        elif isinstance(deserialized, list) and obj_ is not None:
            body = [
                {
                    **id_params,
                    **{
                        k: obj_.__dataclass_fields__[cname].parse(v)
                        for k, v
                        in d.items()
                        if core.strings.utl.isCamelCaseString(k)
                        and isinstance(content, Content)
                        and content.schema is not None
                        and content.schema.properties is not None
                        and k in content.schema.properties
                        and (
                            cname := core.strings.utl.cname_for(k, obj_.fields)
                            ) is not None
                        }
                    }
                for d
                in deserialized
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
                for _s
                in parsed.query.split('&')
                if (s := _s.split('='))
                and len(s) == 2
                and (
                    (k := lib.urllib.parse.unquote(s[0]))
                    and core.strings.utl.isCamelCaseString(k)
                    )
                }
        if obj_ is not None:
            self.query_params = {
                param.name: field.parse(query_param)
                for param
                in (operation.parameters or ())
                if param.name
                and (
                    query_param := (
                        self.query_params.get(
                            param.name,
                            Constants.UNDEFINED
                            )
                        )
                    ) != Constants.UNDEFINED
                and param.schema is not None
                and (
                    cname := core.strings.utl.cname_for(
                        param.name,
                        obj_.fields
                        )
                    ) is not None
                and param.in_ == enm.ParameterLocation.query.value
                and (
                    method == Constants.PATCH
                    or not param.schema['write_only']
                    )
                and (
                    method == Constants.GET
                    or not param.schema['read_only']
                    )
                and (field := obj_.__dataclass_fields__.get(cname))
                }

        return None

    def parse_path_params(self, uri: str, operation: 'Operation') -> None:
        """Parse path parameters from a matched path uri."""

        parsed = lib.urllib.parse.urlparse(self.url)
        path_components = uri.strip('/').split('/')
        if not self.path_params:
            self.path_params = {
                s: lib.urllib.parse.unquote(v)
                for i, v
                in enumerate(parsed.path.strip('/').split('/'))
                if bool(Pattern.PathId.match(k := path_components[i]))
                and (
                    (s := lib.urllib.parse.unquote(k[1:-1]))
                    and core.strings.utl.isCamelCaseString(s)
                    )
                }
        self.path_params = {
            param.name: path_param
            for param
            in (operation.parameters or ())
            if (
                path_param := (
                    self.path_params.get(
                        param.name,
                        Constants.UNDEFINED
                        )
                    )
                ) != Constants.UNDEFINED
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


class Handler(Object):
    """A simple request handler."""

    api: Field[Api]
    file_paths: Field[list[str]] = []

    def __call__(self, request: Request) -> Response:
        """Call on a request to receive a response."""

        from . import utl

        log.info(request)

        response = utl.handle_request(request, self.api)

        if response.status_code < 400:
            log.info(response)
        else:
            log.warning(response)

        return response
