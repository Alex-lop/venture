---
layout: default
title: agent-plan-lint
---

[home](../index.md) · [study](../study.md) · [egresswall](egresswall.md) · [guardrail-checkup](guardrail-checkup.md) · [compare](../compare.md) · [about](../about.md)

# agent-plan-lint

**Reject an agent's plan before anything runs.** Your agent proposes a plan; your project
has a policy. `agent-plan-lint` decides, statically, whether the plan fits inside the
policy — dependency cycles, writes outside the allowed paths, two parallel tasks writing
the same file, success criteria the agent would grade itself on, attempt budgets that do
not add up — and exits non-zero with a typed code per finding.

**Status: 0.1.0, release in progress; install lines appear here when the PyPI upload lands.**
Until then there is nothing to install and nothing public to read: the working copy
(`ventures/plan-lint/`, with its tests, demo and comparison page) is not pushed to
[`Alex-lop/venture`](https://github.com/Alex-lop/venture) as of 2026-08-31. The path and the
issue tracker appear here when that push lands.

## What it prints

A plan with a cycle, a write outside the policy's paths, two tasks fighting over one file,
and a criterion the model marks for itself:

```console
$ agent-plan-lint check demo/plan-bad.json --policy demo/policy.json
invalid: 4 issues in demo/plan-bad.json
  criterion_model_assertion [criterion-checkout-works]: a model assertion cannot verify a success criterion
  cycle: task dependency graph contains a cycle
  parallel_write_conflict: tasks work-api, work-models overlap write scope: app/api.py
  write_path_not_allowed [work-tests]: write path is forbidden: docs/guide.md
```

Exit status is `0` when the plan is within policy, `1` when it is not, and `2` when a
document cannot be loaded, the command line is wrong, or the tool itself fails
unexpectedly — so it drops into CI or an admission hook as-is. `--format json` gives the machine-readable result.

## What it catches

Every finding is one of 36 codes; `agent-plan-lint codes` prints them with their meanings.
Grouped: the task graph is not a DAG (`cycle`, `missing_dependency`); two tasks write the
same path (`parallel_write_conflict`, `ordered_write_conflict`); a task steps outside the
policy's paths (`read_path_not_allowed`, `write_path_not_allowed`,
`output_outside_write_scope`); the plan spends more than the policy grants
(`concurrency_exceeds_policy`, `attempt_budget_too_small`, `attempt_limit_exceeds_policy`);
a task uses a command or role the policy never granted; a success criterion proves nothing
(`criterion_model_assertion`, `criterion_self_verification`, `criterion_no_verifier`, and
four more); artifacts between tasks do not line up; and the merge and verification stages
are not a shape a runtime can execute. The full table is in the package README.

## What it does not do

- It does not execute, spawn, or sandbox anything. There is no subprocess in the package.
- It does not open a socket. There is no network client in the package.
- It does not read the files your plan names — only the plan and policy documents you point it at.
- It does not rewrite or repair a plan. There is no `--fix`.
- It does not watch a directory or run as a daemon. There is no `--watch`.
- It has no plugin system and no config file. The policy document is the configuration.
- It does not carve a hole in a scope: a wildcard read scope that could reach an excluded
  path is refused rather than narrowed, because nothing downstream of this gate enforces
  the hole.
- It does not accept an unbounded document. Every bound is in `docs/schema.md`, and every
  refusal names the bound it crossed.
- It does not know whether the work is a good idea. It checks the plan against the policy,
  nothing else.

## How it is tested

411 collected tests, on CPython 3.11, 3.12 and 3.13, on Ubuntu and macOS. The suite
includes the CLI driven as a subprocess with the demo output compared byte for byte
against `demo/OUTPUT.txt`; a doc-truth test (`tests/test_readme_truth.py`) that asserts the
README's codes, commands, output, "does not do" list and version against the code, and
sweeps every number in its prose so an unaccounted figure fails the suite; a comparison
doc-truth test that holds every quotation and star count on the comparison page to an
archived copy of the page it came from; and a packaging test that installs the built wheel
into a fresh virtual environment and runs the console script from it. The only runtime
dependency is `pydantic>=2.7`.

## Where it came from

The plan admission gate from [Graphene](https://github.com/Alex-lop/Graphene) (Apache-2.0),
a publication-control layer for parallel coding agents, where it sits between a
model-proposed plan and a fenced, parallel execution: no plan runs until it validates
against the project policy. Graphene's release rule came with it — a claim in a README that
no test can back is deleted rather than softened.

## What else does this

One line each; the full both-directions table is on [compare](../compare.md). Every page
below was fetched **2026-08-31 UTC (2026-08-30 local)** and is listed in the package's
`docs/comparison-sources.txt`.

| Tool | What it does that `agent-plan-lint` does not | Source |
| --- | --- | --- |
| Open Policy Agent / Rego (`open-policy-agent/opa`, 12,179★) | A general policy language and evaluation engine over any JSON. You would write the graph traversal in Rego yourself. | [openpolicyagent.org](https://www.openpolicyagent.org/docs/policy-language) |
| Cedar (`cedar-policy/cedar`, 1,701★) | A formally specified authorization evaluator for one request at a time. A plan's failures are *between* the steps. | [docs.cedarpolicy.com](https://docs.cedarpolicy.com/) |
| Kyverno (`kyverno/kyverno`, 8,088★) | Validates, mutates and generates resources from rules you write; now over any JSON payload. | [kyverno.io](https://kyverno.io/docs/introduction/) |
| LangGraph (`langchain-ai/langgraph`, 40,733★) | Builds and runs stateful agent graphs, where a cycle is a feature rather than a defect. | [docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/graph-api) |
| CrewAI planning (`crewAIInc/crewAI`, 57,841★) | Produces the plan. Nothing stands between the planner and the run — that gap is this package. | [docs.crewai.com](https://docs.crewai.com/en/concepts/planning) |
| Claude Code hooks | Real enforcement at a real lifecycle point — but one tool call at a time, after the work that led there was paid for. | [code.claude.com](https://code.claude.com/docs/en/hooks) |
| `cirbuk/plan-lint` (13★, last pushed 2025-08-09, last release 2025-04-29) | The same idea, published first, and it owns the name `plan-lint` and that console script. | [github.com/cirbuk/plan-lint](https://github.com/cirbuk/plan-lint) |

That last row is why this package is called `agent-plan-lint`: the category is open, the
name was not. If your organisation already runs OPA, the honest recommendation is to keep
OPA and either feed it `agent-plan-lint --format json` or port the codes you care about
into Rego. The value here is that the rules are written and tested, not that the engine is
special.

**And what none of them do, this one included:** tell you whether the plan is a *good idea*.
