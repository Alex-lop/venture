# Candidate corpus — non-discriminating tests in agent-authored PRs

Built 2026-08-30, read-only, GitHub REST (`gh api`) only. No writes, no contact with any
repo or maintainer.

## Research question this corpus serves

How often are the tests shipped in agent-authored pull requests *non-discriminating* —
i.e. they pass on the PR's base commit exactly as they pass on the candidate commit, so
they would not have caught the bug the PR claims to fix or failed on the feature it claims
to add? Answering that needs a **differential verifier**: check out base, run the PR's
tests, then check out candidate, run them again, compare. So a repo only earns a place here
if that is mechanically feasible — pinned dependencies, a network-free install, and pytest.

## Selection criteria (applied verbatim)

Repo level:
- public, primary language Python, not a fork, not archived
- >= 50 stars
- `pushed_at` within 60 days of 2026-08-30
- lockfile-driven install: `uv.lock` + `pyproject.toml`, or `poetry.lock`, or a
  `requirements*.txt` (top level or under `requirements/`) with >= 3 `==` pins.
  `Pipfile.lock` / `pdm.lock` accepted as equivalents where present.
- pytest evidence: `pytest.ini`, `[tool.pytest.ini_options]` in `pyproject.toml`,
  a top-level `conftest.py`, or a `tests/` dir containing `test_*.py` / `conftest.py`

PR level (each counted PR must satisfy all):
- merged in the last 90 days (`merged:>2026-06-01`)
- carries an agent trailer **verbatim** in the PR body or in one of its commit messages
- touches >= 1 test path AND >= 1 non-test `.py`/`.pyi` source file
- <= 2,000 changed lines (additions + deletions)
- repo needs >= 3 such PRs

## Exact queries

All stage-1 queries went to `GET /search/issues`, `sort=updated&order=desc&per_page=100`:

```
is:pr is:merged language:Python "<TRAILER>" merged:>2026-06-01
```

with `<TRAILER>` drawn from:

| key | literal searched | unsliced `total_count` | time-sliced? |
|---|---|---:|---|
| `claude-coauthor` | `Co-Authored-By: Claude` | 48200 | yes, 7-day windows |
| `claude-code-gen` | `Generated with Claude Code` | 1224643 | yes, 7-day windows |
| `codex` | `Co-authored-by: Codex` | 1050 | yes, 7-day windows |
| `cursor` | `Co-authored-by: Cursor` | 655 | no (under the 1,000 cap) |
| `copilot` | `Co-authored-by: Copilot` | 2649 | yes, 7-day windows |
| `devin` | `Co-authored-by: devin-ai-integration` | 66 | no (under the 1,000 cap) |
| `openhands` | `Co-authored-by: openhands` | 63 | no (under the 1,000 cap) |
| `sweep` | `Co-authored-by: sweep` | 120 | no (under the 1,000 cap) |
| `aider` | `[aider]` | 2041 | yes, 7-day windows |
| `robot-gen` | `🤖 Generated with` | 1210381 | **no - recall truncated by the 1,000 cap** |

Six pages per query. Because GitHub caps any single search at 1,000 results, the five
saturated trailers (`Co-Authored-By: Claude`, `Generated with Claude Code`,
`Co-authored-by: Copilot`, `Co-authored-by: Codex`, `[aider]`) were re-run **time-sliced**
into consecutive 7-day `merged:A..B` windows across 2026-06-01 .. 2026-08-31, 3 pages each,
to recover results the cap had hidden.

Then, per repo: `GET /repos/{owner}/{repo}` and `GET /repos/{owner}/{repo}/contents/`
(plus `contents/tests`, `contents/requirements`, and raw `pyproject.toml` /
`requirements*.txt` bodies where needed).

Then, per PR: `GET /repos/{o}/{r}/pulls/{n}` (size + body), `GET .../pulls/{n}/commits`
(only when the body carried no trailer), `GET .../pulls/{n}/files?per_page=100`
(test-plus-source check).

## Funnel

| stage | what | in | out | dropped (reason) |
|---|---|---:|---:|---|
| 1 | PR search, 219 search calls, 19104 raw result rows | — | 14417 unique merged PRs in 3956 repos | dedup across trailers and pages |
| 1b | repos with >= 3 trailer-matching PRs found | 3956 | 1047 | 2909 repos had 1-2 hits (cannot reach the >= 3 bar on evidence in hand) |
| 2 | repo metadata gate | 1047 | 94 | 918 < 50 stars; 28 forks; 3 archived; 0 not pushed in 60d; 4 not primary-Python; 0 API errors |
| 3 | lockfile + pytest gate | 94 | 43 | 48 no lockfile / no pinned requirements; 3 no pytest evidence; 0 errors |
| 4 | per-PR verification (279 PRs examined across 43 repos) | 43 | **23** | PRs dropped: 73 trailer not verbatim in body or commits; 52 touched no test path; 18 touched no non-test source; 17 > 2,000 changed lines; 0 errors. Repos then failing the >= 3 bar were dropped. |

Stop condition: **candidate pool exhausted**, not the caps. All 43 repos that
reached stage 4 were fully examined at 279 PRs, leaving 121 of the 400-PR
budget unspent. The 60-repo target was not reachable under these criteria — stage 2 and 3
are what bind, not the search or examination budget.

Lockfile mix in the final set: uv.lock+pyproject.toml=20, pinned=3.

## Known biases — read before using this corpus

1. **`search/issues` indexes PR titles and bodies, not commit messages.** Stage 1 therefore
   finds agent PRs whose *body* echoes the trailer. Agent PRs that carry the trailer only in
   a commit are invisible to stage 1. Stage 4 does read commits, but only for PRs stage 1
   already surfaced, so this is a recall loss, not a precision loss.
2. **GitHub does not honour phrase quoting on these strings.** `"Generated with Claude Code"`
   reported >1.2M results — it is being tokenised and OR-ed, not matched as a phrase. Stage 1
   is consequently a noisy over-fetch. This is corrected at stage 4, where every counted PR is
   re-checked for the trailer **verbatim** (case-insensitive regex, tolerating the markdown
   link form `Generated with [Claude Code](...)`) in its body or commits;
   the `no_verbatim_trailer` column of the funnel is the size of that correction.
3. **1,000-result cap.** Even time-sliced into 7-day windows, the `Co-Authored-By: Claude`
   slices still returned full pages, so recall is truncated for the busiest weeks.
   `🤖 Generated with` reported >1.2M and was **not** sliced, so it is the most
   truncated query in the set. `Cursor`, `devin`, `openhands` and `sweep` sat under the cap
   and were fully recovered.
4. **The >= 3-found-PRs prefilter runs on stage-1 evidence.** A repo with 5 agent PRs of which
   search surfaced 2 was never fetched. `agent_pr_count_90d` in the CSV is therefore a **lower
   bound**, capped further at 12 PRs examined per repo.
5. **`language:Python` is GitHub's primary-language guess.** Polyglot repos where Python is
   the second language are excluded even when their Python test suite is the relevant one.
6. **Popularity skew.** The >= 50-star gate removed 918 of 1047 repos —
   by far the largest single cut. Heavy agent-PR activity concentrates in small personal repos;
   this corpus is deliberately the popular tail and is not representative of agent PR authorship
   overall.
7. **Lockfile detection is top-level (plus `requirements/`) only.** Repos pinning under
   `ci/`, `deps/`, or a nested package dir read as "no lockfile". Recall loss again.
8. **Vendor self-selection.** `Co-authored-by: Copilot` and `[aider]` produce many results but
   `[aider]` in particular is a weak signal — the literal appears in changelogs and docs. Treat
   `trailer_kinds` in the CSV as the ground truth per repo, not the stage-1 query that found it.

## Files

- `candidates.csv` — 23 rows. Columns: `repo, stars, pushed_at, lockfile_type,
  pytest_evidence, agent_pr_count_90d, sample_pr_numbers, trailer_kinds`.
  `sample_pr_numbers` are PRs that passed **every** PR-level check, so they are directly
  usable as differential-verifier inputs.

## Next step — and the thing that kills this study

**100-repo base-snapshot build pilot.** Before any measurement, take each candidate repo,
check out the base commit of one qualifying PR, install from the lockfile with the network
disabled after a warm cache, and run `pytest --collect-only`. Record: install succeeded,
collection succeeded, and the suite ran to a verdict.

**The falsifier: if base builds succeed for fewer than 30% of attempts, the study does not
work.** A differential verifier needs the base commit to build and its tests to run. If most
bases will not build hermetically, per-PR results are unavailable for the majority of the
corpus, whatever the headline non-discrimination rate looks like on the minority that did
build — and that minority is exactly the well-maintained subset, which is the population
least likely to ship non-discriminating tests. A biased 25% sample cannot answer the
question. Run the pilot first; report the build rate before reporting anything else.

The pilot needs more repos than this file holds. Widen by relaxing the >= 50-star gate to
>= 10 and by dropping the >= 3-PR prefilter in favour of a per-repo scoped search
(`repo:X is:pr is:merged merged:>2026-06-01 <trailer>`) for repos with 1-2 stage-1 hits.
