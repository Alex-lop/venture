---
layout: default
title: Compare
---

[home](index.md) · [study](study.md) · [agent-plan-lint](packages/agent-plan-lint.md) · [egresswall](packages/egresswall.md) · [guardrail-checkup](packages/guardrail-checkup.md) · [about](about.md)

# What else does this

Both packages ship a comparison page, and this is the two of them in one place. Every row
names the page or API response it came from and the date that page was fetched. Star counts
are point-in-time reads that drift daily; each one names the repository it was read from, so
you can run the same query.

Where a claim is about a tool's behaviour, it is taken from that tool's own documentation
and both packages' test suites hold the quotation to an archived copy of the page it came
from — a quotation nobody fetched fails CI. Where a cell is a judgement about what a tool
does *not* do, it is mine, no check can re-derive it, and it means: a person read that page
on that date and did not find the capability. Read every such cell as of its date.

Sources of record are `ventures/plan-lint/docs/comparison.md` and
`ventures/egress-guard/docs/comparison.md` inside each package, together with the archived
copies their tests check against. Neither is public yet — both packages are unpushed as of
2026-08-31 — so this page is the readable copy until they land.

## Against `agent-plan-lint`

The question it answers: *does this proposed plan fit inside this project's policy, before
anything runs?* Cycles, out-of-scope reads and writes, two parallel tasks writing one file,
criteria nobody can verify, budgets that do not add up.

| Tool | What it does that this does not | What this does that it does not | Source (fetched) |
| --- | --- | --- | --- |
| Open Policy Agent / Rego — `open-policy-agent/opa` 12,179★ | A general-purpose policy language and evaluation engine over any JSON; sidecar, library or admission controller. | OPA evaluates the rules you write. The page documents no built-in cycle detection, write-conflict analysis or path-scope containment — you would write the graph traversal in Rego and own it. | [openpolicyagent.org/docs/policy-language](https://www.openpolicyagent.org/docs/policy-language) (2026-08-31 UTC) |
| Cedar — `cedar-policy/cedar` 1,701★ | A formally specified evaluator: may this principal do this action on this resource, in this context? | A plan is not one request. The interesting failures are *between* the steps — a cycle, a shared write path, a verifier that runs before its producer. Cedar has no vocabulary for that. | [docs.cedarpolicy.com](https://docs.cedarpolicy.com/) (2026-08-31 UTC) |
| Kyverno — `kyverno/kyverno` 8,088★ | Validates, mutates, generates and cleans up Kubernetes resources, now also over any JSON payload. | Kyverno validates one resource document at a time against rules you write. The plan-shape rules here are cross-task and already written. | [kyverno.io/docs/introduction](https://kyverno.io/docs/introduction/) (2026-08-31 UTC) |
| conftest 3,256★ · Regal 402★ | Test structured configuration with Rego; lint the Rego itself. | Both operate on your *policy*. This operates on the *plan the policy has to judge*. | [conftest](https://github.com/open-policy-agent/conftest) · [Regal](https://github.com/open-policy-agent/regal) (2026-08-31 UTC) |
| LangGraph — `langchain-ai/langgraph` 40,733★ | Builds and runs stateful agent graphs; cycles are a feature, and `.compile()` does basic structural checks. | The object is different: a graph is a program, a plan is a proposal about files. The docs address no path scoping, no write conflicts between parallel nodes, no criteria verification. | [docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/graph-api) (2026-08-31 UTC) |
| CrewAI planning — `crewAIInc/crewAI` 57,841★ | Generates the plan and adds it to each task description before the crew runs. | Nothing stands between the planner and the run. That gap is this package — and a plan from CrewAI can be projected into this schema and checked first. | [docs.crewai.com](https://docs.crewai.com/en/concepts/planning) (2026-08-31 UTC) |
| Claude Code hooks | Runs real code at real lifecycle points and can block a call: `PreToolUse` fires before a tool call and can deny it. | Hooks see one tool call at a time; no event hands them the whole plan before execution. A cycle or a parallel write conflict is not visible from one call at all. | [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks) (2026-08-31 UTC) |
| Cursor rules | Steers the model before it decides: rule contents are included at the start of the model context. | A rule is context, not a gate. Nothing in the page describes a rule blocking an action. A rule asks; this decides, and exits non-zero. | [cursor.com/docs/context/rules](https://cursor.com/docs/context/rules) (2026-08-31 UTC) |
| `microsoft/agentrc` 1,036★ | Measures and generates a repo's agent-facing context and re-evaluates it in CI so it does not go stale. | It is about what the agent is *told*, not what the agent *proposed*. There is no plan object and no admission decision. | [github.com/microsoft/agentrc](https://github.com/microsoft/agentrc) (2026-08-31 UTC) |
| `cirbuk/plan-lint` 13★, last pushed 2025-08-09, last release 2025-04-29 (v0.0.3) | The same idea, published first: a static analysis toolkit for LLM agent plans. It owns the name `plan-lint` on the Python package index and that console script. | Nothing to claim here. It is the direct predecessor, it is why this package is named `agent-plan-lint`, and shipping a second `plan-lint` binary would collide on `PATH`. | [github.com/cirbuk/plan-lint](https://github.com/cirbuk/plan-lint) (2026-08-31 UTC) |

## Against `egresswall`

The question it answers: *does this tool response carry a value my policy never approved?*
Most of the table below **detects and then rewrites** — anonymize, mask, redact, score. Two
can refuse instead, but at the model or at the call, not at the value a tool has returned.

| Tool | What it does that this does not | What this does that it does not | Source (fetched) |
| --- | --- | --- | --- |
| Presidio — `data-privacy-stack/presidio` ~10.7k★, MIT, `2.2.364` (2026-07-22) | Far broader entity coverage, NLP-based context awareness, named-entity recognition, multiple languages, image redaction, tabular de-identification. | Presidio's anonymizer produces a rewritten copy. This has no rewrite path at all, screens by field name and field path as well as by value shape, ships as a transport proxy and a hook, and has zero runtime dependencies. | [github.com/data-privacy-stack/presidio](https://github.com/data-privacy-stack/presidio) (2026-08-30) |
| LLM Guard — `protectai/llm-guard` ~3.2k★, MIT, **archived**, last push 2026-07-08 | Many more scanner classes, model-backed detection, and an anonymize/de-anonymize round trip. All of it frozen: the repository is archived. | LLM Guard screens prompt and completion text on the model boundary. This screens the **tool** boundary — the JSON-RPC result before the client sees it, including names that carry no detectable shape at all. | [github.com/protectai/llm-guard](https://github.com/protectai/llm-guard) (2026-08-30) |
| Snyk Agent Scan — `snyk/agent-scan` ~3.0k★, Apache-2.0, `v0.6.0` (2026-08-19) | Discovers every MCP config and skill on a machine, checks tool descriptions for poisoning, verifies signed binaries. | Agent Scan analyses the components; it does not sit on the wire and screen the values a tool returns at call time. | [github.com/snyk/agent-scan](https://github.com/snyk/agent-scan) (2026-08-30) |
| MCP Gateway — `lasso-security/mcp-gateway` ~380★, MIT, `v1.2.0` (2026-01-21) | A full gateway: several MCP servers, a plugin system, prompt-injection plugins, an optional Presidio plugin, tracing. | It masks the token and lets the response through "while still providing the needed functionality". This returns a JSON-RPC error and the functionality does not proceed. | [github.com/lasso-security/mcp-gateway](https://github.com/lasso-security/mcp-gateway) (2026-08-30) |
| Guardrails AI — `guardrails-ai/guardrails` ~7.3k★, Apache-2.0, `v0.11.0` (2026-08-14) | A large validator hub, structured JSON generation with re-asking, a server mode, an OpenAI-compatible endpoint. | It is the one project here that also raises rather than repairs — but it validates **LLM text** in an application you are writing. This needs no application change: it goes in the MCP client config or the settings file. | [github.com/guardrails-ai/guardrails](https://github.com/guardrails-ai/guardrails) (2026-08-30) |
| Claude Code permissions and hooks | Real permission gating on the call itself, per-tool matchers, the whole hook lifecycle, and an `updatedToolOutput` field that replaces a tool's output. | The built-ins gate *which tool runs*; they say nothing about *what value comes back*. The hook here reports rather than substituting, because substituting is a rewrite; the proxy is the surface that refuses a value before its reader sees it. | [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks) (2026-08-30) |
| OpenAI moderation endpoint | Semantic harm classification across 13 categories, images, and a taxonomy no regex can approximate. | No class for personal data, credentials or API keys — and it returns flags and scores, not a decision. It does not know `patient.mrn` is denied by your policy. | [developers.openai.com](https://developers.openai.com/api/docs/guides/moderation) (2026-08-30) |

## What none of them do, and neither do these

No tool on this page can tell you whether the plan is a *good idea*, or whether the value a
tool returned should have been requested at all. These check a proposal against a policy and
a payload against a policy. Everything past that is still yours.
