# Contributing

Thanks for looking. This package is small on purpose: zero runtime
dependencies, one screening core, three integration surfaces.

## Before you open a PR

1. `./scripts/check.sh` must pass. It runs the checks CI runs before it
   installs the built wheel, and a doc-truth test asserts the two lists are
   equal -- add a step to CI and this script has to grow it too.
2. New behaviour needs a test. New README claims need a test in
   `tests/test_readme_truth.py` -- the README is executed, not trusted.
3. No new runtime dependencies. Development dependencies live in
   `[dependency-groups] dev`.
4. Quoting a source in `README.md` or `docs/comparison.md` means adding it to
   `scripts/refresh_evidence.py` and re-running it, so the quotation is checked
   against a copy of the source under `docs/evidence/`.

## Debugging a failure

Every CLI failure is one line on stderr and exit 2: a traceback would carry the
payload's own field names into a log this package exists to keep values out of.
`egresswall --traceback <subcommand> ...` -- before the subcommand, and not in
`--help` -- re-raises instead, which is what a bug report should carry.

## What the doc-truth suite does not catch

`tests/test_readme_truth.py`, `tests/test_doc_numbers.py` and
`tests/test_comparison_truth.py` execute the README's command blocks and the
demo, and pin every number, every count written as a word, every quotation,
every `--flag` name, every install route, the "does not do" headings, the
"What it catches" examples, the CHANGELOG's capability bullets and the
comparison page's sections and figures. Everything below is what they still
do not see. The list is itself pinned by a test, so it cannot quietly shrink:
if you close one of these, delete the line and the pin fails until you update
it.

- A new prose sentence anywhere on a page that carries no number, no
  number-word, no quotation, no flag and no listed superlative: an invented
  capability written as a plain sentence will ship.
- The body of a "What it does not do" bullet: the bold header is pinned by set
  equality and the sentence after it is not, so a body can be inverted.
- The CHANGELOG's "Changed" and "Fixed" bullets: only the "Added" bullets'
  first sentences are pinned, so a false statement about what a past defect was
  will ship.
- The comparison page's "What X does that egresswall does not" paragraphs: the
  page says nothing under `docs/evidence/` backs them, and nothing does, so a
  false claim about a named third party's product passes.
- The list of tools the README's comparison paragraph names is not tied to the
  sections on `docs/comparison.md`, so it can name a project the page does not
  cover.
- A count in a historical sentence ("six shapes crossed the boundary") names no
  live code expression: the word is accounted for, the sentence is not.
- The timing bounds are wall clock on whatever machine runs the suite. They are
  a regression guard, not a promise about a reader's machine.
- A rule the code has and no document mentions: every test here reads a claim
  and checks it, and none of them reads the code and looks for the claim.
- `CONTRIBUTING.md` itself is outside the number, word, quotation and flag
  checks; only this section is pinned.

## Checking another Python version

`.python-version` pins 3.13, and `uv run` re-resolves the interpreter from it:
`uv sync --python 3.11` followed by a bare `uv run pytest` deletes the 3.11
environment and rebuilds it on 3.13, with both commands exiting 0. Pass
`--python` to **every** `uv run`, and assert the interpreter before trusting
the result:

```
uv run --python 3.11 python -c 'import sys; print(sys.version)'
uv run --python 3.11 pytest -q
```

## Release checklist

- The checks in `./scripts/check.sh` pass on 3.11, 3.12 and 3.13. The script
  itself uses the interpreter `.python-version` names; for the other two, run
  its commands with `--python` on every `uv sync` and `uv run`, as above.
- `python3 scripts/refresh_evidence.py` exits 0 (no cited source has moved).
- Every URL in `[project.urls]` returns 200, and the version being released is
  not already on PyPI (`curl -o /dev/null -w '%{http_code}'
  https://pypi.org/pypi/<name>/<version>/json` returns 404). The name, the
  console script and `NAME` must agree -- the tests enforce that, but the
  registry check is the one CI cannot do.

## AI assistance

If any part of your PR was prepared with AI assistance, say so in the PR
description. State what the tool produced and what you verified yourself. PRs
that do not disclose it will be closed.

## Scope

Things that will be declined: redaction or masking modes, plugin systems,
config frameworks, and detectors that need a model or a network call. The
point of this package is that it blocks a payload whole and that you can read
all of it in one sitting.
