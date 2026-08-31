# Precedents for Track M — every prior measurement of agent-PR test quality, and the exact gap Track M fills | 2026-08-30 | study-precedent-scout (swarm agent) | NOT instrument-biased (HN+GitHub = **7.4%** by distinct URL, 4.5% by distinct source work — verifier recount, far below the 70% threshold); **arXiv-dominant** (81.5% by URL) — see Instrument log | fix pass applied 2026-08-30

## Summary (answers: has anyone published the Track M quantity?)

No. Nobody has run an agent PR's **own added tests against the PR's base commit** on a real-world corpus and published the pass-on-base rate. Four groups came close and each stopped one step short:
1. **SWE-bench (2023)** performs exactly this execution (`log_pre` / `log_post`) but uses it as a *construction filter* and reports only survivors (11,407 → 2,294 = 79.9% discarded), never separating "did not discriminate" from "did not build".
2. **BSG-VA (arXiv 2607.28871, 2026-07-30)** does the differential replay and reports **46.0% of positive comparable events carry no bug-discriminating information** — but on 110 *benchmark* tasks / 643 agent rollouts, not merged real-world PRs.
3. **"Test Coverage Analysis of Agentic Pull Requests" (arXiv 2607.18057, 2026-07-20)** builds and instruments real AIDev agent PRs at scale but measures **diff coverage at head only**; the string "discriminat" appears 0 times in the paper.
4. **"All Smoke, No Alarm" (arXiv 2606.18168, 2026-06-16)** reports **80.2% of agent test patches have weak or no explicit oracle signals** — but *statically*, by parsing assertions, with no execution.
Track M = BSG-VA's method × 2607.18057's real-world corpus, reported in SWE-bench's vocabulary. The dominant risk is not novelty, it is **buildability**: jittest measured 71% inconclusive on historical PRs; 2607.18057 measured 61.8% of Python repos buildable at head. Track M's bases sit between those two conditions but were measured under neither, so 29–62% is a bracket, not a forecast — the 2026-09-20 pilot (<30% → shrink the study) stays a live test.

---

## 1. The precedent table

Ordered by closeness to the Track M quantity. "Measured Track M?" = did it run **the PR's own tests** on **the base commit** of a **real merged PR** and report the pass-on-base rate.

| # | Work | Date | Corpus size | Method | Headline number | Measured Track M? |
|---|---|---|---|---|---|---|
| 1 | BSG-VA (arXiv 2607.28871) | 2026-07-30 | 3,730 events, 643 rollouts, 110 tasks | Dynamic: extract test-only patch, replay on buggy state B / candidate S / gold G | **46.0%** of positive comparable events carry no bug-discriminating information | **Nearly.** Right method, right question — wrong population (benchmark rollouts, not merged PRs) |
| 2 | Test Coverage Analysis of Agentic PRs (arXiv 2607.18057) | 2026-07-20 | 4,882 agent PRs (4,350 Python) from AIDev, 448 Python repos | Dynamic: build repo, run full suite with pytest-cov/JaCoCo at head; test-only patch removed to isolate agent tests | Python diff coverage **27.0%**; **64.8%** of Python PRs have no changed line executed by any existing test | **No.** Coverage at head only. Base commit used solely to diff which tests are new |
| 3 | All Smoke, No Alarm (arXiv 2606.18168) | 2026-06-16 | 86,156 test-file patches, 33,596 agent PRs, 2,807 repos | Static: syntactic taxonomy of 8 oracle-signal categories, 384 patches qualitatively coded | **80.2%** of test patches contain weak or no explicit oracle signals | **No.** Zero execution. This is the *static proxy* for Track M's dynamic number |
| 4 | jittest (an independent single-maintainer OSS project) | v0.3.4, 2026-08-20 | 83 historical PRs (Flask, requests, youtube-dl) | Dynamic: 4-verdict differential execution, Ed25519 receipts | **59/83 (71%) `inconclusive`**; 24/83 (29%) definitive | **Method yes, number no.** Explicitly "evaluating execution capability, not estimating global prevalence" |
| 5 | SWE-bench (arXiv 2310.06770) | 2023-10-10 | 93,139 PRs crawled → 2,294 instances, 12 Python repos | Dynamic: apply test patch, run before and after solution patch | 79.9% of post-conversion candidates removed at execution validation (11,407 → 2,294) | **No.** Same execution, used as a filter; discard reasons never disaggregated |
| 6 | SWE-bench Verified (OpenAI) | 2024-08-13 | 1,699 samples annotated by 93 developers → 500 kept | Human annotation of test appropriateness | **61.1%** flagged for unit tests that may unfairly mark valid solutions incorrect; 68.3% filtered overall | **No — and it measured the opposite failure** (tests too strict, not too weak), by judgment not execution |
| 7 | METR, "Many SWE-bench-passing PRs would not be merged" | 2026-03-10 | 296 AI PRs + 47 golden, 4 maintainers, 3 repos | Human maintainer review of benchmark patches | Grader **24.2pp** (SE 2.7) above maintainer merge decision; golden baseline 68% | **No — and explicitly excluded.** "We ask them to ignore testing requirements in the PR" |
| 8 | Do Autonomous Agents Contribute Test Code? (arXiv 2601.03556) | 2026-01-07 | AIDev | Descriptive: test presence, timing, size, merge outcome | Test-containing PRs larger, slower, similar merge rates | **No.** Presence, not quality |
| 9 | UTBoost (arXiv 2506.09289) | 2025-06-10 | SWE-bench Lite / Verified | LLM-generated test augmentation of benchmark instances | 36 instances with insufficient tests; **345 erroneous patches** mislabeled as passed; 40.9% of SWE-bench Lite leaderboard entries affected | **No.** Proves benchmark tests are too weak, on the benchmark |
| 10 | Are "Solved Issues" Really Solved Correctly? (arXiv 2503.15223) | 2025-03-19 | SWE-bench Verified, 3 tools | PatchDiff differential patch testing | **7.8%** of patches pass but fail the developer test suite; **29.6%** behaviorally diverge from ground truth | **No.** Differential between *patches*, not tests-on-base |
| 11 | TestGen-LLM at Meta (arXiv 2402.09171) | 2024-02-14 | Instagram/Facebook test-a-thons | Filter cascade on LLM-improved tests | **75%** built, **57%** passed reliably, **25%** increased coverage | **No.** Industrial precedent for filtering on *measurable improvement*, not for base-discrimination |
| 12 | JIT Catching Test Generation at Meta (arXiv 2601.22832) | 2026-01-30 | 22,126 generated tests | Code-change-aware catching-test generation | 4x over hardening tests, 20x over coincidentally failing tests; assessors cut review load 70%; 41 reported, 8 confirmed | **No — but it names the category.** "catching tests are meant to fail" |
| 13 | Coverage/mutation replicability (arXiv 2607.22880) | 2026-07-24 | LLM-generated suites, multiple models | Replication of Inozemtseva / Papadakis | Proxy metrics unreliable **exactly in the bug-exposing setting** | **No.** Kills coverage/mutation as substitutes for Track M's number |
| 14 | TestGenEval (arXiv 2410.00752) | 2024-10-01 | 68,647 tests, 1,210 file pairs, 11 repos | Benchmark for test generation | GPT-4o average coverage **35.2%** | **No** |
| 15 | Post-Merge Fate of Agentic Code (arXiv 2607.09902) | 2026-07-10 | 182 repos, longitudinal | Post-merge maintenance tracking | Agentic contributions need significantly more corrective maintenance; +10pp no-review rate → ~6% more agentic maintenance burden | **No — but it is Track M's downstream validation** |

---

## 2. The load-bearing primary sources, verbatim

### 2.1 jittest — the buildability prior (re-fetched today, exact)

Source: `https://raw.githubusercontent.com/Kartik24Hulmukh/jittest/main/README.md`, fetched 2026-08-30 by `curl -sS -A "venture-research/2 (+https://github.com/Alex-lop/venture)"`, HTTP 200, 6,923 bytes.

Session 1's "59/83 = 71% inconclusive" **reproduces exactly**. Verbatim:

> ## The measured status — we publish our denominator
>
> Layer-1 sweep over a frozen benchmark cohort of 83 historical pull requests across Flask, requests, and youtube-dl (evaluating execution capability, not estimating global prevalence). Zero LLM calls, $0.00:
>
> - **83/83** rows attempted, each with a signed receipt
> - **24/83 (29%)** executed to a definitive verdict
> - **5/11** executed bug rows caught with signed proof (`proven_catch`)
> - **0/13** executed controls false-fired
> - **59/83 signed refusals** (`inconclusive`) — historical revisions whose
>   environments could not be restored. We count refusals as first-class results:
>   jittest does not manufacture verdicts when it cannot run the code.

Arithmetic check: 59 / 83 = 0.7108 = **71.1%**; 24 / 83 = 0.2892 = **28.9%**. Both round as cited.

The verdict taxonomy, verbatim:

> | `proven_catch` | test passes on base, fails on head — it discriminates; signed proof |
> | `refuted` | test fails on both — the claim did not hold |
> | `non_discriminating` | test passes on both — proves nothing about the change |
> | `inconclusive` | environment could not be built — a loud refusal, never a guess |

Two things Session 1's files should record and did not:

- **jittest's own scope disclaimer is explicit and self-limiting**: "evaluating execution capability, not estimating global prevalence" and, under Honest boundaries, "Historical environment decay is real: on older revisions jittest will often refuse (`inconclusive`) rather than guess. That is the feature." **jittest does not claim to have measured the Track M quantity, and says so.** Using 71% as a general buildability prior for Track M over-applies it: Track M's bases are days-to-weeks old, jittest's are years old.
- **jittest's `proven_catch` is semantically inverted from the fix-verification framing** — "test passes on base, fails on head" is *regression* catching (Meta's JIT-catching-test framing, which jittest cites as its origin). Track M's quantity is the complement of the *fix*-verification direction: a PR's new test that fails on base and passes on head is SWE-bench's FAIL_TO_PASS. Track M must not borrow jittest's `proven_catch` label without flipping it, or the write-up will contradict SWE-bench's vocabulary.

PyPI metadata (see instrument-log caveat — this fetch violated robots.txt): version 0.3.4, uploaded 2026-08-20T17:45:58Z, summary "Differential test-execution gate for agent-authored pull requests with Ed25519-signed receipts."

### 2.2 SWE-bench — Track M's method and vocabulary, used as a filter and thrown away

Source: `https://arxiv.org/html/2310.06770v3`, fetched 2026-08-30 via `curl -L`, HTTP 200, 1,275,988 bytes. Metadata via `https://export.arxiv.org/api/query?id_list=2310.06770`, re-fetched 2026-08-30: **v3, published 2023-10-10** (`<published>2023-10-10T16:47:29Z</published>`), **last updated 2024-11-11** (`<updated>2024-11-11T23:05:04Z</updated>`). The "2026-08-31" in the first draft was the API *feed's* own `<updated>` element, not the paper's — corrected in the fix pass.

**This is the single most important precedent, because SWE-bench already ran the Track M experiment and did not report it.** Main-text construction, verbatim:

> Stage III: Execution-based filtering. For each candidate task, we apply the PR's test content, and log the associated test results before and after the PR's other content is applied. We filter out task instances without at least one test where its status changes from a fail to pass (henceforth referred to as fail-to-pass test). We also filter out instances that result in installation or runtime errors.

Appendix, on the same step, verbatim:

> If any of the steps (a) through (f) fails, the candidate task instance is discarded from consideration. With moderate variation across repositories, we observe that this step generally removes half of the candidate task instances.

And the four-quadrant vocabulary, verbatim:

> from their respective log_pre and log_post test-to-status mappings, we create a test results data structure where the keys are FAIL_TO_FAIL, FAIL_TO_PASS, PASS_TO_FAIL, and PASS_TO_PASS, and the values are lists of tests.

Field definitions, verbatim from Table 9:

> FAIL_TO_PASS (list) List of tests that change in status from fail to pass
> PASS_TO_PASS (list) List of tests that change in status from pass to pass

Table 10 funnel (verbatim totals): **93,139 PRs crawled → 11,407 post-conversion → 2,294 post-validation (final)**.

Derived (my arithmetic, from the verbatim table): 2,294 / 11,407 = 20.11% kept, so **79.89% of post-conversion candidates were removed at execution-based validation**. 2,294 / 93,139 = **2.46%** of crawled PRs survived end to end.

**Why this is not the Track M number, and this is the crux of the whole artifact.** The 79.9% conflates at least four causes the paper never separates: (i) install/runtime error, (ii) `ImportError`/`AttributeError` in `log_pre`, (iii) no test changed fail→pass, (iv) other conversion failures. Cause (iii) *is* Track M's numerator; causes (i)–(ii) are Track M's buildability denominator problem. **A 2023 corpus of human PRs in 12 elite repos already showed the joint rate is ~80%, and nobody has ever split it.** Track M's contribution is precisely that split, on agent PRs, in 2026.

Note also the population: SWE-bench's instances are drawn from PRs that *resolve an issue and add tests* — the most favourable case. And they are **human** PRs, giving Track M a free human baseline to compare against.

### 2.3 SWE-bench Verified — the opposite failure, measured by judgment

Source: `https://openai.com/index/introducing-swe-bench-verified/`, fetched 2026-08-30 via `curl -L`, HTTP 200, 556,515 bytes. robots.txt: `User-agent: * / Allow: /` (only `/microsoft-for-startups/` disallowed) — permitted. Page date stamp "August 13, 2024" (a second stamp, "August 5, 2024", also appears in the page source; the later is used).

Verbatim:

> We worked with 93 software developers experienced in Python to manually screen SWE-bench samples for quality. We annotated 1,699 random samples from the SWE-bench test set to produce SWE-bench Verified.

> We see that 38.3% of samples were flagged for underspecified problem statements, and 61.1% were flagged for unit tests that may unfairly mark valid solutions as incorrect. Overall, our annotation process resulted in 68.3% of SWE-bench samples being filtered out due to underspecification, unfair unit tests, or other issues.

And the definition Track M should quote when it introduces its terms:

> These unit tests fail before the solution code in the PR is added, but pass afterwards, and are therefore called FAIL_TO_PASS tests. Each sample also has associated PASS_TO_PASS tests, which pass both before and after the PR is merged, and are used to check that existing unrelated functionality in the codebase has not been broken by the PR.

Two consequences for Track M:

- **The 61.1% is the mirror image of Track M's question.** SWE-bench Verified asked "are these tests *too strict*?" (rejecting valid solutions). Track M asks "are these tests *too weak*?" (accepting anything). Nobody has run the weak direction on real PRs. Track M should say this explicitly in its abstract — it is the cleanest one-sentence novelty claim available.
- **PASS_TO_PASS is a desirable category in SWE-bench.** This is the single largest threat to Track M's framing (see Objection 3). A test that passes on base and on head is exactly what a regression test is supposed to do. Track M's headline cannot be "PASS_TO_PASS tests are bad"; it must be "the PR's *newly added* tests contain **zero** FAIL_TO_PASS members."

Also verbatim, the environment problem, named by OpenAI two years before Track M has to solve it:

> It is sometimes difficult to reliably set up the SWE-bench development environments for the agents, inadvertently causing unit tests to fail regardless of the solution. In such cases, perfectly valid solutions might be graded as incorrect.

### 2.4 BSG-VA — the closest published work, on the wrong population

Source: `https://export.arxiv.org/api/query?id_list=2607.28871`, fetched 2026-08-30, HTTP 200. Title: *Validation Evidence in LLM Repair Agents: How Much of What Passes Actually Tests the Bug?* Authors: Xiaonan Xu, Wenjing Wu. Published 2026-07-30. Categories cs.SE, cs.AI.

Verbatim from the abstract:

> When a repair agent runs a test and sees it pass, the result is treated as evidence about the reported defect. We measure how often that treatment is warranted. BSG-VA (buggy-state/candidate-state/gold-fix validation analysis) captures each validation command at its exact working-tree state, extracts a test-only patch, and replays the command on the original buggy code (B), the candidate state (S), and the developer gold fix (G). The captured outcome and the replay results assign every event an evidence role, from gold-aligned bug-discriminating through regression-only to misleading. Across 3,730 events in 643 rollouts on 110 tasks, 46.0% of positive comparable events carry no bug-discriminating information; 23.8% of baseline rollouts, with no feedback injected, close with a patch whose entire positive evidence base is of this kind.

> BSG-VA applies post hoc to any replayable repair trajectory that preserves the required code states and execution environment.

**This is Track M's method, published five weeks ago, and Track M must cite it as the direct antecedent, not as related work.** Its limits define Track M's opening:

- Population is **agent rollouts on 110 benchmark tasks**, not merged PRs in the wild. There is no repository, no maintainer, no merge decision, no lockfile.
- It requires a **replayable trajectory** — access to the agent's own validation commands at working-tree state. Track M has none of that; it has a merged diff and a base SHA. Different instrument, same quantity.
- It measures **evidence events**, not PRs, and its unit ("positive comparable events") is not the unit a practitioner cares about ("this PR").
- The paper's own intervention result is a **null relative to its pre-registered threshold**: "Both estimates fall below the prespecified 10-percentage-point smallest effect size of interest, so practical magnitude remains uncertain." Track M should not cite the 7.8pp as a demonstrated fix.

The three arXiv items jittest lists under "Prior Art & Citations" (2601.22832 JIT catching at Meta, 2607.14890 Proof-or-Stop, 2607.28871 BSG-VA) were all **verified to exist with matching titles** via the arXiv API today. jittest's characterisation of 2607.28871's effect size ("+7.8pp ... below the authors' pre-registered 10pp") matches the abstract **in substance but not word-for-word** — jittest writes "pre-registered" where the abstract says "prespecified 10-percentage-point smallest effect size of interest". Not a quote; a faithful paraphrase.

### 2.5 Test Coverage Analysis of Agentic PRs — the real-world corpus, the wrong measurement, and the best buildability prior in existence

Source: `https://arxiv.org/html/2607.18057v1`, fetched 2026-08-30 via `curl -L`, HTTP 200, 158,274 bytes.

Verbatim from the abstract:

> we analyze 4882 agent-generated PRs from the AIDev dataset (532 Java and 4350 Python PRs) produced by five coding agents. [...] Agents include test changes in only 49.6% of PRs that change code under test files. Existing tests provide an incomplete safety net: they cover 61.5% of agents' changed executable lines in Java and only 27.0% in Python, where 64.8% of PRs have no changed line executed by any existing test. Agent-written tests improve coverage over existing tests, but only in a minority of PRs: 35.9% of Java and 22.5% of Python Code + Tests PRs show a coverage gain.

**Confirmation that it does not measure Track M's quantity** — full-text keyword counts on the fetched HTML (38,631 chars of extracted text): `discriminat` **0**, `FAIL_TO_PASS` **0**, `pass on both` **0**, `base commit` **1**. The single `base commit` occurrence is diffing only, verbatim:

> For each hunk, we compute the set of test-method declarations in the post-change version of the hunk (i.e., the file content at the PR's head commit) minus those in the pre-change version (i.e., the content at the base commit); the difference identifies tests introduced, not merely edited, by the PR.

**The buildability number Track M's 2026-09-20 gate needs, verbatim:**

> PR-level coverage. For each PR, we execute the repository's entire test suite, collecting line coverage with JaCoCo for Java and pytest-cov for Python. Of the repositories in the coverage subset (Section II), 10 of the 14 Java and 34 of the 55 Python repositories could be built and instrumented, yielding coverage results for 213 of the 532 Java PRs and 1664 of the 4350 Python PRs.

Derived (my arithmetic): Python repos built and instrumented = 34 / 55 = **61.8%**. Python PRs yielding coverage = 1,664 / 4,350 = **38.3%** — but note the 4,350 denominator includes PRs from repos excluded by their own "≥10 agentic PRs" filter, so 38.3% is a *lower bound* on the per-eligible-repo rate and **61.8% is the number to plan against**.

**This is the most decision-relevant finding in this artifact.** Track M's kill gate is "<30% base builds → publish the buildability finding and shrink the study." Two priors now bracket it:
- jittest, **29%** definitive — historical PRs, years-old revisions, environment decay, worst case.
- 2607.18057, **61.8%** of Python repos built and instrumented at head — current repos with active agent PRs, best case.

Neither prior was measured under Track M's conditions, and they differ from it in **both** directions: 2607.18057 built at *head*, with no lockfile requirement and no network-free install; jittest built years-old revisions with no lockfile filter at all. Track M measures **base** commits under `--network none` in repos pre-filtered for a lockfile — the lockfile filter should help, `--network none` should hurt, and nobody has published the net. So the honest reading is a **bracket, not a forecast: the plausible base-build rate lies somewhere in the region of 29–62%**, a range whose bottom end (29%) sits *below* the 30% gate. The corpus README's stated fear — "if most bases will not build hermetically" — is *narrowed* by published evidence, not answered by it.

**The 2026-09-20 pilot therefore stays a real test with a real chance of failing.** A result below 30% is a live outcome, not a formality, and it triggers the §9 fallback unchanged: publish the buildability finding itself and shrink the study to the buildable set. (Corrected in the fix pass: the first draft of this section concluded the gate was "very likely to pass" and that the pilot was a confirmation rather than an open question. That is the pre-satisfied gate CLAUDE.md §8 forbids, and the priors do not support it.)

Also note: they **already use the test-only-patch mechanism** Track M needs — "The test-only patch enables us to remove those tests selectively during coverage measurement." Track M applies the same extraction in the other direction (apply the test-only patch to base). Cite it for the mechanism.

### 2.6 All Smoke, No Alarm — the static proxy that Track M is the ground truth for

Source: `https://export.arxiv.org/api/query?id_list=2606.18168`, fetched 2026-08-30, HTTP 200. Published 2026-06-16.

Verbatim from the abstract:

> Test files lacking explicit assertions execute code without verifying behavior, so quality gates based on test-file presence overestimate verification strength. [...] We conduct an empirical study of 86,156 test-file patches from 33,596 agent-authored PRs across 2,807 GitHub repositories produced by five coding agents: OpenAI Codex, GitHub Copilot, Devin, Cursor, and Claude Code. A qualitative analysis of 384 stratified patches informs a syntactic taxonomy of eight oracle signal categories. Applied at scale, 80.2% of test patches contain weak or no explicit oracle signals. While raw merge rates are lower for strong-oracle PRs, a regression analysis adjusting for agent, PR size, repository popularity, task type, and language shows strong oracles significantly improve merge likelihood (OR = 1.28, p < 0.001).

**Strategic reading.** This is the paper that most threatens Track M's *headline*, because "80.2% of agent test patches have weak or no oracle" already sounds like the answer to the question. It is not, and Track M's positioning depends on saying why in one sentence: **a syntactic assertion count cannot tell you whether a test would have failed on the base commit.** A test with a strong assertion can still pass on base (asserting behaviour the PR did not change); a test with a weak assertion can still fail on base (an import error, a signature change). Track M supplies the execution ground truth for exactly this 80.2% — and can report the **correlation between the static oracle taxonomy and the executed verdict**, which is a second publishable result and costs nothing extra.

Note also: their 33,596 PRs across 2,807 repos versus this venture's corpus of 23 repos. Track M cannot compete on scale and should not try; it competes on the *dynamic* axis, where the constraint is compute per PR, not sample count.

### 2.7 METR — the most-cited adjacent result, and it explicitly excluded tests

Source: `https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/`, fetched 2026-08-30 via `curl -L`, HTTP 200, 245,202 bytes. robots.txt permits: re-fetched 2026-08-30, it disallows **three PDFs and one draft path** (`/evaluating-ai-models-for-critical-harms.pdf`, `/may-2025-progress-report.pdf`, `/2024-annual-report.pdf`, `/time-horizon-draft`); the note fetched is not among them.

Verbatim:

> To study how agent success on benchmark tasks relates to real-world usefulness, we had 4 active maintainers from 3 SWE-bench Verified repositories review 296 AI-generated pull requests (PRs).

> the automated grader is on average about 24.2 percentage points (standard error: 2.7) higher than the maintainer merge decision.

> as the golden baseline is 68%, if a model gets 34%, then the golden-baseline-adjusted score is 50%.

**The exclusion, verbatim — this is the sentence that opens the door for Track M:**

> Testing Requirements: We ask them to ignore testing requirements in the PR, as agents are not elicited to include proper tests. This is generous to AI-generated patches, as it removes one requirement of a good patch.

METR's study is the strongest evidence that green tests ≠ good patch, and it establishes the *audience* for Track M's number — but it deliberately says nothing about test quality. Track M is the complement METR named and skipped. This corrects the framing in `ideas/r2-ai-pr-verification-gate.md`, which leans on METR as pain evidence for test non-discrimination; the verifier note already flagged this and it is confirmed today at the primary source.

### 2.8 Everything else, briefly (all verified via arXiv API, 2026-08-30)

- **UTBoost (2506.09289, 2025-06-10):** "the manually written test cases included in these pull requests are often insufficient, allowing generated patches to pass the tests without resolving the underlying issue" — **345 erroneous patches** incorrectly labeled as passed; affects 40.9% of SWE-bench Lite and 24.4% of SWE-bench Verified leaderboard entries. This is the "weak tests" critique Track M should cite for the claim that *human*-written PR tests are also often insufficient.
- **Are "Solved Issues" Really Solved Correctly? (2503.15223, 2025-03-19):** PatchDiff differential patch testing; **7.8%** of patches count as correct while failing the developer-written test suite; **29.6%** of plausible patches induce different behavior than ground truth. Differential *between patches*, not tests-on-base.
- **Investigating Test Overfitting on SWE-bench (2511.16858, 2025-11-20):** "the first empirical study of test overfitting in this setting" — code that "technically passes observed tests but actually misses important cases."
- **TestGen-LLM at Meta (2402.09171, 2024-02-14):** filter cascade — "75% of TestGen-LLM's test cases built correctly, 57% passed reliably, and 25% increased coverage." **The 57% is the flakiness prior Track M needs** (see Objection 4).
- **JIT Catching Test Generation at Meta (2601.22832, 2026-01-30):** "Unlike traditional hardening tests, which pass at generation time, catching tests are meant to fail, surfacing bugs before code lands." Names the hardening/catching distinction Track M is measuring. 22,126 generated tests analysed.
- **Coverage/mutation replicability (2607.22880, 2026-07-24):** proxy metrics are unreliable "in another common scenario where the code-under-test may already be buggy and the goal is to expose the bug" — i.e. **exactly Track M's setting**. This is the citation that forecloses "why not just use mutation score?"
- **Post-Merge Fate of Agentic Code (2607.09902, 2026-07-10):** 182 repos; agentic contributions "require significantly higher rates of corrective maintenance and introduce more security weaknesses"; each 10pp increase in no-review rate → ~6% more agentic maintenance burden. Track M's outcome variable if it ever wants to show non-discrimination *predicts* downstream defects.
- **Do Autonomous Agents Contribute Test Code? (2601.03556, 2026-01-07):** descriptive test inclusion on AIDev; no quality measurement.
- **AIDev (2507.15003, 2025-07-20):** "Spanning over 456,000 pull requests by five leading agents—OpenAI Codex, Devin, GitHub Copilot, Cursor, and Claude Code—across 61,000 repositories and 47,000 developers"; "although agents often outperform humans in speed, their PRs are accepted less frequently, revealing a trust and utility gap."
- **UNVERIFIED — not fetched this session:** SWE-bench Pro (2509.16941), SWE-bench Live (2505.23419), SWE-bench Multimodal (2410.03859), Multi-SWE-bench (2504.02605), SWE-smith, SWE-Gym, GitClear 2025, DORA 2025 AI section, Stanford/Denisov-Blanch, Uplevel, GitHub's own Copilot coding-agent statistics, Cursor/Anthropic/Sourcegraph/Graphite/CodeRabbit blog measurements. Titles for the SWE-bench-family items were confirmed via the arXiv title search; their contents were not read. **None of them is likely to change the gap** — every SWE-bench derivative inherits the same FAIL_TO_PASS construction filter and therefore has the same blind spot — but that expectation is an inference, not a measurement, and is marked as such.

---

## The gap

### What nobody has published

**The Track M quantity: across public repositories with green, lockfile-runnable Python test suites and merged, agent-trailered pull requests, the fraction of those PRs whose own newly-added tests contain zero FAIL_TO_PASS members — that is, every test the PR adds already passes at the PR's base commit.**

Four properties must hold simultaneously, and no published work has all four:

| Property | Who has it | Who lacks it |
|---|---|---|
| (a) **Real merged PRs in the wild** (not benchmark instances, not rollouts) | 2607.18057, 2606.18168, 2601.03556, 2607.09902 | SWE-bench, SWE-bench Verified, METR, BSG-VA, UTBoost, 2503.15223, jittest |
| (b) **Agent-authored**, identified by trailer | AIDev-derived work; jittest (no) | SWE-bench family, METR, TestGen-LLM |
| (c) **The PR's own tests executed on the base commit** | SWE-bench (as a filter), BSG-VA, jittest | 2607.18057, 2606.18168, 2601.03556, METR, TestGenEval |
| (d) **The pass-on-base rate reported as the result**, with its denominator | **nobody** | everybody |

The closest single work, BSG-VA, has (b), (c) and (d) but not (a). The closest real-world work, 2607.18057, has (a) and (b) but measures coverage, not discrimination. The intersection is empty. Track M is a real, narrow, one-number contribution — **and it is narrow enough that the write-up must state the four properties in the abstract or a reviewer will file it as a duplicate of one of the four.**

### The falsifier for novelty — the exact search that would find a duplicate

Run these four and read every title; if any hit satisfies all of (a)–(d), Track M is a duplicate and should be re-scoped to the static-vs-dynamic correlation study instead.

```bash
UA="venture-research/2 (+https://github.com/Alex-lop/venture)"
# 1. The search that surfaced every near-neighbour in this artifact:
curl -sS -A "$UA" "https://export.arxiv.org/api/query?search_query=all:%22agentic%20pull%20requests%22&max_results=50&sortBy=submittedDate&sortOrder=descending"
# 2. The broader net. NOT a superset of #1 — run both, they are complements.
#    Re-run 2026-08-30: HTTP 200, totalResults = 90. At max_results=40 it silently dropped
#    half the corpus; at max_results=100 all 90 return and 6 of #1's 19 IDs are STILL absent
#    (2601.03556 = table row 8, 2601.17413, 2601.18749, 2602.17955, 2606.06752, 2606.13449).
curl -sS -A "$UA" "https://export.arxiv.org/api/query?search_query=all:%22coding%20agent%22%20AND%20all:%22pull%20requests%22&max_results=100&sortBy=submittedDate&sortOrder=descending"
# 3. Version bumps on the four near-duplicates — a v2 that adds base-replay kills the study:
curl -sS -A "$UA" "https://export.arxiv.org/api/query?id_list=2607.18057,2606.18168,2601.03556,2607.28871"
# 4. Semantic Scholar (rate-limited today; retry with >5s spacing):
curl -sS -A "$UA" "https://api.semanticscholar.org/graph/v1/paper/search?query=agent+pull+requests+tests&year=2026&fields=title,year,externalIds,abstract"
```

**Re-run #1, #2 and #3 the week before publication (target 2026-10-10)** — #2 at `max_results=100`, and read #1's and #2's hits separately, because neither contains the other. Search #1 returned 19 results today spanning 2026-01 to 2026-08 and is the single highest-yield query found.

**A caveat that must be stated in the write-up, because it weakens the novelty claim:** the arXiv API searches **metadata only, not full text**. Confirmed today — `all:"FAIL_TO_PASS"` returns **0 results** even though SWE-bench and its entire derivative family use the token throughout. So `all:"non-discriminating tests"` returning 0 and `abs:"pass on the base commit"` returning 0 are **weak** evidence of absence, not strong. The strong evidence is the positive one: the four nearest papers were read and each demonstrably lacks a required property.

### The vocabulary and method Track M should adopt and cite

**Adopt SWE-bench's vocabulary wholesale. Do not invent terms.** Specifically:

1. **FAIL_TO_PASS / PASS_TO_PASS / FAIL_TO_FAIL / PASS_TO_FAIL** (Jimenez et al. 2023), and `log_pre` / `log_post` for the two runs. Track M's headline metric is then stateable in one line that any SWE-bench reader parses instantly: *"the share of merged agent PRs whose added tests yield an empty FAIL_TO_PASS set."* Every reviewer in this field already knows these four tokens. Coining "non-discriminating" as a *primary* term costs comprehension; use it as the plain-English gloss and keep FAIL_TO_PASS as the operational definition.
2. **AIDev's trailer taxonomy and five-agent frame** (Li, Zhang & Hassan, arXiv 2507.15003): OpenAI Codex, Devin, GitHub Copilot, Cursor, Claude Code. The corpus already uses trailers; align the *names and grouping* with AIDev so results are comparable, and report per-agent breakdowns as 2606.18168 and 2607.18057 both do. **Consider using AIDev itself as the sampling frame** rather than re-running GitHub search — the corpus README documents severe recall loss from the 1,000-result cap and from `search/issues` not indexing commit messages, and AIDev has 456,000 PRs with none of those problems.
3. **BSG-VA's evidence-role language** (arXiv 2607.28871): "bug-discriminating", "regression-only", "misleading", and the test-only-patch extraction plus replay. Track M is BSG-VA-in-the-wild and should say so in the first paragraph.
4. **jittest's `inconclusive` as a first-class published verdict** — "We count refusals as first-class results" and "we publish our denominator." Track M's credibility rests entirely on this. Report the build-failure rate *before* the headline, in the abstract.
5. **2607.18057's test-only-patch extraction** for isolating the PR's own tests, and its buildability numbers (34/55 Python repos) as the planning prior — not jittest's 29%.
6. **Meta's hardening/catching distinction** (arXiv 2601.22832) for the framing sentence: a test that passes on base is a *hardening* test; the PR claims to have written a *catching* test.

### The three biggest methodological objections a reviewer will raise

**Objection 1 — "You cannot tell a non-discriminating test from an environment you failed to build."**
*Raised by:* OpenAI in SWE-bench Verified — "It is sometimes difficult to reliably set up the SWE-bench development environments for the agents, inadvertently causing unit tests to fail regardless of the solution. In such cases, perfectly valid solutions might be graded as incorrect." Demonstrated by jittest at **71% inconclusive**, and by SWE-bench's own undifferentiated **79.9%** discard. This is the study's existential risk and its reviewers know it.
*What Track M must do:* three-way outcome per PR — `discriminating` / `non_discriminating` / `unresolved` — never two-way; publish the unresolved rate first; require the base suite to be **green before the test patch is applied** as an admission criterion (a base that is already red is unresolved, not a result); and record a per-PR failure *reason* (install, collect, import, timeout) so the denominator is auditable. Report the headline both as a share of *attempted* PRs and as a share of *resolved* PRs, and state that the true value lies between them.

**Objection 2 — "Your buildable subset is the well-maintained tail, which is the population least likely to ship non-discriminating tests, so your estimate is biased downward and you cannot say by how much."**
*Raised by:* this venture's own corpus README ("that minority is exactly the well-maintained subset, which is the population least likely to ship non-discriminating tests. A biased 25% sample cannot answer the question"), and structurally by OpenAI's admission that SWE-bench Verified's filtering "is likely to be overzealous." The corpus's ≥50-star gate alone removed **918 of 1,047 repos**, and 2607.18057's ≥10-agentic-PR filter cut 448 Python repos to 55.
*What Track M must do:* pre-register the direction of the bias and say the number is a **lower bound**; report covariates that are observable for *unbuilt* repos too (stars, agent, PR size, test-file count, conventional-commit type) and show whether the built and unbuilt sets differ on them; and follow the corpus README's own widening plan (drop to ≥10 stars, per-repo scoped search). Do not claim a population estimate. Claim: "among repos where this is measurable at all, X%."

**Objection 3 — "A test that passes on base is often correct behaviour, not a defect."**
*Raised by:* SWE-bench itself, where PASS_TO_PASS is a **desirable** category — "used to check that existing unrelated functionality in the codebase has not been broken by the PR" — and by BSG-VA, whose taxonomy separates "regression-only" from "misleading" precisely because they are not the same failure. A refactor PR *should* ship tests that pass on both sides; so should a docs or type-annotation PR; so should a PR that adds coverage to existing untested code (which 2607.18057 shows is badly needed, at 27.0% Python diff coverage).
*What Track M must do:* stratify by PR intent before reporting anything. Use conventional-commit type, which 2607.18057 already extracts at scale from this exact population (Python: feat 2315, fix 1802, docs 1376, test 449, refactor 438). **The headline should be restricted to `fix` PRs** — where a test that passes on base provably would not have caught the bug — with feat/refactor reported separately and explicitly not counted as defects. A headline computed over all PR types will be dismissed as measuring the wrong thing, correctly.

**Honourable mention — Objection 4, "your single run is flaky."** *Raised by:* Meta's TestGen-LLM, whose filter cascade found only **57% passed reliably** against 75% that built at all — an 18-point gap attributable to flakiness alone, at industrial scale. A test that "passes on base" once may be order-dependent, time-dependent, or network-dependent. Track M should run the base suite **at least twice** (SWE-bench's `--network none` posture plus a repeat run) and classify disagreement as `unresolved`, not as a pass.

---

## Suggested citations

Format: `[key] Authors. "Title." Venue/host, date. URL — one line on what Track M takes from it.`

- `[jimenez2023swebench]` Jimenez, Yang, Wettig, Yao, Pei, Press, Narasimhan. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" arXiv:2310.06770, 2023-10-10 (v3 fetched 2026-08-30). https://arxiv.org/abs/2310.06770 — **Vocabulary source.** FAIL_TO_PASS / PASS_TO_PASS / FAIL_TO_FAIL / PASS_TO_FAIL; `log_pre`/`log_post`; the execution-based filter that performs Track M's measurement and discards the result (93,139 → 11,407 → 2,294).
- `[openai2024verified]` OpenAI. "Introducing SWE-bench Verified." openai.com, 2024-08-13. https://openai.com/index/introducing-swe-bench-verified/ — **The mirror-image measurement.** 93 developers, 1,699 samples, 61.1% flagged for unit tests that may unfairly mark valid solutions incorrect; and the canonical plain-English FAIL_TO_PASS/PASS_TO_PASS definitions.
- `[xu2026bsgva]` Xu, Wu. "Validation Evidence in LLM Repair Agents: How Much of What Passes Actually Tests the Bug?" arXiv:2607.28871, 2026-07-30. https://arxiv.org/abs/2607.28871 — **Direct antecedent.** B/S/G replay of test-only patches; 46.0% of positive comparable events carry no bug-discriminating information, on 110 benchmark tasks. Track M is this method on merged real-world PRs.
- `[testcov2026agentic]` "Test Coverage Analysis of Agentic Pull Requests." arXiv:2607.18057, 2026-07-20. https://arxiv.org/abs/2607.18057 — **Corpus shape and buildability prior.** 4,882 AIDev PRs; 34 of 55 Python repos could be built and instrumented (61.8%); Python diff coverage 27.0%; test-only-patch extraction mechanism.
- `[smoke2026oracle]` "All Smoke, No Alarm: Oracle Signals in Agent-Authored Test Code." arXiv:2606.18168, 2026-06-16. https://arxiv.org/abs/2606.18168 — **The static proxy Track M grounds.** 80.2% of 86,156 agent test patches have weak or no explicit oracle signals; strong oracles raise merge odds (OR = 1.28, p < 0.001).
- `[li2025aidev]` Li, Zhang, Hassan. "The Rise of AI Teammates in Software Engineering (SE) 3.0." arXiv:2507.15003, 2025-07-20. https://arxiv.org/abs/2507.15003 — **Sampling frame and agent taxonomy.** 456,000+ PRs, five agents, 61,000 repos; agents' PRs accepted less frequently.
- `[metr2026merge]` METR. "Many SWE-bench-passing PRs would not be merged into main." metr.org, 2026-03-10. https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/ — **The audience, and the explicit exclusion.** 24.2pp (SE 2.7) grader-vs-maintainer gap; "We ask them to ignore testing requirements in the PR."
- `[jittest2026]` jittest (v0.3.4). README, GitHub, fetched 2026-08-30. https://github.com/Kartik24Hulmukh/jittest — **Prior-art disclosure and refusal discipline.** 59/83 (71%) `inconclusive`; the `non_discriminating` token; "We count refusals as first-class results."
- `[harman2026jit]` Harman et al. "Just-in-Time Catching Test Generation at Meta." arXiv:2601.22832, FSE Companion '26, 2026-01-30. https://arxiv.org/abs/2601.22832 — **Framing.** "catching tests are meant to fail"; hardening vs catching; 22,126 tests analysed.
- `[alshahwan2024testgenllm]` Alshahwan et al. "Automated Unit Test Improvement using Large Language Models at Meta." arXiv:2402.09171, 2024-02-14. https://arxiv.org/abs/2402.09171 — **Flakiness prior.** 75% built correctly, 57% passed reliably, 25% increased coverage.
- `[utboost2025]` "UTBoost: Rigorous Evaluation of Coding Agents on SWE-Bench." arXiv:2506.09289, 2025-06-10. https://arxiv.org/abs/2506.09289 — **Human PR tests are weak too.** 345 erroneous patches mislabeled as passed; 40.9% of SWE-bench Lite entries affected.
- `[solved2025really]` "Are 'Solved Issues' in SWE-bench Really Solved Correctly? An Empirical Study." arXiv:2503.15223, 2025-03-19. https://arxiv.org/abs/2503.15223 — **Differential technique, patch-level.** PatchDiff; 7.8% pass but fail the developer suite; 29.6% behaviourally divergent.
- `[proxy2026replic]` "Do Coverage and Mutation Scores of LLM-Generated Test Suites Correlate with Their Effectiveness? (Replicability Study)." arXiv:2607.22880, 2026-07-24. https://arxiv.org/abs/2607.22880 — **Forecloses the substitute.** Proxy metrics unreliable in the bug-exposing setting, which is Track M's setting.
- `[postmerge2026]` "Do These Violent Delights Have Violent Ends? Measuring the Post-Merge Fate of Agentic Code." arXiv:2607.09902, 2026-07-10. https://arxiv.org/abs/2607.09902 — **Downstream outcome.** 182 repos; agentic code needs more corrective maintenance; +10pp no-review rate → ~6% more burden.
- `[testincl2026]` "Do Autonomous Agents Contribute Test Code? A Study of Tests in Agentic Pull Requests." arXiv:2601.03556, 2026-01-07. https://arxiv.org/abs/2601.03556 — **Baseline on test presence**, which Track M assumes and does not re-derive.
- `[testgeneval2024]` Jain et al. "TestGenEval: A Real World Unit Test Generation and Test Completion Benchmark." arXiv:2410.00752, 2024-10-01. https://arxiv.org/abs/2410.00752 — **LLM test-quality ceiling.** 68,647 tests, 11 repos; best model averages 35.2% coverage.
- `[overfit2025]` "Investigating Test Overfitting on SWE-bench." arXiv:2511.16858, 2025-11-20. https://arxiv.org/abs/2511.16858 — Adjacent framing: passing observed tests while missing important cases.

---

## Instrument log

### Venues and APIs tried

| Venue / API | Result | Notes |
|---|---|---|
| `export.arxiv.org/api/query` (arXiv API) | **reachable** | Primary instrument. ~12 queries, all HTTP 200. **Limitation confirmed in-session: metadata-only search.** `all:"FAIL_TO_PASS"` → 0 results despite the token appearing throughout SWE-bench and its derivatives. Null results from this API are weak evidence of absence |
| `arxiv.org/html/<id>` (full-text HTML) | **reachable** | 2310.06770v3 (1,275,988 B), 2607.18057v1 (158,274 B). Both HTTP 200 via `curl -L`. This is how the load-bearing verbatim quotes and keyword counts were obtained |
| `raw.githubusercontent.com` | **reachable** | jittest README, HTTP 200, 6,923 B. `raw.githubusercontent.com/robots.txt` → 404 (no restrictions) |
| `openai.com` | **reachable** | robots.txt: `User-agent: * / Allow: /`, only `/microsoft-for-startups/` disallowed. SWE-bench Verified page HTTP 200, 556,515 B |
| `metr.org` | **reachable** | robots.txt disallows three PDFs and one draft path (`/time-horizon-draft`), not "four PDFs" as first written; the note fetched is not among them. HTTP 200, 245,202 B |
| `pypi.org/pypi/jittest/json` | **reachable but ROBOTS-DISALLOWED — my error** | `pypi.org/robots.txt` contains `Disallow: /pypi/*/json`. I fetched robots.txt and the JSON in the same command and did not read the disallow before the request landed. One request, no retries, and **no further PyPI JSON requests were made**. The two facts taken from it (version 0.3.4, upload 2026-08-20) are also visible on the allowed project page and in the repo's CHANGELOG; treat them as low-confidence pending re-verification from an allowed path. Recording this rather than quietly dropping the citation |
| `api.semanticscholar.org/graph/v1/paper/search` | **429 Too Many Requests** | All 3 queries rate-limited; 0 results retrieved. `api.semanticscholar.org/robots.txt` → 404. Needs an API key or >5s spacing. **This is the largest unclosed hole in the search** — it is the instrument that would catch non-arXiv venues (IEEE, ACM, journal-only work) |
| `gitclear.com`, `dora.dev` | **robots checked, permitted; not fetched** | Ran out of time-box before reaching the industry-report tier. Marked UNVERIFIED in §2.8 |
| Hacker News (Algolia API) | **not tried** | Deliberate. The brief flags HN over-reliance as Session 1's instrument bias; the precedent question is answerable from primary literature and vendor pages, and prior HN evidence for this thesis is already logged in `ideas/r2-ai-pr-verification-gate.md` |
| GitHub `gh api` / code search | **not tried** | Not needed for a precedent survey; corpus construction already used it (`ventures/c-measurement/corpus/README.md`) |
| WebSearch tool | **not used (0 of ~200 calls)** | Everything needed was reachable by `curl` against JSON/HTML APIs. Budget left entirely unspent for other agents |

### Citations by host

| Host | Citations | Share |
|---|---:|---:|
| `arxiv.org` + `export.arxiv.org` | 16 | 72.7% |
| `raw.githubusercontent.com` / `github.com` (jittest) | 1 | 4.5% |
| `openai.com` | 1 | 4.5% |
| `metr.org` | 1 | 4.5% |
| `pypi.org` (robots-disallowed, flagged) | 1 | 4.5% |
| In-repo prior artifacts (`ideas/`, `ventures/c-measurement/corpus/`) | 2 | 9.1% |
| **Total** | **22** | **100%** |

### Required disclosure

**HN + GitHub share of citations = 1 / 22 = 4.5%** by distinct source work (the count above), and **2 / 27 = 7.4%** by distinct citation URL (the quote-verifier's independent recount; the two jittest URLs are one project). `news.ycombinator.com` appears zero times in this file. Under either count the share is far below the 70% threshold in CLAUDE.md §8, so this file is **not labeled INSTRUMENT-BIASED** and its conclusions are held at their stated confidence — with the single exception of the buildability conclusion in §2.5, which the fix pass downgraded for a different reason (a pre-satisfied gate, not instrument bias).

**However, an honest reading substitutes a different bias, and it should be recorded:** 72.7% of citations come from arXiv. The §8 rule was written to catch HN/GitHub over-reliance and does not fire here, but a single-instrument concentration of 72.7% is a real limitation with two concrete consequences:
1. **Peer-reviewed venues that do not post preprints (IEEE TSE, ICSE/FSE proceedings behind ACM DL, industry journals) are invisible to this survey.** Semantic Scholar was the instrument that would have covered them and it returned 429 on every attempt.
2. **Vendor and industry measurements are under-sampled** — GitClear, DORA 2025, GitHub's own Copilot statistics, and the Cursor/Sourcegraph/Graphite/CodeRabbit blog tier were reached only as far as robots.txt and are marked UNVERIFIED in §2.8.

Accordingly: the **positive** findings in this file (what each of the 15 precedents did and did not measure) are high confidence — each rests on a verbatim quote from a primary source fetched today. The **negative** finding (that nobody has published the Track M quantity) is held at **medium** confidence, not high, for the two reasons above plus the arXiv metadata-only search limitation demonstrated by the `FAIL_TO_PASS` → 0 result. The falsifier search in "The gap" is the operational remedy and should be re-run before publication.

### Deviations and self-corrections

- One robots.txt violation (`pypi.org/pypi/jittest/json`), disclosed above, one request, not repeated.
- No message, comment, issue, PR, or post was sent to any human or venue. No account created, no ToS accepted, no money spent. No `git commit`, no `git push`, no writing `gh` command. All fetches were read-only GETs with the mandated User-Agent.
- **No private individual is named in the body of this file — with one referral outstanding.** The first draft's precedent-table row 4 used a personal GitHub account name as jittest's author byline; that byline now reads "an independent single-maintainer OSS project", and the earlier claim in this note that no private individual was named was, at the time it was written, inaccurate. The project's `github.com` and `raw.githubusercontent.com` URLs are retained because they *are* the evidence for §2.1, and the account name they contain is **referred to the Wave-0 `redactor`** for a decision (logged in `private/REDACTION-LOG.md`) rather than deleted unilaterally here; the same URL already appears in `ideas/r2-ai-pr-verification-gate.md`. Paper authors are cited by published byline, which is public scholarly attribution, not personal data.
- The topical citation keys (`[testcov2026agentic]`, `[smoke2026oracle]`, `[proxy2026replic]`, `[postmerge2026]`, `[testincl2026]`, `[overfit2025]`, `[utboost2025]`, `[solved2025really]`) are a **deliberate style choice, not an instrument limitation.** The first draft said the arXiv listing "did not surface authors within the time-box"; that was untrue — author names are present in the same `export.arxiv.org` responses used for every one of those papers. Struck in the fix pass.
- Time-box: approximately 80 minutes. The industry-report tier (GitClear, DORA, vendor blogs) and Semantic Scholar are the two known-incomplete areas, both marked.

### Fix-pass re-fetches (2026-08-30, `precedents-fix-pass`)

Three read-only GETs, same mandated User-Agent, no new venues and no new citation hosts (so the citation-by-host
counts and the HN+GitHub share above are unchanged):

| Command | Result | What it settled |
|---|---|---|
| `curl -sS -A "$UA" https://metr.org/robots.txt` | HTTP 200; `Disallow:` × 4 → three `.pdf` paths + `/time-horizon-draft` | §2.7's "four named PDFs" was wrong; the compliance conclusion (the note fetched is permitted) still holds |
| `curl -sS -A "$UA" "https://export.arxiv.org/api/query?id_list=2310.06770"` | entry `<published>2023-10-10T16:47:29Z</published>`, `<updated>2024-11-11T23:05:04Z</updated>`; **feed-level** `<updated>2026-08-31T00:39:31Z</updated>` | §2.2's "2026-08-31" was the feed's timestamp read as the paper's |
| `curl -sS -A "$UA" ".../search_query=all:%22coding%20agent%22%20AND%20all:%22pull%20requests%22&max_results=100&..."` | HTTP 200, 222,803 B, `totalResults` = 90, 90 `<entry>` elements | Falsifier #2's true size. Diffing its 90 IDs against #1's 19 (`comm -23`) leaves **6** of #1's IDs absent even at full recall — #2 is a complement of #1, never a superset |

---

## Verification (2026-08-30, quote-verifier)

Adversarial re-fetch of every citation, number and quoted string in the body above. Method: `curl -sS -A "venture-research/2 (+https://github.com/Alex-lop/venture)"` against each cited URL today, plus re-running the four falsifier searches in "The gap" and the two rate-limited/robots-blocked calls. The body above was not edited; the author's fix pass owns that. **79 claims checked: 71 VERIFIED, 5 MISMATCH, 0 UNREACHABLE, 3 UNCHECKED.** Every one of the ~25 verbatim block quotes reproduced exactly; all five mismatches are in the file's own provenance metadata and in one falsifier command, not in a source quote or a headline number.

### Claim table

| # | Claim (file location) | Verdict | Evidence / actual text |
|---|---|---|---|
| 1 | jittest README, HTTP 200, 6,923 bytes (§2.1) | **VERIFIED** | Re-fetched today: HTTP 200, `size_download` = 6923 — byte-exact |
| 2 | "83 historical pull requests across Flask, requests, and youtube-dl (evaluating execution capability, not estimating global prevalence)" + the five bullet counts (§2.1) | **VERIFIED** | Verbatim in README, including `83/83`, `24/83 (29%)`, `5/11`, `0/13`, `59/83 signed refusals` |
| 3 | Arithmetic 59/83 = 71.1%, 24/83 = 28.9% (§2.1) | **VERIFIED** | 59/83 = 0.71084; 24/83 = 0.28916 |
| 4 | Four-verdict taxonomy table, all four rows (§2.1) | **VERIFIED** | Verbatim, including `non_discriminating` = "test passes on both — proves nothing about the change" |
| 5 | "Historical environment decay is real: on older revisions jittest will often refuse (`inconclusive`) rather than guess. That is the feature." (§2.1) | **VERIFIED** | Verbatim under "Honest boundaries" |
| 6 | "We count refusals as first-class results" / "we publish our denominator" (§2.1, §"vocabulary" item 4) | **VERIFIED** | Both verbatim |
| 7 | jittest version 0.3.4 (§2.1, row 4) | **VERIFIED** | README PyPI badge reads `PyPI-v0.3.4`; the GitHub Action pin is `@v0.3.4` |
| 8 | jittest PyPI upload 2026-08-20T17:45:58Z and the summary string (§2.1) | **UNCHECKED** | Deliberately not re-fetched: `pypi.org/robots.txt` re-read today and does contain `Disallow: /pypi/*/json`, so the author's self-reported violation is accurate and I did not repeat it. The allowed path `pypi.org/project/jittest/` returned HTTP 200 but a JavaScript bot-challenge page with no version data. The upload date remains unverified; the version is corroborated by the README |
| 9 | "jittest's characterisation of 2607.28871's effect size … also matches the abstract verbatim" (§2.4) | **MISMATCH** (minor) | Substance matches; the wording does not. jittest writes "below the authors' **pre-registered** 10pp"; the abstract says "**prespecified** 10-percentage-point smallest effect size of interest". Also verified: jittest's "~1/3 of the effect attributable to reminder prompts" ↔ abstract "Roughly a third of the improvement traces to the reminder alone". Fix: say "matches in substance", not "verbatim" |
| 10 | jittest's three Prior-Art arXiv items exist with matching titles (§2.4) | **VERIFIED** | 2601.22832 *Just-in-Time Catching Test Generation at Meta* (Harman among authors); 2607.14890 *Proof-or-Stop: Don't Trust the Agent, Trust the Evidence…*; 2607.28871 *Validation Evidence in LLM Repair Agents…* (Xu, Wu). All HTTP 200 |
| 11 | SWE-bench HTML 2310.06770v3, HTTP 200, 1,275,988 bytes (§2.2) | **VERIFIED** | Byte-exact today |
| 12 | SWE-bench arXiv metadata "published 2023-10-10, **last updated 2026-08-31**" (§2.2) | **MISMATCH** | Actual `<updated>` = **2024-11-11T23:05:04Z**. `<published>` = 2023-10-10T16:47:29Z (correct). A 2026-08-31 stamp is also one day in the future. Fix: strike "last updated 2026-08-31", write "v3, last updated 2024-11-11" |
| 13 | "Stage III: Execution-based filtering. For each candidate task, we apply the PR's test content…" (§2.2) | **VERIFIED** | Verbatim in the main text |
| 14 | "If any of the steps (a) through (f) fails… this step generally removes half of the candidate task instances" (§2.2) | **VERIFIED** | Verbatim in the appendix |
| 15 | "from their respective log_pre and log_post test-to-status mappings, we create a test results data structure where the keys are FAIL_TO_FAIL, FAIL_TO_PASS, PASS_TO_FAIL, and PASS_TO_PASS, and the values are lists of tests." (§2.2) | **VERIFIED** | Verbatim (the HTML renders the subscripts as MathML; the token sequence is exact) |
| 16 | Table 9 field definitions for FAIL_TO_PASS / PASS_TO_PASS (§2.2) | **VERIFIED** | Verbatim |
| 17 | Table 10 funnel 93,139 → 11,407 → 2,294 (§2.2, row 5) | **VERIFIED** | Table 10 "Total" row: 93,139 / 11,407 / 2,294 |
| 18 | Derived 20.11% kept, 79.89% removed, 2.46% end-to-end (§2.2) | **VERIFIED** | 2294/11407 = 0.201105; 1 − that = 0.798895; 2294/93139 = 0.024630 |
| 19 | 2,294 instances across 12 Python repos (row 5) | **VERIFIED** | Abstract, verbatim |
| 20 | SWE-bench Verified page HTTP 200, 556,515 bytes (§2.3) | **VERIFIED, delta noted** | HTTP 200; 556,471 bytes today — **−44 bytes** from the author's figure. Dynamic marketing page; content identical on every checked string |
| 21 | openai.com robots.txt `User-agent: * / Allow: /`, only `/microsoft-for-startups/` disallowed (§2.3) | **VERIFIED** | Exact |
| 22 | Both date stamps "August 13, 2024" and "August 5, 2024" present (§2.3) | **VERIFIED** | Both strings present in the page source |
| 23 | "We worked with 93 software developers… 1,699 random samples… to produce SWE-bench Verified." (§2.3) | **VERIFIED** | Verbatim |
| 24 | "38.3% … underspecified problem statements, and 61.1% … unfairly mark valid solutions as incorrect… 68.3% … filtered out" (§2.3, row 6) | **VERIFIED** | Verbatim |
| 25 | The FAIL_TO_PASS / PASS_TO_PASS plain-English definition quote (§2.3) | **VERIFIED** | Verbatim, incl. "used to check that existing unrelated functionality in the codebase has not been broken by the PR" |
| 26 | "It is sometimes difficult to reliably set up the SWE-bench development environments…" (§2.3, Objection 1) | **VERIFIED** | Verbatim |
| 27 | "is likely to be overzealous" (Objection 2) | **VERIFIED** | Verbatim: "this filtering process is likely to be overzealous but allows us to have high confidence…" |
| 28 | 500 samples kept (row 6) | **VERIFIED** | "500 samples that constitute SWE-bench Verified" |
| 29 | BSG-VA metadata: title, Xu & Wu, 2026-07-30, cs.SE + cs.AI (§2.4) | **VERIFIED** | arXiv API HTTP 200; published 2026-07-30T22:32:14Z |
| 30 | BSG-VA abstract quote — 3,730 events / 643 rollouts / 110 tasks / 46.0% / 23.8% (§2.4, row 1, summary) | **VERIFIED** | Verbatim, word for word |
| 31 | "BSG-VA applies post hoc to any replayable repair trajectory…" (§2.4) | **VERIFIED** | Verbatim |
| 32 | "Both estimates fall below the prespecified 10-percentage-point smallest effect size of interest, so practical magnitude remains uncertain." (§2.4) | **VERIFIED** | Verbatim |
| 33 | 2607.18057 HTML HTTP 200, 158,274 bytes (§2.5) | **VERIFIED** | Byte-exact today |
| 34 | 2607.18057 abstract quote — 4882 PRs / 532 Java / 4350 Python / 49.6% / 61.5% / 27.0% / 64.8% / 35.9% / 22.5% (§2.5, row 2, summary) | **VERIFIED** | Verbatim including the two `[...]` elisions |
| 35 | Keyword counts on the fetched HTML: `discriminat` 0, `FAIL_TO_PASS` 0, "pass on both" 0, "base commit" 1 (§2.5) | **VERIFIED** | Independently re-extracted and recounted: 0 / 0 / 0 / 1. (The author's "38,631 chars of extracted text" came out as 40,038 under my extractor — tag-stripping is method-dependent and this is not a claim about the source) |
| 36 | The single `base commit` occurrence, quoted in full (§2.5) | **VERIFIED** | Verbatim: "…minus those in the pre-change version (i.e., the content at the base commit); the difference identifies tests introduced, not merely edited, by the PR." |
| 37 | "PR-level coverage. For each PR, we execute the repository's entire test suite… 10 of the 14 Java and 34 of the 55 Python repositories could be built and instrumented, yielding coverage results for 213 of the 532 Java PRs and 1664 of the 4350 Python PRs." (§2.5) | **VERIFIED** | Verbatim (source uses a curly apostrophe in "repository's") |
| 38 | Derived 34/55 = 61.8%, 1664/4350 = 38.3% (§2.5, summary, gate discussion) | **VERIFIED** | 34/55 = 0.61818; 1664/4350 = 0.38253 |
| 39 | "The test-only patch enables us to remove those tests selectively during coverage measurement." (§2.5) | **VERIFIED** | Verbatim |
| 40 | Conventional-commit Python mix: feat 2315, fix 1802, docs 1376, test 449, refactor 438 (Objection 3) | **VERIFIED** | Verbatim from the paper's corpus description |
| 41 | "2607.18057's ≥10-agentic-PR filter cut 448 Python repos to 55" (Objection 2) | **VERIFIED** | "4350 Python PRs across 448 repositories… we consider only merged PRs from repositories with at least 10 agentic PRs… This filter retains 14 Java and 55 Python repositories." |
| 42 | 2606.18168 metadata: title, published 2026-06-16 (§2.6, row 3) | **VERIFIED** | arXiv API HTTP 200; 2026-06-16T17:06:51Z |
| 43 | 2606.18168 abstract quote — 86,156 patches / 33,596 PRs / 2,807 repos / 384 stratified / eight categories / 80.2% / OR = 1.28, p < 0.001 (§2.6, row 3, summary) | **VERIFIED** | Verbatim |
| 44 | METR note HTTP 200, 245,202 bytes (§2.7) | **VERIFIED** | Byte-exact today |
| 45 | metr.org robots.txt "disallows four named PDFs only" (§2.7, instrument log) | **MISMATCH** (minor) | Actual: three PDFs (`evaluating-ai-models-for-critical-harms.pdf`, `may-2025-progress-report.pdf`, `2024-annual-report.pdf`) plus `Disallow: /time-horizon-draft`, which is not a PDF. The fetched note is still permitted, so the compliance conclusion stands; the description does not. Fix: "three PDFs and one draft path" |
| 46 | "we had 4 active maintainers from 3 SWE-bench Verified repositories review 296 AI-generated pull requests (PRs)." (§2.7, row 7) | **VERIFIED** | Verbatim |
| 47 | "the automated grader is on average about 24.2 percentage points (standard error: 2.7) higher than the maintainer merge decision" (§2.7, row 7) | **VERIFIED** | Verbatim |
| 48 | "as the golden baseline is 68%, if a model gets 34%, then the golden-baseline-adjusted score is 50%" (§2.7) | **VERIFIED** | Verbatim |
| 49 | "Testing Requirements: We ask them to ignore testing requirements in the PR, as agents are not elicited to include proper tests. This is generous to AI-generated patches, as it removes one requirement of a good patch." (§2.7, row 7, summary) | **VERIFIED** | Verbatim — this is the load-bearing novelty quote and it is exact |
| 50 | "296 AI PRs + 47 golden" (row 7) | **VERIFIED** | "maintainer merge decisions on 47 original human-written PRs that were actually merged into main (hereafter 'golden patches')" |
| 51 | The METR framing correction against `ideas/r2-ai-pr-verification-gate.md` (§2.7) | **VERIFIED** | That file's own verification section already records the same caveat, incl. the identical "Testing Requirements" quote and the 68% golden-baseline point |
| 52 | UTBoost 2506.09289: quote + 36 instances + 345 erroneous patches + 40.9% Lite / 24.4% Verified (§2.8, row 9) | **VERIFIED** | All verbatim from the abstract |
| 53 | 2503.15223: PatchDiff, 7.8%, 29.6% (§2.8, row 10) | **VERIFIED** | Verbatim: "causes 7.8% of all patches to count as correct while failing the developer-written test suite… 29.6% plausible patches induce different behavior" |
| 54 | 2511.16858: "the first empirical study of test overfitting in this setting"; "technically passes observed tests but actually misses important cases" (§2.8) | **VERIFIED** | Both verbatim |
| 55 | TestGen-LLM 2402.09171: "75% … built correctly, 57% passed reliably, and 25% increased coverage" (§2.8, row 11, Objection 4) | **VERIFIED** | Verbatim |
| 56 | 2601.22832: "catching tests are meant to fail"; 22,126 tests; 4x / 20x; 70% review-load cut; 41 reported, 8 confirmed (§2.8, row 12) | **VERIFIED** | All verbatim |
| 57 | 2607.22880: proxy metrics unreliable "in another common scenario where the code-under-test may already be buggy and the goal is to expose the bug" (§2.8, row 13) | **VERIFIED** | Verbatim (the source continues "…within the code-under-test"; the truncation changes nothing) |
| 58 | 2607.09902: 182 repos; "require significantly higher rates of corrective maintenance and introduce more security weaknesses"; 10pp → ~6% (§2.8, row 15) | **VERIFIED** | Verbatim; source continues "…and dependency vulnerabilities" |
| 59 | 2601.03556: descriptive, test-containing PRs larger/slower/similar merge rates (§2.8, row 8) | **VERIFIED** | Abstract: "tend to be larger and take longer to complete, while merge rates remain largely similar" |
| 60 | AIDev 2507.15003: "Spanning over 456,000 pull requests by five leading agents… across 61,000 repositories and 47,000 developers"; "their PRs are accepted less frequently, revealing a trust and utility gap" (§2.8) | **VERIFIED** | Verbatim (source renders the dashes as `--`) |
| 61 | TestGenEval 2410.00752: 68,647 tests, 1,210 file pairs, 11 repos, GPT-4o 35.2% (row 14) | **VERIFIED** | Verbatim |
| 62 | The §2.8 UNVERIFIED list (2509.16941, 2505.23419, 2410.03859, 2504.02605, SWE-smith, SWE-Gym, GitClear, DORA, vendor blogs) | **UNCHECKED** | Correctly self-labeled UNVERIFIED by the author; I did not spend budget confirming things the file already declines to assert |
| 63 | Falsifier: `all:"FAIL_TO_PASS"` → 0 results ("The gap") | **VERIFIED** | Re-run today: HTTP 200, `totalResults` = 0 |
| 64 | Falsifier: `all:"non-discriminating tests"` → 0 | **VERIFIED** | HTTP 200, totalResults = 0 |
| 65 | Falsifier: `abs:"pass on the base commit"` → 0 | **VERIFIED** | HTTP 200, totalResults = 0 |
| 66 | Search #1 "returned 19 results today spanning 2026-01 to 2026-08" | **VERIFIED** | Re-run today: totalResults = 19, 19 entries, published 2026-01-01 to 2026-08-20. Reading all 19 titles: none satisfies (a)–(d); the two closest are 2607.18057 (already table row 2) and 2601.03556 (row 8) |
| 67 | Search #2 "(40 results, **superset of #1**)" | **MISMATCH** | HTTP 200 but `totalResults` = **90**, truncated to 40 by `max_results=40` under `sortBy=submittedDate&sortOrder=descending`. **11 of search #1's 19 arXiv IDs are absent** from what #2 returns (2601.00477, 2601.03556, 2601.15195, 2601.17413, 2601.18749, 2602.17955, 2604.03551, 2604.09409, 2604.24450, 2606.06752, 2606.13449) — including 2601.03556, which is table row 8. It is not a superset, and as written the falsifier silently drops half its own recall. Fix: `max_results=100`, and drop the word "superset" |
| 68 | Semantic Scholar 429 on every attempt | **VERIFIED** | Reproduced today: HTTP 429, `{"message": "Too Many Requests…"}`. The hole in the search is real and still open |
| 69 | `pypi.org/robots.txt` contains `Disallow: /pypi/*/json` (self-reported violation) | **VERIFIED** | Exact. The self-disclosure is accurate and the violation is a single GET, not repeated |
| 70 | Corpus README: "≥50-star gate alone removed 918 of 1,047 repos" (Objection 2) | **VERIFIED** | `ventures/c-measurement/corpus/README.md`: "918 < 50 stars" in the funnel table and "The >= 50-star gate removed 918 of 1047 repos" |
| 71 | Corpus README quote: "that minority is exactly the well-maintained subset, which is the population least likely to ship non-discriminating tests. A biased 25% sample cannot answer the question" (Objection 2) | **VERIFIED** | Verbatim |
| 72 | Corpus README: "if most bases will not build hermetically" (§2.5) | **VERIFIED** | Verbatim (sentence-initial "If" in source) |
| 73 | Corpus README documents 1,000-result cap and `search/issues` not indexing commit messages (vocabulary item 2) | **VERIFIED** | README limitations 1 and 3 |
| 74 | "this venture's corpus of 23 repos" (§2.6) | **VERIFIED** | `candidates.csv` — 23 rows, per the README's own Files section |
| 75 | Deviations: "Where a paper's arXiv listing did not surface authors within the time-box, the citation key uses a topic slug instead of a surname" | **MISMATCH** (minor) | Authors are present in the same `export.arxiv.org` responses the author fetched, for every slug-keyed paper: 2607.18057 (Dipongkor, Baral, Lam, Moran), 2606.18168 (Banik, Chowdhury, Shamim), 2503.15223 (Wang, Pradel, Liu), 2506.09289 (Yu, Zhu, He, Kang), 2607.22880 (Zhao, Zhou, Cohen), 2607.09902 (Xia, Miller), 2511.16858 (Ahmed, Ganhotra, Shinnar, Hirzel), 2601.03556 (Haque, Ingale, Csallner). The slugs are fine as keys; the stated reason is not true. Fix: say the keys are topical by choice, or fill in the surnames |
| 76 | Header: "HN+GitHub = 1/22 citations = 4.5%" | **VERIFIED (direction), recounted below** | 1/22 = 4.545%. My independent recount gives 2/27 = 7.4% by distinct URL. Both are an order of magnitude below the 70% threshold; the "not INSTRUMENT-BIASED" label holds under either count |
| 77 | Header/log: "arXiv-dominant (16/22 = 72.7%)" | **VERIFIED (arithmetic), understated (count)** | 16/22 = 72.727%. By distinct citation URL the arXiv family is 22/27 = **81.5%**. The author's disclosure of single-instrument concentration is if anything too generous to itself |
| 78 | "WebSearch tool — not used (0 of ~200 calls)" | **UNCHECKED** | No instrument exists for me to audit another agent's tool-call ledger. Recorded as unverifiable, not disputed |
| 79 | "Time-box: approximately 80 minutes" | **VERIFIED as disclosed, out of policy** | The spawn brief's time-box was ~60 minutes. Self-disclosed overrun, correctly recorded |

### Recounted instrument log

I extracted every `http(s)` URL from the file and grouped by host, discarding the three occurrences of `https://github.com/Alex-lop/venture` (the mandated User-Agent string, not a citation).

| Host | Distinct citation URLs | Share |
|---|---:|---:|
| `arxiv.org` (14 `/abs/`, 2 `/html/`) + `export.arxiv.org` (6 API calls) | 22 | 81.5% |
| `github.com` + `raw.githubusercontent.com` (jittest, one project, two URLs) | 2 | 7.4% |
| `openai.com` | 1 | 3.7% |
| `metr.org` | 1 | 3.7% |
| `api.semanticscholar.org` (query template, 0 results retrieved) | 1 | 3.7% |
| **Total** | **27** | **100%** |

- **HN + GitHub share, recounted: 2/27 = 7.4%** by distinct URL; **1/22 = 4.5%** by distinct source work, which is the author's method and is also correct. `news.ycombinator.com` appears **zero** times in the file — the "HN Algolia: not tried" entry in the instrument log is confirmed by absence. Under both counts the file is **far** below the 70% threshold and the "NOT instrument-biased" header label **stands**.
- **arXiv concentration, recounted: 22/27 = 81.5%** by URL versus the author's 16/22 = 72.7% by source work. The author's own caveat — that a single-instrument concentration this high is a real limitation even though §8's rule does not fire — is correct and, on my count, understated by nine points. The two consequences the author names (peer-reviewed non-preprint venues invisible; vendor/industry tier unsampled) both reproduce: Semantic Scholar returned 429 again today, and no IEEE/ACM/vendor host appears in the file at all.
- No PyPI URL survives as a citation in the body text (the two facts drawn from it are prose-only), so the author's "pypi.org = 1 citation" row counts a source, not a URL. Either accounting is defensible; neither changes any threshold.

### CLAUDE.md §8 sins

- **Pre-satisfied gate — present.** §2.5 concludes "**The 30% gate is very likely to pass**" and "the pilot should be scoped as a confirmation, not as an open question." §9 makes the 100-repo buildability pilot (2026-09-20, <30% → shrink the study) an operational falsifier; re-framing it as a confirmation is exactly the move §8 forbids. The evidence does not support the reframing either: 2607.18057's 61.8% was measured **at head, without a lockfile requirement and without a network-free install**, while Track M measures **base** commits under `--network none` — and the file's own caveat says so two sentences later. The prior narrows the plausible range; it does not pre-satisfy the gate.
- **Named private individual — present.** The precedent table's row 4 attributes the work to a named personal GitHub account ("jittest (<personal GitHub account name — redacted in the fix pass; the byline now reads \"an independent single-maintainer OSS project\">)"), and the account name recurs in two URLs and one citation key. Company and product names are fine; a personal account name used as an author byline is not, under CLAUDE.md §2 and the Wave-0 `redactor`'s remit. The URLs are the evidence and cannot simply be deleted — that is the redactor's call — but the parenthetical byline can and should be a role description ("an independent single-maintainer OSS project").
- **Undefined terms — none.** "Non-discriminating" is given an operational definition (the PR's added tests yield an empty FAIL_TO_PASS set), and the file explicitly argues against promoting it to a primary term. "Buildability", "resolved/unresolved", and the four properties (a)–(d) are all defined where used.
- **"Incumbent exists = kill" — absent, inverted correctly.** The file's whole method is to measure what each near-neighbour did and did not do rather than treating four adjacent papers as a kill; the property table is the right instrument for that.
- **Pain-as-demand without budget — not applicable and correctly not attempted.** This is a novelty survey, not a demand dossier; it makes no budget claim and no revenue claim. Worth stating plainly for the record: **nothing in this file is evidence that anyone will pay for the Track M number.** Track M's justification is credibility and distribution, not budget, and the file should not be cited later as if it established demand.
- **Paraphrase presented as quote — none found.** Every one of the ~25 block quotes was re-fetched and matched verbatim, including all six load-bearing ones. The one wording problem is the reverse case: a paraphrase (jittest's) described as "verbatim" (claim 9).

### Verdict

**The file's conclusions hold at the stated confidence, with two corrections and one framing fix.** The central negative finding — that no published work reports the pass-on-base rate of an agent PR's own added tests on a real merged-PR corpus — survives adversarial re-fetching: every quote is exact, every headline number reproduces from its primary source, all four falsifier searches return today what the author said they returned, and reading all 19 hits of the highest-yield search surfaces no work satisfying properties (a)–(d). The author's own "medium confidence" rating on the negative finding is the right level and should not be raised, because the two holes they identify are real and still open today (Semantic Scholar 429 reproduced; arXiv metadata-only search demonstrated by `FAIL_TO_PASS` → 0). The five mismatches are all in provenance metadata rather than in evidence — a wrong `last updated` date, a miscounted robots.txt, an inaccurate "verbatim", an untrue reason for the citation-key style — except one that matters operationally: **falsifier search #2 is not a superset of #1 and silently drops 11 of #1's 19 results**, so as written the pre-publication novelty re-check is weaker than the file claims; raise `max_results` to 100 before 2026-10-10. The one substantive disagreement is the buildability gate: 61.8%-at-head-without-lockfile is not evidence that a base-commit, network-free build will clear 30%, and §9's pilot must stay a real test with a real chance of failing. Recount of the instrument log confirms the "NOT instrument-biased" label under every counting method (HN+GitHub 4.5%–7.4%, versus a 70% threshold) while showing arXiv concentration is 81.5% by URL rather than 72.7% — the author's disclosure of that substitute bias is honest and, if anything, too kind to itself.

Fix pass (2026-08-30, precedents-fix-pass): 5 items fixed, 0 marked UNVERIFIED, 1 conclusion downgraded.
