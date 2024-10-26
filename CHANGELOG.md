# CHANGELOG


## v0.1.7 (2024-10-26)

### Bug Fixes

* fix: better api logging and error handling ([`ef6b5b0`](https://github.com/dan1hc/ft3/commit/ef6b5b097012c1de09bf47836203eeef33c761d7))


## v0.1.6 (2024-10-25)

### Bug Fixes

* fix: traceback formatting and path param parsing ([`afbbb59`](https://github.com/dan1hc/ft3/commit/afbbb592bbfbdf9ae6e66afd7ea25a2de46777b1))

### Documentation

* docs: __v0.1.6__ [skip ci] ([`f0c6522`](https://github.com/dan1hc/ft3/commit/f0c6522bf6cce6deff9b0fb72cf0c17033e72988))


## v0.1.5 (2024-10-25)

### Bug Fixes

* fix: pluralizations aws key redaction api log exc (#29)

* fix: pluralizations aws key redaction api log exc

* docs: __v0.1.5-rc.1__ [skip ci]

* fix: serialize json api resp with default str

* docs: __v0.1.5-rc.2__ [skip ci]

* fix: need to serialize resp with default for content len

* docs: __v0.1.5-rc.3__ [skip ci]

* fix: protection for custom query param passing

* docs: __v0.1.5-rc.4__ [skip ci]

---------

Co-authored-by: github-actions <action@github.com> ([`22c78c9`](https://github.com/dan1hc/ft3/commit/22c78c9400b588ebcb5aeb50aab66283d0a6cf36))

### Documentation

* docs: __v0.1.5__ [skip ci] ([`9060cc6`](https://github.com/dan1hc/ft3/commit/9060cc6464937469c6f0db44be8bd5e7ab2c3192))

* docs: update readme and trigger ci ([`76918f8`](https://github.com/dan1hc/ft3/commit/76918f84d5e595955afcca7574286c3dfd43d5f9))


## v0.1.4 (2024-10-22)

### Bug Fixes

* fix: only allow endpoint hierarchy expansion if field is named same (#27)

* fix: only allow endpoint hierarchy expansion if field is named same

* docs: __v0.1.4-rc.1__ [skip ci]

* fix: allow headers on POST

* docs: __v0.1.4-rc.2__ [skip ci]

* fix: __ior__ and update typing for objs

* docs: __v0.1.4-rc.3__ [skip ci]

---------

Co-authored-by: github-actions <action@github.com> ([`34b685a`](https://github.com/dan1hc/ft3/commit/34b685a2e73012b84b560576ba6afd7ffea24357))

### Continuous Integration

* ci: workaround sem release pr no trigger issue ([`9b6b82a`](https://github.com/dan1hc/ft3/commit/9b6b82aad9aa9e1132e6c78f75c30d8b83e1cae6))

### Documentation

* docs: __v0.1.4__ [skip ci] ([`1323cf2`](https://github.com/dan1hc/ft3/commit/1323cf220940311e8360ff616998899f42db4fb1))


## v0.1.3 (2024-10-22)

### Bug Fixes

* fix: syntax fix to trigger ci ([`84158f8`](https://github.com/dan1hc/ft3/commit/84158f81a3eb53742fe4f49322ef7a45543fd78e))

* fix: openapi headers and string types also py in md docs (#25)

* fix: openapi headers and string types also py in md docs

* docs: __v0.1.3-rc.1__ [skip ci]

---------

Co-authored-by: github-actions <action@github.com> ([`87fcf5c`](https://github.com/dan1hc/ft3/commit/87fcf5c47925cccbe6fe4b5aa1e65b1224006c57))

### Documentation

* docs: __v0.1.3__ [skip ci] ([`0e61b95`](https://github.com/dan1hc/ft3/commit/0e61b9538c6c3efccd89710125760f7c01d7174b))


## v0.1.2 (2024-10-21)

### Bug Fixes

* fix: allow for custom response headers (#23)

* fix: allow for custom response headers

* style: escape template resp header asterisk

* docs: __v0.1.2-rc.1__ [skip ci]

---------

Co-authored-by: github-actions <action@github.com> ([`df84bb5`](https://github.com/dan1hc/ft3/commit/df84bb511edb60a69d4a2f876cf3983a2c04e2a7))

### Documentation

* docs: __v0.1.2__ [skip ci] ([`e890c2f`](https://github.com/dan1hc/ft3/commit/e890c2f2b22a1c0ba247f8df90c3ff9fdd2cf43e))

### Unknown

* Response headers   (#24)

* fix: allow for custom response headers

* style: escape template resp header asterisk

* fix: allow use of custom response headers by injecting on request object ([`2d1b396`](https://github.com/dan1hc/ft3/commit/2d1b3968fbd398874c0c944815bfe96e6c997c66))


## v0.1.1 (2024-10-20)

### Bug Fixes

* fix: __multiple_fixes__ (#19)

* fix: __multiple_fixes__

Fixes multiple issues for ft3, primarily parsing on instantiation and automatic validation.

fixes #18

* docs: __v0.1.1-rc.1__ [skip ci]

* fix: typ ordering and comment cleanup

* docs: __v0.1.1-rc.2__ [skip ci]

* fix: hash does not need to be reserved

* docs: __v0.1.1-rc.3__ [skip ci]

* fix: align log format with lambda and polish

* docs: __v0.1.1-rc.4__ [skip ci]

* docs: minor readme touchups

* fix: install static html

* docs: __v0.1.1-rc.5__ [skip ci]

* fix: need to pop template not del

* docs: __v0.1.1-rc.6__ [skip ci]

* fix: mypy compliance pytyped

* docs: __v0.1.1-rc.7__ [skip ci]

* fix: dont build tests and dont auto-include version prefix

* docs: __v0.1.1-rc.8__ [skip ci]

* fix: build

* docs: __v0.1.1-rc.9__ [skip ci]

* fix: version prefix for swagger

* docs: __v0.1.1-rc.10__ [skip ci]

* fix: favicon path

* docs: __v0.1.1-rc.11__ [skip ci]

* fix: log formatting fix

* docs: __v0.1.1-rc.12__ [skip ci]

* fix: default connection header to keep-alive

* docs: __v0.1.1-rc.13__ [skip ci]

* perf: improve typing for parse

* fix: correctly type parse fn

* docs: __v0.1.1-rc.14__ [skip ci]

* fix: use default factory for openapi schema definition

* docs: __v0.1.1-rc.15__ [skip ci]

* fix: allow default on field to be a Callable[[], AnyType@Field]

* docs: __v0.1.1-rc.16__ [skip ci]

* feat: allow for optional inclusion of specific request headers with decorator

* docs: __v0.2.0-rc.1__ [skip ci]

* feat(api): implement api key security scheme

---------

Co-authored-by: dan <dan@dans-MacBook-Air.local>
Co-authored-by: github-actions <action@github.com> ([`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

### Documentation

* docs: __v0.1.1__ [skip ci] ([`4d3baf4`](https://github.com/dan1hc/ft3/commit/4d3baf45ad4bfa1c9eecdc8591be95231134bb93))

### Testing

* test: simple case to expand coverage for security schemes (#22)

* test: simple case to expand coverage for security schemes

* feat: fix oas rendering with optional type on schema ([`fd93e27`](https://github.com/dan1hc/ft3/commit/fd93e27cb74e061fe8448757e4da44798df34e42))


## v0.1.0 (2024-09-18)

### Build System

* build(deps): update sphinx requirement from ==7.* to >=7,<9 (#9)

Updates the requirements on [sphinx](https://github.com/sphinx-doc/sphinx) to permit the latest version.
- [Release notes](https://github.com/sphinx-doc/sphinx/releases)
- [Changelog](https://github.com/sphinx-doc/sphinx/blob/master/CHANGES.rst)
- [Commits](https://github.com/sphinx-doc/sphinx/compare/v7.0.0rc1...v8.0.0)

---
updated-dependencies:
- dependency-name: sphinx
  dependency-type: direct:production
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`7b3ccce`](https://github.com/dan1hc/ft3/commit/7b3ccce705a7fef8a73ddf0b61972defc65b3c1c))

* build(deps): update pre-commit requirement from ==3.7.* to >=3.7,<3.9 (#10)

Updates the requirements on [pre-commit](https://github.com/pre-commit/pre-commit) to permit the latest version.
- [Release notes](https://github.com/pre-commit/pre-commit/releases)
- [Changelog](https://github.com/pre-commit/pre-commit/blob/main/CHANGELOG.md)
- [Commits](https://github.com/pre-commit/pre-commit/compare/v3.7.0...v3.8.0)

---
updated-dependencies:
- dependency-name: pre-commit
  dependency-type: direct:production
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`f3e9fd1`](https://github.com/dan1hc/ft3/commit/f3e9fd1e52c6d5b54b6614914d9d733308fd71e8))

### Documentation

* docs: __v0.1.0__ [skip ci] ([`ee93236`](https://github.com/dan1hc/ft3/commit/ee93236193bbd4dc07e7bff225eba95169e1b8b7))

* docs: __get_funding__ ([`e39c69a`](https://github.com/dan1hc/ft3/commit/e39c69ad32b1462fb322a0b8b9d6028c30e58e78))

### Features

* feat: progress toward full OAS integration (#14)

* feat: progress toward full OAS integration

* feat: __checkpointing_add_basic_components__

* docs: __v0.1.0-rc.1__ [skip ci]

* feat: now the rest but skipped the tests

* fix: template api str locations

* fix: Self import for 310

* docs: __v0.1.0-rc.2__ [skip ci]

* fix: template polished

* docs: __v0.1.0-rc.3__ [skip ci]

* fix: handle sub objs without hash fields and sub obj precedence

* docs: __v0.1.0-rc.4__ [skip ci]

* feat: __basic_OAS_support__

Add working support for an OpenAPI spec.

closes #5

* fix: 310 support error

* docs: __v0.1.0-rc.5__ [skip ci]

---------

Co-authored-by: github-actions <action@github.com> ([`a36847e`](https://github.com/dan1hc/ft3/commit/a36847e01c6116e25cfc916e19ae8c83d23947c5))

### Testing

* test: re-test readme ([`3fa848f`](https://github.com/dan1hc/ft3/commit/3fa848f14d972a227a5b3cf34115728f198f779f))


## v0.0.1 (2024-07-28)

### Build System

* build: dunder init ([`6ce6400`](https://github.com/dan1hc/ft3/commit/6ce6400aa6abbaa51865524108f3ecee65218c7c))

### Documentation

* docs: __v0.0.1__ ([`b1eeb3e`](https://github.com/dan1hc/ft3/commit/b1eeb3e7ac12eab17e5281673a6aee283ff9fc1e))
