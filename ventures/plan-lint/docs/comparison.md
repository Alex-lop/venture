# What else does this, and what it does instead

Every page below was fetched on **2026-08-31 UTC** (2026-08-30 local); every URL
is listed in `comparison-sources.txt`, and `scripts/refresh-comparison.sh` re-fetches
them and re-checks every quotation on this page against what comes back, writing each
one it found -- with every page it was found on -- into `comparison-quotes.txt`, which
`tests/test_comparison_truth.py` then holds this page to offline, so a quotation
nobody fetched fails CI rather than waiting for the next release. A quotation has
to have been found on a page its own row cites, so a real sentence moved into a
neighbouring tool's row fails the same way a fabricated one does; and every row of
every table below names a tool and a URL that `comparison-sources.txt` records as
a pair, so a row about a tool nobody read cannot be added to a table at all. Star counts
come from `gh api repos/<owner>/<repo>` on the same day, and each count names its
repository so you can run the same command. A star count is a point-in-time read
and drifts daily: `scripts/refresh-comparison.sh` re-reads every count on this page and fails when
a count has moved by more than 2 per cent, or by more than five where that is the
larger number, so a smaller difference is drift and not an error. Where a claim is about a tool's
behaviour it is quoted verbatim from that tool's own documentation; where it is a
judgement about what the tool does not do, it is unquoted, it is ours, and no
check can re-derive it -- a person read the page on the fetch date and did not
find the capability. Read every unquoted cell as of that date. <!-- claim: test_every_page_the_comparison_cites_was_captured, test_the_fetch_date_is_real_and_is_not_in_the_future, test_every_star_count_on_the_page_is_one_the_manifest_recorded, test_the_page_says_the_unquoted_judgements_are_not_machine_checked, test_every_quotation_is_one_the_refresh_script_found_on_a_page_the_page_cites, test_a_quotation_printed_under_another_tools_url_would_fail_the_check, test_every_comparison_row_is_a_tool_and_a_page_the_manifest_recorded, test_every_row_the_manifest_records_is_still_on_the_page -->

`agent-plan-lint` answers one question: *does this proposed plan fit inside this
project's policy, before anything runs?* Cycles, out-of-scope reads and writes,
two parallel tasks writing one file, criteria nobody can verify, budgets that do
not add up. Everything below overlaps some part of that and misses another part.

## Policy engines: the language, not the analysis

| Tool | Stars | What it does that this does not | What this does that it does not |
| --- | --- | --- | --- |
| [Open Policy Agent / Rego](https://www.openpolicyagent.org/docs/policy-language) | `open-policy-agent/opa` 12,179 | A general-purpose policy language and evaluation engine over any JSON: "OPA is purpose built for policy evaluation and uses its declarative language Rego to reason about structured data like API requests, infrastructure-as-code files, and configuration data." Deployable as a sidecar, a library, a k8s admission controller. | OPA evaluates the rules you write. The page documents no built-in dependency-cycle detection, write-conflict analysis or path-scope containment — you would write the graph traversal in Rego yourself, and then own it. This ships those rules, as 36 named codes, with the tests. |
| [Cedar](https://docs.cedarpolicy.com/) | `cedar-policy/cedar` 1,701 | An authorization language with a formally specified evaluator: "who (the principal) is allowed to perform which actions, on which resources, and in what context". | Cedar answers one request at a time: may this principal do this action on this resource? A plan is not one request: the interesting failures are *between* the steps — a cycle, two tasks sharing a write path, a criterion whose verifier runs before its producer. Cedar has no vocabulary for that. |
| [Kyverno](https://kyverno.io/docs/introduction/) | `kyverno/kyverno` 8,088 | Kyverno "is a cloud native policy engine" that can "validate, mutate, generate, or cleanup (remove) any Kubernetes resource", now also over "any JSON payload including Terraform resources, cloud resources, and service authorization". Admission control, policy reports, exceptions. | Kyverno validates one resource document at a time against rules you write in YAML/CEL. The plan-shape rules here are cross-task and already written. |
| [conftest](https://github.com/open-policy-agent/conftest) · [Regal](https://github.com/open-policy-agent/regal) | `open-policy-agent/conftest` 3,256 · `open-policy-agent/regal` 402 | Test structured configuration with Rego; lint the Rego itself. | Both operate on your *policy*. This operates on the *plan the policy has to judge*. |
<!-- claim: test_every_quotation_is_one_the_refresh_script_found_on_a_page_the_page_cites, test_the_page_says_the_unquoted_judgements_are_not_machine_checked -->

If your organisation already runs OPA, the honest recommendation is: keep OPA, and
use `agent-plan-lint --format json` as the thing that produces a decided, typed
result for OPA to act on — or port the codes you care about into Rego and skip this
package. The value here is that the rules are written and tested, not that the
engine is special.

## Agent frameworks: they run plans, they do not admit them

| Tool | Stars | What it does that this does not | What this does that it does not |
| --- | --- | --- | --- |
| [LangGraph](https://docs.langchain.com/oss/python/langgraph/graph-api) | `langchain-ai/langgraph` 40,733 | Builds and runs stateful agent graphs. Cycles are a feature — "complex, looping workflows that evolve the state over time". `.compile()` "provides a few basic checks on the structure of your graph (no orphaned nodes, etc)". | A cycle is a feature there and a defect here, because the object is different: a LangGraph graph is a program, a plan is a proposal about files. The docs address no file-path scoping, no write conflicts between parallel nodes, no success-criteria verification. |
| [CrewAI planning](https://docs.crewai.com/en/concepts/planning) | `crewAIInc/crewAI` 57,841 | Generates the plan: "before each Crew iteration, all Crew information is sent to an AgentPlanner that will plan the tasks step by step, and this plan will be added to each task description." | The plan an LLM wrote is added to the task descriptions and executed. Nothing stands between the planner and the run. That gap is this package. |

<!-- claim: test_every_comparison_row_is_a_tool_and_a_page_the_manifest_recorded, test_every_quotation_is_one_the_refresh_script_found_on_a_page_the_page_cites, test_the_page_says_the_unquoted_judgements_are_not_machine_checked -->

Neither is a competitor so much as the thing that produces the input. A plan from
either can be projected into this schema and checked before the run starts.

## Guardrails at the tool call, not at the plan

| Tool | What it does that this does not | What this does that it does not |
| --- | --- | --- |
| [Claude Code hooks](https://code.claude.com/docs/en/hooks) | Runs real code at real lifecycle points and can stop a call: `PreToolUse` fires "Before a tool call executes. Can block it", with `permissionDecision: "deny"`. Enforcement, not advice. | Hooks see one tool call at a time, inside the agentic loop; there is no event that hands them the whole plan before execution begins. So a hook can refuse the write to `infra/deploy.yaml`, but only when it is attempted — after the work that led there was already paid for. A cycle or a parallel write conflict is not visible from a single call at all. |
| [Cursor rules](https://cursor.com/docs/context/rules) | Steers the model where it matters most — before it decides: "rule contents are included at the start of the model context". | A rule is context, not a gate: it is put in front of the model and the model may or may not follow it. Nothing in the page describes a rule blocking an action. A rule asks. This decides, and exits non-zero. |
| [microsoft/agentrc](https://github.com/microsoft/agentrc) — `microsoft/agentrc` 1,036 stars | Measures and generates a repo's agent-facing context — instructions, dev configs, evals — and re-evaluates them in CI so they do not go stale. Glob-scoped "areas" per part of the codebase. | It is about what the agent is *told*, not about what the agent *proposed*. There is no plan object and no admission decision. |

The two are complementary in the obvious way: this decides, a hook enforces. A
`PreToolUse` hook that shells out to `agent-plan-lint check` is a reasonable
integration, and needs nothing from this package that is not already in the CLI. <!-- claim: test_the_readme_names_the_exit_statuses_the_cli_actually_uses, test_the_page_says_the_unquoted_judgements_are_not_machine_checked -->

## The one direct predecessor

[`cirbuk/plan-lint`](https://github.com/cirbuk/plan-lint) — "Static analysis
toolkit for LLM agent plans" — is the same idea, published first, and it owns the
PyPI name `plan-lint` and the `plan-lint` console script.
`cirbuk/plan-lint` 13 stars, last pushed 2025-08-09, last released
2025-04-29 (v0.0.3). Each of those figures, and the command that reads it, is
listed in `comparison-sources.txt`; `tests/test_comparison_truth.py` fails when
this page states one that is not.

That is why this package is called `agent-plan-lint` and installs a console script
of the same name: shipping a second `plan-lint` binary would collide on `PATH` for
anyone who has both. The category is open; the name was not.

## What none of them do, and neither does this

No tool on this page can tell you whether the plan is a *good idea* — whether the
mission is worth doing, whether the tasks are the right decomposition, or whether
the agent will actually do what its contract says. This checks a plan against a
policy. Everything past that is still yours. <!-- claim: test_every_bullet_of_the_disclaimer_list_still_disclaims_something, test_the_page_says_the_unquoted_judgements_are_not_machine_checked -->
