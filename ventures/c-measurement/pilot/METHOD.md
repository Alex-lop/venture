# Base-snapshot buildability pilot — method

**What this measures.** For each repo in the Track M corpus, take the *base* commit of its
first qualifying agent PR and ask three questions, in order:

1. **install_ok** — does the dependency set install *from the lockfile alone*?
2. **collect_ok** — does `pytest --collect-only` succeed, with the network off?
3. **run_ok** — does `pytest` reach a verdict (a summary line with counts), network off?

This is the study's falsifier. A differential verifier needs the base commit to build and
its tests to run; if most bases do not build hermetically, per-PR results are unavailable
for the majority of the corpus and the surviving minority is exactly the well-maintained
subset — the population least likely to ship non-discriminating tests. `CLAUDE.md` §9:
**if fewer than 30% build, the study shrinks to the buildable set and the buildability
finding itself is published.**

## Inputs

`../corpus/candidates-pilot-100.csv` — the fixed 100-repo pilot manifest selected from the
110 qualifying rows in `candidates-v2.csv` (`corpus/README.md` documents the funnel). Three
columns drive the pilot: `base_sha_of_first_sample_pr` (the commit checked out),
`python_requires`, and `lock_kind` (`uv.lock` 85, `pinned-requirements` 9, `poetry.lock` 5,
`Pipfile.lock` 1).
No repo needed a `gh api .../pulls/N --jq .base.sha` lookup: every row already carried a
base SHA.

## Isolation

Candidate code is untrusted and never runs on the host.

- Every phase is a `docker run --rm`. **No host path is ever bind-mounted.** The work tree
  lives in a per-repo docker volume (`pilot-<owner>__<repo>`) mounted at `/w`, destroyed in
  a `finally:` block once the repo's row is written, so disk stays bounded.
- Two shared cache volumes: `pilot-uvcache` → `/uvcache` (`UV_CACHE_DIR`) and
  `pilot-pipcache` → `/pipcache`. They make the warm-cache install realistic and cheap.
- Per container: `--memory 2500m --cpus 2 --pids-limit 2048`.
- The clone and install phases have network. **The collect and run phases are
  `--network none`** — that is what makes a test-time network dependency visible instead of
  silently satisfied.
- Logs are the container's stdout+stderr, captured by the host process; the repo's files
  never touch the host filesystem.

## Images

One image per Python minor version, `pilot-py:3.9` … `pilot-py:3.14` (see `Dockerfile`):
`python:<X.Y>-slim`, plus `git` and `ca-certificates` from apt, plus `uv` copied from
`ghcr.io/astral-sh/uv:0.11.29`. Nothing else — a missing compiler or system library is a
finding (`native-deps`), not something to paper over.

**Interpreter choice** (`pick_python`): the repo's `.python-version` at the base commit
wins when we have an image for it; otherwise the first version admitted by
`requires-python` in preference order `3.12, 3.13, 3.11, 3.10, 3.14, 3.9` — newest is not
safest, since third-party wheels lag the newest release. Default `3.12` when neither is
declared. `UV_PYTHON_DOWNLOADS=never` inside the container, so uv cannot quietly fetch a
different interpreter and defeat the choice; a genuine mismatch surfaces as a
`python-version` failure instead.

## Phases and caps

| phase | network | cap | command |
|---|---|---|---|
| clone | on | 10 min | `git clone --filter=blob:none` then `git checkout --force <base_sha>` |
| install | on | 10 min | by `lock_kind`, below |
| collect | **none** | 5 min | `.venv/bin/python -m pytest --collect-only -q` |
| run | **none** | 15 min | `.venv/bin/python -m pytest -q -x --timeout=600 -p no:cacheprovider` |

Caps are enforced twice: `timeout -k 10 <cap>` as the container's entrypoint (exit 124) and
a host-side `subprocess` timeout at cap+120s as a backstop.

## Install — lockfile only, never a resolution

Unpinned dependency resolution is an install *failure by definition*; the pilot never
resolves its way to a green install.

- **`uv.lock`** → a ladder, widest first:
  `uv sync --frozen --all-extras --all-groups`, then `--all-groups`, then a bare
  `uv sync --frozen`; the first rung that succeeds wins and the fallbacks are recorded in
  `notes`. `--frozen` forbids re-locking: a lock that no longer matches `pyproject.toml`
  fails rather than silently updating. Extras and groups are **resolved inside `uv.lock`**,
  so syncing them is not a resolution.

  Syncing them is also not optional. Two failures during harness development forced this:
  a bare `uv sync --frozen` on `commit-check/commit-check` installed 2 packages and no
  pytest at all, and `ohdearquant/lionagi` failed collection with
  `studio extra not installed`. (Both were smoke runs predating the final run, so their
  logs are not in `logs/`; `logs/` holds only rows that are in `results.csv`.) A default sync measures whether the *runtime* dependency
  set installs; the question here is whether the *test* suite runs, and its dependencies
  live in groups and extras. The widest rung is tried first and the ladder falls back so
  that an extra that genuinely cannot install (a GPU or proprietary wheel) does not score
  the whole repo unbuildable.

  **Each rung carries its own inner timeout — 300 s, 160 s, 120 s, inside the phase's
  600 s cap.** Without them a slow widest rung on a large monorepo consumes the whole
  install cap and the fallbacks never run, turning a repo that installs fine with a default
  sync into a spurious `timeout`. That is exactly the direction of error a falsifier cannot
  afford, and it was observed on `crewAIInc/crewAI` before the inner timeouts were added.
- **`poetry.lock`** → `uv tool install poetry`, then
  `POETRY_VIRTUALENVS_IN_PROJECT=true poetry install --no-interaction --all-extras`
  (300 s), falling back to the same command without `--all-extras` (200 s). Poetry installs
  from the lock and errors if the lock is stale. Poetry itself is a *tool*, resolved at
  its latest version; that is the harness, not the repo's dependency set.
- **`Pipfile.lock`** → `uv tool install pipenv`, then `pipenv sync --dev`, falling back to
  `pipenv sync`. Both sync directly from the lock; Pipenv itself is a harness tool.
- **`pinned-requirements`** → the requirements file named in the corpus row
  (`lockfile_type: pinned:<file>`) is first checked line by line: every non-comment,
  non-flag line must carry `==` or `@`. If any line is unpinned the repo is recorded
  `install_ok=0`, `failure_class=no-lock` **without installing anything** — an unpinned
  requirements file is not a lock. If the file is absent at the base commit, same class.
  Otherwise `uv venv .venv` + `uv pip install -r <file>`, then
  `uv pip install --no-deps -e .` when the repo has a `pyproject.toml`/`setup.py`, so the
  project's own package is importable. `--no-deps` means no resolution.

**Two harness packages may be added to the venv, and both are recorded in `notes`:**
`pytest` itself when the lockfile install left it absent (the alternative is to score a
repo unbuildable for a missing harness), and `pytest-timeout`, which supplies
`--timeout=600`. If `pytest-timeout` cannot be installed the run phase drops the flag and
relies on the 15-minute wall cap. Both installs happen in the network-on install phase, so
the collect and run phases stay hermetic.

## Verdict parsing

- `collected_count` — the largest of `N tests collected` / `collected N items` in the
  collect log.
- `passed` / `failed` / `errored` — from the pytest summary line of the run log.
- **`run_ok = 1` iff pytest exited 0 or 1 *and* a summary line was parsed.** Exit 1 (tests
  failed) still counts as *built and run to a verdict* — that is the question this pilot
  asks. Those rows carry `failure_class=tests-failed-at-base`, which is informational, not
  a buildability failure; exclude it when counting build failures.
- Exit 2/3/4/5 (interrupted, internal error, usage error, no tests collected) and timeouts
  are `run_ok=0` with a real failure class.

## Failure classes

The first phase that fails decides the class. `notes` carries the matched evidence string
so every classification is auditable against the log.

| class | how it is recognised |
|---|---|
| `no-lock` | requirements file unpinned, or the declared lockfile absent at the base commit |
| `lock-unresolvable` | uv/poetry rejects the lock (stale, hash mismatch, missing distribution) |
| `build-backend` | PEP 517 backend problems: `Getting requirements to build wheel`, `BackendUnavailable`, missing `setuptools`/`hatchling`/`poetry.core`/`maturin` |
| `native-deps` | compiler or system library missing: `Python.h`, `gcc … failed`, `Failed building wheel`, Rust/CMake toolchain |
| `python-version` | interpreter incompatibility (`requires Python`, `no interpreter found`) |
| `network-at-test-time` | DNS/socket failure in the collect or run phase — with `--network none` this is the class that proves the suite is not hermetic |
| `env-var/secret required` | the suite demands an API key, token, or credential |
| `collection-error` | `--collect-only` failed, or the run phase died in collection |
| `timeout` | a phase hit its cap (exit 124) |
| `other` | failed with no known signature — the log is the record |

Classification is heuristic string matching over the log tail (the last 40 KB). It is a
convenience over the logs, not a substitute for them: `logs/<owner>__<repo>/{install,
collect,run}.log` holds the evidence, each truncated to 200 KB (first 100 KB + last 100 KB,
with an explicit truncation marker) because failures are legible at both ends.

Raw logs are gitignored because they contain arbitrary third-party output. The tracked
evidence layer is one `receipts/<owner>/<repo>.json` per manifest row: result fields plus
the byte length and SHA-256 of each phase log, with no log excerpts or notes. `receipts.py
--check` requires an exact 100-repo set and byte-for-byte receipt regeneration.

## Reproducing

```sh
cd ventures/c-measurement/pilot
./run.sh                       # fixed 100-repo manifest; JOBS=n to change
python3 pilot.py --selfcheck   # classifier + parser asserts, no docker, no network
python3 pilot.py --summary     # the funnel over results.csv (--md for markdown)
python3 fill_readme.py         # regenerate README.md's results block from results.csv
python3 receipts.py --check    # exact receipt set, result fields and phase-log hashes
```

`run.sh` is resumable: `results.csv` is appended per repo under an `flock` with an `fsync`,
and any repo already present is skipped, so a kill loses at most the rows in flight. A
harness exception still writes a row (`failure_class=other`, `notes=harness exception: …`)
rather than dropping the repo.

## Deviations from the brief, and what they cost

1. **`--memory 2500m`, not `4g`.** The docker VM on this machine has 8.3 GB total; three
   concurrent 4 GB caps overcommit it and risk an OOM that would show up as spurious build
   failures. Three 2500 MB caps fit. A repo whose install genuinely needs >2.5 GB would be
   misclassified; none of the observed failures carry an OOM signature (`Killed`, exit 137),
   and `PILOT_MEM=4g` re-runs any row on a larger host.
2. **linux/arm64.** Docker here is `aarch64`, so every container is arm64. Packages that
   publish x86-64 wheels but no `manylinux` aarch64 wheel fall back to building from sdist,
   which can turn a would-be clean install into a `native-deps` failure. **This biases
   `native-deps` upward relative to an x86-64 CI runner** and is the single largest caveat
   on the headline number; rows classed `native-deps` should be re-run on amd64 before the
   class is quoted in the write-up. `install_ok` on wheel-only stacks is unaffected.
3. **Clone is its own container and its own 10-minute cap**, separate from the install cap,
   so a slow clone cannot consume the install budget.
4. **`pytest` may be installed when the lockfile omits it** (see above), which is more
   generous than a strict lockfile-only reading. Every such row says so in `notes`.
5. **Containers run as root.** Tests that assert a `PermissionError` after `chmod 000` do
   not fail for root, so a handful of suites report a failed test that would pass on a CI
   runner. This affects `passed`/`failed` counts, never `install_ok`/`collect_ok`/`run_ok`,
   which is what the falsifier is about. Observed during harness development on
   `commit-check/commit-check`
   (`tests/config_test.py::TestConfigEdgeCases::test_load_config_file_permission_error`
   failed with `DID NOT RAISE PermissionError`).
6. **`pinned-requirements` is a corpus label, not a verified fact.** The corpus gate looked
   for a requirements file; the pilot checks whether it is actually pinned. Where it is not,
   the row is `no-lock` — the first such row (`omicverse/omicverse`) has 41 unpinned lines
   in the `requirements.txt` the corpus recorded as `pinned:requirements.txt`.
7. **Infrastructure recovery.** The first concurrent extension run filled Docker's host
   cache and tainted eight rows with daemon I/O, DNS or container-start failures. Those rows
   and their logs were removed, the task-specific caches were cleared, and exactly those
   eight were rerun sequentially. A ninth row was rerun after the harness gained direct
   `Pipfile.lock` sync support. The tracked CSV and receipts contain only the replacement
   outcomes; final logs contain no Docker host-failure signature.
