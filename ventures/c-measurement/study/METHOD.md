# Track M differential verifier — method

The quantity: **for each merged, agent-trailered pull request in a repo whose base
snapshot builds, run the PR's own tests on the PR's base commit and on the PR's merge
commit, and classify every PR-touched test.** A PR whose tests all pass on both sides
shipped no test that could have caught what the PR claims to fix. In SWE-bench's
vocabulary that is a PR with an empty `FAIL_TO_PASS` set.

Vocabulary is borrowed, not invented — `FAIL_TO_PASS` / `PASS_TO_PASS` from SWE-bench
(Jimenez et al. 2023), the base/candidate replay of a test-only patch from BSG-VA
(arXiv 2607.28871), `UNRESOLVED` as a first-class published verdict from jittest, and the
fail-closed evidence rules from this venture's own `Nemisis` (`src/nemisis/junit.py`,
`src/nemisis/matrix.py`). See `research/precedents.md`.

## Inputs

| input | what it supplies |
|---|---|
| `../pilot/results.csv` | the **buildable set**: rows with `install_ok=1, collect_ok=1, run_ok=1, errored=0, passed+failed>=1` — 25 of the pilot's 60 repos. Also supplies each repo's Python minor version and lock kind, both known to install at that repo's base. |
| `../corpus/candidates-v2.csv` | `sample_pr_numbers` (PRs that passed every PR-level criterion in `../corpus/README.md`: verbatim agent trailer, >=1 test path and >=1 non-test source file, <=2,000 changed lines), `lockfile_type`, `trailer_kinds`. |
| `../pilot/pilot.py` | imported, not copied: the container image, `docker_run`, the install ladder (`INSTALL_SH`), the caps, the log truncation and the volume cleanup are the pilot's, verbatim. |
| GitHub REST, read-only | `repos/O/R/pulls/N`, `.../pulls/N/files`, and `.../pulls/N/commits` (only when the PR body carries no agent trailer). |

## Isolation and budget

Every line of third-party code runs in a container: `--network none` during all five pytest
runs (pre-patch, base twice, candidate twice), `--memory 4g --cpus 2 --pids-limit 2048`, no host path ever mounted. The work tree
lives in a per-PR docker volume that is removed in a `finally`, so a crash cannot leak
one. The only persistent volumes are the uv and pip caches shared with the pilot;
`cache_guard()` wipes the uv cache at startup when it exceeds 8 GB (`STUDY_CACHE_CAP_MB`),
because the pilot's 60-repo run left 41 GB in it and the brief's disk budget is 20 GB.
Six images (~5.9 GB) plus an 8 GB cache is the steady state.

## Per-PR procedure — the exact commands

Numbers 1–3 run on the host; 4–11 are each one `docker run`.

1. `gh api repos/O/R/pulls/N` → `base.sha`, `merge_commit_sha`, `merged_at`,
   `additions + deletions`, plus two derived tokens: `cc_type` (the leading
   conventional-commit type of the title — `fix`, `feat`, `refactor`, `docs`, `test`,
   `chore`, `perf`, `build`, `ci`, `style`, `revert`, or empty) and `pr_trailer_kinds`
   (which of the corpus's ten agent trailers appear **in this PR**, matched with
   `corpus/scripts/widen.py`'s regexes against the body, falling back to
   `gh api .../pulls/N/commits --jq '.[] | {message: .commit.message}'` when the body
   carries none). Only the type token and the trailer *keys* are stored; no title text,
   body, login or email reaches a tracked file.
2. `gh api repos/O/R/pulls/N/files?per_page=100 --paginate --jq '.[] | {filename,
   previous_filename, status, additions, deletions}'`.
   All responses are cached under `raw/` (gitignored — PR payloads carry author logins,
   which never reach a tracked file).
3. Partition the changed files with the corpus README's test-path rule, verbatim — a
   `tests/` path segment, or a basename matching `test_*.py`, `*_test.py`, `conftest.py`:
   - **patch set** = every test-path file not `removed` (plus `previous_filename` for
     renames). This is what gets applied on base.
   - **run set** = the patch-set files whose basename matches `test_*.py` / `*_test.py`.
     `conftest.py` and data files under `tests/` are applied but never passed to pytest.
     An empty run set is `UNRESOLVED / no runnable test file`.
   - `infra_changed=1` if the PR touched `conftest.py`, `pytest.ini`, `tox.ini`,
     `setup.cfg`, or anything under a `fixtures/` directory — test-infrastructure changes
     are applied *with* the tests, and flagged, because they move the base run's goalposts.
   - `unmatched_testish_files` = files a deliberately **wider auditor rule**
     (`is_testish_path`: any `.py`/`.pyi` whose path contains `test`, plus `spec_*.py` and
     `check_*.py` — so `test/`, `tests.py`, `testing/`, `src/**/mytest.py`) calls a test
     while the strict rule does not. The auditor rule selects nothing to run; it only
     bounds the strict rule's misses (see Known limits #1).
4. **Clone the base tree** (network on, 15 min). The test patch is computed but **not yet
   applied**:
   ```sh
   git clone --filter=blob:none --quiet https://github.com/O/R.git repo
   git fetch --quiet origin <base.sha> <merge_commit_sha> || true
   git checkout --quiet --force <base.sha>
   git rev-parse --verify --quiet <merge_commit_sha>^1   # -> base_is_merge_first_parent
   for f in <run set>; do [ -f "$f" ] && echo "$f"; done  # -> the pre-patch run set
   git diff <base.sha> <merge_commit_sha> -- <patch set> > /w/test.patch
   ```
   Only the PR's own test paths are in the pathspec, so nothing else from the merge
   commit enters the base tree. `base_is_merge_first_parent` is `1` when `base.sha` is
   exactly the merge commit's first parent — i.e. when the base actually is the target
   branch immediately before the PR landed (Known limits #4).
5. **Install at base** (network on, 10 min): `pilot.INSTALL_SH` unchanged — `uv sync
   --frozen --all-extras --all-groups` with its two narrower fallbacks, or `poetry install
   --all-extras`, or a pinned-`requirements.txt` check followed by `uv pip install -r`.
   `pytest` and `pytest-timeout` are installed into the venv if the lockfile omits them.
   The patch is test-only, so installing before applying it changes nothing about the
   environment.
6. **Pre-patch base run** (`--network none`, 15 min) — the run-set files that already
   exist at the unpatched base, if any. Its per-id outcomes become `pre_patch_outcome`
   ∈ `passed | failed | error | skipped | absent` in `results-tests.csv`. This is
   Objection 1's base-greenness criterion, *recorded* so a reader can apply it as a
   filter, rather than enforced as a discard. One deviation from the fail-closed rules
   below, in this phase only: pytest exit 5 (nothing collected) is `absent`, not `error`.
   A run-set file that exists at base but holds no test yet is exactly the added-test
   case; calling it `error` would make a reader filtering on base greenness discard
   legitimate `FAIL_TO_PASS` rows, which is the direction that flatters the thesis. Every
   other fatal condition (timeout, exit 2/3/4, unusable report) still makes the whole
   pre-run `error`, because there the base's state is genuinely unknown.
7. **Apply the test patch** (network on — `git apply --3way` may need a blob the
   `--filter=blob:none` clone omitted; no untrusted code runs in this step):
   ```sh
   git apply --whitespace=nowarn /w/test.patch \
     || git apply --3way --whitespace=nowarn /w/test.patch   # exit 23 -> apply_failed
   ```
8. **Run the PR's tests on base, twice** (`--network none`, 15 min each):
   ```sh
   .venv/bin/python -m pytest <run set> -q --timeout=600 -p no:cacheprovider \
     --continue-on-collection-errors --junitxml=/w/base.xml -o junit_family=xunit2
   # then again, --junitxml=/w/base2.xml
   ```
   The XML is streamed out through stdout between markers (no host mount exists to read
   it from) and capped at 512 KB, `nemisis/junit.py`'s `MAX_JUNIT_BYTES`. An id whose two
   observations disagree is `flaky` on that side (Objection 4).
9. **Fresh candidate tree** (network on): `git checkout --force <merge_commit_sha>` then
   `git clean -xffdq`, which deletes `.venv` and every build artifact. The script exits 25
   if `.venv` survives, so a stale environment can never be reused across sides.
10. **Install at candidate**: step 5 again, unmodified — the candidate may change the
    lockfile, so the install is re-run rather than reused.
11. **Run the same test files on candidate, twice**: step 8 with `/w/cand.xml` and
    `/w/cand2.xml`.

Then the volume is removed and all five reports are classified on the host.

## Reading a JUnit report — fail-closed

Adapted from `nemisis/junit.py`. **An ERROR is absence of evidence, not a failure**, and
anything that makes the report untrustworthy is absence of evidence for the whole run:

| condition | result |
|---|---|
| the container hit its 15-minute cap | whole run fatal: `timeout` |
| pytest exit code 2 / 3 / 4 (interrupted, internal error, usage error) | whole run fatal |
| pytest exit code 5 (nothing collected) | whole run fatal: `no tests collected` |
| report absent, empty, over 512 KB, or unparseable | whole run fatal |
| two `<testcase>` elements with the same id | that id becomes `error` |
| `<testcase>` with an `<error>` child | `error` (wins over `<failure>` and `<skipped>`) |
| `<testcase>` with `<skipped>` | `skipped` — never counted as a pass |
| `<testcase>` with `<failure>` | `failed` |
| otherwise | `passed` |

A **fatal** run makes every test in it `error`, the PR `UNRESOLVED`, **and every one of
that PR's rows in `results-tests.csv` `UNRESOLVED` as well**, whatever the other side
says. This is the guard that stops a broken base environment from manufacturing
`FAIL_TO_PASS` rows wholesale, and it is applied to the test rows and the PR row together
so the two published files can never contradict each other: no test-level aggregate can
count a run that never happened as discriminating evidence.

**Each side is observed twice** (`base`/`base2`, `cand`/`cand2`). An id whose two
observations of the same side disagree is `flaky` on that side, which no cell of the
verdict table resolves — Objection 4's remedy, against Meta's 18-point built-vs-reliable
gap. A side is fatal if *either* of its two observations is fatal.

Test id is `classname::name` from the report (e.g.
`tests.test_server::test_upload_rejects_oversize_input`). The expected id set is the
**union** of the two sides. An id absent from one side is `missing` there — except when
that side reported a *collection failure for the id's module*, which pytest emits as a
classname-less `<testcase name="dotted.module"><error message="collection failure">`. Then
the id is `error`, not `missing`. That single rule is what makes the canonical
discriminating case work: a PR that adds `tests/test_x.py` for a module the PR also adds
cannot even import at base, and SWE-bench treats exactly that as `FAIL`.

## The verdict table

Per test (`results-tests.csv`), base outcome × candidate outcome:

| base \ candidate | passed | failed | error | skipped | missing | flaky |
|---|---|---|---|---|---|---|
| **passed** | `PASS_TO_PASS` | UNRESOLVED (PASS_TO_FAIL) | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |
| **failed** | **`FAIL_TO_PASS`** | UNRESOLVED (FAIL_TO_FAIL) | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |
| **error** | **`FAIL_TO_PASS`** | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |
| **skipped** | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |
| **missing** | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |
| **flaky** | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |

Overridden to `UNRESOLVED` for every row of the PR when either side's run was fatal.
`pre_patch_outcome` is carried alongside and never enters the verdict: it is a covariate
the reader filters on, not a term in the classification.

`FAIL_TO_PASS` is discriminating. `PASS_TO_PASS` is non-discriminating *for this PR's
claim* — it is the desirable regression category in SWE-bench and is not a defect here
either; it just is not evidence that the PR's change was necessary. Everything else is
`UNRESOLVED`, and the row's own `base_outcome`/`candidate_outcome` pair is the reason.

Per PR (`results-prs.csv`):

| condition | `pr_verdict` |
|---|---|
| either side's run was fatal, or clone/apply/install failed, or the run set was empty | `UNRESOLVED` + `unresolved_reason` |
| >=1 `FAIL_TO_PASS` | `DISCRIMINATING` |
| >=1 `PASS_TO_PASS`, zero `FAIL_TO_PASS`, **and zero UNRESOLVED rows** | `NON_DISCRIMINATING` |
| >=1 `PASS_TO_PASS`, zero `FAIL_TO_PASS`, some UNRESOLVED rows | `UNRESOLVED / partial evidence: N unresolved rows` |
| no test resolved on both sides | `UNRESOLVED / no test resolved on both sides` |

The rule is deliberately asymmetric. One `FAIL_TO_PASS` is positive evidence and unresolved
rows beside it cannot take it away. Zero `FAIL_TO_PASS` is only evidence *of*
non-discrimination when there was nothing left unobserved: a PR with 1 `PASS_TO_PASS` and
40 no-evidence rows is `partial evidence`, not the headline verdict. `runner.py --summary`
therefore publishes the headline as an **interval** — `strict` counts only fully resolved
PRs, `permissive` also counts `partial evidence` PRs as non-discriminating — and the study
reports both ends, never the permissive number alone.

`unresolved_reason` is one of `api_error`, `no merge_commit_sha`, `no runnable test file`,
`clone_failed`, `base_checkout_failed`, `diff_failed`, `clone_timeout`, `clone_rc_<n>`,
`apply_failed`, `apply_timeout`,
`install_failed_base`, `install_timeout_base`, `candidate_checkout_failed`,
`candidate_timeout`, `install_failed_candidate`, `install_timeout_candidate`,
`base_run: <fatal>`, `candidate_run: <fatal>`, `partial evidence: N unresolved rows`,
`no test resolved on both sides`, `harness_exception: …`. Every one of them is a published
denominator line, not a dropped row: **the study reports the unresolved rate before the
headline** (jittest's discipline, and the answer to Objection 1 in
`research/precedents.md`).

## Stratification — what the headline is computed over

precedents.md Objection 3 is pre-registered against a headline computed over all PR types:
a refactor, docs or coverage PR *should* ship tests that pass on both sides. So the
headline is **restricted to `cc_type == "fix"`**, with the other types reported separately
and explicitly not counted as defects, and the all-types number published as context only.
`--summary` prints the `fix` interval first, then all types, then the number restricted to
`base_is_merge_first_parent == 1`, then a per-`cc_type` and per-`pr_trailer_kinds`
breakdown (the per-agent breakdown precedents.md item 2 requires, from the PR's own
trailers rather than its repo's).

A caveat the smoke already surfaces: **conventional-commit titles are not universal in this
population.** None of the six smoke PRs carried one, so `cc_type` was empty for all six. If
that holds at 107, the `fix`-restricted headline will be small-n and the write-up must say
so and report the `(none)` stratum's size rather than quietly widening back to all types.

## Departures from SWE-bench, and why

1. **Only the PR's own test files are run, not the repo's whole suite.** SWE-bench runs
   the full suite to populate `PASS_TO_PASS`. Here `PASS_TO_PASS` is scoped to the tests
   the PR itself touched, because the question is about the PR's tests. A repo-wide
   regression that the PR causes elsewhere is invisible to this instrument.
2. **`error` at base counts as `FAIL` when the candidate passes.** SWE-bench's log parsers
   do the same (a test that cannot import at base is a failing test). **It is not one
   mechanism.** Crosstabbing `base_outcome` against `pre_patch_outcome` over the 2,948
   `FAIL_TO_PASS` rows (`python3 analysis.py`, `== RED-TEAM PASS ==` block, tag `[A2]`)
   gives: 1,727 rows (58.6%) are ids that existed and *passed* on the unpatched base and
   were turned into collection errors by an import the PR's own test-only patch added;
   only 454 (15.4%) are the module-arrives-with-its-test shape; 635 (21.5%) are newly-added
   tests failing an assertion. An earlier draft of this file called the second the dominant
   shape; it is not, and `WRITEUP.md` §Results 3 publishes the full table. The safeguard
   against the obvious abuse — a broken environment erroring everything — is the whole-run
   fatal rule above, plus the buildable-set admission criterion; the safeguard against the
   *collateral* shape driving a headline is that the per-PR result is re-scored without
   those rows and is unchanged at 0/99.
3. **`--continue-on-collection-errors`.** Without it a single unimportable module aborts
   the whole pytest session (exit 2) and erases the evidence for every other file in the
   run set. With it, that module's tests are `error` and the rest still report.
4. **Base greenness is recorded per test, not enforced as an admission criterion.**
   SWE-bench Verified requires a green base. Here the buildable set is only a *repo-level*
   filter (the pilot ran each repo's suite at one base commit), so the per-test
   `pre_patch_outcome` column carries the missing signal: how each id behaved at the
   unpatched base. The earlier argument — that a red base yields `FAIL_TO_FAIL`, which
   lands in UNRESOLVED — covered only `failed -> failed`. It did **not** cover
   `failed -> passed` arising from a pre-existing red base (a changed lockfile that pins a
   newer dependency repairing an unrelated breakage; an intervening commit that fixes it),
   which would score as `FAIL_TO_PASS`. Filtering on `pre_patch_outcome == "passed"` (or
   `"absent"`, the added-test case) is the reader's answer to that, and it is a filter
   they can apply because the column exists rather than data the harness threw away.

## Departures from Nemisis, and why

Nemisis classifies claims about an artifact it built itself, so an `ERROR` there is always
absence of evidence and never scores. Two changes:

1. **`ERROR` at base is admissible evidence** when the candidate side is clean (see
   above). Nemisis never faces a world where the code under test does not exist yet; this
   study's central case is exactly that world.
2. **No `ExpectedRelation`.** Nemisis is told whether a test is a `CHANGE_WITNESS` or an
   `INVARIANT`; a PR does not label its tests, so this instrument reports the observed
   transition and lets the PR-level rule ("zero `FAIL_TO_PASS`") do the work.
   `NON_DISCRIMINATING` keeps Nemisis's exact meaning: base and candidate agree, so the
   test separates nothing.

Kept verbatim: the fail-closed parse (a bad report is `ERROR` for everything in it),
`ERROR` beating `FAILURE` and `SKIPPED` on the same `<testcase>`, `SKIPPED` never counting
as a pass, duplicate ids poisoning to `ERROR`, and the 512 KB report cap.

## Known limits

1. **Test selection is by path, not by import graph — and the error has a direction and a
   measured bound.** A PR that adds a test to a file the strict path rule does not
   recognise (`test/` singular, Django `tests.py`, `spec_*.py`, `check_*.py`, `testing/`,
   tests inside `src/`, doctests — pytest runs without `--doctest-modules`) contributes
   nothing to the run set. The rule is the corpus's own, kept deliberately identical so the
   corpus and the study measure the same population. **The direction is the problem:** a
   missed test file means a possible `FAIL_TO_PASS` is never observed, which pushes the PR
   toward `NON_DISCRIMINATING` — toward the study's own thesis. So a second, wider
   *auditor* rule runs over the same files payload and records
   `unmatched_testish_files` per PR; the published upper bound on this error is **the share
   of `NON_DISCRIMINATING` PRs with a nonzero value**, printed by `--summary`. Doctests
   remain outside even the auditor rule and are an acknowledged, unbounded residue.
2. **Test-infrastructure changes are applied with the tests, and only test-*path*
   infrastructure.** `conftest.py` and `tests/fixtures/**` travel with the patch and set
   `infra_changed=1`. Pytest configuration that lives in `pyproject.toml` or a `Makefile`
   does **not** — those are not test paths, so the base run uses the base's configuration
   while running the candidate's tests. Read `infra_changed=1` rows as lower-confidence.
3. **Each side is observed twice; two observations are not proof of stability.**
   Disagreement between the two runs makes the id `flaky` and the row `UNRESOLVED`
   (Objection 4, against TestGen-LLM's 18-point built-vs-reliable gap). Two runs catch a
   coin-flip test roughly half the time, and a test that fails only on a cold cache, a
   different day, or a different ordering can still agree with itself twice. The two runs
   are also consecutive in the same container, so state a test leaves behind shows up as
   flakiness in the *second* run — which is the honest direction, but means the flaky rate
   published here mixes true nondeterminism with order dependence. Read the `flaky` count
   as a floor on instability, not an estimate of it.
4. **The counterfactual is `base.sha`, not `merge_commit_sha^1`, and the divergence is
   recorded.** Track M's quantity wants "the target branch immediately before this PR
   landed"; `pulls/N.base.sha` is the base ref as of the PR's last synchronization. Where
   they differ, both pytest runs and the `git diff` attribute every intervening commit's
   effect to this PR, which inflates `FAIL_TO_PASS` and deflates the headline. `base.sha`
   is nevertheless what the runs use, because `merge^1` is wrong for a **rebase merge**:
   there `merge_commit_sha` is the last commit of the rebased series, so its first parent
   is another commit of the same PR. Instead the harness records
   `base_is_merge_first_parent` (`1` when they coincide, `0` when they do not, empty when
   `merge^1` could not be resolved), and `--summary` publishes the headline restricted to
   `1` alongside the full-set number as a sensitivity check. All six smoke PRs were `1`.
   The pathspec separately bounds — but does not eliminate — contamination of the test
   patch itself; a per-PR `head.sha` diff would be tighter but is often unfetchable
   (deleted branches).
5. **The Python version and lock kind come from the pilot's row for the repo**, which was
   determined at the base commit of the *first* sample PR. Another PR's base may declare a
   different `requires-python`. Using one interpreter for both sides is deliberate — a
   version switch between base and candidate would confound the comparison — but a repo
   that changed its floor mid-window can show `install_failed_base`.
6. **Test ids are `classname::name`.** A PR that renames a test module, moves a test
   between classes, or changes a `@parametrize` id produces `missing` on one side and
   therefore `UNRESOLVED`, even when a human would call it the same test.
7. **`--memory 4g` with `--jobs 3` overcommits an 8.3 GB docker VM.** The pilot lowered
   this to `2500m` for exactly that reason. The brief specifies 4 GB, so 4 GB is the
   default; an OOM would surface as `install_failed_*` (an UNRESOLVED row), never as a
   wrong verdict. Set `PILOT_MEM=2500m` or `JOBS=2` on a small host.
8. **linux/arm64** — inherited from the pilot. Packages without an aarch64 wheel build from
   sdist and can fail to install, so `install_failed_*` is biased upward relative to an
   x86-64 runner.
9. **The corpus's own biases carry through**: >=10 stars, primary-language Python,
   lockfile-driven, trailer visible to GitHub search. See `../corpus/README.md` §"Known
   biases". This instrument measures *repos where the question is answerable at all*.

## Outputs

`results-tests.csv` — one row per PR-touched test:
`repo, pr, test_id, pre_patch_outcome, base_outcome, candidate_outcome, verdict`.
`pre_patch_outcome` ∈ `passed | failed | error | skipped | absent` (the unpatched base);
`base_outcome`/`candidate_outcome` ∈ `passed | failed | error | skipped | missing |
flaky`; `verdict` ∈ `FAIL_TO_PASS | PASS_TO_PASS | UNRESOLVED`. Every row of a PR whose
run was fatal is `UNRESOLVED`, so the file can be aggregated on its own without joining to
`results-prs.csv`.

`results-prs.csv` — one row per PR:
`repo, pr, base_sha, merge_sha, merged_at, n_tests, n_f2p, n_p2p, n_unresolved,
pr_verdict, unresolved_reason, cc_type, pr_trailer_kinds, base_is_merge_first_parent,
unmatched_testish_files, changed_lines, test_files_new, test_files_modified,
infra_changed, repo_trailer_kinds, duration_s`.

`pr_trailer_kinds` is **this PR's** agent trailers; `repo_trailer_kinds` is the repo-level
column carried over from `candidates-v2.csv` and is an attribute of the repo, not of the
row it sits in — only `pr_trailer_kinds` may be used for a per-agent breakdown.

Neither file contains an author name, a login, an email address, a PR title or a PR body —
only the conventional-commit type token and the trailer *keys* are extracted from them.
Raw API responses (which do carry logins) stay in `raw/`, and `logs/` holds the per-phase
container output; both are gitignored.

## Reproducing

```sh
cd ventures/c-measurement/study
./run.sh                        # every sample PR of every buildable repo, 3 at a time
./run.sh --smoke 2              # the two buildable repos with the smallest suites
./run.sh --repo O/R --limit 1   # one PR
JOBS=2 ./run.sh                 # fewer containers at once
python3 runner.py --selfcheck   # parser + verdict asserts, no docker, no network
python3 runner.py --summary     # verdict counts over results-prs.csv (--md for markdown)
```

The full run is **107 sample PRs across the 25 buildable repos**. Each PR is now ten
container steps (clone, install, pre-patch run, apply, base ×2, candidate checkout,
install, candidate ×2) rather than six: the post-fix smoke's six PRs averaged 28.4 s each
against 10.6 s before, on a warm uv cache. The corpus's heavy repos (`raptor` 35k
collected tests, `Datus-agent` 21k, `codex-lb` 9k) will dominate, and the 15-minute
per-run cap now bounds a PR at roughly 75 minutes worst case (five capped pytest phases
plus two capped installs).

`run.sh` is resumable: both CSVs are appended under an `flock` with an `fsync` after every
PR, and any `(repo, pr)` already present in `results-prs.csv` is skipped, so a kill loses
at most the PRs in flight. GitHub responses are cached in `raw/`, so a resumed run costs
no extra API calls for PRs it already fetched. Every failure path writes a row — a harness
exception becomes `UNRESOLVED / harness_exception: …` rather than a dropped PR.

## Review changes, 2026-08-30

A method review of the pre-fix instrument raised two blockers and six majors. All eight are
fixed in `runner.py` and recorded here; the smoke was re-run afterwards on the same two
repos and reproduced the pre-fix verdicts exactly (58 `FAIL_TO_PASS` / 93 `PASS_TO_PASS`,
same five `DISCRIMINATING` PRs and the same `install_failed_base` row), so the restructure
is behaviour-preserving where it should be.

| # | severity | what was wrong | fix |
|---|---|---|---|
| 1 | blocker | On a fatal run the PR row said `UNRESOLVED` but its **test rows still carried `FAIL_TO_PASS`** (`side_outcome` returns `error` for every id, and `error -> passed` is `FAIL_TO_PASS`). The two published files could contradict each other, and any test-level aggregate would count broken environments as discriminating evidence - Objection 1 realised inside the dataset. | `build_rows` stamps `UNRESOLVED` on **every row** of a PR with a fatal side, so `results-tests.csv` is safe to aggregate without a join. Asserted in `--selfcheck`. |
| 2 | blocker | `NON_DISCRIMINATING` fired whenever `n_p2p > 0`, regardless of `n_unresolved`: a PR with 1 `PASS_TO_PASS` and 40 no-evidence rows was published as the headline verdict - moving the exact number the study exists to publish, in the direction of its own thesis. | `pr_verdict_of` requires `n_unresolved == 0`; otherwise `UNRESOLVED / partial evidence: N unresolved rows`. `--summary` publishes the headline as an interval [strict, permissive] rather than a single permissive number. Asserted in `--selfcheck`. |
| 3 | major | No per-test base-greenness signal, so Objection 1's admission criterion could not be applied even after the fact, and `failed -> passed` arising from a pre-existing red base scored as `FAIL_TO_PASS`. | One extra pytest phase before the test patch is applied; `pre_patch_outcome` in `passed / failed / error / skipped / absent` per test id. Recorded as a filter for the reader, not enforced as a discard. See Departures #4. |
| 4 | major | `trailer_kinds` was a **repo-level** column written into every PR row of that repo, and would be read as a per-PR claim. It cannot support the per-agent breakdown precedents.md item 2 requires. | Renamed `repo_trailer_kinds`, and a real per-PR `pr_trailer_kinds` is derived from the PR body (falling back to its commit messages) with `widen.py`'s verbatim regexes. Only trailer *keys* are stored. The smoke proves the difference: `grok-mcp-server#33` is `copilot`, its repo is `claude-code-gen;copilot;robot-gen`. |
| 5 | major | No PR-intent field, so Objection 3's `fix`-only headline could not be computed at all, and could not be recovered later without re-fetching every PR. | `cc_type` from the leading conventional-commit token of the title. `--summary` reports the `fix`-restricted headline first. See "Stratification". |
| 6 | major | `base.sha` was used as the counterfactual without ever checking it equals `merge_commit_sha^1`; where they differ, an intervening commit's effect is attributed to this PR (inflates `FAIL_TO_PASS`, deflates the headline). | `base_is_merge_first_parent` is recorded per PR and the headline is published restricted to `1`, with the full set as a sensitivity check. `merge^1` was **not** adopted as the base, because it is an intra-PR commit for rebase merges. See Known limits #4. |
| 7 | major | The strict path rule misses `test/`, `tests.py`, `spec_*.py`, `check_*.py`, `testing/` and doctests, and every miss pushes a PR toward `NON_DISCRIMINATING` with no measured bound. | A wider auditor rule (`is_testish_path`) records `unmatched_testish_files` per PR; `--summary` publishes the share of `NON_DISCRIMINATING` PRs with a nonzero value as the upper bound. See Known limits #1. |
| 8 | major | Single observation per side, against a named precedent (TestGen-LLM: 75 percent built vs 57 percent passed reliably) whose remedy the method had deferred. | Each side is run twice; an id whose observations disagree is `flaky`, which no verdict cell resolves. See Known limits #3 for what two runs still do not catch. |

One further fix, found while watching the first 21 PRs of the full run rather than raised
by the review: pytest exit 5 in the **pre-patch phase** was being treated as a fatal run,
stamping `error` on every id, when it actually means the run-set file existed at base and
held no test yet. That is `absent`. Left as `error` it would have made a reader filtering
on base greenness discard legitimate `FAIL_TO_PASS` rows - the direction that flatters the
thesis. The first 21 rows were discarded and the run restarted from empty, so every
published row comes from one version of the instrument.

Not changed, deliberately: the strict path rule still selects the run set (keeping the
corpus and the study on the same population - the auditor rule only bounds it), and
`base.sha` is still the base commit (item 6).

## Smoke-test record - 2026-08-30 (post-fix)

Two repos, chosen as the buildable repos with the smallest collected suites
(`--smoke 2`): `open-reaction-database/ord-data` (30 tests collected at base in the pilot)
and `djtelicloud/grok-mcp-server` (155). All 6 of their sample PRs ran end to end at
`--jobs 3`. Sum of per-PR durations 170.4 s (28.4 s mean, up from 10.6 s: five pytest
phases per PR instead of two); wall clock under three minutes. Console record: `smoke.log`.
The pre-fix run's outputs are kept for comparison under `raw/pre-review-smoke/`
(gitignored).

`results-prs.csv`, verbatim:

```
repo,pr,base_sha,merge_sha,merged_at,n_tests,n_f2p,n_p2p,n_unresolved,pr_verdict,unresolved_reason,cc_type,pr_trailer_kinds,base_is_merge_first_parent,unmatched_testish_files,changed_lines,test_files_new,test_files_modified,infra_changed,repo_trailer_kinds,duration_s
open-reaction-database/ord-data,262,7a9d0546585bae12b128312472428c3acad99377,1ca9e60cca24ed1e13b5006b707b4c992c762658,2026-08-02T01:32:00Z,0,0,0,0,UNRESOLVED,install_failed_base,,claude-code-gen;robot-gen,1,0,1410,1,0,0,claude-code-gen;robot-gen,3.0
djtelicloud/grok-mcp-server,508,765997fb36713c3c7e4880843b8d9ec723e67169,ffef9a64c45b51fe50331bae393da703432a2a4e,2026-07-19T01:57:02Z,18,15,3,0,DISCRIMINATING,,,claude-code-gen;robot-gen,1,0,323,1,0,0,claude-code-gen;copilot;robot-gen,20.4
djtelicloud/grok-mcp-server,500,a99b521b463adbc55537e054c2cd01a955e1f534,e08ca3f43d6f6d9ebf68c1ec4ab3229b06fe3b59,2026-07-18T17:19:59Z,19,6,13,0,DISCRIMINATING,,,claude-code-gen;robot-gen,1,0,359,0,1,0,claude-code-gen;copilot;robot-gen,23.3
open-reaction-database/ord-data,263,1ca9e60cca24ed1e13b5006b707b4c992c762658,01979ec78e5c1168c3b151714bd509352a8baf9b,2026-08-02T02:00:23Z,20,20,0,0,DISCRIMINATING,,,claude-code-gen;robot-gen,1,0,1510,1,0,0,claude-code-gen;robot-gen,49.9
open-reaction-database/ord-data,266,01979ec78e5c1168c3b151714bd509352a8baf9b,13c6895981a636d1b770a8751aa77cc484e77b83,2026-08-02T02:14:50Z,40,13,27,0,DISCRIMINATING,,,claude-code-gen;robot-gen,1,0,167,0,1,0,claude-code-gen;robot-gen,50.9
djtelicloud/grok-mcp-server,33,6b152fa016e7f4a5d74c15ff25f19e93e5df2b17,d503bf30a9b8d7f3708983b830eef13fd5e03568,2026-07-12T12:14:33Z,54,4,50,0,DISCRIMINATING,,,copilot,1,0,157,0,1,0,claude-code-gen;copilot;robot-gen,22.9
```

151 test rows: 58 `FAIL_TO_PASS`, 93 `PASS_TO_PASS`, 0 `UNRESOLVED` - identical to the
pre-fix run, which is the evidence that the ten-step pipeline did not change what the
instrument measures.

**These six PRs are a plumbing check, not an estimate.** Two repos, chosen for being
cheap to run, cannot say anything about the population; both are young, actively
maintained projects. Do not quote 5/5.

What the six rows establish, each verified against the container logs under `logs/`:

- **The discriminating case via assertion failures.** `grok-mcp-server#33`: 4 failed and
  50 passed at base, 54 passed at candidate -> 4 `FAIL_TO_PASS`, 50 `PASS_TO_PASS`. A
  mixed row like this is the strongest evidence the instrument is not simply reporting
  whatever the candidate does.
- **The discriminating case via a collection error.** `ord-data#263` adds
  `scripts/process_dataset.py` and its test in one PR; at base the test module raises
  `ModuleNotFoundError: No module named 'process_dataset'`, which the module-level
  collection-error rule turns into `error` for all 20 ids -> 20 `FAIL_TO_PASS`.
- **A real UNRESOLVED.** `ord-data#262`'s base commit predates the repo's `pyproject.toml`,
  so `uv sync --frozen` cannot run there at all (`error: No pyproject.toml found`) ->
  `install_failed_base`, 3.0 s, no verdict claimed. The repo is in the buildable set on a
  *later* base commit; buildability is per-commit, not per-repo, and this row is the
  reason the study must publish the unresolved rate.
- **Partial discrimination.** `ord-data#266` (13 F2P / 27 P2P) and `grok-mcp-server#508`
  (15 F2P / 3 P2P) both show the PR's tests split across the two resolved categories,
  which is what a real bug-fix-plus-regression-tests PR looks like.

New columns, on real data:

- **`pre_patch_outcome`** - 85 `passed`, 66 `absent`, **0 `failed` and 0 `error`**: every
  test id that already existed at the unpatched base was green there, so none of these 58
  `FAIL_TO_PASS` rows is the pre-existing-red-base artefact Objection 1 warns about. Two
  rows are `passed` -> `FAIL_TO_PASS`: an existing test the PR *modified*, green before the
  patch, failing at base in its new form, passing on the candidate. That is the shape the
  column exists to make visible.
- **`pr_trailer_kinds`** - narrower than the repo column on 4 of 6 PRs, and on
  `grok-mcp-server#33` it is `copilot` where the repo says
  `claude-code-gen;copilot;robot-gen`. The per-agent breakdown is now computable, and would
  have been wrong before.
- **`cc_type`** - empty for all six: not one of these PR titles is a conventional commit.
  See "Stratification" for what that does to the `fix`-restricted headline.
- **`base_is_merge_first_parent`** - `1` for all six, matching the reviewer's manual check.
- **`unmatched_testish_files`** - `0` for all six.
- **Flakiness** - no id disagreed between its two observations on either side, so no
  `flaky` row appeared. Ten pytest runs across six PRs is not a flakiness estimate.

Still not exercised on real data, and honestly so: `NON_DISCRIMINATING`, `partial
evidence`, `flaky`, and the fatal-run row override. All four are covered by `--selfcheck`
asserts over the pure classification functions, but the first *observed* instance of each
will come from the full run, and the write-up must not claim otherwise until it does.
