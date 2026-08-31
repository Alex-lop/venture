# Base-snapshot buildability pilot

**Question:** across the Track M corpus, how often does the *base* commit of a merged
agent-authored PR install from its lockfile and run its test suite to a verdict, offline?

**Why it decides the study.** A differential verifier compares base against candidate. If
the base does not build, there is no comparison — the PR is inconclusive, exactly the
failure mode that left jittest's sweep 71% inconclusive. `CLAUDE.md` §9 makes it the
falsifier: **under 30% and the study shrinks to the buildable set, and the buildability
number becomes the published finding.**

## Files

| path | what it is |
|---|---|
| `run.sh` | the entry point. Resumable — repos already in `results.csv` are skipped |
| `pilot.py` | the whole method: image choice, the three phases, parsing, classification. `--selfcheck` runs the asserts with no docker and no network; `--summary [--md]` prints the funnel |
| `Dockerfile` | `python:<X.Y>-slim` + `git` + `uv 0.11.29`, one image per Python minor |
| `results.csv` | one row per repo, appended under an `flock` with an `fsync` |
| `logs/<owner>__<repo>/` | `install.log`, `collect.log`, `run.log`, each capped at 200 KB |
| `fill_readme.py` | regenerates the results block below from `results.csv`, so no number here is typed by hand |
| `METHOD.md` | **the method, exactly** — caps, install ladder, classifier, and every deviation |
| `run.log` | the driver's own progress log |

```sh
./run.sh                        # 3 repos concurrently, ../corpus/candidates-v2.csv
python3 pilot.py --selfcheck    # classifier + parser asserts, offline
python3 pilot.py --summary      # the funnel, from results.csv
```

Untrusted candidate code never runs on the host: every phase is a `docker run` with no
host path mounted, and the collect and run phases have `--network none`. `METHOD.md` has
the details and the caveats — read it before quoting any number from here.

## How to read a row

- `install_ok` — the locked dependency set installed. No unpinned resolution is ever
  attempted; an unpinned requirements file is `no-lock`, not an install.
- `collect_ok` — `pytest --collect-only -q` exited clean, offline.
- `run_ok` — pytest reached a verdict. **This is the buildability number.** A suite whose
  tests fail at base still counts (`failure_class=tests-failed-at-base`); a suite that
  never reaches a summary line does not.
- `collected_count` is recorded even when collection then errored, so a repo that collects
  6,000 tests and errors on 10 modules is visibly different from one that collects nothing.

<!--SUMMARY-->
## Results

**The run is complete:** all **60** repos in `candidates-v2.csv` have a row in `results.csv`.
Every number below is regenerated from `results.csv` by `fill_readme.py` — none of it is
typed by hand.

| step | n | share of attempted |
|---|---:|---:|
| attempted | 60 | — |
| `install_ok` | 48 | 80% |
| `collect_ok` | 34 | 57% |
| **`run_ok` (reached a verdict)** | **29** | **48%** |

Tests collected in total, including partial collections that then errored: **185077**.

| failure_class | n |
|---|---:|
| `tests-failed-at-base` | 17 |
| `clean-pass` | 12 |
| `collection-error` | 11 |
| `python-version` | 8 |
| `no-lock` | 4 |
| `other` | 3 |
| `env-var/secret required` | 3 |
| `timeout` | 1 |
| `network-at-test-time` | 1 |

| lock_kind | reached a verdict | attempted |
|---|---:|---:|
| `pinned-requirements` | 2 | 7 |
| `poetry.lock` | 1 | 3 |
| `uv.lock` | 26 | 50 |
<!--/SUMMARY-->

## Status

The run **finished 2026-08-30** at 60 of 60 repos; `results.csv` is complete and the block
above is regenerated from it. It writes one row at a time under an `flock` with an `fsync`,
so a kill loses at most the rows in flight — which is why re-running is safe.

**To re-run, or to finish a partial run on another machine:**

```sh
cd ventures/c-measurement/pilot
nohup ./run.sh > run.log 2>&1 &   # skips every repo already in results.csv
tail -f run.log
python3 fill_readme.py            # refresh the block above
```

**Watch the throughput.** `candidates-v2.csv` is ordered by the corpus funnel, not by size,
and its first rows are its heaviest repos (`crewAIInc/crewAI`, 57k stars, a monorepo). The
worst case for one repo is 40 minutes — 10 clone + 10 install + 5 collect + 15 run — and
three run at once, so the tail of the corpus lands long after the head. Judge progress by
`results.csv` rows, not by elapsed time.

**Housekeeping.** `docker builder prune -af` after the six images are built
reclaims a few GB; per-repo volumes are destroyed as each row is written, so steady-state
disk is the six images plus the two shared caches (`pilot-uvcache`, `pilot-pipcache`).

## What the rows show

- `omicverse/omicverse` is recorded in the corpus as `pinned:requirements.txt`, but its
  `requirements.txt` at the base commit has **41 unpinned lines** (`scipy < 1.12`,
  `pandas`, `scanpy`, …). It is `no-lock` here. **The corpus's `lockfile_type` gate checked
  that a requirements file exists, not that it pins anything** — so the corpus's
  7 `pinned-requirements` repos are an upper bound on how many are really locked, and the
  study should treat that column as a claim the pilot verifies rather than an input it
  trusts.

