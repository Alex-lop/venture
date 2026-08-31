# Do merged agent-authored pull requests ship tests that could have caught anything?

**A differential execution study of 107 merged, agent-trailered pull requests across 25
public Python repositories.** Instrument, dataset and method: this directory.
Date: 2026-08-31. Status: run complete (107 of 107 sample PRs); **revised 2026-08-31 after a
three-team red-team pass — see §Red-team pass at the end for every objection and its
disposition.**

**Provenance rule.** Every number here is printed by one of four commands, tagged at the
point of use and run from `ventures/c-measurement/study/`: **[A]** `python3 analysis.py`
(its `== RED-TEAM PASS ==` block prints everything added in this revision), **[R]**
`python3 runner.py --summary --md`, **[P]** `python3 ../pilot/pilot.py --summary`, **[F]**
the one-liner quoted inline. The four result CSVs are `results-prs.csv`, `results-tests.csv`,
`../pilot/results.csv` and `../corpus/candidates-v2.csv`; the funnel adds a fifth,
`../corpus/funnel-v2.csv` (see §Corpus and funnel for how it is emitted). Nothing is
typed from memory. Every prior-work claim cites
`research/precedents.md` or an arXiv id fetched via `export.arxiv.org` on the date given.

## Abstract

This is **BSG-VA's base/candidate replay (arXiv:2607.28871) applied to merged real-world
agent pull requests.** Across 107 merged PRs carrying a verbatim coding-agent trailer, drawn
from the 25 of 60 corpus repositories whose base commit installs from its lockfile and runs
its suite to a verdict offline, we applied each PR's own test files to the PR's base commit,
ran them twice on base and twice on the merge commit, and classified every PR-touched test id
in SWE-bench's vocabulary. 99 of 107 PRs reached a verdict (8 unresolved, 7.5%).

**The pre-registered quantity** — `research/precedents.md` §"The gap" defines it over *the
PR's own newly-added tests* — is **1 of 99 = 1.0%, Wilson [0.2%, 5.5%]**: exactly one resolved
PR added test ids that all already passed at its base commit. With the repository as the unit
of analysis, 1 of 25 = 4.0%, [0.7%, 19.5%]. On the `fix` stratum `precedents.md` Objection 3
asked us to headline, **0 of 41, [0.0%, 8.6%]** (15 repos; with the repo as the unit,
[0.0%, 20.4%]) [A].

**Under the broader bar** — zero `FAIL_TO_PASS` among *all* tests in the PR's test files, new
and pre-existing — the count is **0 of 99, [0.0%, 3.7%]**; with the repo as the unit,
0 of 25, **[0.0%, 13.3%]**; and if every unresolved PR were non-discriminating, 8 of 107 =
7.5%, [3.8%, 14.1%] [A]. The strong form of the thesis this study was built to test — that
merged agent PRs routinely ship tests that all pass on base — is **not supported** in this
population under either bar.

The per-PR bar is weak, and the per-test picture runs the other way, but only for
*pre-existing* tests. Of 13,380 resolved PR-touched **test ids** (parametrize-expanded, so
one test function can contribute hundreds), 10,432 (78.0%) are `PASS_TO_PASS`. That row-level
figure treats 13,380 ids as independent draws when they are not: a cluster bootstrap over the
25 repos gives **[71.0%, 87.2%]**, twelve times the Wilson width, and dropping two PRs of one
repo moves it to 86.4% [A]. Restricted to the **1,217 resolved ids the PRs actually added**,
the `PASS_TO_PASS` share is **10.5%, [8.9%, 12.4%]** — the 78.0% is overwhelmingly a
statement about pre-existing tests being re-run [A]. Under a stricter per-PR bar (≥1 test that
*failed an assertion* at base), **14 of 99 (14.1%, [8.6%, 22.3%])** have none.

This is a measurement, not a population estimate: it speaks for the buildable,
lockfile-driven, ≥10-star Python tail, 92 of 107 PRs carry one trailer family, and the
question is conditioned on the PR shipping a test file at all (288 of 937 examined PRs did
not, 30.7%) [F].

**Novelty, hedged.** In an arXiv-metadata search re-run and triaged in full on 2026-08-31 (90
hits on the broad query, every title read, six abstracts fetched), plus an OpenAlex search
that reaches non-arXiv venues, we found no work holding all four of the properties
`precedents.md` §"The gap" lists. The search remains incomplete — Semantic Scholar has
429'd on every attempt — so this is *"we found none"*, not *"there is none"*. See §Relation to
prior work and §Red-team pass, objection B1.

## The question, and its two units

`research/precedents.md` §"The gap" states four properties that no published work holds
simultaneously: (a) real merged PRs in the wild, (b) agent-authored, identified by trailer,
(c) the PR's own tests executed on the base commit, (d) the pass-on-base rate reported as the
result, with its denominator. It defines the quantity as *"the fraction of those PRs whose own
**newly-added** tests contain zero FAIL_TO_PASS members."*

The instrument applies the PR's whole test-only patch, so it observes **two** units, and this
revision publishes both:

1. **Newly-added test ids** — `pre_patch_outcome == "absent"`, i.e. the id did not exist on
   the unpatched base. This is `precedents.md`'s quantity. The column is a *proxy* for
   "introduced by this PR": a renamed module or a changed `@parametrize` id also reads as
   absent (`METHOD.md` Known limits #6), which dilutes the bucket with pre-existing tests
   and therefore makes 10.5% an **upper** bound on the `PASS_TO_PASS` share of genuinely new
   tests.
2. **All PR-touched test ids** — every id in a file the patch touched, pre-existing ones
   included. This is the broader bar and the larger denominator; it is what §Results 2
   reports, and it is **not** comparable to prior work that isolates introduced tests.

Operationally, in SWE-bench's tokens (Jimenez et al., arXiv:2310.06770): *for a merged PR,
apply only the PR's own test-path files to the PR's base commit, run them there and on the
merge commit, and classify each test; a PR with an empty `FAIL_TO_PASS` set shipped no test
that could have distinguished base from candidate.* `NON_DISCRIMINATING` is the plain-English
gloss, `FAIL_TO_PASS` the operational term.

## Corpus and funnel

| stage | in | out | source |
|---|---:|---:|---|
| stage-1 PR search → repos with ≥1 trailer-carrying merged PR | — | 1,908 | `corpus/funnel-v2.csv` [A] |
| repo gate (≥10 stars, primary-Python, not fork/archived, pushed ≥2026-07-01) | 1,908 | 335 | same [A] |
| lockfile + pytest gate | 335 | 145 | same [A] |
| per-PR verification, **937 PRs examined** — dropped: **288 no test path (30.7%, [27.9%, 33.8%])**, 101 no verbatim trailer, 69 too large, 62 no source path — then ≥3 qualifying PRs per repo | 145 | **60 repos / 265 sample PRs** | same [A]; `corpus/candidates-v2.csv` [A] |
| base-snapshot buildability pilot | 60 | **25 repos** = 41.7%, [30.1%, 54.3%] | [P], [A] |
| sample PRs of those 25 repos | 265 | **107 PRs** | [A] |
| reached a verdict | 107 | **99** | [A], [R] |

**The question is conditioned on shipping a test.** 288 of the 937 PRs examined at stage 4
were dropped because they touched no test path at all — **30.7%, [27.9%, 33.8%]** [A], and the
single largest drop reason. A PR that ships no test cannot ship a non-discriminating one; this
study asks what the tests that *do* ship are worth, and the 30.7% is the population it says
nothing about.

**Where the funnel numbers come from, and the dedupe rule they depend on.** Every row of the
table above is recomputed by `analysis.py` from **`corpus/funnel-v2.csv`** — one row per repo
(`repo, stage, verdict, examined, qualifying, sample_prs`, plus a column per per-PR drop
reason), tracked in this repository. It is emitted by `corpus/scripts/funnel_csv.py` from
`widen.py`'s append-only checkpoint log `corpus/raw/repo_results.jsonl`, which is
**gitignored**
because it carries PR-author logins. That log is resumable, so a re-processed repo appears more
than once: **2,015 rows for 1,908 repos, and the dedupe rule is last row per repo.** Reading it
without that rule gives 981 examined and 302 `no_test_path` — the wrong funnel. `funnel_csv.py`
asserts the published totals (1,908 / 937 / 288 / 60 QUALIFIED / 265 sample PRs) and exits
non-zero if the dedupe stops reproducing them. `corpus/FUNNEL-v2.md`'s prose stage table is the
same numbers, hand-written; the CSV, not the prose, is the source.

Window and cost: PRs merged 2026-06-12 .. 2026-08-31; 4.3 h of container time, mean 145 s per
PR, max 4,576 s [A].

## Method, in one page

The full method, every cap and every known limit is `METHOD.md`. Per PR, ten `docker run`
steps, `--network none` during all five pytest phases: clone at `base.sha` and compute the
test-only patch (`git diff base merge -- <test paths>`); install at base from the lockfile
(`uv sync --frozen` / `poetry install` / pinned `requirements.txt`, never an unpinned
resolution); a **pre-patch base run** of the run-set files that already exist there, recorded
as `pre_patch_outcome` — a covariate for the reader, never a term in the verdict; apply the
patch and run the PR's test files on base **twice**; then `git checkout merge_commit_sha &&
git clean -xffdq` (the script exits 25 if `.venv` survives), reinstall, and run the same
files **twice**.

Reading a JUnit report is fail-closed, inherited from this venture's `Nemisis`: a timeout,
pytest exit 2/3/4/5, or an absent/oversized/unparseable report makes the **whole run** fatal
and stamps `UNRESOLVED` on the PR row **and every one of its test rows**; `error` beats
`failure` beats `skipped`; `skipped` is never a pass; duplicate ids poison to `error`; and an
id whose two observations of one side disagree is `flaky`, which no verdict cell resolves.

`error` at base counts as `FAIL` when the candidate passes — SWE-bench's log parsers do the
same. **It is not one mechanism, and §Results 2 splits it into three** (a new module arriving
with its test; a pre-existing passing test collaterally broken by an import the patch itself
adds; an assertion). The earlier claim that it is "the dominant shape for a PR that adds a
module and its test together" was **wrong** and is corrected there.

Per PR: `DISCRIMINATING` if ≥1 `FAIL_TO_PASS`; `NON_DISCRIMINATING` if ≥1 `PASS_TO_PASS`,
zero `FAIL_TO_PASS` **and zero unresolved rows**; otherwise `UNRESOLVED / partial evidence:
N`. The asymmetry is deliberate — one `FAIL_TO_PASS` is positive evidence, but zero is
evidence of non-discrimination only when nothing was left unobserved. **The strict denominator
is therefore outcome-conditioned**: a PR with ≥1 `FAIL_TO_PASS` enters it however many rows
went unobserved, while a PR with zero enters only if it has none. The strict..permissive pair
is consequently *not* a bound on the unresolved PRs, and the worst-case row below is.

## Results

### 1. Per-PR, the pre-registered quantity: newly-added test ids only

`precedents.md` §"The gap" defines the quantity over the PR's own newly-added tests. All 99
resolved PRs added at least one test id [A]:

| stratum | zero `FAIL_TO_PASS` among newly-added ids | Wilson 95% | Clopper-Pearson 95% |
|---|---|---|---|
| **all resolved PRs** | **1/99 = 1.0%** | **[0.2%, 5.5%]** | [0.0%, 5.5%] |
| same, with the **repository** as the unit | 1/25 = 4.0% | [0.7%, 19.5%] | [0.1%, 20.4%] |
| **`cc_type == "fix"` (`precedents.md` Objection 3's headline)** | **0/41 = 0.0%**, 15 repos | **[0.0%, 8.6%]** | [0.0%, 8.6%] |
| same, with the repository as the unit | 0/15 = 0.0% | [0.0%, 20.4%] | [0.0%, 21.8%] |

The single exception is `helpfulengineering/supply-graph-ai#422`: 3 newly-added ids, all
three `PASS_TO_PASS`, zero `FAIL_TO_PASS` [A].

Of the newly-added ids' discriminating evidence, **58.3% is an assertion failing at base**
(635 of 1,089) and 41.7% an import/collection error (454) [A]. Among the tests these PRs
actually wrote, assertion evidence is the majority — the opposite of the all-ids picture in
§Results 2, and the earlier draft of this write-up got that backwards.

### 2. Per-PR, the broader bar: all PR-touched test ids

[R]:

| PR verdict | n | share of attempted |
|---|---:|---:|
| `DISCRIMINATING` | 99 | 93% |
| `NON_DISCRIMINATING` | **0** | **0%** |
| `UNRESOLVED` | 8 | 7% |

[A], with intervals. **`n repos` is printed because `cc_type` and repository are confounded
here** — see §Threats 3:

| stratum | non-discriminating | n repos | Wilson 95% | Clopper-Pearson 95% |
|---|---|---:|---|---|
| unresolved share of attempted | 8/107 = 7.5% | 25 | [3.8%, 14.1%] | [3.3%, 14.2%] |
| **all resolved PRs (strict)** | **0/99 = 0.0%** | 25 | **[0.0%, 3.7%]** | [0.0%, 3.7%] |
| **same, with the repository as the unit (cluster-robust)** | **0/25 = 0.0%** | 25 | **[0.0%, 13.3%]** | [0.0%, 13.7%] |
| permissive (counts the 1 `partial evidence` PR) | 1/100 = 1.0% | 25 | [0.2%, 5.4%] | [0.0%, 5.4%] |
| **worst case: every unresolved PR non-discriminating** | **8/107 = 7.5%** | 25 | **[3.8%, 14.1%]** | [3.3%, 14.2%] |
| `cc_type == "fix"` | 0/41 = 0.0%, n=45 attempted | 15 | [0.0%, 8.6%] | [0.0%, 8.6%] |
| `base == merge^1` only | 0/77 = 0.0%, n=82 attempted | 24 | [0.0%, 4.8%] | [0.0%, 4.7%] |

**A deviation from the pre-registration, stated plainly.** `precedents.md` Objection 3 said
*"the headline should be restricted to `fix` PRs … a headline computed over all PR types will
be dismissed as measuring the wrong thing, correctly,"* and `METHOD.md` §Stratification
adopted it. The earlier draft led with the all-types number instead. That deviation **narrows
the published interval** ([0.0%, 3.7%] rather than [0.0%, 8.6%]) and the all-types denominator
is majority non-`fix` — 58 of 99 resolved PRs are `(none)` 28, `feat` 25, `perf` 2, `chore` 1,
`ci` 1, `refactor` 1 [A]. Both are now published side by side: the abstract's second
paragraph gives the all-types quantity (1/99, then the repo unit) and then the `fix`
stratum, so the `fix` number is published *beside* the all-types number, not ahead of
it. The deviation is disclosed here rather than reversed.

Every cell is 0. The permissive end is one PR, `SenolIsci/mykg#57`, and counting it as
non-discriminating is generous to the thesis: its 22 rows are 6 `PASS_TO_PASS`, 15
`FAIL_TO_FAIL` and 1 `PASS_TO_FAIL` — a **red candidate side**, not tests that agree
(`python3 -c "import csv,collections; rows=[r for r in csv.DictReader(open('results-tests.csv',newline='')) if (r['repo'],r['pr'])==('SenolIsci/mykg','57')]; print(collections.Counter((r['base_outcome'],r['candidate_outcome']) for r in rows))"`) [F].

Per-`cc_type` and per-`pr_trailer_kinds` breakdowns [R], with repo counts [A], are 0 in every
stratum: `fix` 0/41 (15 repos), `(none)` 0/28 (11), `feat` 0/25 (12), `perf` 0/2 (1), `chore`
0/1 (1), `ci` 0/1 (1), `refactor` 0/1 (1); `claude-code-gen;robot-gen` 0/85 (22 repos),
`claude-coauthor` 0/10 (4), `copilot` 0/4 (2).

**Read this as a null result against the study's own thesis.**

### 3. Per-test — what the evidence is actually made of

"≥1 `FAIL_TO_PASS`" is a weak per-PR bar. Two measurements bound how much of §2 that
explains, and **both are reported with a cluster bootstrap over the 25 repos, because the
row-level Wilson interval is not honest here** [A]:

| quantity | value | Wilson 95% (rows independent) | **cluster bootstrap 95% (25 repos, 20,000 draws, seed 0)** |
|---|---|---|---|
| PR-touched test ids | 13,564 (10,432 `PASS_TO_PASS`, 2,948 `FAIL_TO_PASS`, 184 `UNRESOLVED`) | — | — |
| **`PASS_TO_PASS` share of resolved ids** | **10,432/13,380 = 78.0%** | [77.3%, 78.7%] | **[71.0%, 87.2%]** |
| **`PASS_TO_PASS` share of the 1,217 resolved *newly-added* ids** | **128/1,217 = 10.5%** | [8.9%, 12.4%] | — |
| **`FAIL_TO_PASS` whose base outcome is `error`** | **2,181/2,948 = 74.0%** | [72.4%, 75.5%] | **[36.1%, 87.6%]** |
| `FAIL_TO_PASS` whose base outcome is `failed` (an assertion) | 767/2,948 = 26.0% | [24.5%, 27.6%] | — |

**Neither row-level figure is robust.** 2,181 error-at-base rows come from just **87
module-level collection events**, and the two largest — both in `Soju06/codex-lb`, PRs #1973
and #1974, the same module — are 1,475 of 2,948 = **50.0% of every `FAIL_TO_PASS` row in the
study**. Dropping those two PRs moves `PASS_TO_PASS` from 78.0% to **86.4%** and the
import-error share from 74.0% to **48.4%** — the latter is eight times the width of its Wilson
interval. Leave-one-repo-out: 76.1%..83.5% and 49.8%..77.2%. Per-repo `PASS_TO_PASS` shares
run 0.0% to 96.0%, unweighted mean 68.5%, sd 25.0 [A]. The unweighted per-PR figure is
**higher**, not lower: the median resolved PR is **83.7%** `PASS_TO_PASS`, and 16 of 99
resolved PRs have zero `PASS_TO_PASS` [A]. Test ids per PR run **0 .. 1,919 (median 42) over
all 107 PRs — 6 produced no test row at all** — or 1 .. 1,919 (median 43) over the 101 that
did; one repo contributes 4,954 of 13,564 ids (36.5%) [A].

**What `FAIL_TO_PASS` is made of, and the mechanism this write-up previously got wrong.**
Crosstabbing `base_outcome` against `pre_patch_outcome` over all 2,948 `FAIL_TO_PASS` rows
[A]:

| base outcome | pre-patch outcome | rows | share | mechanism |
|---|---|---:|---:|---|
| `error` | `passed` | 1,727 | **58.6%** | **collateral**: the id existed and *passed* on the unpatched base, and the PR's own test-only patch broke its module's import |
| `failed` | `absent` | 635 | 21.5% | a newly-added test failing an assertion at base — the strongest shape |
| `error` | `absent` | 454 | **15.4%** | the new-module-with-its-test shape |
| `failed` | `passed` | 131 | 4.4% | a pre-existing test the patch edited into failing at base |
| `failed` | `failed` | 1 | 0.0% | — |

The earlier draft glossed the 74.0% as "a PR that adds a module and a test for it in one
commit" and as "existence-of-code evidence". **That is right for 15.4% of the rows and wrong
for 58.6%.** The dominant shape is a pre-existing green test converted to an error by one
import line the patch added — visible in `logs/Soju06__codex-lb__pr1973/run-base.log`
(gitignored, present locally): `ImportError: cannot import name
'HTTP_BRIDGE_EVENTLESS_TIMEOUT_CODE' from 'app.core.errors'` turns 742 previously-passing ids
into `FAIL_TO_PASS` at once.

**This does not move the per-PR headline.** Re-scoring §Results 2 with every
(`error`, `passed`) collateral row deleted still gives **0/99** [A]; and §Results 1's
newly-added-ids quantity never counted them.

### 4. Per-PR under the stricter bar

Requiring at least one test that **failed an assertion** at base and passes on the candidate
(`base_outcome == "failed"`), over all PR-touched ids [A]:

| stratum | no assertion-level `FAIL_TO_PASS` | Wilson 95% | Clopper-Pearson 95% |
|---|---|---|---|
| all resolved PRs | **14/99 = 14.1%** | [8.6%, 22.3%] | [8.0%, 22.6%] |
| `cc_type == "fix"` | 6/41 = 14.6% | [6.9%, 28.4%] | [5.6%, 29.2%] |

All 14 have their entire `FAIL_TO_PASS` evidence in import/collection error, and 13 of the 14
added a new test file [A]. **But their evidence is not mostly the new file**: their
`FAIL_TO_PASS` rows are 736 (`error`, `passed`) collateral and 194 (`error`, `absent`)
new-module — **79.1% of it comes from pre-existing tests broken by the patch, not from the
test the PR wrote** [A]. That is a weaker claim than "the module-arrives-with-its-test
shape" and
it is the claim the data supports. A further 19 resolved PRs mix both kinds of `FAIL_TO_PASS`.

So the honest three-sentence result: **the pre-registered claim is refuted (1 of 99 PRs adds
only tests that already pass at base, [0.2%, 5.5%]); the broader claim is refuted too (0/99,
0/25 repos, [0.0%, 13.3%] cluster-robust); and the tests these PRs *touch* are mostly
pre-existing and mostly `PASS_TO_PASS` (78.0% pooled, [71.0%, 87.2%] cluster-robust), while
the tests they *add* are mostly not (10.5% `PASS_TO_PASS`).**

### 5. The eight unresolved PRs

`awk -F, 'NR==1||$10=="UNRESOLVED"' results-prs.csv` [F]:

| PR | reason | what it is |
|---|---|---|
| `open-reaction-database/ord-data#262` | `install_failed_base` | the base commit predates the repo's `pyproject.toml`; `uv sync --frozen` cannot run there. Buildability is per-commit, not per-repo. |
| `Ishannaik/agent-sweep#2`, `#3` | `install_failed_base` | same class: `uv.lock` does not exist at these PRs' bases — `error: Unable to find lockfile at 'uv.lock', but '--frozen' was provided`, on all three rungs of the install ladder (`logs/Ishannaik__agent-sweep__pr2/install-base.log`, gitignored). |
| `AvaCodeSolutions/django-email-learning#760` | `no runnable test file` | the PR's only test-path files were `conftest.py` / fixtures — applied, never run. |
| `SenolIsci/mykg#59` | `base_run: junit xml unparseable` | fail-closed parse; the base's state is unknown, so no verdict is claimed. |
| `SenolIsci/mykg#57` | `partial evidence: 16 unresolved rows` | 6 `PASS_TO_PASS`, 15 `FAIL_TO_FAIL`, 1 `PASS_TO_FAIL` — a red candidate side. |
| `gadievron/raptor#920` | `base_run: timeout` | the 15-minute per-run cap; the pilot collected 35,096 tests in this repo (`grep '^gadievron/raptor,' ../pilot/results.csv`). |
| `Datus-ai/Datus-agent#1354` | `base_run: timeout` | same cap; 4,576 s of container time before it was cut. |

Six of the eight are environment or harness limits; two (`#760`, `#57`) are properties of the
PR. **Every failure path writes a PR row** — no PR is a silent drop. That is not true of
`results-tests.csv`: 6 PRs produced zero test rows there [A].

## Threats to validity, and the direction of each

**1. Selection: who this speaks for — and the bias direction we can no longer claim.** The
corpus is ≥10 stars, GitHub-primary-language Python, non-fork, non-archived, pushed since
2026-07-01, with a top-level lockfile and pytest evidence, holding ≥3 merged PRs that carry a
**verbatim** agent trailer, touch ≥1 test path **and** ≥1 non-test source file, and change
≤2,000 lines — 60 repos, 26 of them 10–49 stars. The study runs only the 25 whose base builds
(41.7% of 60, [30.1%, 54.3%] [P][A]).

`precedents.md` Objection 2 required us to *"report covariates that are observable for unbuilt
repos too … and show whether the built and unbuilt sets differ on them."* Done, and it does
**not** support the "well-maintained tail" story earlier drafts of this write-up repeated [A]:

| | n | stars (min / median / max) | `agent_pr_count_90d` median | `uv.lock` |
|---|---:|---|---:|---:|
| built | 25 | 10 / **64** / 59,516 | 6 | 22/25 |
| unbuilt | 35 | 10 / **351** / 68,115 | 6 | 28/35 |

The built set is the **less** popular one. On agent PR volume the two are identical and the
lock-kind mix is near-identical. So the buildability filter selects small, single-lockfile,
recently-active projects — not, on any covariate we can observe, better-maintained ones.
**The claim that the selection biases the result toward 0, and that 0/99 is therefore a
floor, is withdrawn: no observable covariate supports it, and the one that differs runs the
other way.** What remains true is narrower and still worth stating: nothing here transfers to
repos without lockfiles or pytest, under 10 stars, or with unbuildable bases, and the
direction of the residual bias is **unknown**.

**2. Agent coverage, and no non-agent control arm.** 92 of 107 PRs are
`claude-code-gen;robot-gen`, 11 `claude-coauthor`, 4 `copilot` [R]; **zero** Codex, Devin,
Cursor, aider, openhands or sweep PRs survived. Per-agent comparison is impossible here.
**Nor is there a human-PR control arm**, so no sentence in this study may claim that anything
measured here is *specific to agents* — it is a measurement of agent PRs, not a comparison.
The nearest published control is arXiv:2601.21194 (fetched 2026-08-31), which compares 6,582
human-agent PRs to 3,122 human PRs on the same AIDev frame and finds test-inclusion
likelihood comparable (42.9% vs 40.0%) and "negligible effect sizes" on test-smell quality.

**3. Clustering, and `cc_type`–repository confounding.** 107 PRs sit inside 25 repos, 3–5 per
repo (median 5) [A]. Every row-level Wilson and Clopper-Pearson interval in this file assumes
independence and is therefore **narrower than the truth**; the cluster bootstrap and the
repo-as-unit rows are the honest ends and are now published beside every headline. Separately,
`cc_type` is a **repo-level convention**: the 41 resolved `fix` PRs come from 15 repos, and
repos that do not use conventional-commit titles contribute zero `fix` PRs by construction
(`fix` appears in 16 of 25 repos (15 with a resolved fix PR), `(none)` in 11, `feat` in 12) [A]. The `fix` stratum
therefore cannot be read as a random sample of fix-intent PRs; it is partly a stratification
of repositories, and its honest interval is the repo-unit one, [0.0%, 20.4%].

**4. Test selection is by path, not by import graph.** The strict rule (a `tests/` path
segment, or a basename matching `test_*.py` / `*_test.py` / `conftest.py`) is the corpus's
own; it misses `test/`, Django `tests.py`, `spec_*.py`, `check_*.py`, `testing/`, tests under
`src/`, and doctests. A miss means a possible `FAIL_TO_PASS` is never observed, pushing a PR
toward `NON_DISCRIMINATING` — toward the thesis. The earlier draft's bound was "0 of 0
`NON_DISCRIMINATING` PRs have unmatched files", which is **vacuous whenever the headline is
0**; it is withdrawn. The real exposure: **3 of 107 PRs have ≥1 file the wider auditor rule
calls a test and the strict rule does not, and one of them — `taoq-ai/ziran#403` — is among
the 14 stricter-bar PRs in §Results 4** [A], where a missed test file would have *removed* an
assertion-level `FAIL_TO_PASS` and so inflated the 14.

**5. Flakiness — and the level at which this design has no power.** Each side is observed
twice and disagreement makes the id `flaky`. Observed: **3 flaky observations across 27,128
side-observations, all in one module** [A]. The design replicates *ids*, but the failure mode
that drives this dataset is the **collection event**: 87 module-level import decisions, each
replicated to every id in its module, and the two runs share one container, one ordering and
one environment back to back. One unstable import would move up to 742 rows in a single
stroke and would be observed twice identically, never marked flaky. **Instability at
collection time is not bounded by this design at all**; "3 of 27,128" is a floor on id-level
instability and nothing more. Direction, for what it bounds: an undetected flaky test that
fails twice at base and passes twice on the candidate scores `FAIL_TO_PASS`, pushing the
per-PR headline *toward 0*.

**6. The counterfactual is `base.sha`, not `merge_commit_sha^1` — and this threat is
untested, not cleared.** Where they differ, an intervening commit's effect is attributed to
this PR. The per-PR sensitivity check (0/77 restricted to `base_is_merge_first_parent == 1`)
**has no power**: with zero in both cells, no divergence could ever change it. The per-test
rate does move, and it is uninterpretable for the reason in §Results 3 — `FAIL_TO_PASS` rate
1,216/7,457 = 16.3% where base == merge^1 versus 1,732/5,923 = 29.2% where it does not, which
looks like the predicted inflation; but both `Soju06/codex-lb` PRs carry
`base_is_merge_first_parent=0`, and dropping them **reverses the sign** to 16.3% vs
242/3,263 = 7.4% [A]. Read this threat as untested.

**7. The trailer is an unvalidated proxy, and review-time repair is a confound.** A verbatim
trailer says an agent was involved; it does not establish that the agent wrote the test code
that landed. A human reviewer may have repaired or replaced the tests between the PR opening
and the merge commit — the study observes only the merged state, so **"agent-authored tests"
should everywhere be read as "tests on an agent-trailered merged PR."** Direction: review-time
repair would push the tests toward discriminating, i.e. toward the 0 this study reports. No
validation of the trailer regexes against ground truth was run; arXiv:2606.24429 (fetched
2026-08-31) is a validated multi-method agent census and is the instrument that would close it.

**8. Test-infrastructure changes.** `conftest.py` and `tests/fixtures/**` travel with the
patch and set `infra_changed=1` (5 of 107 PRs [A]); pytest configuration in `pyproject.toml`
or a `Makefile` does not. Read `infra_changed=1` rows as lower-confidence.

**9. Not computable from this dataset.** (i) **Self-merged vs independently-merged**:
`candidates-v2.csv` has no `merged_by`/`author` column and this venture's brief forbids author
identities in a tracked file, so the stratification is absent by construction — a real gap.
(ii) Repo-wide regressions the PR causes outside its own test files. (iii) Doctests.
(iv) Whether a `PASS_TO_PASS` test is a *good* regression test; SWE-bench treats
`PASS_TO_PASS` as desirable and this study does not contradict that.

**10. Platform.** linux/arm64, `--memory 4g`, `--jobs 3`: packages without an aarch64 wheel
build from sdist and can fail, so `install_failed_*` is biased upward against an x86-64
runner — inflating the 7.5% unresolved rate, not the headline.

## Pre-registration status, and conflicts of interest

**"Pre-registered" here means specified in writing before the run, in this repository — not
lodged with a registry.** `research/precedents.md` (2026-08-30) states the quantity and the
three objections; `METHOD.md` states the stratification and the verdict table; both predate
`results-prs.csv`. Both live in the same git repository as the results, with no external
timestamp, and `METHOD.md`'s mtime sits nine minutes after `smoke.log`'s and cites it. So this
is **self-attestation**, and a reader who does not trust the author should treat it as such.
**Two deviations from it matter, and both are recorded.**

*(i) The `fix`-only headline.* `precedents.md` Objection 3 asked for the headline restricted
to `fix` PRs; this write-up publishes the all-types number beside it and does not lead with
`fix`. §Results 2 states the cause, the direction (it tightens the published interval) and the
majority-non-`fix` denominator.

*(ii) The green-base admission criterion.* `precedents.md` Objection 1 asked us to *"require
the base suite to be **green before the test patch is applied** as an admission criterion (a
base that is already red is unresolved, not a result)."* It was **recorded rather than
enforced**: the per-test `pre_patch_outcome` column carries the signal and no row was ever
discarded for it (`METHOD.md` Departures #4 and Instrument defects #3 say so; the write-up's
pre-registration section previously did not). The exposure, and the check that bounds it:

```sh
python3 -c "import csv,collections as C; T=list(csv.DictReader(open('results-tests.csv',newline=''))); \
print(C.Counter(r['pre_patch_outcome'] for r in T)); \
b=[r for r in T if r['pre_patch_outcome'] in ('failed','skipped')]; \
print(C.Counter(r['verdict'] for r in b)); \
f=C.Counter((r['repo'],r['pr']) for r in T if r['verdict']=='FAIL_TO_PASS'); \
d=C.Counter((r['repo'],r['pr']) for r in b if r['verdict']=='FAIL_TO_PASS'); \
print([k for k in d if f[k]==d[k]])"
```

[F] → `passed` 12,165, `absent` 1,248, `skipped` 136, `failed` 15 of 13,564 rows; of the 151
non-green ones, **150 are `UNRESOLVED` anyway and exactly one is a `FAIL_TO_PASS`**; and no PR
loses all of its `FAIL_TO_PASS` evidence when every non-green-base row is dropped (`[]`), so no
verdict in §Results 1–4 rests on a red or skipped base. **Direction:** a red base repaired by
something other than the PR scores `FAIL_TO_PASS`, which pushes the headline *toward* the 0
reported here — enforcing the criterion could only have moved the result away from this study's
own thesis. That is an argument about the size of the deviation, not a reason it was not one.

**Conflicts of interest.** The author maintains two commercial concepts in this same public
repository that would benefit from a *positive* finding here:
`ideas/r2-ai-pr-verification-gate.md` (a hosted PR-verification gate) and
`ideas/r2-agent-guardrails-per-repo.md`. **The result reported is against that interest** —
the study's own thesis is refuted — which is worth stating precisely because the incentive
ran the other way. No funding, no sponsorship, no vendor relationship. Built and written with
heavy AI assistance; the method, the instrument and every number are the author's to defend.

## Relation to prior work

All claims cite `research/precedents.md`, which records the fetch date and exact quoted text,
or an arXiv id fetched via `export.arxiv.org` on 2026-08-31 (HTTP 200) and marked **[new]**.

- **SWE-bench** (arXiv:2310.06770) performs this exact execution as a *construction filter* —
  93,139 PRs crawled → 11,407 → 2,294 instances, 79.9% of post-conversion candidates removed
  at execution validation — and never separates "did not discriminate" from "did not build".
  This study takes its vocabulary wholesale and publishes the discard reasons (§Results 5).
- **BSG-VA** (arXiv:2607.28871) is the method this study transfers: the same base/candidate
  replay of a test-only patch, reporting **46.0% of positive comparable events carry no
  bug-discriminating information** — on 110 benchmark tasks and 643 agent rollouts, not merged
  PRs. Our 1/99 is not a contradiction: in a benchmark rollout the buggy base *contains* the
  code under test, so a non-discriminating test can still run there; in a merged real-world PR
  the base frequently does not contain the code at all. Different population, different
  mechanism, different number. BSG-VA is also a three-arm experiment with a prespecified
  effect size over 3,730 events; this study is one arm at n=99 with zero events.
- **jittest** (v0.3.4, an independent single-maintainer OSS project) is the nearest *tooling*
  antecedent and the property table in `precedents.md` files it wrongly. **jittest already
  performs this base-replay on real merged pull requests** — a frozen cohort of 83 historical
  Flask / requests / youtube-dl PRs — and already ships a published verdict literally named
  `non_discriminating`, alongside `inconclusive` and its denominator (83/83 attempted, 24/83
  definitive, 59/83 signed refusals). It holds properties (a), (c) and most of (d). **The
  property it lacks is (b): its PRs are human-authored.** This study's delta over jittest is
  the agent-authored population and the rate itself, not the method. `precedents.md` §"The
  gap"'s property-(a) row lists jittest under "Who lacks it"; that cell is wrong and is
  recorded as objection B3 below.
- **"All Smoke, No Alarm"** (arXiv:2606.18168) reports **80.2% of 86,156 agent test patches
  have weak or no explicit oracle signals**, statically, with zero execution. This study does
  not contradict it and the two are compatible: oracle strength and base-discrimination are
  different axes. **They also have different denominators** — 80.2% is over test *patches*,
  our 78.0% is over *all test ids in touched files* and our 10.5% is over *newly-added ids*.
  The number to place beside 80.2% is 10.5%, not 78.0%.
- **"Test Coverage Analysis of Agentic Pull Requests"** (arXiv:2607.18057) has the real-world
  corpus (4,882 AIDev PRs; 34 of 55 Python repos buildable, 61.8%) but measures diff coverage
  at head — 27.0%; 64.8% of Python PRs have no changed line executed by any existing test —
  and never runs the PR's tests on base. It isolates *introduced* tests by declaration diff;
  §Results 1's `pre_patch_outcome == absent` is a coarser proxy for the same thing.
- **AIDev** (arXiv:2507.15003) is the trailer taxonomy and **the sampling frame this study
  should have used and did not**; §Threats 2 and 3 are the cost of that choice, and it would
  fix agent coverage, the 1,000-result search cap and §Threats 9(i) in one move.
- **[new] "Human-Agent versus Human Pull Requests: A Testing-Focused Characterization and
  Comparison"** (arXiv:2601.21194, 2026-01-29). 6,582 human-agent and 3,122 human PRs from
  AIDev; test-inclusion likelihood 42.9% vs 40.0%; test smells statistically different in
  places but with negligible effect sizes; makes its own "first characterization" claim on
  human-agent testing practice. **Holds (a) and (b); lacks (c) and (d) — no execution.** It is
  the nearest thing to the control arm this study lacks, and its 42.9% is the sourced figure
  that replaces the "most agent PRs add tests" line an earlier draft of the arXiv abstract
  carried.
- **[new] Change2Task** (arXiv:2607.28591, 2026-07-30) converts merged PRs into verified tasks
  on healthy revisions and validates the base→task→restored lifecycle, publishing a yield with
  a denominator: 1,130 eligible source changes → **79.6%** verified construction success.
  **Holds (a) and (c) and publishes a denominator; lacks (b)** — the PRs are repository
  history, not agent-authored — **and (d)**: the rate published is construction success, not
  the pass-on-base rate of a PR's own tests. Same blind spot as SWE-bench, at a larger scale.
- **[new] SWE-Universe** (arXiv:2602.02361, 2026-02-02) builds 807,693 verifiable environments
  from GitHub PRs and is explicitly about "low production yield, weak verifiers". Same
  disposition as Change2Task: construction yield, not discrimination rate; lacks (b) and (d).
- **[new] "Beyond Bug Fixes"** (arXiv:2601.20109, 2026-01-27) runs a **differential base-vs-
  merge analysis on 1,210 merged agent bug-fix PRs from AIDev** — the closest population and
  the closest differential design in the literature — but with SonarQube, statically. Holds
  (a) and (b); lacks (c) and (d).
- **[new] Also triaged and disposed of, all lacking (c)+(d)**: arXiv:2607.21832 (descriptive
  characterization of agentic PRs on AIDev), arXiv:2606.13468 (qualitative study of 306
  *rejected* agent fix PRs; 46.41% of agent fixes rejected).

**Novelty claim, hedged to what the search supports.** No work we found holds all four of:
(a) real merged PRs in the wild, (b) agent-authored by trailer, (c) the PR's own tests
executed on the base commit, (d) the pass-on-base rate reported as the result with its
denominator. jittest holds (a), (c) and most of (d); BSG-VA holds (b), (c), (d); Change2Task
holds (a), (c) and a denominator. **The intersection is still empty and the gap is one
property wide in two directions, not four.** The evidence behind the claim, stated as its
limits: the arXiv API searches metadata only (`all:"FAIL_TO_PASS"` → 0 results though
SWE-bench's whole family uses the token), so absence searches there are weak; on 2026-08-31
the broad query returned 90 hits, **all 90 titles were read** (10 were already in
`precedents.md`), and the six most plausible abstracts were fetched and disposed of above;
OpenAlex (`api.openalex.org`, `robots.txt` = `Allow: /`, HTTP 200) was queried three ways to
reach non-arXiv venues and surfaced no work with the four properties; **Semantic Scholar
returned 429 again on 2026-08-31, so IEEE/ACM/journal-only work remains under-searched.** The
searches are re-run before publication (`DECISION.md` §3, 2026-10-03).

## Reproduction

```sh
cd ventures/c-measurement/study
python3 runner.py --selfcheck        # parser + verdict asserts; no docker, no network
python3 analysis.py --selfcheck      # the interval maths, against closed forms
python3 analysis.py                  # every number in this file, incl. == RED-TEAM PASS ==
python3 runner.py --summary --md     # the verdict tables above
```

To re-run the measurement itself (docker + a read-only `gh` login; ~4.3 h of container time
at `--jobs 3`):

```sh
./run.sh                             # 107 sample PRs, 25 repos; resumable, skips finished rows
./run.sh --smoke 2                   # the two buildable repos with the smallest suites
JOBS=2 ./run.sh                      # fewer containers at once
```

`results-prs.csv` is both the output and the resume key; both CSVs are appended under an
`flock` with an `fsync` per PR. `DATASET-CARD.md` documents every column.

**What would change the answer.** (i) The same instrument over AIDev's frame — more agents,
more repos, no 1,000-result cap, and a human-PR control arm. (ii) Dropping the buildability
filter and paying the unresolved rate jittest paid, which tests §Threats 1 directly, now that
its direction is unknown. (iii) An `is_new_test` column from a declaration diff rather than
the `pre_patch_outcome == absent` proxy. (iv) One side re-run in a fresh container, to bound
collection-time instability (§Threats 5). (v) `merged_by` in the corpus. None is done here.

## Red-team pass (2026-08-31)

Three independent red teams reviewed the pre-revision write-up: **A** on statistics and
method, **B** on novelty and prior work, **C** on the defence, hygiene and disclosure. Their
objections are listed verbatim below with a disposition. Every FIXED item's number is printed
by `python3 analysis.py`'s `== RED-TEAM PASS ==` block unless another command is given.

### A — statistics and method

| # | Objection (verbatim claim) | Disposition |
|---|---|---|
| A1 | *"The two per-test headline numbers (78.0% PASS_TO_PASS, 74.0% import-error) and their Wilson/Clopper-Pearson intervals treat 13,380 test rows as independent draws. They are not: the FAIL_TO_PASS population is generated by a small number of module-level collection events, and two PRs of one repo determine half of it. Dropping those two PRs moves 74.0% to 48.4% — 8x the published interval width."* | **FIXED.** §Results 3 now publishes a 25-repo cluster bootstrap beside both figures ([71.0%, 87.2%] and [36.1%, 87.6%]), the leave-one-repo-out ranges, the drop-two-PRs values, the 87-collection-event count and the per-repo spread. The unweighted per-PR median (83.7%) is stated in the same paragraph. |
| A2 | *"The published mechanism for the 74.0% import-error figure is wrong for the majority of those rows … only 15.4% of FAIL_TO_PASS rows are error-at-base on a test id that did not exist at the base; 58.6% are ids that existed and PASSED at the unpatched base and were converted to `error` by applying the PR's own test-only patch."* | **FIXED.** The `base_outcome` × `pre_patch_outcome` crosstab is now a table in §Results 3; the mechanism sentence in §Method and the "module-arrives-with-its-test" sentence in §Results 4 are rewritten (the 14 PRs' evidence is 736 collateral / 194 new-module). The same wrong sentence in `METHOD.md` is corrected. Re-scoring §Results 2 without the collateral rows still gives 0/99, and that is published. |
| A3 | *"The headline was pre-registered as the `fix`-only stratum and the write-up silently promotes the all-types number instead, which halves the published interval."* | **FIXED as a disclosure, not as a reordering.** The `fix` stratum (0/41, [0.0%, 8.6%]) is now published in the abstract beside the all-types number — the abstract's second paragraph still gives all-types first — and in §Results 1 and §Results 2 as its own row; §Results 2 carries an explicit deviation note naming the cause, the direction (it tightens the interval, [0.0%, 3.7%] against [0.0%, 8.6%]) and the majority-non-`fix` denominator (58 of 99). The pre-registered ordering was **not** restored. |
| A4 | *"`cc_type` is a repo-level convention, not a PR-intent partition … the 45-PR fix stratum is 16 clusters, not 45 independent observations."* | **FIXED.** Repo counts are printed for every stratum in §Results 2; the `fix` stratum's repo-unit interval (0/15, [0.0%, 20.4%]) is published in §Results 1 and 2; §Threats 3 states the confounding plainly. |
| A5 | *"The strict/permissive interval does not bracket the unresolved PRs, because the denominator is conditioned on the outcome … The published bracket is 0/99 .. 1/100; the honest one is 0/99 .. 8/107."* | **FIXED.** §Results 2 adds a worst-case row (8/107 = 7.5%, [3.8%, 14.1%]) and §Method states the outcome-conditioning in one clause. |
| A6 | *"The `base_is_merge_first_parent` sensitivity check has no power to detect the bias it exists to test, and the per-test signal that does exist is entirely an artefact of the same two codex-lb PRs."* | **FIXED.** §Threats 6 now says the per-PR check is powerless at 0/99, publishes the per-test rates by flag (16.3% vs 29.2%), shows that dropping the two PRs reverses the sign (16.3% vs 7.4%), and labels the threat **untested, not cleared**. |
| A7 | *"The two-runs-per-side flakiness design cannot bound the failure mode that actually drives this dataset … '3 flaky observations across 27,128 side-observations' is then quoted as though it bounded instability."* | **FIXED.** §Threats 5 reports the flake at module level (3 rows in 1 module) against 87 collection events and states that collection-time instability is **not bounded by this design at all**. The word "bounds" is removed from `DATASET-CARD.md`. |
| A8 | *"The published upper bound on path-based test selection is vacuous — a share with an empty denominator — and its direction argument does not cover §Results 3."* | **FIXED.** The 0-of-0 ratio is withdrawn. §Threats 4 leads with 3 of 107 and names `taoq-ai/ziran#403` as the one that *is* among the 14 stricter-bar PRs, with the inflation direction stated. |
| A9 | *"'13,564 tests' and 'PR-touched test' overstate what a row is: the unit is a JUnit `<testcase>` id including @parametrize expansions … 'the tests these PRs touch' includes pre-existing tests the PR never wrote."* | **FIXED.** "test ids (parametrize-expanded)" at first use in the abstract and in `SUMMARY.md`; §Results 1 is a new section over newly-added ids only (1,089 F2P / 128 P2P / 31 unresolved of 1,248), and §Results 3 carries the 10.5% row. |
| A10 | *"'Test rows per PR run 1 .. 1,919' silently excludes six PRs that produced zero rows, and 'every failure path writes a row' is true only of results-prs.csv."* | **FIXED.** §Results 3 states 0 .. 1,919 (median 42) over all 107 and 1 .. 1,919 (median 43) over the 101 that produced a row; §Results 5 says "every failure path writes a **PR** row" and names the 6. |

### B — novelty and prior work

| # | Objection (verbatim claim) | Disposition |
|---|---|---|
| B1 | *"The 'first' claim rests on a falsifier search that was run but never triaged. Re-running the write-up's own novelty search #2 today returns 90 arXiv ids; 80 of them appear nowhere in research/precedents.md … The largest hole precedents.md itself names — Semantic Scholar, i.e. every non-arXiv venue — is still 429 and still unclosed today."* | **FIXED in part, ACKNOWLEDGED in part.** Re-run 2026-08-31: `curl … search_query=all:"coding agent" AND all:"pull requests"&max_results=100` → HTTP 200, `totalResults` 90; 10 of the 90 ids appear in `precedents.md`, 80 did not. **All 90 titles were read**, the six most plausible abstracts fetched, and all six disposed of by property in §Relation to prior work — three of them (2601.21194, 2607.28591, 2602.02361) are the ones this objection named, and all three are now cited. The non-arXiv hole is **narrowed, not closed**: OpenAlex (`robots.txt` = `Allow: /`, HTTP 200) answered three queries and surfaced no four-property work; Semantic Scholar returned 429 again. The claim is downgraded throughout to *"no work we found holds all four,"* with the search's limits stated inline. |
| B2 | *"The study is dominated by design and says so itself … the two findings that carry information are the ones nearest to prior work at 1/100th to 1/6500th of prior sample sizes, on one agent family."* | **ACKNOWLEDGED**, and partly acted on. The abstract now opens with the method transfer ("BSG-VA's replay applied to merged real-world agent PRs") rather than a novelty claim, and leads with the quantities that carry information. AIDev remains named as the frame that should have been used (§Threats 2, §Relation to prior work, §What would change the answer). Re-running over AIDev is out of scope for a revision and is the first item under "What would change the answer". |
| B3 | *"jittest is mis-assigned in the four-property table the novelty claim depends on … jittest already performs the base-replay on real merged PRs and already ships a verdict literally named `non_discriminating`; the only property it lacks is (b) agent-authored."* | **FIXED here, and recorded as a defect in `precedents.md`.** §Relation to prior work now states plainly that jittest runs this replay on human-authored merged PRs, publishes a `non_discriminating` verdict and its denominator, and that this study's delta is the population plus the rate. The novelty claim is restated as "one property wide in two directions". `research/precedents.md` §"The gap"'s property-(a) row still files jittest under "Who lacks it"; that cell is wrong and the correction belongs to that file's owner. |
| B4 | *"The study does not measure the quantity precedents.md says nobody has published. The gap is defined over the PR's newly-added tests; the study runs every test in every PR-touched test file, including pre-existing tests the agent never wrote."* | **FIXED.** §Results 1 is now the pre-registered quantity computed over newly-added ids: **1/99 = 1.0%, [0.2%, 5.5%]**; `fix` 0/41; repo-unit 1/25. §Results 3 adds the 10.5% `PASS_TO_PASS` share over newly-added ids beside the 78.0% over all touched ids, and §"The question, and its two units" states which is which and that only 10.5% belongs beside 2606.18168's 80.2%. The `pre_patch_outcome == absent` proxy and its direction are stated. |
| B5 | *"The arXiv abstract draft in outreach/queue.md drops the write-up's novelty hedge and states a fact contradicted by the study's own cited prior work"* (*"most of those PRs add tests"*). | **FIXED** in `outreach/queue.md`: the sentence is replaced with the sourced figures (49.6% from 2607.18057; 42.9% from 2601.21194) and the write-up's hedge is carried into the abstract verbatim. |
| B6 | *"The novelty is a four-clause conjunction and the write-up leads with it instead of with the antecedent, against precedents.md's own instruction"* (*"Track M is BSG-VA-in-the-wild and should say so in the first paragraph"*). | **FIXED.** The abstract's first sentence is now the method transfer; the four properties appear as the delta, hedged, in the last paragraph. |

### C — the defence, hygiene and disclosure

| # | Objection (verbatim claim) | Disposition |
|---|---|---|
| C1 | *"The study's central defense — that the buildability filter selects the 'well-maintained tail' and therefore biases the result toward 0, making 0/99 a floor — is contradicted by the study's own corpus data … Built repos are the LESS popular set: median 64 stars vs 351."* | **FIXED.** §Threats 1 publishes the built-vs-unbuilt covariate table `precedents.md` Objection 2 required (stars 64 vs 351, `agent_pr_count_90d` 6 vs 6, `uv.lock` 22/25 vs 28/35) and **withdraws the bias-direction claim** in the write-up, `SUMMARY.md`, the HN comment, both Bluesky posts and the newsletter blurb. The residual bias direction is now stated as unknown. |
| C2 | *"The 78.0% PASS_TO_PASS figure that all four launch drafts lead with as 'the other direction' is 98.8% composed of test ids that already existed and passed at the unpatched base … Restricted to the PR's own newly-added tests the number is 10.5% (128/1,217) and appears nowhere in any file."* | **FIXED.** 128/1,217 = 10.5%, [8.9%, 12.4%] is now in the abstract, §Results 3, `SUMMARY.md` and every launch draft, beside the 78.0% and labelled by unit. The objection's 98.8% reproduces exactly on its own denominator — 10,304 of the 10,432 `PASS_TO_PASS` rows already passed on the *unpatched* base — and on all resolved ids the pre-existing share is 90.9% [A]. Both are published. |
| C3 | *"There is no non-agent control arm, yet the HN title and Bluesky 1/6 assert agent-specific facts."* | **FIXED.** §Threats 2 states that no sentence may claim agent-specificity and cites arXiv:2601.21194 as the nearest published control. The HN title and Bluesky 1/6 are rewritten to describe the population measured rather than a property of agents. |
| C4 | *"The CI ignores repo clustering the authors themselves admit invalidates it (0/25 repos gives [0,13.3%], not [0,3.7%])."* | **FIXED.** 0/25 = [0.0%, 13.3%] is published in the abstract and as its own row in §Results 2; §Threats 3 names the row-level intervals as the optimistic end. |
| C5 | *"The trailer proxy is never validated and review-time test repair is an unnamed confound."* | **FIXED as an acknowledgement.** New §Threats 7 states that the trailer establishes agent involvement, not test authorship; that review-time repair is unseparable in the merged state; that its direction pushes toward the reported 0; and names arXiv:2606.24429 as the validation instrument not used. "Agent-authored tests" is read as "tests on an agent-trailered merged PR" throughout. |
| C6 | *"The corpus drops 288 of 937 examined agent PRs (30.7%) for shipping no test file at all, which is precisely the population the title's question implies."* | **FIXED.** The funnel table carries the 288/937 = 30.7% figure with its command, and a paragraph under it states that the whole question is conditioned on the PR shipping a test. |
| C7 | *"There is no conflict-of-interest disclosure although ideas/r2-ai-pr-verification-gate.md and ideas/r2-agent-guardrails-per-repo.md sit in the same public repo."* | **FIXED.** New §"Pre-registration status, and conflicts of interest" names both files, states the incentive ran toward a positive finding, and notes the reported result runs against it. Also added to `SUMMARY.md`. |
| C8 | *"'pre-registered' is self-attested inside a two-hour window with no external timestamp, with METHOD.md written nine minutes after smoke.log and citing it."* | **FIXED.** The same new section defines what "pre-registered" means here — specified in writing before the run, in this repository, with no registry and no external timestamp — and names the nine-minute gap. |
| C9 | *"The only exposure is WRITEUP.md lines 120-123 and 185-189, which name personal GitHub account handles with quality judgments attached."* | **REJECTED, with evidence.** The governing brief permits repository names and PR numbers explicitly and forbids author, committer and handle identities; `owner/repo#N` is a repository identifier, is required to make the result checkable, and is already present in the published CSVs. No author, login, email, committer, PR title or PR body appears in any tracked file: `grep -ciE 'author\|login\|email\|committer' results-prs.csv results-tests.csv` → 24 and 322, every one enumerated and benign in `DATASET-CARD.md`; `grep -c '@' results-tests.csv` → 0. The descriptions attached to those repos ("a red candidate side", "the base commit predates the repo's `pyproject.toml`") are measurement outcomes, not judgments of a person. |

**What this pass did not fix.** B2 (the AIDev frame) and the Semantic Scholar half of B1 are
acknowledged, not closed: both need a new run, not a new sentence. §Threats 5's
collection-time instability needs one side re-run in a fresh container. §Threats 9(i)'s
`merged_by` stratification stays absent by construction.
