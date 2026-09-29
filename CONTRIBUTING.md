Contributing
============

ft3 is built for agents as its only users, and its contributors are
expected to be agents too. Read [AGENTS.md](AGENTS.md) first: it is the
rulebook the code enforces. [V2.md](V2.md) is the plan of record.

Read our [Code of Conduct](https://github.com/dan1hc/ft3/blob/main/CODE_OF_CONDUCT.md).

Development install
-------------------

```bash
pip install -e ".[develop]"
pre-commit install -f
```

Verify loop
-----------

Every commit must pass all of these; the pre-commit hooks run them, and
CI runs them again on Python 3.11 through 3.14 on Linux, macOS, and
Windows.

```bash
ruff format . && ruff check .
python -m mypy
pytest                    # 100% coverage is required
ft3 check ft3.template    # the bundled reference package must stay valid
```

Rules that are not obvious from the code:

* Every behavior ft3 guarantees to downstream packages is pinned in
  `src/tests/contracts/`. Changing a pin is a coordinated release, not a
  refactor: update `V2.md` and the downstream checklist in the same change.
* Every Python block in `README.md` is executed by the test suite. Keep
  examples runnable and self-contained.
* Nothing may run at import time that scales with the size of an API.
  OpenAPI generation is a build step (`ft3 openapi`).
* Zero dependency. Stdlib only.
* Production consumers must never break: wire-visible changes ship behind
  `FT3_LEGACY_WIRE` / `ft3.configure(legacy_wire=...)`.

Commit messages
---------------

One line, angular style, validated by the commit-msg hook and by CI:

```
<type>(<scope>)?: <subject>
```

`type` is one of `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`,
`refactor`, `revert`, `style`, `test`. `feat!:` or `fix!:` marks a
breaking change. `fix` and `perf` release a patch, `feat` a minor, `!` a
major; releases are cut by semantic-release from `main`, and pull requests
publish `rc` prereleases. Trailer lines are not accepted by the validator.
