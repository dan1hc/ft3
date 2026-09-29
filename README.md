# [![banner](https://1howardcapital.s3.amazonaws.com/images/ft3/banner.png)](https://ft3.readthedocs.io)

[![MinVersion](https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/dan1hc/ft3/main/pyproject.toml&color=gold)](https://pypi.org/project/ft3)
[![PyVersions](https://img.shields.io/pypi/pyversions/ft3?color=brightgreen)](https://pypi.org/project/ft3)
[![readthedocs](https://readthedocs.org/projects/ft3/badge)](https://ft3.readthedocs.io)
[![CI](https://github.com/dan1hc/ft3/actions/workflows/main.yml/badge.svg?branch=main&event=push)](https://github.com/dan1hc/ft3/actions)
[![codeql](https://github.com/dan1hc/ft3/workflows/codeql/badge.svg)](https://github.com/dan1hc/ft3/actions/workflows/codeql.yml)
[![coverage](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/dan1hc/ft3/main/pyproject.toml&query=tool.coverage.report.fail_under&label=coverage&suffix=%25&color=brightgreen)](https://github.com/dan1hc/ft3/actions)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![PyPI](https://img.shields.io/pypi/v/ft3?color=blue)](https://pypi.org/project/ft3)
[![License](https://img.shields.io/pypi/l/ft3?color=blue)](https://www.gnu.org/licenses/lgpl-3.0)

# Overview

**Author:** dan@1howardcapital.com

**Summary:** Zero-dependency Python framework for object-oriented services.
Declare an `Object` once; ft3 derives validation, JSON serialization, a
REST API with an OpenAPI document, and structured logging from it.

ft3 is built for agents as its only users. Every rule it enforces is
written down in [AGENTS.md](AGENTS.md), every error names the fix, and
`ft3 check` tells you whether a package is correct before you serve it.
Every Python block in this file is executed by the test suite, so the
examples cannot drift.

## Getting started

```sh
pip install ft3
ft3 check my_pkg      # validate a package: routes, errors, per-field notices
ft3 openapi my_pkg    # write openapi.json (a build artifact)
ft3 api my_pkg        # serve locally with the stdlib server
```

### Declare an Object

```python
import ft3


class Pet(ft3.Object):
    """A pet. The docstring is the resource description."""

    id_: ft3.Field[str]
    name: ft3.Field[str]
    type_: ft3.Field[str] = ft3.Field(default='dog', enum=['cat', 'dog'])
    is_tail_wagging: ft3.Field[bool] = True


pet = Pet({'id': 'abc123', 'name': 'Bob', 'type': 'cat'})

assert pet.id_ == 'abc123' and pet.type_ == 'cat'
assert pet.as_response == {
    'id': 'abc123',
    'name': 'Bob',
    'type': 'cat',
    'isTailWagging': True,
}
```

Field names are `snake_case`; trailing underscores are stripped on the
wire, and camelCase keys are accepted on input. A field with no default and
no `Optional` type is required.

### Strict and lenient validation

Plain construction is lenient, so stored records always hydrate: constraint
violations are kept and logged once per field. Request input is always
strict. A class opts in to strict construction with `strict=True`.

```python
import ft3


class Order(ft3.Object, strict=True):
    """Strict classes raise instead of warning."""

    order_id: ft3.Field[str]
    quantity: ft3.Field[int] = ft3.Field(default=1, minimum=1, maximum=10)


try:
    Order(order_id='o1', quantity=99)
except ft3.objects.exc.ConstraintViolationError as error:
    assert error.code == 'constraint_violation_error'
    assert (error.field, error.constraint, error.limit) == ('quantity', 'maximum', 10)
else:
    raise AssertionError('strict classes reject out-of-range values')

try:
    Order()
except ft3.objects.exc.MissingRequiredFieldError as error:
    assert error.field == 'order_id'
else:
    raise AssertionError('strict classes require required fields')

assert Order.quantity.parse('3', strict=True) == 3

try:
    Order.quantity.parse(3.9, strict=True)
except ft3.objects.exc.ConstraintViolationError as error:
    assert error.constraint == 'lossless'
else:
    raise AssertionError('strict parsing only allows lossless coercion')
```

Every ft3 exception is an ordinary `Exception` with a stable `code`.

### Serve an API

Register an `Object`, attach handlers, and the routes, request parsing,
error responses, and OpenAPI document follow. The bundled `ft3.template`
package is a complete example.

```python
import ft3

api = ft3.api.api_from_package(
    'ft3.template', 'v1', '/', include_version_prefix=True
)
client = ft3.api.Client(api)

created = client.post('/v1/petWithPets', body={'name': 'Rex', 'type': 'dog'})
assert created.status_code == 201

rejected = client.post('/v1/petWithPets', body={'name': 'Rex', 'type': 'turtle'})
assert rejected.status_code == 400
assert rejected.body['errorRef'] == 'constraint_violation_error'
assert 'enum' in rejected.body['errorMessage']

assert client.get('/v1/nothing').status_code == 404
assert client.get('/v1/healthz').status_code == 200
```

`ft3.api.Handler(api=api)(request)` is the same entry point for a gateway
event. `ft3 api` wraps it in the stdlib HTTP server for local development.

### Query generation

Comparisons against class-level fields build a database-agnostic query
document.

```python
import ft3


class Pet(ft3.Object):
    """A pet."""

    id_: ft3.Field[str]
    name: ft3.Field[str]
    type_: ft3.Field[str] = ft3.Field(default='dog', enum=['cat', 'dog'])


query = ((Pet.type_ == 'dog') & (Pet.name == 'Fido')) | Pet.name % ('fido', 0.75)
query += 'name'

assert dict(query) == {
    'limit': None,
    'or': [
        {
            'and': [
                {'eq': 'dog', 'field': 'type', 'limit': None, 'sorting': []},
                {'eq': 'Fido', 'field': 'name', 'limit': None, 'sorting': []},
            ],
            'limit': None,
            'sorting': [],
        },
        {
            'field': 'name',
            'like': 'fido',
            'limit': None,
            'sorting': [],
            'threshold': 0.75,
        },
    ],
    'sorting': [{'direction': 'asc', 'field': 'name'}],
}
```

### Logging

`ft3.log` emits one valid JSON document per record and redacts values that
should never be logged. `print()` calls become INFO records instead of
reaching stdout.

```python
import ft3

ft3.log.info({'api_key': 'sk-123', 'note': 'hello'})
# >>> {"level": "INFO", "timestamp": "2026-09-29T15:26:20.083Z", "logger": "ft3",
#      "message": {"content": {"api_key": "[ REDACTED :: API_KEY_TOKEN ]", "note": "hello"}}}
```

## Upgrading from 1.x

ft3 2.0 changes validation, error, serialization, routing, and logging
semantics. [V2.md](V2.md) lists every change. Set `FT3_LEGACY_WIRE=true`
to keep all 1.x wire behavior during the upgrade, run `ft3 check` to get
the per-field migration list, then turn the switch off.

## Acknowledgments

* #### @sol.courtney
    * Teaching me the difference between chicken-scratch, duct tape, and bubble
    gum versus actual engineering, and why it matters.
