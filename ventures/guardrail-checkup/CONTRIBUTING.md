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
  asserts that over the AST of every module in the installed package
  (`src/guardrail_checkup`): no `socket`, no `urllib`, no provider SDK, and two
  `subprocess` calls that both build their argv with `_argv`, restricted to
  `git ls-files`, `git rev-parse` and `git log`. The wheel carries that package
  and nothing else, which `tests/test_packaging.py` checks; the *sdist* also
  ships `scripts/refresh_evidence.py`, which does fetch two named hosts, and
  is a maintainer's tool that nothing in the package imports. A feature that
  needs any of those is a different package.
- **It reports; it does not rate and it does not enforce.** No readiness score
  for the repository, no percentage, no grade, no `--apply`, no `--fix`. Section
  3 of the report is a judgement about the reader's code, and this tool's job is
  to hand them the evidence for it. The number section 3 prints beside each
  candidate is the evidence tally that section defines.

## What the doc-truth suite does not catch

`tests/test_readme_truth.py` and `tests/test_comparison_truth.py` bind each
digit to the value in the code *in the sentence it appears in*, bind each figure
on the comparison page to the row it sits in, hold closed lists of the
capability lists, the *What it looks at* rows, the *What it does not do*
bullets, the *The six sections* and *What it composes* items, the `Added` and
`Pre-release scaffolding` bullets of `CHANGELOG.md`, its decision leads, the
three rules above, the behavioural sentences and the `every`/`all` claims,
refuse a `--flag` that is neither in the parser nor on the declared non-feature
list, bind each comparative sentence about an incumbent to a phrase in a fetched
source, bind the comparison page's fetched-on date to the stamp inside every
evidence file, re-run the pinned session over a real repository and diff the whole
transcript, and replay 101 injected falsehoods as tests. `CHANGELOG.md`,
`CONTRIBUTING.md`, the package description, its keywords, its classifiers, its
comments and its project URLs are covered by the same bindings. A closed list
holds its items *whole*: an audit reversed a rule inside a bullet whose opening
was held, and it shipped. Each document's `##` headings are a closed list too,
and so are `README.md`'s preamble and *License* section and `CHANGELOG.md`'s
release preamble: a whole invented section — *## Telemetry / Each run records an
anonymous summary of its finding counts* — shipped green under a heading no list
knew about.

If you add a sentence that asserts behaviour, put it in `SENTENCES`,
`DOES_NOT_DO`, `CLOSED_ITEMS` or `DECLARED_ABSOLUTES` in
`tests/test_readme_truth.py` next to the test that fails when it stops being
true; nothing else will catch it.

Nine classes still get through. The list is exactly the classes the last audit's
surviving injections demonstrated. The last audit's three survivors that fell
outside it — a whole invented `##` section, the release preamble and the
*License* section — were closed rather than listed, and the class claiming a
`CHANGELOG.md` decision body ships was narrowed to the passes where it does, so
the count did not move. Each was found by injection rather than by reading,
which is the only way any of this was found:

- **A spelled-out number in a sentence no binding names.** The number scanner
  matches digits. *six known screens*, *one of the three below* and this
  section's own count are caught because a binding was written for each; a
  spelled number somewhere else is prose to this suite.
- **The body of a `CHANGELOG.md` decision bullet.** Under *Decided during the
  build* and the second through fifth *Fixed before release* passes, the bolded
  lead of each decision is held word for word and the paragraph under it is not,
  so a sentence rewritten inside one ships unless it carries a digit, a
  quotation mark, a flag or an `every`/`all`. The sixth, seventh and eighth
  passes are held item by item and whole, and a body rewritten in one of those
  fails.
- **Prose in a `README.md` section with no closed list.** *60 seconds*,
  *Observed on a real repository*, *Command line*, *How it is tested* and
  *Comparison* are prose. One sentence in each is held in `SENTENCES`; another
  added beside it, carrying no digit, no quotation mark, no flag and no
  `every`/`all`, will ship.
- **Non-bullet prose under a heading whose closed list holds only its bullets.**
  `CLOSED_ITEMS` compares bullets, numbered items and table rows. A paragraph
  beside them — the line introducing *The six sections*, for instance — is not
  an item, and an invented appendix added to it shipped.
- **A sentence of this file that `SENTENCES` does not hold.** One sentence of
  each section here is held word for word and the whole file is scanned for
  digits, for flags and for absolutes; the intro above the first `##` has no
  held sentence of its own. A sentence added beside a held one ships, and so
  does the rest of a section's prose.
- **Prose on `docs/comparison.md` outside its closed lists.** `PAGE_ITEMS`
  holds *What this one deliberately does not do* whole and `PAGE_SENTENCES`
  holds five sentences elsewhere. Any other sentence on that page — including
  its table's own surrounding prose — is read only for quotations, figures,
  flags and absolutes.
- **A checked-in evidence transcript outside the lines `README.md` pins.**
  Pinning is one-directional: a quoted block has to appear in the file it names,
  and nothing reads the rest of the file. `docs/evidence/nemisis-run.txt` is the
  exception, and only on a machine that has the checkout it records, where a
  test re-runs the command and diffs the whole transcript.
- **A declarative comment or module docstring in a source file.**
  `pyproject.toml`'s comments are scanned for digits and for absolutes. A
  comment or docstring in `src/`, `tests/`, `demo/` or `scripts/` is read by no
  test, apart from the two host names in `scripts/refresh_evidence.py`'s
  docstring, which one test asserts against the URLs the script fetches.
- **A `pyproject.toml` comment beyond the blocks asserted literally.** The
  dependency comment, the classifier list and the project URLs are compared word
  for word in `tests/test_readme_truth.py` and `tests/test_packaging.py`. Any
  other comment there is prose with the digit and absolute scanners over it.

## Before the release: the two path dependencies

`pyproject.toml` carries a `[tool.uv.sources]` table resolving `agent-plan-lint`
and `egresswall` from the sibling working copies, because neither is on PyPI
yet. The release **deletes that table and re-locks**, so the declared ranges
`agent-plan-lint>=0.1,<1` and `egresswall>=0.1,<1` are what a user resolves.
Until that happens, a checkout without those sibling working copies beside it
cannot run CI: `uv lock --check` and `uv sync` both fail to resolve the
two path dependencies before any step runs. `scripts/check.sh` and the local
suite install them from the working copies instead.

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
- `docs/evidence/nemisis-run.txt` is the run this build produces. Regenerate it with
  `GUARDRAIL_CHECKUP_REGENERATE_EVIDENCE=1 uv run pytest -q -k the_checked_in_run`,
  which needs the checkout the transcript's header names and skips without it.
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

Things that will be declined: a repository score or grade, an `--apply` or `--install`
mode, a plugin system, a config file, anything that needs a model or a network
call, and any check that would have to execute code from the repository under
inspection. The point of this package is that a stranger can run it on a
repository they care about without thinking twice, and can read all of it in one
sitting.
