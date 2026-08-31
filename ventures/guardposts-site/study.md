---
layout: default
title: The study
---

[home](index.md) · [agent-plan-lint](packages/agent-plan-lint.md) · [egresswall](packages/egresswall.md) · [guardrail-checkup](packages/guardrail-checkup.md) · [compare](compare.md) · [about](about.md)

# One page: do merged agent PRs ship tests that could have caught anything?

**2026-08-31 · 107 merged, agent-trailered pull requests · 25 public Python repositories ·
run complete · revised after a three-team red-team pass.** Full study:
[`WRITEUP.md`](https://github.com/Alex-lop/venture/blob/main/ventures/c-measurement/study/WRITEUP.md)
(its §Red-team pass lists every objection and its disposition). Method:
[`METHOD.md`](https://github.com/Alex-lop/venture/blob/main/ventures/c-measurement/study/METHOD.md).
Data:
[`DATASET-CARD.md`](https://github.com/Alex-lop/venture/blob/main/ventures/c-measurement/study/DATASET-CARD.md).

## The number

This is **BSG-VA's base/candidate replay (arXiv:2607.28871) applied to merged real-world
agent PRs.** We took each PR's own test files, applied them to the PR's **base** commit, ran
them twice there and twice on the merge commit, and classified every **test id**
(parametrize-expanded) in SWE-bench's vocabulary.

`research/precedents.md` §"The gap" defines the quantity over the PR's own **newly-added**
tests. Both units are published and the pre-registered *unit* leads; the `fix`-only
restriction `precedents.md` Objection 3 asked for the headline is published **beside** the
all-types number, not ahead of it (`WRITEUP.md` §Results 2 states that deviation).

| | value | 95% interval |
|---|---|---|
| PRs that reached a verdict | 99 of 107 (8 unresolved, 7.5%) | Wilson [3.8%, 14.1%] on the unresolved share |
| **PRs whose *newly-added* tests all passed on base** (the pre-registered quantity) | **1 of 99 = 1.0%** | **Wilson [0.2%, 5.5%]** |
| same, `fix`-titled PRs only (`precedents.md` Objection 3's headline; 15 repos) | 0 of 41 = 0.0% | [0.0%, 8.6%]; repo as unit [0.0%, 20.4%] |
| PRs whose *entire* test-file set passed on base (the broader bar) | 0 of 99 = 0.0% | [0.0%, 3.7%] |
| **same, with the repository as the unit (cluster-robust)** | **0 of 25 = 0.0%** | **[0.0%, 13.3%]** |
| worst case: every unresolved PR non-discriminating | 8 of 107 = 7.5% | [3.8%, 14.1%] |
| **`PASS_TO_PASS` share of the 1,217 resolved *newly-added* test ids** | **128 = 10.5%** | [8.9%, 12.4%] |
| `PASS_TO_PASS` share of all 13,380 resolved PR-touched ids | 10,432 = 78.0% | Wilson [77.3%, 78.7%]; **cluster bootstrap over 25 repos [71.0%, 87.2%]** |
| `FAIL_TO_PASS` rows that are import/collection errors at base | 2,181 of 2,948 = 74.0% | Wilson [72.4%, 75.5%]; **cluster bootstrap [36.1%, 87.6%]** |
| PRs with **no assertion-level** `FAIL_TO_PASS` (all touched ids) | 14 of 99 = 14.1% | [8.6%, 22.3%] |

## What it means

**The pre-registered claim is refuted.** Exactly one of 99 resolved PRs added test ids that
all already passed at its base commit. The broader bar is cleared too: every one of the 99
shipped at least one test in a touched file that behaved differently on base.

**And the two per-test figures are about different things.** 78.0% of the ids these PRs
*touch* pass on both sides — but 90.9% of resolved ids are pre-existing tests being re-run.
Restricted to the ids the PRs actually **added**, `PASS_TO_PASS` is **10.5%**, and 58.3% of
the new tests' discriminating evidence is a genuine assertion failing at base.

**The 74.0% import-error figure is not what an earlier draft said it was.** Only 15.4% of
`FAIL_TO_PASS` rows are "the PR added the module too"; **58.6% are pre-existing tests that
passed at base and were broken by an import the PR's own test patch added.** Re-scoring the
per-PR result without those rows still gives 0/99.

## What it does not mean

- **Not a population estimate, and the bias direction is unknown.** 25 repositories that
  install from a lockfile and run their suite offline at base — 41.7% of the 60-repo corpus.
  Earlier drafts called this "the well-maintained tail" and said the selection biases the
  result toward 0. **That claim is withdrawn:** built repos have median 64 stars against 351
  for the 35 that failed to build, identical agent-PR volume (median 6) and a near-identical
  lock-kind mix. The filter selects small, single-lockfile projects, not better-maintained
  ones. Nothing here transfers to repos without lockfiles or pytest, under 10 stars, or with
  unbuildable bases.
- **Not a claim about agents specifically.** There is no human-PR control arm. The nearest
  published one, arXiv:2601.21194, finds test-inclusion likelihood comparable (42.9% agent
  vs 40.0% human) and negligible test-smell differences.
- **Not a per-agent comparison.** 92 of 107 PRs carry one trailer family; zero Codex, Devin,
  Cursor, aider, openhands or sweep PRs survived. And the trailer proves agent *involvement*,
  not that the agent wrote the tests that landed — review-time repair is unseparable here.
- **Not independent observations.** 107 PRs sit inside 25 repos; every row-level Wilson
  interval is narrower than the truth, which is why the cluster-robust ends are printed above.
  The two largest module-level **collection events** — both the same module, in two PRs of
  one repo — supply 1,475 of 2,948 = 50.0% of all `FAIL_TO_PASS` rows (those two PRs together
  supply 1,490 = 50.5%).
- **Not a question about PRs that ship no tests.** 288 of the 937 PRs examined (30.7%,
  [27.9%, 33.8%]) were dropped for touching no test path at all — recomputed by `analysis.py`
  from the tracked per-repo funnel `../corpus/funnel-v2.csv` (one row per repo, emitted by
  `funnel_csv.py` from a 2,015-row append-only checkpoint log under the last-row-per-repo
  rule; see `WRITEUP.md` §Corpus and funnel).
- **Not a contradiction of "All Smoke, No Alarm"** (arXiv:2606.18168, 80.2% of agent test
  patches have weak or no explicit oracle signals, measured statically). Different axes, and
  different denominators — the number to place beside 80.2% is 10.5%, not 78.0%.
- **Not a claim that `PASS_TO_PASS` is a defect.** SWE-bench treats it as the desirable
  regression category.
- **Not stratified by who merged it.** No `merged_by` column exists. A real gap.

## Pre-registration and conflicts

"Pre-registered" means **specified in writing before the run, in this repository** —
`research/precedents.md` and `METHOD.md`, both predating `results-prs.csv`. There is no
registry and no external timestamp, so it is self-attestation. **Two deviations from it are
recorded in `WRITEUP.md`** §"Pre-registration status": the `fix`-only headline is published
beside the all-types number rather than ahead of it, and Objection 1's green-base *admission
criterion* was recorded per test (`pre_patch_outcome`) rather than enforced as a discard
(`METHOD.md` Departures #4) — 15 `failed` and 136 `skipped` pre-patch rows of 13,564, of which
150 are `UNRESOLVED` anyway and exactly one is a `FAIL_TO_PASS`. The author maintains two
commercial concepts in the same public repo that a *positive* finding would have helped
(`ideas/r2-ai-pr-verification-gate.md`, `ideas/r2-agent-guardrails-per-repo.md`); the result
runs against that interest. Built and written with heavy AI assistance; the method and the
numbers are the author's to defend.

## Reproduce in three commands

In a clone of [`Alex-lop/venture`](https://github.com/Alex-lop/venture):

```sh
cd ventures/c-measurement/study
python3 runner.py --selfcheck     # parser + verdict asserts; no docker, no network
python3 analysis.py               # every number on this page, incl. == RED-TEAM PASS ==
python3 runner.py --summary --md  # the verdict tables
```

To re-run the measurement itself: `./run.sh` (docker + a read-only `gh` login; ~4.3 h of
container time at `--jobs 3`; resumable).

## Novelty, stated precisely

`precedents.md` §"The gap" records four properties: (a) real merged PRs in the wild, (b)
agent-authored by trailer, (c) the PR's own tests executed on the base commit, (d) the
pass-on-base rate reported as the result, with its denominator. **No work we found holds all
four** — but the gap is one property wide in two directions, not four: jittest already runs
this replay on 83 *human-authored* merged PRs and publishes a verdict named
`non_discriminating` with its denominator; BSG-VA holds (b), (c) and (d) on benchmark
rollouts. The search behind "we found none" is arXiv-metadata-only (weak evidence of absence,
by its own instrument log), was re-run and triaged in full on 2026-08-31 — 90 hits, every
title read, six abstracts fetched and disposed of — and extended to OpenAlex for non-arXiv
venues. Semantic Scholar 429'd again, so IEEE/ACM/journal-only work remains under-searched.

## Data, method, instrument

Everything below is checked in, and every number on this page is reprinted by
`analysis.py` from those files:

| File | What it is |
| --- | --- |
| [`SUMMARY.md`](https://github.com/Alex-lop/venture/blob/main/ventures/c-measurement/study/SUMMARY.md) | This page, in the repository |
| [`WRITEUP.md`](https://github.com/Alex-lop/venture/blob/main/ventures/c-measurement/study/WRITEUP.md) | The study, with the red-team pass and every limit |
| [`METHOD.md`](https://github.com/Alex-lop/venture/blob/main/ventures/c-measurement/study/METHOD.md) | The method, its departures and its known limits |
| [`DATASET-CARD.md`](https://github.com/Alex-lop/venture/blob/main/ventures/c-measurement/study/DATASET-CARD.md) | Columns, provenance, licensing, and what is deliberately absent |
| [`results-prs.csv`](https://github.com/Alex-lop/venture/blob/main/ventures/c-measurement/study/results-prs.csv) | One row per PR: verdict, counts, strata |
| [`results-tests.csv`](https://github.com/Alex-lop/venture/blob/main/ventures/c-measurement/study/results-tests.csv) | One row per PR-touched test id: pre-patch, base, candidate, verdict |
| [`runner.py`](https://github.com/Alex-lop/venture/blob/main/ventures/c-measurement/study/runner.py) | The instrument |
| [`analysis.py`](https://github.com/Alex-lop/venture/blob/main/ventures/c-measurement/study/analysis.py) | Every number above, recomputed from the CSVs |

Raw per-PR API payloads and container logs are deliberately **not** published: they carry
PR-author logins and commit emails, which never reach a tracked file.
