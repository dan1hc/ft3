# CHANGELOG


## v0.2.3 (2025-04-15)

### Bug Fixes

- __redundancy_for_id_as_query_param__
  ([`9570ada`](https://github.com/dan1hc/ft3/commit/9570ada35a41f470405bb8ee0804ac68093bebba))

### Continuous Integration

- __skip_broken_311_temporarily__
  ([`9f39aaf`](https://github.com/dan1hc/ft3/commit/9f39aaf6a4ca142df4bf0010add2e0b4c88ac799))


## v0.2.2 (2025-04-07)

### Bug Fixes

- Correct obscure error where trailing d would get replaced.
  ([`1406091`](https://github.com/dan1hc/ft3/commit/14060911c5c223d6dfdc9d305529a826a7b0deb0))


## v0.2.1 (2024-11-17)

### Bug Fixes

- Allow GET for Objects without hash_fields to return singular Object
  ([`d4f79d1`](https://github.com/dan1hc/ft3/commit/d4f79d1e0d47755c236746ec8a0197513a147d9c))


## v0.2.0 (2024-11-17)

### Documentation

- Minor documentation fixes [skip ci]
  ([`4a9f30c`](https://github.com/dan1hc/ft3/commit/4a9f30c5ec0bdbb77f9438ea48c19cf667bc08c9))

### Refactoring

- Repattern api decorators
  ([`2f57b2a`](https://github.com/dan1hc/ft3/commit/2f57b2aa82f836b2ef56d27e3563b2189b398432))

Re-implements api method decorators to allow for decoration from fields.

BREAKING CHANGE: Applications which had decorated directly from Objects will need to re-decorate
  from Fields.

### Breaking Changes

- Applications which had decorated directly from Objects will need to re-decorate from Fields.


## v0.1.17 (2024-11-13)

### Bug Fixes

- Update is_union caching
  ([`92cc637`](https://github.com/dan1hc/ft3/commit/92cc6379bd373a938419fced0a143a30ea26ab49))

### Performance Improvements

- More type caching speedups
  ([`32913e7`](https://github.com/dan1hc/ft3/commit/32913e7e58ce4422e2c194a1abf7bca77e1c29a8))


## v0.1.16 (2024-11-05)

### Performance Improvements

- More improvements to type parsing
  ([`7aa733a`](https://github.com/dan1hc/ft3/commit/7aa733a57d460d73f04d996d7d9b7ddb723b1bd4))


## v0.1.15 (2024-11-03)

### Bug Fixes

- Request routing, pathing for sub objs, improved logging
  ([`afe82af`](https://github.com/dan1hc/ft3/commit/afe82af1072fa21ec5aae2ef27161b397fec7a9e))


## v0.1.14 (2024-11-03)


## v0.1.13 (2024-11-02)

### Bug Fixes

- Do not log traceback by default
  ([`005fe7c`](https://github.com/dan1hc/ft3/commit/005fe7c5a8297ad69f95d592a424c3b817e600e4))


## v0.1.12 (2024-11-02)

### Bug Fixes

- Isolate api parse error logging and improve parse order for union tps
  ([`7138390`](https://github.com/dan1hc/ft3/commit/7138390d41dc642de333d180dbff43eb8a8a8c56))

### Documentation

- Update readme and trigger ci
  ([`3befe50`](https://github.com/dan1hc/ft3/commit/3befe50f076ebe4632e3508581ee37caed21c99a))

### Performance Improvements

- Cache improvements ([#31](https://github.com/dan1hc/ft3/pull/31),
  [`6258037`](https://github.com/dan1hc/ft3/commit/62580377c5005e7d8743f63cbbac839acdc00851))

* perf: cache fixes, enum parse from literals, perf boost

* perf: more caching improvements

* docs: __v0.1.12-rc.1__ [skip ci]

---------

Co-authored-by: github-actions <action@github.com>


## v0.1.11 (2024-10-28)

### Bug Fixes

- Further improve error logging for api
  ([`58a2d0d`](https://github.com/dan1hc/ft3/commit/58a2d0d0aa7def9e5545d5250c9c277a2c7682f4))

### Continuous Integration

- Fix angular commit msg pattern [skip ci]
  ([`dc1d080`](https://github.com/dan1hc/ft3/commit/dc1d080bc42487ebcd8348754e27eb7a1f809604))


## v0.1.10 (2024-10-27)

### Performance Improvements

- Cache type check functions for big speedup
  ([`78c6b9c`](https://github.com/dan1hc/ft3/commit/78c6b9c1cde8ae6b6613076b03b34e0f49e87d11))


## v0.1.9 (2024-10-27)

### Bug Fixes

- Minimalize response objs and allow _id fields through
  ([`8b71b61`](https://github.com/dan1hc/ft3/commit/8b71b615767b99600e6a51da2ea5c7911b603206))


## v0.1.8 (2024-10-26)

### Bug Fixes

- Allow for more robust logging of parse errors in api
  ([`7a296e4`](https://github.com/dan1hc/ft3/commit/7a296e45408f69b917aaeabd165af0409ca094e2))


## v0.1.7 (2024-10-26)

### Bug Fixes

- Better api logging and error handling
  ([`ef6b5b0`](https://github.com/dan1hc/ft3/commit/ef6b5b097012c1de09bf47836203eeef33c761d7))


## v0.1.6 (2024-10-25)

### Bug Fixes

- Traceback formatting and path param parsing
  ([`afbbb59`](https://github.com/dan1hc/ft3/commit/afbbb592bbfbdf9ae6e66afd7ea25a2de46777b1))


## v0.1.5 (2024-10-25)

### Bug Fixes

- Pluralizations aws key redaction api log exc ([#29](https://github.com/dan1hc/ft3/pull/29),
  [`22c78c9`](https://github.com/dan1hc/ft3/commit/22c78c9400b588ebcb5aeb50aab66283d0a6cf36))

* fix: pluralizations aws key redaction api log exc

* docs: __v0.1.5-rc.1__ [skip ci]

* fix: serialize json api resp with default str

* docs: __v0.1.5-rc.2__ [skip ci]

* fix: need to serialize resp with default for content len

* docs: __v0.1.5-rc.3__ [skip ci]

* fix: protection for custom query param passing

* docs: __v0.1.5-rc.4__ [skip ci]

---------

Co-authored-by: github-actions <action@github.com>

### Documentation

- Update readme and trigger ci
  ([`76918f8`](https://github.com/dan1hc/ft3/commit/76918f84d5e595955afcca7574286c3dfd43d5f9))


## v0.1.4 (2024-10-22)

### Bug Fixes

- Only allow endpoint hierarchy expansion if field is named same
  ([#27](https://github.com/dan1hc/ft3/pull/27),
  [`34b685a`](https://github.com/dan1hc/ft3/commit/34b685a2e73012b84b560576ba6afd7ffea24357))

* fix: only allow endpoint hierarchy expansion if field is named same

* docs: __v0.1.4-rc.1__ [skip ci]

* fix: allow headers on POST

* docs: __v0.1.4-rc.2__ [skip ci]

* fix: __ior__ and update typing for objs

* docs: __v0.1.4-rc.3__ [skip ci]

---------

Co-authored-by: github-actions <action@github.com>

### Continuous Integration

- Workaround sem release pr no trigger issue
  ([`9b6b82a`](https://github.com/dan1hc/ft3/commit/9b6b82aad9aa9e1132e6c78f75c30d8b83e1cae6))


## v0.1.3 (2024-10-22)

### Bug Fixes

- Openapi headers and string types also py in md docs ([#25](https://github.com/dan1hc/ft3/pull/25),
  [`87fcf5c`](https://github.com/dan1hc/ft3/commit/87fcf5c47925cccbe6fe4b5aa1e65b1224006c57))

* fix: openapi headers and string types also py in md docs

* docs: __v0.1.3-rc.1__ [skip ci]

---------

Co-authored-by: github-actions <action@github.com>

- Syntax fix to trigger ci
  ([`84158f8`](https://github.com/dan1hc/ft3/commit/84158f81a3eb53742fe4f49322ef7a45543fd78e))


## v0.1.2 (2024-10-21)

### Bug Fixes

- Allow for custom response headers ([#23](https://github.com/dan1hc/ft3/pull/23),
  [`df84bb5`](https://github.com/dan1hc/ft3/commit/df84bb511edb60a69d4a2f876cf3983a2c04e2a7))

* fix: allow for custom response headers

* style: escape template resp header asterisk

* docs: __v0.1.2-rc.1__ [skip ci]

---------

Co-authored-by: github-actions <action@github.com>


## v0.1.1 (2024-10-20)

### Bug Fixes

- __multiple_fixes__ ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

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

Co-authored-by: github-actions <action@github.com>

### Testing

- Simple case to expand coverage for security schemes ([#22](https://github.com/dan1hc/ft3/pull/22),
  [`fd93e27`](https://github.com/dan1hc/ft3/commit/fd93e27cb74e061fe8448757e4da44798df34e42))

* test: simple case to expand coverage for security schemes

* feat: fix oas rendering with optional type on schema


## v0.1.0 (2024-09-18)

### Build System

- **deps**: Update pre-commit requirement from ==3.7.* to >=3.7,<3.9
  ([#10](https://github.com/dan1hc/ft3/pull/10),
  [`f3e9fd1`](https://github.com/dan1hc/ft3/commit/f3e9fd1e52c6d5b54b6614914d9d733308fd71e8))

Updates the requirements on [pre-commit](https://github.com/pre-commit/pre-commit) to permit the
  latest version. - [Release notes](https://github.com/pre-commit/pre-commit/releases) -
  [Changelog](https://github.com/pre-commit/pre-commit/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/pre-commit/pre-commit/compare/v3.7.0...v3.8.0)

--- updated-dependencies: - dependency-name: pre-commit dependency-type: direct:production ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Update sphinx requirement from ==7.* to >=7,<9
  ([#9](https://github.com/dan1hc/ft3/pull/9),
  [`7b3ccce`](https://github.com/dan1hc/ft3/commit/7b3ccce705a7fef8a73ddf0b61972defc65b3c1c))

Updates the requirements on [sphinx](https://github.com/sphinx-doc/sphinx) to permit the latest
  version. - [Release notes](https://github.com/sphinx-doc/sphinx/releases) -
  [Changelog](https://github.com/sphinx-doc/sphinx/blob/master/CHANGES.rst) -
  [Commits](https://github.com/sphinx-doc/sphinx/compare/v7.0.0rc1...v8.0.0)

--- updated-dependencies: - dependency-name: sphinx dependency-type: direct:production ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

### Documentation

- __get_funding__
  ([`e39c69a`](https://github.com/dan1hc/ft3/commit/e39c69ad32b1462fb322a0b8b9d6028c30e58e78))

### Features

- Progress toward full OAS integration ([#14](https://github.com/dan1hc/ft3/pull/14),
  [`a36847e`](https://github.com/dan1hc/ft3/commit/a36847e01c6116e25cfc916e19ae8c83d23947c5))

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

Co-authored-by: github-actions <action@github.com>

### Testing

- Re-test readme
  ([`3fa848f`](https://github.com/dan1hc/ft3/commit/3fa848f14d972a227a5b3cf34115728f198f779f))


## v0.0.1 (2024-07-28)

### Build System

- Dunder init
  ([`6ce6400`](https://github.com/dan1hc/ft3/commit/6ce6400aa6abbaa51865524108f3ecee65218c7c))

### Documentation

- __v0.0.1__
  ([`b1eeb3e`](https://github.com/dan1hc/ft3/commit/b1eeb3e7ac12eab17e5281673a6aee283ff9fc1e))
