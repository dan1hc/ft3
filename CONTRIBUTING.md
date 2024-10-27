Contributing
============

Read our [Code of Conduct](https://github.com/dan1hc/ft3/blob/main/CODE_OF_CONDUCT.md).

* Step 1 - [Create New Issue](https://github.com/dan1hc/ft3/issues/new)
* Step 2 - Create New Branch (Corresponding to New Issue)
* Step 3 - Clone Branch & [Development Install](#development-install)
* Step 4 - Make Changes
* Step 5 - Push & [Create New PR](https://github.com/dan1hc/ft3/pulls)
* Step 6 - Wait for Review / Approval

Development Install
-------------------

```bash
pip install -e ".[develop]"
pre-commit install -f
```

Styling, Testing, and Typing
----------------------------

Assuming you installed pre-commit hooks, the below will happen when you make a commit.

*It will certainly happen on a CI runner when you push your commit.*

```bash
ruff check
python -m mypy
pytest
```

Coverage requirements: `100%`

Commit Messages
---------------

Additionally, commit messages must adhere to [angular commit guidelines](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits) (templates below).

#### _multi-line_

---

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

#### _single-line_

---

```
<type>(<scope>): <subject>
```

#### Special Rules

* `<subject>` as a pythonic `__dunder__` can be cool.
* `<subject>` must be appropriately descriptive of the change.
* If the multi-line template is used, at least one issue ref must be correctly [keyworded](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/using-keywords-in-issues-and-pull-requests) in the footer.


#### _regex_

---

```python
import re

pattern = re.compile(
    r'((^[mM]erge .*$)|(^((build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\(.+\))?!?: .+)((\n\n(.+)\n\n)((BREAKING CHANGE|DEPRECATED)(: )(.+)\n\n(.+))?(\n\n\nresolve[ds]? \#[A-Z0-9\-]+|fix(ed|es)? \#[A-Z0-9\-]+|close[ds]? \#[A-Z0-9\-]+)((, )(resolve[ds]? \#[A-Z0-9\-]+|fix(ed|es)? \#[A-Z0-9\-]+|close[ds]? \#[A-Z0-9\-]+))?)?)?$)|(^revert: ((build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\(.+\))?!?: .+)(\n\n(This reverts commit [a-z0-9]{40}\..*))(\n\n(fix(ed|es)? \#[A-Z0-9\-]+)((, )(fix(ed|es)? \#[A-Z0-9\-]+))?)?$)'
    )

assert bool(pattern.match('feat: __valid_example__\n\noptional body text\n\ncloses #1, resolve #2')) is True
assert bool(pattern.match('feat!: __new_stuff__\n\nbody text.\n\nBREAKING CHANGE: Breaks stuff.\n\nDetails on how stuff breaks and what to do.\n\n\nresolves #1')) is True
assert bool(pattern.match('revert: feat! __new_stuff__\n\nThis reverts commit 2c4ed28b069267f39974b5da50795c5210040e33. Because reasons.\n\nfixes #TKT-123')) is True
assert bool(pattern.match('test: __short_valid_example__')) is True

```
