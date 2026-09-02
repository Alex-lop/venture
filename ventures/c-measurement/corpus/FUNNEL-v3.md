# FUNNEL v3 — completed widened corpus (2026-09-01)

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
| 1 | PR search, 175 search calls, 20455 raw result rows | — | 13433 unique merged PRs in 3633 repos | dedup across trailers and pages |
| 2 | repo metadata gate (>= 10 stars, primary-Python, not fork, not archived, pushed >= 2026-07-01) | 3633 | 580 | 2806 under_stars; 137 fork; 85 not_python; 19 archived; 6 stale |
| 3 | lockfile + pytest gate | 580 | 252 | 307 no_lockfile; 21 no_pytest |
| 3b | per-repo recovery, repos with 1-2 stage-1 hits | 200 | 3228 extra trailer-carrying PRs pooled | scoped search + REST closed-PR listing |
| 4 | per-PR verification, 1614 PRs examined | 252 | **110** | PRs dropped: 502 no_test_path; 143 no_verbatim_trailer; 121 no_source_path; 121 too_large. Repos then failing the >= 3 bar: 142. |

**Result: 110 qualifying repos** (v1: 23). 46 of them have 10-49 stars — they exist only because of the relaxed star gate. 87 of them had 1-2 stage-1 hits — they exist only because the >= 3-hit prefilter was replaced by stage 3b.

**Stop condition:** search calls 274/500, other calls 738/3000. The stage-1 repo pool was exhausted — every repo the search surfaced was processed.

Lock kind mix in the final set: 92 uv.lock; 11 pinned-requirements; 6 poetry.lock; 1 Pipfile.lock.

The public `funnel-v3.csv` pseudonymizes one non-qualifying row whose repository name is on the private redaction denylist. Its stage and counts are unchanged.

## Stage 3b — what the recovery step returned

| repo | stage-1 hits | mechanism (PRs returned) | recovered | qualifying |
|---|---:|---|---:|---:|
| omicverse/omicverse | 1 | rest-closed-pr-listing+scoped-search(search=1,rest=96) | 49 | 12 |
| crewAIInc/crewAI | 2 | rest-closed-pr-listing(search=0,rest=47) | 15 | 12 |
| Soju06/codex-lb | 1 | rest-closed-pr-listing+scoped-search(search=1,rest=69) | 12 | 11 |
| ohdearquant/lionagi | 1 | rest-closed-pr-listing+scoped-search(search=14,rest=79) | 14 | 11 |
| reflex-dev/reflex | 1 | rest-closed-pr-listing(search=0,rest=46) | 12 | 11 |
| openshift-eng/art-tools | 1 | rest-closed-pr-listing(search=0,rest=91) | 24 | 10 |
| brcampidelli/chimera-agent | 1 | rest-closed-pr-listing(search=0,rest=97) | 62 | 10 |
| bcorfman/freytag-forge | 2 | rest-closed-pr-listing(search=0,rest=99) | 34 | 10 |
| psd-tools/psd-tools | 1 | rest-closed-pr-listing(search=0,rest=77) | 37 | 10 |
| Human-Agent-Society/CORAL | 1 | rest-closed-pr-listing(search=0,rest=86) | 26 | 10 |
| martymcenroe/AssemblyZero | 1 | rest-closed-pr-listing(search=0,rest=99) | 10 | 10 |
| agentcage/agentcage | 1 | rest-closed-pr-listing(search=0,rest=73) | 55 | 9 |
| Charli3-Official/charli3-dendrite | 1 | rest-closed-pr-listing(search=0,rest=54) | 13 | 9 |
| helpfulengineering/supply-graph-ai | 1 | rest-closed-pr-listing(search=0,rest=95) | 71 | 9 |
| kayl-codes/homeassistant-truenas | 2 | rest-closed-pr-listing(search=0,rest=100) | 64 | 9 |
| Perseus-Computing-LLC/perseus | 1 | rest-closed-pr-listing(search=0,rest=87) | 20 | 9 |
| SenolIsci/mykg | 1 | rest-closed-pr-listing(search=0,rest=42) | 37 | 8 |
| eniklas/gamatrix | 1 | rest-closed-pr-listing(search=0,rest=45) | 31 | 8 |
| paulomtts/pyjinhx | 1 | rest-closed-pr-listing(search=0,rest=97) | 85 | 8 |
| cymoo/lovia | 1 | rest-closed-pr-listing(search=0,rest=100) | 99 | 8 |
| Comfy-Org/comfy-cli | 1 | rest-closed-pr-listing(search=0,rest=84) | 38 | 8 |
| Agentix-Project/Agentix | 1 | rest-closed-pr-listing(search=0,rest=37) | 34 | 8 |
| posit-dev/rsconnect-python | 1 | rest-closed-pr-listing(search=0,rest=36) | 8 | 8 |
| headroomlabs-ai/headroom | 2 | rest-closed-pr-listing+scoped-search(search=101,rest=74) | 99 | 7 |
| commit-check/commit-check | 1 | rest-closed-pr-listing(search=0,rest=88) | 10 | 7 |
| usestrix/strix | 1 | rest-closed-pr-listing(search=0,rest=56) | 8 | 7 |
| Datus-ai/Datus-agent | 1 | rest-closed-pr-listing(search=0,rest=78) | 17 | 7 |
| tconbeer/harlequin | 1 | rest-closed-pr-listing(search=0,rest=90) | 37 | 7 |
| roboflow/inference | 1 | rest-closed-pr-listing(search=0,rest=75) | 9 | 7 |
| hhopke/intervals-icu-mcp | 1 | rest-closed-pr-listing(search=0,rest=39) | 14 | 7 |
| ric03uec/clawrium | 1 | rest-closed-pr-listing(search=0,rest=93) | 40 | 7 |
| drussell23/JARVIS | 1 | rest-closed-pr-listing(search=0,rest=50) | 50 | 7 |
| sdebruyn/fabric-dw-mcp-cli | 1 | rest-closed-pr-listing(search=0,rest=97) | 40 | 7 |
| vllm-project/guidellm | 2 | rest-closed-pr-listing+scoped-search(search=15,rest=43) | 10 | 6 |
| debpalash/VoiceStudio | 1 | rest-closed-pr-listing+scoped-search(search=1,rest=94) | 28 | 6 |
| karanhudia/borg-ui | 1 | rest-closed-pr-listing+scoped-search(search=1,rest=70) | 5 | 6 |
| experientiallabs/experiential | 1 | rest-closed-pr-listing+scoped-search(search=100,rest=91) | 104 | 6 |
| vamseeachanta/workspace-hub | 1 | rest-closed-pr-listing(search=0,rest=92) | 8 | 6 |
| taoq-ai/ziran | 1 | rest-closed-pr-listing(search=0,rest=50) | 10 | 6 |
| MadSkittles/Router-Maestro | 1 | rest-closed-pr-listing(search=0,rest=95) | 62 | 6 |
| PriorLabs/tabpfn-extensions | 2 | rest-closed-pr-listing(search=0,rest=69) | 20 | 6 |
| Extelligence-ai/bagel | 1 | rest-closed-pr-listing(search=0,rest=67) | 63 | 6 |
| cdeust/Cortex | 1 | rest-closed-pr-listing(search=0,rest=88) | 38 | 6 |
| KR8MER/eas-station | 1 | rest-closed-pr-listing(search=0,rest=95) | 81 | 6 |
| FalkorDB/QueryWeaver | 1 | rest-closed-pr-listing+scoped-search(search=7,rest=52) | 11 | 5 |
| partcad/partcad | 1 | rest-closed-pr-listing+scoped-search(search=75,rest=98) | 77 | 5 |
| UiPath/coder_eval | 1 | rest-closed-pr-listing(search=0,rest=71) | 43 | 5 |
| cyzus/suzent | 1 | rest-closed-pr-listing(search=0,rest=89) | 12 | 5 |
| Jamie-BitFlight/claude_skills | 1 | rest-closed-pr-listing(search=0,rest=92) | 74 | 5 |
| pvliesdonk/markdown-vault-mcp | 1 | rest-closed-pr-listing(search=0,rest=76) | 24 | 5 |

(150 more rows in `raw/repo_results.jsonl`.)

## Exact query log — stage 1

GraphQL `search(type: ISSUE, first: 100)` with
`query: 'is:pr is:merged language:Python "<TRAILER>" merged:<RANGE> sort:updated-desc'`,
cursor-paginated. `total_count` is the endpoint's `issueCount` for that query.

| trailer key | window | page | total_count | returned |
|---|---|---:|---:|---:|
| aider | 2026-06-01..2026-06-08 | 1 | 227 | 100 |
| aider | 2026-06-01..2026-06-08 | 2 | 227 | 100 |
| aider | 2026-06-01..2026-06-08 | 3 | 227 | 27 |
| aider | 2026-06-08..2026-06-15 | 1 | 224 | 100 |
| aider | 2026-06-08..2026-06-15 | 2 | 224 | 100 |
| aider | 2026-06-08..2026-06-15 | 3 | 224 | 24 |
| aider | 2026-06-15..2026-06-22 | 1 | 167 | 100 |
| aider | 2026-06-15..2026-06-22 | 2 | 165 | 65 |
| aider | 2026-06-22..2026-06-29 | 1 | 185 | 100 |
| aider | 2026-06-22..2026-06-29 | 2 | 186 | 86 |
| aider | 2026-06-29..2026-07-06 | 1 | 156 | 100 |
| aider | 2026-06-29..2026-07-06 | 2 | 156 | 56 |
| aider | 2026-07-06..2026-07-13 | 1 | 167 | 100 |
| aider | 2026-07-06..2026-07-13 | 2 | 167 | 67 |
| aider | 2026-07-13..2026-07-20 | 1 | 207 | 100 |
| aider | 2026-07-13..2026-07-20 | 2 | 207 | 100 |
| aider | 2026-07-13..2026-07-20 | 3 | 207 | 7 |
| aider | 2026-07-20..2026-07-27 | 1 | 164 | 100 |
| aider | 2026-07-20..2026-07-27 | 2 | 165 | 65 |
| aider | 2026-07-27..2026-08-03 | 1 | 189 | 100 |
| aider | 2026-07-27..2026-08-03 | 2 | 189 | 89 |
| aider | 2026-08-03..2026-08-10 | 1 | 164 | 100 |
| aider | 2026-08-03..2026-08-10 | 2 | 166 | 66 |
| aider | 2026-08-10..2026-08-17 | 1 | 161 | 100 |
| aider | 2026-08-10..2026-08-17 | 2 | 176 | 76 |
| aider | 2026-08-17..2026-08-24 | 1 | 206 | 100 |
| aider | 2026-08-17..2026-08-24 | 2 | 203 | 100 |
| aider | 2026-08-17..2026-08-24 | 3 | 203 | 3 |
| aider | 2026-08-24..2026-08-31 | 1 | 150 | 100 |
| aider | 2026-08-24..2026-08-31 | 2 | 169 | 69 |
| claude-coauthor | 2026-06-01..2026-06-08 | 1 | 1797 | 100 |
| claude-coauthor | 2026-06-01..2026-06-08 | 2 | 1799 | 100 |
| claude-coauthor | 2026-06-01..2026-06-08 | 3 | 1799 | 100 |
| claude-coauthor | 2026-06-08..2026-06-15 | 1 | 2242 | 100 |
| claude-coauthor | 2026-06-08..2026-06-15 | 2 | 2242 | 100 |
| claude-coauthor | 2026-06-08..2026-06-15 | 3 | 2242 | 100 |
| claude-coauthor | 2026-06-15..2026-06-22 | 1 | 3568 | 100 |
| claude-coauthor | 2026-06-15..2026-06-22 | 2 | 3591 | 100 |
| claude-coauthor | 2026-06-15..2026-06-22 | 3 | 3591 | 100 |
| claude-coauthor | 2026-06-22..2026-06-29 | 1 | 3370 | 100 |
| claude-coauthor | 2026-06-22..2026-06-29 | 2 | 3376 | 100 |
| claude-coauthor | 2026-06-22..2026-06-29 | 3 | 3376 | 100 |
| claude-coauthor | 2026-06-29..2026-07-06 | 1 | 4455 | 100 |
| claude-coauthor | 2026-06-29..2026-07-06 | 2 | 4479 | 100 |
| claude-coauthor | 2026-06-29..2026-07-06 | 3 | 4479 | 100 |
| claude-coauthor | 2026-07-06..2026-07-13 | 1 | 5053 | 100 |
| claude-coauthor | 2026-07-06..2026-07-13 | 2 | 5065 | 100 |
| claude-coauthor | 2026-07-06..2026-07-13 | 3 | 5065 | 100 |
| claude-coauthor | 2026-07-13..2026-07-20 | 1 | 4812 | 100 |
| claude-coauthor | 2026-07-13..2026-07-20 | 2 | 4809 | 100 |
| claude-coauthor | 2026-07-13..2026-07-20 | 3 | 4809 | 100 |
| claude-coauthor | 2026-07-20..2026-07-27 | 1 | 4639 | 100 |
| claude-coauthor | 2026-07-20..2026-07-27 | 2 | 4631 | 100 |
| claude-coauthor | 2026-07-20..2026-07-27 | 3 | 4631 | 100 |
| claude-coauthor | 2026-07-27..2026-08-03 | 1 | 4564 | 100 |
| claude-coauthor | 2026-07-27..2026-08-03 | 2 | 4537 | 100 |
| claude-coauthor | 2026-07-27..2026-08-03 | 3 | 4537 | 100 |
| claude-coauthor | 2026-08-03..2026-08-10 | 1 | 5006 | 100 |
| claude-coauthor | 2026-08-03..2026-08-10 | 2 | 5053 | 100 |
| claude-coauthor | 2026-08-03..2026-08-10 | 3 | 5053 | 100 |
| claude-coauthor | 2026-08-10..2026-08-17 | 1 | 5184 | 100 |
| claude-coauthor | 2026-08-10..2026-08-17 | 2 | 5209 | 100 |
| claude-coauthor | 2026-08-10..2026-08-17 | 3 | 5209 | 100 |
| claude-coauthor | 2026-08-17..2026-08-24 | 1 | 5689 | 100 |
| claude-coauthor | 2026-08-17..2026-08-24 | 2 | 5650 | 100 |
| claude-coauthor | 2026-08-17..2026-08-24 | 3 | 5650 | 100 |
| claude-coauthor | 2026-08-24..2026-08-31 | 1 | 4841 | 100 |
| claude-coauthor | 2026-08-24..2026-08-31 | 2 | 5623 | 100 |
| claude-coauthor | 2026-08-24..2026-08-31 | 3 | 5623 | 100 |
| claude-code-gen | 2026-06-01..2026-06-08 | 1 | 84962 | 100 |
| claude-code-gen | 2026-06-01..2026-06-08 | 2 | 85270 | 100 |
| claude-code-gen | 2026-06-01..2026-06-08 | 3 | 85270 | 100 |
| claude-code-gen | 2026-06-08..2026-06-15 | 1 | 100014 | 100 |
| claude-code-gen | 2026-06-08..2026-06-15 | 2 | 100303 | 100 |
| claude-code-gen | 2026-06-08..2026-06-15 | 3 | 100303 | 100 |
| claude-code-gen | 2026-06-15..2026-06-22 | 1 | 108214 | 100 |
| claude-code-gen | 2026-06-15..2026-06-22 | 2 | 108361 | 100 |
| claude-code-gen | 2026-06-15..2026-06-22 | 3 | 108361 | 100 |
| claude-code-gen | 2026-06-22..2026-06-29 | 1 | 104855 | 100 |
| claude-code-gen | 2026-06-22..2026-06-29 | 2 | 105213 | 100 |
| claude-code-gen | 2026-06-22..2026-06-29 | 3 | 105213 | 100 |
| claude-code-gen | 2026-06-29..2026-07-06 | 1 | 120074 | 100 |
| claude-code-gen | 2026-06-29..2026-07-06 | 2 | 120410 | 100 |
| claude-code-gen | 2026-06-29..2026-07-06 | 3 | 120410 | 100 |
| claude-code-gen | 2026-07-06..2026-07-13 | 1 | 124665 | 100 |
| claude-code-gen | 2026-07-06..2026-07-13 | 2 | 124633 | 100 |
| claude-code-gen | 2026-07-06..2026-07-13 | 3 | 124633 | 100 |
| claude-code-gen | 2026-07-13..2026-07-20 | 1 | 120411 | 100 |
| claude-code-gen | 2026-07-13..2026-07-20 | 2 | 120238 | 100 |
| claude-code-gen | 2026-07-13..2026-07-20 | 3 | 120238 | 100 |
| claude-code-gen | 2026-07-20..2026-07-27 | 1 | 113168 | 100 |
| claude-code-gen | 2026-07-20..2026-07-27 | 2 | 112677 | 100 |
| claude-code-gen | 2026-07-20..2026-07-27 | 3 | 112676 | 100 |
| claude-code-gen | 2026-07-27..2026-08-03 | 1 | 109523 | 100 |
| claude-code-gen | 2026-07-27..2026-08-03 | 2 | 108968 | 100 |
| claude-code-gen | 2026-07-27..2026-08-03 | 3 | 108968 | 100 |
| claude-code-gen | 2026-08-03..2026-08-10 | 1 | 106683 | 100 |
| claude-code-gen | 2026-08-03..2026-08-10 | 2 | 106117 | 100 |
| claude-code-gen | 2026-08-03..2026-08-10 | 3 | 106117 | 100 |
| claude-code-gen | 2026-08-10..2026-08-17 | 1 | 107749 | 100 |
| claude-code-gen | 2026-08-10..2026-08-17 | 2 | 107539 | 100 |
| claude-code-gen | 2026-08-10..2026-08-17 | 3 | 107539 | 100 |
| claude-code-gen | 2026-08-17..2026-08-24 | 1 | 110960 | 100 |
| claude-code-gen | 2026-08-17..2026-08-24 | 2 | 110722 | 100 |
| claude-code-gen | 2026-08-17..2026-08-24 | 3 | 110722 | 100 |
| claude-code-gen | 2026-08-24..2026-08-31 | 1 | 99712 | 100 |
| claude-code-gen | 2026-08-24..2026-08-31 | 2 | 113999 | 100 |
| claude-code-gen | 2026-08-24..2026-08-31 | 3 | 113999 | 100 |
| codex | 2026-06-01..2026-06-08 | 1 | 170 | 100 |
| codex | 2026-06-01..2026-06-08 | 2 | 170 | 70 |
| codex | 2026-06-08..2026-06-15 | 1 | 69 | 69 |
| codex | 2026-06-15..2026-06-22 | 1 | 73 | 73 |
| codex | 2026-06-22..2026-06-29 | 1 | 49 | 49 |
| codex | 2026-06-29..2026-07-06 | 1 | 62 | 62 |
| codex | 2026-07-06..2026-07-13 | 1 | 59 | 59 |
| codex | 2026-07-13..2026-07-20 | 1 | 88 | 88 |
| codex | 2026-07-20..2026-07-27 | 1 | 85 | 85 |
| codex | 2026-07-27..2026-08-03 | 1 | 59 | 59 |
| codex | 2026-08-03..2026-08-10 | 1 | 150 | 100 |
| codex | 2026-08-03..2026-08-10 | 2 | 150 | 50 |
| codex | 2026-08-10..2026-08-17 | 1 | 121 | 100 |
| codex | 2026-08-10..2026-08-17 | 2 | 121 | 21 |
| codex | 2026-08-17..2026-08-24 | 1 | 90 | 90 |
| codex | 2026-08-24..2026-08-31 | 1 | 98 | 98 |
| copilot | 2026-06-01..2026-06-08 | 1 | 285 | 100 |
| copilot | 2026-06-01..2026-06-08 | 2 | 285 | 100 |
| copilot | 2026-06-01..2026-06-08 | 3 | 285 | 85 |
| copilot | 2026-06-08..2026-06-15 | 1 | 219 | 100 |
| copilot | 2026-06-08..2026-06-15 | 2 | 219 | 100 |
| copilot | 2026-06-08..2026-06-15 | 3 | 219 | 19 |
| copilot | 2026-06-15..2026-06-22 | 1 | 230 | 100 |
| copilot | 2026-06-15..2026-06-22 | 2 | 230 | 100 |
| copilot | 2026-06-15..2026-06-22 | 3 | 230 | 30 |
| copilot | 2026-06-22..2026-06-29 | 1 | 260 | 100 |
| copilot | 2026-06-22..2026-06-29 | 2 | 260 | 100 |
| copilot | 2026-06-22..2026-06-29 | 3 | 260 | 60 |
| copilot | 2026-06-29..2026-07-06 | 1 | 269 | 100 |
| copilot | 2026-06-29..2026-07-06 | 2 | 269 | 100 |
| copilot | 2026-06-29..2026-07-06 | 3 | 269 | 69 |
| copilot | 2026-07-06..2026-07-13 | 1 | 384 | 100 |
| copilot | 2026-07-06..2026-07-13 | 2 | 384 | 100 |
| copilot | 2026-07-06..2026-07-13 | 3 | 384 | 100 |
| copilot | 2026-07-13..2026-07-20 | 1 | 273 | 100 |
| copilot | 2026-07-13..2026-07-20 | 2 | 273 | 100 |
| copilot | 2026-07-13..2026-07-20 | 3 | 273 | 73 |
| copilot | 2026-07-20..2026-07-27 | 1 | 168 | 100 |
| copilot | 2026-07-20..2026-07-27 | 2 | 168 | 68 |
| copilot | 2026-07-27..2026-08-03 | 1 | 158 | 100 |
| copilot | 2026-07-27..2026-08-03 | 2 | 158 | 58 |
| copilot | 2026-08-03..2026-08-10 | 1 | 185 | 100 |
| copilot | 2026-08-03..2026-08-10 | 2 | 185 | 85 |
| copilot | 2026-08-10..2026-08-17 | 1 | 223 | 100 |
| copilot | 2026-08-10..2026-08-17 | 2 | 223 | 100 |
| copilot | 2026-08-10..2026-08-17 | 3 | 223 | 23 |
| copilot | 2026-08-17..2026-08-24 | 1 | 201 | 100 |
| copilot | 2026-08-17..2026-08-24 | 2 | 201 | 100 |
| copilot | 2026-08-17..2026-08-24 | 3 | 201 | 1 |
| copilot | 2026-08-24..2026-08-31 | 1 | 176 | 100 |
| copilot | 2026-08-24..2026-08-31 | 2 | 200 | 100 |
| cursor | all | 1 | 657 | 100 |
| cursor | all | 2 | 657 | 100 |
| cursor | all | 3 | 671 | 100 |
| cursor | all | 4 | 671 | 100 |
| cursor | all | 5 | 671 | 100 |
| cursor | all | 6 | 671 | 100 |
| devin | all | 1 | 66 | 66 |
| openhands | all | 1 | 63 | 63 |
| robot-gen | all | 1 | 1217473 | 100 |
| robot-gen | all | 2 | 1249258 | 100 |
| robot-gen | all | 3 | 1249292 | 100 |
| robot-gen | all | 4 | 1249314 | 100 |
| robot-gen | all | 5 | 1249316 | 100 |
| robot-gen | all | 6 | 1249316 | 100 |
| sweep | all | 1 | 121 | 100 |
| sweep | all | 2 | 121 | 21 |

Search-call accounting: 175 stage-1 calls are logged above; the budget counter reads 274 because ~50 further stage-1 calls were discarded and re-run after a process restart lost their pagination cursors, and each stage-3b scoped search also draws on the same 500-call pool.

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
