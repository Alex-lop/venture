# How egresswall compares

Every figure, licence, release tag, date and quotation below comes from a page or API
response fetched on **2026-08-30**. Those responses and the quoted passages are checked in
under [evidence/](evidence/), and
`tests/test_comparison_truth.py` fails if a figure, a licence, a release tag or a quotation
on this page is not in them. The *What X does that egresswall does not* paragraphs are the
author's reading of each project's own documentation on that date, not quotations, and
nothing under evidence/ backs them. `python3 scripts/refresh_evidence.py` re-fetches everything;
that is deliberately not part of CI, so refreshing the numbers shows up as a diff. Star
counts are rounded, because they move daily. Where a project changed hands or has been
archived, that is noted, because it changes what you are adopting.

The short version: most of the projects in this table **detect and then rewrite** —
anonymize, mask, redact, score. Two of them can refuse instead: Guardrails AI raises when a
validator is configured with `on_fail=OnFailAction.EXCEPTION`, and Claude Code's permissions
stop a call before it runs — but both act on the model's text or on the call, not on the
value a tool has already returned. Snyk Agent Scan rewrites nothing either; it scans the
components rather than the traffic. egresswall **refuses** the value itself, at the
transport. A redacted payload still tells you the tool assembled the value; a blocked one
tells you it never left. If you want the value to keep flowing in a modified form, one of
the tools below is a better fit than this one.

---

## Presidio — `data-privacy-stack/presidio`

- ~10.7k stars, MIT, latest release `2.2.364` (2026-07-22), last push 2026-08-30.
  The project has moved: the repository is `data-privacy-stack/presidio` and its README
  carries a "Presidio is moving to a new home" banner
  (https://github.com/data-privacy-stack/presidio, fetched 2026-08-30).
- What it is: "Context aware, pluggable and customizable PII de-identification service
  for text and images" providing "fast identification and anonymization modules for
  private entities in text such as credit card numbers, names, locations, social
  security numbers, bitcoin wallets, US phone numbers, financial data and more" (README,
  fetched 2026-08-30).

**What Presidio does that egresswall does not.** Far broader entity coverage, NLP-based
context awareness rather than regex, named-entity recognition, multiple languages, image
redaction, and structured/tabular de-identification. If you need to know that a sentence
contains a person's name, use Presidio.

**What egresswall does that Presidio does not.** Presidio is a library for
de-identifying content; the anonymizer's job is to produce a rewritten copy. egresswall
has no rewrite path at all, screens the whole JSON tree of an MCP result by field name and
field path as well as by value shape, and ships as a transport-level proxy and a Claude
Code hook. Presidio's analyzer also pulls in an NLP stack; egresswall has zero runtime
dependencies.

## LLM Guard — `protectai/llm-guard`

- ~3.2k stars, MIT, **archived by its maintainer**, no GitHub release published, last push
  2026-07-08. The GitHub API returns `archived: true` and the README opens with
  "THIS PROJECT HAS BEEN ARCHIVED", saying the project and its models are "no longer under
  active development or maintained" (https://github.com/protectai/llm-guard, fetched
  2026-08-30).
- What it is: "The Security Toolkit for LLM Interactions", offering "sanitization,
  detection of harmful language, prevention of data leakage, and resistance against prompt
  injection", with input scanners including `Anonymize` and `Secrets` and an output scanner
  `Deanonymize` (README, fetched 2026-08-30).

**What LLM Guard does that egresswall does not.** Many more scanner classes (toxicity,
prompt injection, topic bans, code detection), model-backed detection, and a
de-anonymize/re-anonymize round trip so the model can work on placeholder text. All of it
as a snapshot: the repository is archived, so what you would adopt is frozen.

**What egresswall does that LLM Guard does not.** LLM Guard screens prompt and completion
text on the model boundary. egresswall screens the **tool** boundary: the JSON-RPC result
of an MCP `tools/call` before the client sees it, including the field names and field paths
that carry no detectable value shape at all (`api_key: ""` is still a violation). And the
`Deanonymize` scanner is the design egresswall rejects: nothing is ever placed in a
payload to be restored later.

## Snyk Agent Scan — `snyk/agent-scan`

- ~3.0k stars, Apache-2.0, latest release `v0.6.0` (2026-08-19), last push 2026-08-28
  (https://github.com/snyk/agent-scan, fetched 2026-08-30).
- What it is: "a security scanning tool to both scan and inspect the supply chain of agent
  components on your machine. It scans for common security vulnerabilities like prompt
  injections, tool poisoning, toxic flows, or vulnerabilities in agent skills", and it
  "scan[s] MCP servers, tools, prompts, resources, and skills, and automatically
  discover[s] supported agent configurations such as Claude Code/Desktop, Cursor, Gemini
  CLI, and Windsurf" (README, fetched 2026-08-30).

**What Agent Scan does that egresswall does not.** Discovers every MCP config and skill on
a machine, checks tool *descriptions* for poisoning and injection, verifies signed binaries,
and covers a supply-chain threat model egresswall has no opinion about.

**What egresswall does that Agent Scan does not.** Agent Scan analyses the components; it
does not sit on the wire and screen the values a tool returns at call time. The v0.6 README
documents `scan` and `inspect` commands and no runtime response filter.

## MCP Gateway — `lasso-security/mcp-gateway`

- ~380 stars, MIT, latest release `v1.2.0` (2026-01-21), last push 2026-01-22 — the longest
  since its last push of the projects here still accepting changes
  (https://github.com/lasso-security/mcp-gateway, fetched 2026-08-30).
- What it is: a plugin gateway that "Intercepts requests and responses to sanitize sensitive
  information"; its documented behaviour is that "MCP Gateway will automatically mask the
  sensitive token in the response, preventing exposure of credentials while still providing
  the needed functionality" (README, fetched 2026-08-30).

**What MCP Gateway does that egresswall does not.** It is a full gateway: it orchestrates
several MCP servers, has a plugin system with prompt-injection and harmful-content plugins,
an optional Presidio plugin for PII masking, and tracing.

**What egresswall does that MCP Gateway does not.** MCP Gateway masks the token and lets
the response through
"while still providing the needed functionality". egresswall returns a JSON-RPC error and
the functionality does not proceed, because a masked response is evidence that the tool
already assembled the credential. egresswall also has zero runtime dependencies and no
plugin system to audit.

## Guardrails AI — `guardrails-ai/guardrails`

- ~7.3k stars, Apache-2.0, latest release `v0.11.0` (2026-08-14), last push 2026-08-27
  (https://github.com/guardrails-ai/guardrails, fetched 2026-08-30).
- What it is: input and output "Guards" built from validators that "intercept the inputs and
  outputs of LLMs", with `on_fail=OnFailAction.EXCEPTION` available so a failing validator
  raises. Their README's news section states validators are moving to standard PyPI packages
  and that "Guardrails is discontinuing its hosted remote inferencing. ... Planned cutoff:
  August 25, 2026" (README, fetched 2026-08-30).

**What Guardrails does that egresswall does not.** A large hub of validators, structured
JSON generation with re-asking, a server mode, and an OpenAI-compatible endpoint.

**What egresswall does that Guardrails does not.** Guardrails is the one project here that
will also raise rather than repair, but it validates **LLM text** in an application you are
writing. egresswall needs no application change: it goes in the MCP client config or the
Claude Code settings file and screens tool responses for MCP servers you did not write, at
the transport.

## Claude Code permissions and hooks

- Source: https://code.claude.com/docs/en/hooks (fetched 2026-08-30).
- Permissions decide which tools may run before they run. `PostToolUse` runs after: the
  page's exit-code table lists it as non-blocking, "Shows stderr to Claude; the tool already
  ran". It is not powerless, though — its decision-control section documents
  `updatedToolOutput`, which "Replaces the tool's output with the provided value before it is
  sent to Claude", and the page recommends exactly that: "For redaction or transformation use
  cases, intercept at PreToolUse for outbound tool inputs and PostToolUse for inbound tool
  results."

**What the built-ins do that egresswall does not.** Real permission gating on the call
itself, per-tool matchers, and the whole hook lifecycle.

**What egresswall does that they do not.** The built-ins gate *which tool runs*; they say
nothing about *what value comes back*. `egresswall hook` reports rather than substitutes: it
exits 2 so the violation reaches the model and the transcript. It does not return
`updatedToolOutput`, because substituting a value is a rewrite and this package does not
rewrite — which also means that by the time the hook speaks, the value is already in the
transcript. `egresswall proxy` is the surface that refuses a value before its reader sees it,
because it sits below the client on the stdio transport. If you want the redaction the docs
describe, write that hook yourself; egresswall will not.

## Provider content filters (OpenAI moderation endpoint)

- Source: https://developers.openai.com/api/docs/guides/moderation (fetched 2026-08-30).
- The endpoint classifies harmful content. Its response carries one `categories` object with
  13 flags — `sexual`, `sexual/minors`, `harassment`, `harassment/threatening`, `hate`,
  `hate/threatening`, `illicit`, `illicit/violent`, `self-harm`, `self-harm/intent`,
  `self-harm/instructions`, `violence`, `violence/graphic` — and no class for personal data,
  credentials or API keys. It returns flags and scores, not a decision: "Use the results to
  enforce your application's policy".

**What content filters do that egresswall does not.** Semantic harm classification, images,
and a category taxonomy no regex can approximate.

**What egresswall does that they do not.** Content filters do not know your customer's
email address is not allowed to reach a model, that `patient.mrn` is denied by your policy,
or that `ACME-INTERNAL-CASE-9931` must never appear in a tool response. And they classify;
they do not block.

---

## When not to use egresswall

- You want the response to keep flowing with the sensitive parts removed. Use MCP Gateway or
  Presidio; egresswall has no redaction mode and will not grow one.
- You need names, addresses or free-text PII recognised in prose. Use Presidio; ten regex
  detectors are not an NER model.
- Your risk is a poisoned tool description or a malicious MCP package rather than a value
  coming back. Use Snyk Agent Scan.
- You need an HTTP or SSE MCP transport. egresswall's proxy is stdio only today.
