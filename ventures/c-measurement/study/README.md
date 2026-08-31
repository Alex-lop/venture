# Track M study — running it, resuming it, reading it

The instrument is `runner.py`; the method it implements (and every known limit) is
`METHOD.md`. Everything untrusted runs in docker, `--network none` during every pytest
phase. Nothing here writes to GitHub.

## Where progress is read

| question | command / file |
|---|---|
| how far along is the run? | `wc -l results-prs.csv` — one data row per finished PR, 108 rows (107 PRs + header) when complete |
| what happened just now? | `tail -20 run.log` — one `START`/`DONE` line per PR |
| is it still alive? | `ps -p <pid>`, or `ls -l run.log` (mtime advances every PR) |
| what does it say so far? | `python3 runner.py --summary` (add `--md` for the tables the write-up uses) |
| why was a PR unresolved? | the `unresolved_reason` column, then `logs/<owner>__<repo>__pr<N>/` |

`results-prs.csv` is the progress file *and* the resume key: a `(repo, pr)` already in it
is never re-run. Both CSVs are appended under an `flock` with an `fsync` per PR, so they
are safe to read while the run is in flight.

## Resume

Killed, crashed, laptop slept, session ended — same command, no flags, no cleanup:

```sh
cd ventures/c-measurement/study
nohup ./run.sh > run.log 2>&1 &        # appends to run.log; use >> to keep the old log
```

It re-reads `results-prs.csv`, skips what is done, and runs the rest. GitHub responses are
cached under `raw/`, so a resume costs no extra API calls for PRs already fetched. At most
the PRs in flight at the moment of the kill are lost, and they are simply re-run.

Useful variants:

```sh
./run.sh --smoke 2               # the two buildable repos with the smallest suites
./run.sh --repo O/R --limit 1    # one PR
JOBS=2 ./run.sh                  # fewer containers at once (see METHOD Known limits #7)
python3 runner.py --selfcheck    # parser + verdict asserts; no docker, no network
```

## Outputs

- `results-prs.csv` — one row per PR (verdict, counts, `cc_type`, `pr_trailer_kinds`,
  `base_is_merge_first_parent`, `unmatched_testish_files`, …). Tracked.
- `results-tests.csv` — one row per PR-touched test (`pre_patch_outcome`, base, candidate,
  verdict). Tracked.
- `run.log`, `smoke.log` — console records. `run.log` is tracked; it contains no author
  data.
- `logs/`, `raw/` — per-phase container output and cached API responses. **Gitignored:**
  raw PR payloads carry author logins and emails, which never reach a tracked file.

## Before quoting a number

Read `METHOD.md` § "Stratification" first. The headline is the `NON_DISCRIMINATING` share
of **`fix`** PRs, published as an interval (strict .. permissive), with the unresolved rate
reported before it. `--summary` prints it that way on purpose.
