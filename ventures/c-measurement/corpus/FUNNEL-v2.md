# FUNNEL v2 — widened candidate corpus (2026-08-30)

Built by `scripts/widen.py`. Raw checkpoints in `raw/*.jsonl` (every stage resumable).
Criteria are identical to `candidates.csv` except the two changes the corpus README's
"Next step" prescribes: **star gate >= 50 -> >= 10**, and the **">= 3 stage-1 hits"**
**prefilter replaced by a per-repo recovery step** (stage 3b) for repos with 1-2 hits.

**Transport deviation, recorded.** REST `/search/issues` was under a persistent
*secondary* rate limit for this token on 2026-08-30 (4 calls through, then minutes of
403s at a time), so stage 1 and stage 3b's scoped search ran on the **GraphQL**
`search(type: ISSUE)` endpoint with the identical query strings, windows and page depth.
GraphQL returns repo metadata inline with each search hit, which is what makes stage 2
free and a >= 10-star corpus affordable inside the call budget. No gate changed.

## Stage table

| stage | what | in | out | dropped (reason) |
|---|---|---:|---:|---|
| 1 | PR search, 72 search calls, 11443 raw result rows | — | 6362 unique merged PRs in 1908 repos | dedup across trailers and pages |
| 2 | repo metadata gate (>= 10 stars, primary-Python, not fork, not archived, pushed >= 2026-07-01) | 1908 | 335 | 1437 under_stars; 82 fork; 44 not_python; 6 archived; 4 stale |
| 3 | lockfile + pytest gate | 335 | 145 | 178 no_lockfile; 12 no_pytest |
| 3b | per-repo recovery, repos with 1-2 stage-1 hits | 112 | 1861 extra trailer-carrying PRs pooled | scoped search + REST closed-PR listing |
| 4 | per-PR verification, 937 PRs examined | 145 | **60** | PRs dropped: 288 no_test_path; 101 no_verbatim_trailer; 69 too_large; 62 no_source_path. Repos then failing the >= 3 bar: 85. |

**Result: 60 qualifying repos** (v1: 23). 26 of them have 10-49 stars — they exist only because of the relaxed star gate. 49 of them had 1-2 stage-1 hits — they exist only because the >= 3-hit prefilter was replaced by stage 3b.

**Stop condition:** search calls 171/200, other calls 406/3000. The stage-1 repo pool was exhausted — every repo the search surfaced was processed.

Lock kind mix in the final set: 50 uv.lock; 7 pinned-requirements; 3 poetry.lock.

## Stage 3b — what the recovery step returned

| repo | stage-1 hits | mechanism (PRs returned) | recovered | qualifying |
|---|---:|---|---:|---:|
| omicverse/omicverse | 1 | rest-closed-pr-listing+scoped-search(search=1,rest=96) | 49 | 12 |
| crewAIInc/crewAI | 2 | rest-closed-pr-listing(search=0,rest=47) | 15 | 12 |
| Soju06/codex-lb | 1 | rest-closed-pr-listing+scoped-search(search=1,rest=69) | 12 | 11 |
| ohdearquant/lionagi | 1 | rest-closed-pr-listing+scoped-search(search=14,rest=79) | 14 | 11 |
| openshift-eng/art-tools | 1 | rest-closed-pr-listing(search=0,rest=91) | 24 | 10 |
| brcampidelli/chimera-agent | 1 | rest-closed-pr-listing(search=0,rest=97) | 62 | 10 |
| agentcage/agentcage | 1 | rest-closed-pr-listing(search=0,rest=73) | 55 | 9 |
| Charli3-Official/charli3-dendrite | 1 | rest-closed-pr-listing(search=0,rest=54) | 13 | 9 |
| helpfulengineering/supply-graph-ai | 1 | rest-closed-pr-listing(search=0,rest=95) | 71 | 9 |
| SenolIsci/mykg | 1 | rest-closed-pr-listing(search=0,rest=42) | 37 | 8 |
| eniklas/gamatrix | 1 | rest-closed-pr-listing(search=0,rest=45) | 31 | 8 |
| paulomtts/pyjinhx | 1 | rest-closed-pr-listing(search=0,rest=97) | 85 | 8 |
| cymoo/lovia | 1 | rest-closed-pr-listing(search=0,rest=100) | 99 | 8 |
| headroomlabs-ai/headroom | 2 | rest-closed-pr-listing+scoped-search(search=101,rest=74) | 99 | 7 |
| commit-check/commit-check | 1 | rest-closed-pr-listing(search=0,rest=88) | 10 | 7 |
| usestrix/strix | 1 | rest-closed-pr-listing(search=0,rest=56) | 8 | 7 |
| Datus-ai/Datus-agent | 1 | rest-closed-pr-listing(search=0,rest=78) | 17 | 7 |
| vllm-project/guidellm | 2 | rest-closed-pr-listing+scoped-search(search=15,rest=43) | 10 | 6 |
| debpalash/VoiceStudio | 1 | rest-closed-pr-listing+scoped-search(search=1,rest=94) | 28 | 6 |
| karanhudia/borg-ui | 1 | rest-closed-pr-listing+scoped-search(search=1,rest=70) | 5 | 6 |
| experientiallabs/experiential | 1 | rest-closed-pr-listing+scoped-search(search=100,rest=91) | 104 | 6 |
| vamseeachanta/workspace-hub | 1 | rest-closed-pr-listing(search=0,rest=92) | 8 | 6 |
| taoq-ai/ziran | 1 | rest-closed-pr-listing(search=0,rest=50) | 10 | 6 |
| MadSkittles/Router-Maestro | 1 | rest-closed-pr-listing(search=0,rest=95) | 62 | 6 |
| FalkorDB/QueryWeaver | 1 | rest-closed-pr-listing+scoped-search(search=7,rest=52) | 11 | 5 |
| partcad/partcad | 1 | rest-closed-pr-listing+scoped-search(search=75,rest=98) | 77 | 5 |
| UiPath/coder_eval | 1 | rest-closed-pr-listing(search=0,rest=71) | 43 | 5 |
| cyzus/suzent | 1 | rest-closed-pr-listing(search=0,rest=89) | 12 | 5 |
| Jamie-BitFlight/claude_skills | 1 | rest-closed-pr-listing(search=0,rest=92) | 74 | 5 |
| pvliesdonk/markdown-vault-mcp | 1 | rest-closed-pr-listing(search=0,rest=76) | 24 | 5 |
| Consiliency/pmcp | 1 | rest-closed-pr-listing(search=0,rest=84) | 61 | 5 |
| Ikalus1988/MisakaNet | 2 | rest-closed-pr-listing(search=0,rest=52) | 9 | 5 |
| PostHog/posthog | 1 | rest-closed-pr-listing+scoped-search(search=100,rest=44) | 98 | 4 |
| Ishannaik/agent-sweep | 2 | rest-closed-pr-listing(search=0,rest=75) | 3 | 4 |
| Kohei-Wada/taskdog | 1 | rest-closed-pr-listing(search=0,rest=81) | 18 | 4 |
| CERTCC/Vultron | 1 | rest-closed-pr-listing(search=0,rest=99) | 24 | 4 |
| Project-N-E-K-O/N.E.K.O | 2 | rest-closed-pr-listing+scoped-search(search=19,rest=79) | 23 | 3 |
| Azure/gpt-rag-orchestrator | 2 | rest-closed-pr-listing+scoped-search(search=4,rest=86) | 3 | 3 |
| FZJ-IEK3-VSA/HiSim | 2 | rest-closed-pr-listing+scoped-search(search=2,rest=70) | 12 | 3 |
| ifnull/ha-airspace | 2 | rest-closed-pr-listing+scoped-search(search=5,rest=63) | 3 | 3 |
| open-reaction-database/ord-data | 1 | rest-closed-pr-listing+scoped-search(search=20,rest=33) | 16 | 3 |
| djtelicloud/grok-mcp-server | 1 | rest-closed-pr-listing(search=0,rest=64) | 22 | 3 |
| druide67/asiai | 1 | rest-closed-pr-listing(search=0,rest=71) | 66 | 3 |
| mvanhorn/last30days-skill | 1 | rest-closed-pr-listing(search=0,rest=78) | 3 | 3 |
| harbor-framework/harbor | 1 | rest-closed-pr-listing(search=0,rest=74) | 4 | 3 |
| xyTom/coding-tools-mcp | 1 | rest-closed-pr-listing(search=0,rest=29) | 8 | 3 |
| promptdriven/pdd | 1 | rest-closed-pr-listing(search=0,rest=61) | 6 | 3 |
| ffroliva/gflow-cli | 1 | rest-closed-pr-listing(search=0,rest=96) | 20 | 3 |
| FunFR/ha-indygo-pool | 1 | rest-closed-pr-listing(search=0,rest=93) | 3 | 3 |
| verl-project/verl | 1 | rest-closed-pr-listing+scoped-search(search=2,rest=46) | 2 | 2 |

(62 more rows in `raw/repo_results.jsonl`.)

## Exact query log — stage 1

GraphQL `search(type: ISSUE, first: 100)` with
`query: 'is:pr is:merged language:Python "<TRAILER>" merged:<RANGE> sort:updated-desc'`,
cursor-paginated. `total_count` is the endpoint's `issueCount` for that query.

| trailer key | window | page | total_count | returned |
|---|---|---:|---:|---:|
| aider | 2026-06-01..2026-06-08 | 1 | 227 | 100 |
| aider | 2026-06-08..2026-06-15 | 1 | 224 | 100 |
| aider | 2026-06-15..2026-06-22 | 1 | 167 | 100 |
| aider | 2026-06-22..2026-06-29 | 1 | 185 | 100 |
| aider | 2026-06-29..2026-07-06 | 1 | 156 | 100 |
| aider | 2026-07-06..2026-07-13 | 1 | 167 | 100 |
| aider | 2026-07-13..2026-07-20 | 1 | 207 | 100 |
| aider | 2026-07-20..2026-07-27 | 1 | 164 | 100 |
| aider | 2026-07-27..2026-08-03 | 1 | 189 | 100 |
| aider | 2026-08-03..2026-08-10 | 1 | 164 | 100 |
| aider | 2026-08-10..2026-08-17 | 1 | 161 | 100 |
| aider | 2026-08-17..2026-08-24 | 1 | 206 | 100 |
| aider | 2026-08-24..2026-08-31 | 1 | 150 | 100 |
| claude-coauthor | 2026-06-01..2026-06-08 | 1 | 1797 | 100 |
| claude-coauthor | 2026-06-08..2026-06-15 | 1 | 2242 | 100 |
| claude-coauthor | 2026-06-15..2026-06-22 | 1 | 3568 | 100 |
| claude-coauthor | 2026-06-22..2026-06-29 | 1 | 3370 | 100 |
| claude-coauthor | 2026-06-29..2026-07-06 | 1 | 4455 | 100 |
| claude-coauthor | 2026-07-06..2026-07-13 | 1 | 5053 | 100 |
| claude-coauthor | 2026-07-13..2026-07-20 | 1 | 4812 | 100 |
| claude-coauthor | 2026-07-20..2026-07-27 | 1 | 4639 | 100 |
| claude-coauthor | 2026-07-27..2026-08-03 | 1 | 4564 | 100 |
| claude-coauthor | 2026-08-03..2026-08-10 | 1 | 5006 | 100 |
| claude-coauthor | 2026-08-10..2026-08-17 | 1 | 5184 | 100 |
| claude-coauthor | 2026-08-17..2026-08-24 | 1 | 5689 | 100 |
| claude-coauthor | 2026-08-24..2026-08-31 | 1 | 4841 | 100 |
| claude-code-gen | 2026-06-01..2026-06-08 | 1 | 84962 | 100 |
| claude-code-gen | 2026-06-08..2026-06-15 | 1 | 100014 | 100 |
| claude-code-gen | 2026-06-15..2026-06-22 | 1 | 108214 | 100 |
| claude-code-gen | 2026-06-22..2026-06-29 | 1 | 104855 | 100 |
| claude-code-gen | 2026-06-29..2026-07-06 | 1 | 120074 | 100 |
| claude-code-gen | 2026-07-06..2026-07-13 | 1 | 124665 | 100 |
| claude-code-gen | 2026-07-13..2026-07-20 | 1 | 120411 | 100 |
| claude-code-gen | 2026-07-20..2026-07-27 | 1 | 113168 | 100 |
| claude-code-gen | 2026-07-27..2026-08-03 | 1 | 109523 | 100 |
| claude-code-gen | 2026-08-03..2026-08-10 | 1 | 106683 | 100 |
| claude-code-gen | 2026-08-10..2026-08-17 | 1 | 107749 | 100 |
| claude-code-gen | 2026-08-17..2026-08-24 | 1 | 110960 | 100 |
| claude-code-gen | 2026-08-24..2026-08-31 | 1 | 99712 | 100 |
| codex | 2026-06-01..2026-06-08 | 1 | 170 | 100 |
| codex | 2026-06-08..2026-06-15 | 1 | 69 | 69 |
| codex | 2026-06-15..2026-06-22 | 1 | 73 | 73 |
| codex | 2026-06-22..2026-06-29 | 1 | 49 | 49 |
| codex | 2026-06-29..2026-07-06 | 1 | 62 | 62 |
| codex | 2026-07-06..2026-07-13 | 1 | 59 | 59 |
| codex | 2026-07-13..2026-07-20 | 1 | 88 | 88 |
| codex | 2026-07-20..2026-07-27 | 1 | 85 | 85 |
| codex | 2026-07-27..2026-08-03 | 1 | 59 | 59 |
| codex | 2026-08-03..2026-08-10 | 1 | 150 | 100 |
| codex | 2026-08-10..2026-08-17 | 1 | 121 | 100 |
| codex | 2026-08-17..2026-08-24 | 1 | 90 | 90 |
| codex | 2026-08-24..2026-08-31 | 1 | 98 | 98 |
| copilot | 2026-06-01..2026-06-08 | 1 | 285 | 100 |
| copilot | 2026-06-08..2026-06-15 | 1 | 219 | 100 |
| copilot | 2026-06-15..2026-06-22 | 1 | 230 | 100 |
| copilot | 2026-06-22..2026-06-29 | 1 | 260 | 100 |
| copilot | 2026-06-29..2026-07-06 | 1 | 269 | 100 |
| copilot | 2026-07-06..2026-07-13 | 1 | 384 | 100 |
| copilot | 2026-07-13..2026-07-20 | 1 | 273 | 100 |
| copilot | 2026-07-20..2026-07-27 | 1 | 168 | 100 |
| copilot | 2026-07-27..2026-08-03 | 1 | 158 | 100 |
| copilot | 2026-08-03..2026-08-10 | 1 | 185 | 100 |
| copilot | 2026-08-10..2026-08-17 | 1 | 223 | 100 |
| copilot | 2026-08-17..2026-08-24 | 1 | 201 | 100 |
| copilot | 2026-08-24..2026-08-31 | 1 | 176 | 100 |
| cursor | all | 1 | 657 | 100 |
| cursor | all | 2 | 657 | 100 |
| devin | all | 1 | 66 | 66 |
| openhands | all | 1 | 63 | 63 |
| robot-gen | all | 1 | 1217473 | 100 |
| sweep | all | 1 | 121 | 100 |
| sweep | all | 2 | 121 | 21 |

Search-call accounting: 72 stage-1 calls are logged above; the budget counter reads 171 because ~50 further stage-1 calls were discarded and re-run after a process restart lost their pagination cursors, and each stage-3b scoped search also draws on the same 200-call pool.

Plus the 26 REST `/search/issues` calls made before the transport switch. Their rows are archived in `raw/prs_rest_partial.jsonl` and were **not** used to build the corpus, so the counts above are self-contained.

| trailer key | window | page | total_count | returned |
|---|---|---:|---:|---:|
| aider | 2026-06-01..2026-06-08 | 1 | 227 | 100 |
| claude-coauthor | 2026-06-01..2026-06-08 | 1 | 1797 | 100 |
| claude-code-gen | 2026-06-01..2026-06-08 | 1 | 84981 | 100 |
| codex | 2026-06-01..2026-06-08 | 1 | 170 | 100 |
| copilot | 2026-06-01..2026-06-08 | 1 | 285 | 100 |
| aider | 2026-06-08..2026-06-15 | 1 | 224 | 100 |
| claude-coauthor | 2026-06-08..2026-06-15 | 1 | 2242 | 100 |
| claude-code-gen | 2026-06-08..2026-06-15 | 1 | 100021 | 100 |
| codex | 2026-06-08..2026-06-15 | 1 | 69 | 69 |
| copilot | 2026-06-08..2026-06-15 | 1 | 219 | 100 |
| aider | 2026-06-15..2026-06-22 | 1 | 167 | 100 |
| claude-coauthor | 2026-06-15..2026-06-22 | 1 | 3568 | 100 |
| claude-code-gen | 2026-06-15..2026-06-22 | 1 | 108217 | 100 |
| codex | 2026-06-15..2026-06-22 | 1 | 73 | 73 |
| copilot | 2026-06-15..2026-06-22 | 1 | 230 | 100 |
| aider | 2026-06-22..2026-06-29 | 1 | 185 | 100 |
| claude-coauthor | 2026-06-22..2026-06-29 | 1 | 3370 | 100 |
| claude-code-gen | 2026-06-22..2026-06-29 | 1 | 104855 | 100 |
| codex | 2026-06-22..2026-06-29 | 1 | 49 | 49 |
| copilot | 2026-06-22..2026-06-29 | 1 | 260 | 100 |
| aider | 2026-06-29..2026-07-06 | 1 | 156 | 100 |
| claude-coauthor | 2026-06-29..2026-07-06 | 1 | 4455 | 100 |
| claude-code-gen | 2026-06-29..2026-07-06 | 1 | 120078 | 100 |
| codex | 2026-06-29..2026-07-06 | 1 | 62 | 62 |
| copilot | 2026-06-29..2026-07-06 | 1 | 269 | 100 |
| aider | 2026-07-06..2026-07-13 | 1 | 167 | 100 |

## Stage 3b query form

Prescribed form, run first: `repo:<O/R> is:pr is:merged merged:>2026-06-01 "<TRAILER>"` (GraphQL ISSUE search), for up to the two trailer keys that surfaced the repo at stage 1.

Fallback, run for every stage-3b repo: `GET /repos/<O/R>/pulls?state=closed&sort=updated&direction=desc&per_page=100`, filtered to `merged_at > 2026-06-01`. It is not subject to the 1,000-result search cap and costs one call per repo instead of one per trailer. Recovered PRs are body-screened for a verbatim trailer before any further call is spent on them, then run the identical stage-4 checks as every other PR.

**Asymmetry to know about.** Repos with >= 3 stage-1 hits are *not* re-enumerated, exactly as in v1, so their `agent_pr_count_90d` stays a lower bound capped at 12 examined PRs. Repos with 1-2 hits get the fuller stage-3b enumeration. Counts are therefore not comparable *between* those two groups; membership in the corpus is.
