# CHANGELOG


## v2.0.0 (2026-10-05)

### Bug Fixes

- Accept read_only fields on input under FT3_LEGACY_WIRE as 1.x did
  ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- Parse --port argument as int ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- Parse --port argument as int
  ([`af81115`](https://github.com/dan1hc/ft3/commit/af81115eaa2d7bc87738a802baf5bf565874decd))

### Continuous Integration

- Modernize actions, enforce ruff lint and format, and parse squash commits so main releases 2.0.0
  ([`5f20991`](https://github.com/dan1hc/ft3/commit/5f20991aebb3c44173da77ee78fbecabd86029d6))

- Pin @actions/core and @actions/github to their CommonJS majors
  ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

### Documentation

- Agent rulebook, llms.txt, and an executable README for 2.0
  ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- Package docstrings, contributing guide, metadata, and release plan for agents
  ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- Refresh stale python and version badges and pin the python badge to the classifiers
  ([`e6c2578`](https://github.com/dan1hc/ft3/commit/e6c2578bbf9b8bf59ba014403c6fe0618e680de2))

- Rewrite docstrings, contributing guide, and metadata for agents as the only users
  ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- V2 plan of record and compatibility design ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

### Features

- Drop unknown keys everywhere with a warning and require fields in strict mode
  ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- Enforce declared field constraints and lossless coercion in strict mode
  ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- Exact route matching, api-path routing, handler-returned responses, and unregistered-handler
  warning ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- Ft3 check and ft3 openapi commands, in-process Client, keyword CLI dispatch, redaction allowlist
  ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- Ft3 exceptions subclass Exception and carry stable codes
  ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- Ft3.configure sets legacy wire, redaction allowlist, and log settings from code
  ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- Remove frame inspection from item access, per-Api route cache, correct type-check cache keys
  ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- Safe truthiness, isolated deepcopy, and per-field wire options behind FT3_LEGACY_WIRE
  ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- Strict request parsing with input policy, MRO error mapping, and FT3_LEGACY_WIRE
  ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- Support Python 3.11 through 3.14 and drop 3.10 with its last dependency
  ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- V2 ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))

- Valid JSON log records, full tracebacks, print routing, and redaction gaps
  ([#59](https://github.com/dan1hc/ft3/pull/59),
  [`d8b6fc1`](https://github.com/dan1hc/ft3/commit/d8b6fc1ed43c4e7d8fc3949663185916bb3d2f84))


## v1.1.3 (2026-05-19)

### Bug Fixes

- Lazy_docs should be true by default
  ([`c5966fe`](https://github.com/dan1hc/ft3/commit/c5966fe97615e302f4226f7e11f03d2ecee75d39))


## v1.1.2 (2026-05-19)

### Performance Improvements

- Lazy doc gen by default
  ([`dff4c8f`](https://github.com/dan1hc/ft3/commit/dff4c8fa4ef037a0cfa6a18739a4540a9ec885ab))


## v1.1.1 (2026-04-29)

### Performance Improvements

- Massive speedup for large apis
  ([`4ab5698`](https://github.com/dan1hc/ft3/commit/4ab5698bd23896eed424b13ccad51b561d95552d))


## v1.1.0 (2025-12-27)

### Features

- Serve at swagger path
  ([`f67c006`](https://github.com/dan1hc/ft3/commit/f67c0065f93a1438b07c9d0ca71fdc45504953a8))


## v1.0.2 (2025-10-13)

### Bug Fixes

- __standardizations_and_fixes__ ([#43](https://github.com/dan1hc/ft3/pull/43),
  [`f7d041d`](https://github.com/dan1hc/ft3/commit/f7d041d8497eafe0f722946e11fa7fc9f203cfa3))

- Corrected spelling of 'PACAKGE' to 'PACKAGE'. ([#43](https://github.com/dan1hc/ft3/pull/43),
  [`f7d041d`](https://github.com/dan1hc/ft3/commit/f7d041d8497eafe0f722946e11fa7fc9f203cfa3))

- Minor styling fix to trigger CI.
  ([`2c8f889`](https://github.com/dan1hc/ft3/commit/2c8f889a8c0db09bc49ad98a8c8962c81fceea5c))

- PACKAGE spelling mistake. ([#43](https://github.com/dan1hc/ft3/pull/43),
  [`f7d041d`](https://github.com/dan1hc/ft3/commit/f7d041d8497eafe0f722946e11fa7fc9f203cfa3))

- Testing for 3.13 II. ([#43](https://github.com/dan1hc/ft3/pull/43),
  [`f7d041d`](https://github.com/dan1hc/ft3/commit/f7d041d8497eafe0f722946e11fa7fc9f203cfa3))

- Testing for 3.13 III. ([#43](https://github.com/dan1hc/ft3/pull/43),
  [`f7d041d`](https://github.com/dan1hc/ft3/commit/f7d041d8497eafe0f722946e11fa7fc9f203cfa3))

- Testing for 3.13 IV. ([#43](https://github.com/dan1hc/ft3/pull/43),
  [`f7d041d`](https://github.com/dan1hc/ft3/commit/f7d041d8497eafe0f722946e11fa7fc9f203cfa3))

- Testing for 3.13. ([#43](https://github.com/dan1hc/ft3/pull/43),
  [`f7d041d`](https://github.com/dan1hc/ft3/commit/f7d041d8497eafe0f722946e11fa7fc9f203cfa3))

### Continuous Integration

- Fix ruff format. ([#43](https://github.com/dan1hc/ft3/pull/43),
  [`f7d041d`](https://github.com/dan1hc/ft3/commit/f7d041d8497eafe0f722946e11fa7fc9f203cfa3))


## v1.0.1 (2025-06-30)

### Bug Fixes

- __to_dict_array_serialization__
  ([`b2c59a4`](https://github.com/dan1hc/ft3/commit/b2c59a487cc26643ee6d3a6d9aec737bcdc66a36))


## v1.0.0 (2025-06-11)

### Bug Fixes

- Correctly check array types are not Objects.
  ([`ed8c6f1`](https://github.com/dan1hc/ft3/commit/ed8c6f1363791034b04f83c38e53cd39a7a5b88c))


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

- Cache fixes, enum parse from literals, perf boost ([#31](https://github.com/dan1hc/ft3/pull/31),
  [`6258037`](https://github.com/dan1hc/ft3/commit/62580377c5005e7d8743f63cbbac839acdc00851))

- Cache improvements ([#31](https://github.com/dan1hc/ft3/pull/31),
  [`6258037`](https://github.com/dan1hc/ft3/commit/62580377c5005e7d8743f63cbbac839acdc00851))

- More caching improvements ([#31](https://github.com/dan1hc/ft3/pull/31),
  [`6258037`](https://github.com/dan1hc/ft3/commit/62580377c5005e7d8743f63cbbac839acdc00851))


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

- Need to serialize resp with default for content len ([#29](https://github.com/dan1hc/ft3/pull/29),
  [`22c78c9`](https://github.com/dan1hc/ft3/commit/22c78c9400b588ebcb5aeb50aab66283d0a6cf36))

- Pluralizations aws key redaction api log exc ([#29](https://github.com/dan1hc/ft3/pull/29),
  [`22c78c9`](https://github.com/dan1hc/ft3/commit/22c78c9400b588ebcb5aeb50aab66283d0a6cf36))

- Protection for custom query param passing ([#29](https://github.com/dan1hc/ft3/pull/29),
  [`22c78c9`](https://github.com/dan1hc/ft3/commit/22c78c9400b588ebcb5aeb50aab66283d0a6cf36))

- Serialize json api resp with default str ([#29](https://github.com/dan1hc/ft3/pull/29),
  [`22c78c9`](https://github.com/dan1hc/ft3/commit/22c78c9400b588ebcb5aeb50aab66283d0a6cf36))

### Documentation

- Update readme and trigger ci
  ([`76918f8`](https://github.com/dan1hc/ft3/commit/76918f84d5e595955afcca7574286c3dfd43d5f9))


## v0.1.4 (2024-10-22)

### Bug Fixes

- __ior__ and update typing for objs ([#27](https://github.com/dan1hc/ft3/pull/27),
  [`34b685a`](https://github.com/dan1hc/ft3/commit/34b685a2e73012b84b560576ba6afd7ffea24357))

- Allow headers on POST ([#27](https://github.com/dan1hc/ft3/pull/27),
  [`34b685a`](https://github.com/dan1hc/ft3/commit/34b685a2e73012b84b560576ba6afd7ffea24357))

- Only allow endpoint hierarchy expansion if field is named same
  ([#27](https://github.com/dan1hc/ft3/pull/27),
  [`34b685a`](https://github.com/dan1hc/ft3/commit/34b685a2e73012b84b560576ba6afd7ffea24357))

### Continuous Integration

- Workaround sem release pr no trigger issue
  ([`9b6b82a`](https://github.com/dan1hc/ft3/commit/9b6b82aad9aa9e1132e6c78f75c30d8b83e1cae6))


## v0.1.3 (2024-10-22)

### Bug Fixes

- Openapi headers and string types also py in md docs ([#25](https://github.com/dan1hc/ft3/pull/25),
  [`87fcf5c`](https://github.com/dan1hc/ft3/commit/87fcf5c47925cccbe6fe4b5aa1e65b1224006c57))

- Syntax fix to trigger ci
  ([`84158f8`](https://github.com/dan1hc/ft3/commit/84158f81a3eb53742fe4f49322ef7a45543fd78e))


## v0.1.2 (2024-10-21)

### Bug Fixes

- Allow for custom response headers ([#24](https://github.com/dan1hc/ft3/pull/24),
  [`2d1b396`](https://github.com/dan1hc/ft3/commit/2d1b3968fbd398874c0c944815bfe96e6c997c66))

- Allow for custom response headers ([#23](https://github.com/dan1hc/ft3/pull/23),
  [`df84bb5`](https://github.com/dan1hc/ft3/commit/df84bb511edb60a69d4a2f876cf3983a2c04e2a7))

- Allow use of custom response headers by injecting on request object
  ([#24](https://github.com/dan1hc/ft3/pull/24),
  [`2d1b396`](https://github.com/dan1hc/ft3/commit/2d1b3968fbd398874c0c944815bfe96e6c997c66))

### Code Style

- Escape template resp header asterisk ([#24](https://github.com/dan1hc/ft3/pull/24),
  [`2d1b396`](https://github.com/dan1hc/ft3/commit/2d1b3968fbd398874c0c944815bfe96e6c997c66))

- Escape template resp header asterisk ([#23](https://github.com/dan1hc/ft3/pull/23),
  [`df84bb5`](https://github.com/dan1hc/ft3/commit/df84bb511edb60a69d4a2f876cf3983a2c04e2a7))


## v0.1.1 (2024-10-20)

### Bug Fixes

- __multiple_fixes__ ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

- Align log format with lambda and polish ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

- Allow default on field to be a Callable[[], AnyType@Field]
  ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

- Correctly type parse fn ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

- Default connection header to keep-alive ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

- Dont build tests and dont auto-include version prefix
  ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

- Favicon path ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

- Hash does not need to be reserved ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

- Install static html ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

- Log formatting fix ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

- Mypy compliance pytyped ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

- Need to pop template not del ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

- Typ ordering and comment cleanup ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

- Use default factory for openapi schema definition ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

- Version prefix for swagger ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

### Documentation

- Minor readme touchups ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

### Features

- Allow for optional inclusion of specific request headers with decorator
  ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

- Fix oas rendering with optional type on schema ([#22](https://github.com/dan1hc/ft3/pull/22),
  [`fd93e27`](https://github.com/dan1hc/ft3/commit/fd93e27cb74e061fe8448757e4da44798df34e42))

- **api**: Implement api key security scheme ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

### Performance Improvements

- Improve typing for parse ([#19](https://github.com/dan1hc/ft3/pull/19),
  [`015dd74`](https://github.com/dan1hc/ft3/commit/015dd74cbc7316eaafb0b3416421f62fdee514ba))

### Testing

- Simple case to expand coverage for security schemes ([#22](https://github.com/dan1hc/ft3/pull/22),
  [`fd93e27`](https://github.com/dan1hc/ft3/commit/fd93e27cb74e061fe8448757e4da44798df34e42))


## v0.1.0 (2024-09-18)

### Bug Fixes

- 310 support error ([#14](https://github.com/dan1hc/ft3/pull/14),
  [`a36847e`](https://github.com/dan1hc/ft3/commit/a36847e01c6116e25cfc916e19ae8c83d23947c5))

- Handle sub objs without hash fields and sub obj precedence
  ([#14](https://github.com/dan1hc/ft3/pull/14),
  [`a36847e`](https://github.com/dan1hc/ft3/commit/a36847e01c6116e25cfc916e19ae8c83d23947c5))

- Self import for 310 ([#14](https://github.com/dan1hc/ft3/pull/14),
  [`a36847e`](https://github.com/dan1hc/ft3/commit/a36847e01c6116e25cfc916e19ae8c83d23947c5))

- Template api str locations ([#14](https://github.com/dan1hc/ft3/pull/14),
  [`a36847e`](https://github.com/dan1hc/ft3/commit/a36847e01c6116e25cfc916e19ae8c83d23947c5))

- Template polished ([#14](https://github.com/dan1hc/ft3/pull/14),
  [`a36847e`](https://github.com/dan1hc/ft3/commit/a36847e01c6116e25cfc916e19ae8c83d23947c5))

### Build System

- **deps**: Update pre-commit requirement from ==3.7.* to >=3.7,<3.9
  ([#10](https://github.com/dan1hc/ft3/pull/10),
  [`f3e9fd1`](https://github.com/dan1hc/ft3/commit/f3e9fd1e52c6d5b54b6614914d9d733308fd71e8))

- **deps**: Update sphinx requirement from ==7.* to >=7,<9
  ([#9](https://github.com/dan1hc/ft3/pull/9),
  [`7b3ccce`](https://github.com/dan1hc/ft3/commit/7b3ccce705a7fef8a73ddf0b61972defc65b3c1c))

### Documentation

- __get_funding__
  ([`e39c69a`](https://github.com/dan1hc/ft3/commit/e39c69ad32b1462fb322a0b8b9d6028c30e58e78))

### Features

- Now the rest but skipped the tests ([#14](https://github.com/dan1hc/ft3/pull/14),
  [`a36847e`](https://github.com/dan1hc/ft3/commit/a36847e01c6116e25cfc916e19ae8c83d23947c5))

- Progress toward full OAS integration ([#14](https://github.com/dan1hc/ft3/pull/14),
  [`a36847e`](https://github.com/dan1hc/ft3/commit/a36847e01c6116e25cfc916e19ae8c83d23947c5))

### Testing

- Re-test readme
  ([`3fa848f`](https://github.com/dan1hc/ft3/commit/3fa848f14d972a227a5b3cf34115728f198f779f))


## v0.0.1 (2024-07-28)

- Initial Release
