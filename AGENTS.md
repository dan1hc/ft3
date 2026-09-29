# ft3 for agents

ft3 is a zero-dependency Python framework for object-oriented services.
You declare an `Object` once, and ft3 derives validation, JSON
serialization, a REST API with an OpenAPI document, and structured logging
from that one declaration. This file is the complete rulebook for writing
and calling ft3 code. `V2.md` records the design decisions behind it.

## Verify loop

After every edit, run these from the package's repo root. All three must
pass before work is done.

```sh
ft3 check my_pkg            # JSON report: errors, routes, per-field notices; exit 1 on errors
python -m mypy              # ft3 is fully typed
pytest                      # the repo's own tests
```

`ft3 check --format text` prints the same report for a human. `ft3 openapi
my_pkg -o openapi.json` writes the API document; it is a build artifact,
generate it in CI, never at import time.

## Objects and Fields

```python
import ft3


class Pet(ft3.Object):
    """A pet. The docstring is the resource description."""

    id_: ft3.Field[str] = ft3.Field(default=lambda: '...', read_only=True)
    name: ft3.Field[str]                      # required, no default
    type_: ft3.Field[str] = ft3.Field(default='dog', enum=['cat', 'dog'])
    """Attribute docstrings become the field's description."""
    tags: ft3.Field[list[str]] = []           # mutable defaults are copied per instance
```

Rules the metaclass enforces at class definition (each raises a named
error with the fix in its message):

- Every annotation is `ft3.Field[T]`. `x: int` raises `FieldAnnotationError`.
- Every field name is `snake_case`. Anything else in the class body that is
  not snake_case raises `IncorrectCasingError`.
- Reserved names (`get`, `items`, `keys`, `update`, `fields`, `GET`, ...)
  raise `ReservedKeywordError`; the fix is a trailing underscore (`items_`).
  Trailing underscores are stripped on the wire (`id_` serializes as `id`).
- A field may be declared as a bare default, a `Field(...)`, or a dict of
  Field keys. A callable default is a factory. A missing default with no
  `Optional` type means the field is required.
- Fields named `*id` or `*key` are hash fields: they define equality,
  hashing, and path parameters.

Field options: `default`, `required`, `enum`, `minimum`, `maximum`,
`exclusive_minimum`, `exclusive_maximum`, `multiple_of`, `min_length`,
`max_length`, `pattern`, `min_items`, `max_items`, `unique_items`,
`read_only`, `write_only`, `camel_case_keys`, `drop_null_items`.

## Validation: strict and lenient

Two modes. **Strict** enforces every declared constraint, allows only
lossless coercion (`'3'` to `3` is fine; `3.9` to an int raises; a bool in
an int field raises), and requires every `required` field to be present and
non-null. **Lenient** is the hydrate path for stored records: types are
coerced as before, constraint violations are kept, and each kind of
violation is logged once per class and field at WARNING.

| Path | Mode |
|---|---|
| Generated request parsing (body, query, path) | strict |
| `Field.parse(value, strict=True)` | strict |
| `class Model(ft3.Object, strict=True)` and its subclasses | strict on construction and assignment |
| Plain `Model(record)` | lenient |

Errors: `TypeValidationError` (wrong type), `ConstraintViolationError`
(`.field`, `.constraint`, `.limit`, `.value`), `MissingRequiredFieldError`
(`.object`, `.field`). Unknown keys are dropped everywhere with one WARNING
per class and key, never rejected.

## Serialization

- `obj.as_response`: camelCase keys, nulls omitted, private (`_x`) and
  `write_only` fields omitted, `read_only` fields included. This is the wire.
- `obj.to_dict()`: snake_case, nulls included, private included,
  `read_only` fields **omitted** unless `include_read_only=True`.
  Persistence layers rely on this default.
- Dict-typed field values are never re-keyed; set `camel_case_keys=True` on
  the field for 1.x behavior. `None` items in list fields keep their
  position; set `drop_null_items=True` to drop them.
- `bool(obj)` is True when any field differs from its default and never
  raises. `a == b` compares hash fields only. `a - b` is a dict of `b`'s
  values that differ. `copy.deepcopy(obj)` shares nothing with the original.
- `dict(obj)` converts nested Objects to dicts by inspecting the caller for
  the name `dict`; prefer `to_dict()` in new code.

## Errors

Every ft3 exception subclasses `Exception`, so `except Exception` catches
it, and carries a stable `code` (its snake_case class name unless set).
`ft3.core.exc.code_for(SomeError)` gives the same code for any exception
class. Error bodies on the wire are
`{"errorMessage", "errorCode", "errorRef"}` where `errorRef` is that code.

HTTP mapping walks the exception MRO, so subclasses inherit their parent's
status: `RequestError` 400, `NotAuthenticatedError` 401,
`NotAuthorizedError` 403, `ResourceNotFoundError` 404,
`ResourceLockedError` 423, `RateLimitedError` 429,
`MethodNotImplementedError` 501, anything else 500. Built-ins are mapped
too: `SyntaxError` and `JSONDecodeError` 400, `PermissionError` 403,
`FileNotFoundError` 404, `NotImplementedError` 501. ft3 validation errors
raised anywhere in a request map to 400.

## API

```python
import ft3


@ft3.Api.register
class Pet(ft3.Object):
    """Served at /pets and /pets/{petId}."""

    id_: ft3.Field[str] = ft3.Field(default=lambda: 'p1', read_only=True)
    name: ft3.Field[str]


@Pet.GET
def list_pets(request: ft3.api.Request) -> list[Pet]:
    """GET /pets: return a list."""
    return [Pet(name='Rex')]


@Pet.POST
def create_pet(request: ft3.api.Request) -> Pet:
    """POST /pets: request.body is already parsed and validated."""
    return Pet(request.body)
```

- Register the class with `@ft3.Api.register` **and** attach handlers with
  `@Cls.GET/POST/PUT/PATCH/DELETE`. Handlers on an unregistered class are
  reported by `ft3 check` and logged at startup.
- Routes derive from the class: `/{plural camelCase name}` for `POST` and
  list `GET`, `/{plural}/{nameId}` for single `GET`, `PUT`, `PATCH`,
  `DELETE`. Sub-resources come from a field typed as another registered
  Object with hash fields: `@Parent.child_field.GET`.
- One GET surface per resource: a list `GET` filtered by query params, or a
  single `GET` by id, decided by the handler's return annotation. No custom
  verb paths; model state transitions as `PUT` with `action_*` booleans.
- The return annotation is required and drives OpenAPI. Return an
  `Object`, a list of them, a `str`, `None` (204 on DELETE), or
  `ft3.api.Response(status_code=..., headers=..., body=...)` to set the
  status and per-response headers explicitly.
- Request input policy: body and query values are parsed strictly (400 on a
  violation); private `_x` fields are rejected (400); `read_only` fields
  are dropped with a one-time WARNING; `POST` and `PUT` bodies must carry
  every `required` field. Malformed JSON is a 400 before any handler runs.
  `PATCH` reads its fields from query params.
- Routes match exactly. `/pets` never matches `/petsitters`. A trailing
  slash is tolerated; the query string is ignored for matching.
- `@ft3.api.Header.request(...)`, `@ft3.api.Header.response(...)` and
  `@ft3.api.SecurityScheme.api_key(...)` document headers and auth in the
  OpenAPI output. They do not enforce anything.
- `/healthz` is served unless `include_heartbeat=False`.

Build and drive an API in-process:

```python
import ft3

api = ft3.api.api_from_package('my_pkg', 'v1', '/', include_version_prefix=True)
client = ft3.api.Client(api)
response = client.get('/v1/pets', query={'name': 'Rex'})
```

`ft3 api my_pkg --port 8080` serves it with the stdlib HTTP server for
local development only. Deploy behind a gateway: pass the gateway event to
`ft3.api.Handler(api=api)(request)`.

## Logging

`ft3.log` is the only logger. Every record is one valid JSON document:
`{"level", "timestamp", "logger", "message"}`. Log a `str`, `dict`, `list`,
`Object`, or Object class; anything else raises
`InvalidLogMessageTypeError`. printf-style args work (`log.info('x %s', y)`).

- `ERROR` and above inside an `except` block attach the whole traceback as a
  list of lines. `exc_info=False` suppresses it.
- `print()` becomes an `INFO` record with a `printed` key. Use `log.debug`.
- Values under keys that look sensitive (`api_key`, `password`, `*token`,
  `secret`, `credential`, `cookie`, `authorization`) and values that look
  like secrets (cloud keys, JWTs, connection-string passwords, card and
  SSN numbers) are redacted. `LOG_REDACT_ALLOW=a,b` exempts key names.
- Long strings are wrapped and truncated; tracebacks are not.

## Environment variables

| Variable | Default | Effect |
|---|---|---|
| `ENV` | `local` | runtime environment name |
| `LOG_LEVEL` | `DEBUG` locally, else `INFO` | logger level; unknown names fall back to `INFO` |
| `LOG_FORMAT` | `json` | `json` one line per record, `pretty` indented |
| `LOG_TRACEBACK` | `true` | attach tracebacks to ERROR+ |
| `INTERCEPT_PRINTS` | `true` | route `print()` into the log (`LOG_PRINTS=true` also disables) |
| `LOG_REDACT_ALLOW` | empty | key names never redacted by key |
| `FT3_LEGACY_WIRE` | `false` | restore every 1.x wire behavior (see below) |
| `FT3_EXTRACT_ATTRIBUTE_DOCS` | `1` | read attribute docstrings from source |
| `INDENT`, `MAX_CHARS`, `CUTOFF_LEN`, `WRAP_WIDTH` | `2`, `384`, `12`, `64` | repr and log formatting |

All are read once at import.

## Compatibility with 1.x

`FT3_LEGACY_WIRE=true` restores every 1.x request-side and response-side
behavior at once: dict keys camelCased, list nulls dropped, private fields
and missing required fields accepted with a one-time WARNING, and request
parse failures logged instead of returning 400. Per-field
`camel_case_keys` and `drop_null_items` override it. Non-wire fixes
(exception base, `bool()`, `deepcopy`, exact routing) are not switchable.
`ft3 check` lists every field relying on a changed default.

## Contract tests

`src/tests/contracts/` pins every behavior above. Downstream projects mirror
those pins. Change one only with a coordinated release.
