# Contributing

Thanks for looking. This package is small on purpose: two runtime dependencies,
both siblings, one scan, one report, and no way for it to change the repository
it reads.

## Before you open a PR

1. `./scripts/check.sh` must pass. It runs the checks CI runs before it installs
   the built wheel, and `tests/test_packaging.py` asserts the two lists are
   equal — add a step to CI and this script has to grow it too.
2. New behaviour needs a test. New README claims need a test in
   `tests/test_readme_truth.py`: the README is executed or pinned, not trusted.
3. No new runtime dependencies. Development dependencies live in
   `[dependency-groups] dev`.
4. Quoting a source in `README.md` or `docs/comparison.md` means adding it to
   `scripts/refresh_evidence.py` and re-running it, so the quotation is checked
   against a copy of the source under `docs/evidence/`.
5. Regenerate the demo if you changed anything the report prints:
   `PATH="$PWD/.venv/bin:$PATH" ./demo/demo.sh /tmp/keep > demo/OUTPUT.txt 2>&1 &&
   cp /tmp/keep/OUTPUT.md demo/OUTPUT.md`. CI diffs both.

## The three rules this package will not bend

- **It never writes into the repository it reads.** `--out` and `--emit-dir` are
  refused if either resolves inside `PATH`. Anything that would need to write
  there is out of scope.
- **It contacts no network and calls no model.** `tests/test_readonly.py`
  asserts that over the AST of every shipped module: no `socket`, no `urllib`,
  no provider SDK, and one `subprocess.run` restricted to `git ls-files`,
  `git rev-parse` and `git log`. A feature that needs any of those is a
  different package.
- **It reports; it does not score and it does not enforce.** No percentage, no
  grade, no `--apply`, no `--fix`. Section 3 of the report is a judgement about
  the reader's code, and this tool's job is to hand them the evidence for it.

## What the doc-truth suite cannot see

`tests/test_readme_truth.py` and `tests/test_comparison_truth.py` are a
whitelist over numbers, number-words, quotations, install routes, `--flag`
names, the category nouns, and a named list of absolute claims. A *new* prose
claim that carries no digit, no quotation mark, no flag and no listed phrase is
not covered by any of them — an invented capability written as a plain sentence
will ship. If you add a sentence that asserts behaviour, add it to the claims
list with the test that fails when it stops being true; nothing else will catch
it.

## Before the release: the two path dependencies

`pyproject.toml` carries a `[tool.uv.sources]` table resolving `agent-plan-lint`
and `egresswall` from the sibling working copies, because neither is on PyPI
yet. The release **deletes that table and re-locks**, so the declared ranges
`agent-plan-lint>=0.1,<1` and `egresswall>=0.1,<1` are what a user resolves.
Until that happens, CI's wheel-install step cannot resolve the two dependencies
from the registry; `scripts/check.sh` and the local suite install them from the
working copies instead.

## Checking another Python version

`.python-version` pins 3.11, and `uv run` re-resolves the interpreter from it:
`uv sync --python 3.13` followed by a bare `uv run pytest` can rebuild the
environment on 3.11, with both commands exiting 0. Pass `--python` to **every**
`uv run`, and assert the interpreter before trusting the result:

```
uv run --python 3.13 python -c 'import sys; print(sys.version)'
uv run --python 3.13 pytest -q
```

## Release checklist

- `./scripts/check.sh` passes on 3.11, 3.12 and 3.13.
- `python3 scripts/refresh_evidence.py` exits 0 (no cited source has moved).
- `[tool.uv.sources]` is deleted, `uv lock` re-run, and both dependencies
  resolve from PyPI.
- Every URL in `[project.urls]` returns 200, and the version being released is
  not already on PyPI. The distribution name, the console script and `NAME` must
  agree — the tests enforce that, but the registry check is the one CI cannot
  do.

## AI assistance

This package was written with AI assistance. If any part of your PR was too, say
so in the PR description: state what the tool produced and what you verified
yourself. PRs that do not disclose it will be closed.

## Scope

Things that will be declined: a score or a grade, an `--apply` or `--install`
mode, a plugin system, a config file, anything that needs a model or a network
call, and any check that would have to execute code from the repository under
inspection. The point of this package is that a stranger can run it on a
repository they care about without thinking twice, and can read all of it in one
sitting.
