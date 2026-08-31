---
layout: default
title: egresswall
---

[home](../index.md) · [study](../study.md) · [agent-plan-lint](agent-plan-lint.md) · [guardrail-checkup](guardrail-checkup.md) · [compare](../compare.md) · [about](../about.md)

# egresswall

**Stop your agent's tools from handing back a customer's email address, an API key, or a
record your policy never approved — by refusing the whole response instead of redacting it.**

Zero runtime dependencies, Python 3.11+, one screening core and three places to put it: an
MCP stdio proxy, a Claude Code hook, and a CI check.

**Status: 0.1.0, release in progress; install lines appear here when the PyPI upload lands.**
Until then there is nothing to install and nothing public to read: the working copy
(`ventures/egress-guard/`, with its tests, demo and comparison page) is not pushed to
[`Alex-lop/venture`](https://github.com/Alex-lop/venture) as of 2026-08-31. The path and the
issue tracker appear here when that push lands.

Why refuse rather than redact: a redacted response still means your tool assembled the
value, put it on the wire, and something downstream had to be trusted to remove it. A
refused response means it never left the tool boundary. egresswall has no redaction mode
and will not grow one.

## What it prints

One tool response, one bad row. Nothing is rewritten; the whole payload is refused and the
exit status is 1:

```console
$ egresswall check demo/leaky.json --policy demo/policy.json
BLOCKED: demo/leaky.json
  RAW_IDENTIFIER at response.customer.contact_email: the email detector matched
  RAW_IDENTIFIER at response.customer.national_id: the ssn detector matched
  DENIED_FIELD_PATH at response.patient.mrn: denied field 'patient.mrn' carries a value
  FORBIDDEN_KEY at response.integration.api_key: field name 'api_key' is forbidden by policy
  SECRET_MATERIAL at response.integration.api_key: the openai_key detector matched
  FORBIDDEN_VALUE at response.note: a forbidden literal value was assembled
6 violations
```

In front of a live MCP server, the client is not changed and never sees the value — only a
JSON-RPC error naming the reason and the path.

## What it catches

Eight reason codes, and your alerting can switch on them: `RAW_IDENTIFIER` (the `email`,
`ssn` and `phone` detectors, anywhere in any string), `JOIN_TOKEN` (an HMAC-prefixed
pseudonymous key that can re-link records), `SECRET_MATERIAL` (six key and token
detectors), `FORBIDDEN_KEY` (a field *name* your policy lists, matched with case and
separators removed), `DENIED_FIELD_PATH` (a field your policy denies, by bare name or
dotted path), `FORBIDDEN_VALUE` (a literal string, as a substring), and `PAYLOAD_TOO_DEEP`
/ `PAYLOAD_TOO_LARGE` (screening could not finish, so the payload is refused).

Field **names** are screened as strings too, because a table keyed by an identifier is what
a lookup tool returns. A field name that is itself an identifier is reported by its
position, `<key#3>`, and never by its text — so the report is safe to log.

## What it does not do

- **It does not redact, mask or rewrite.** No `--redact`, no `--mask`, no `--fix`. A
  violating payload is refused whole.
- **It does not screen tool inputs.** The hook looks at `tool_response` only.
- **It does not recognise names, addresses or free-text PII.** Ten regular expressions. No
  model, no network call, no training data.
- **It does not speak HTTP or SSE.** The proxy is newline-delimited JSON-RPC over stdio.
- **It does not stop a Claude Code tool call.** The hook runs after the tool ran, and
  egresswall reports rather than substituting an output; only the proxy refuses a value
  before its reader sees it.
- **It does not exempt documented placeholders.** A published example domain is a violation
  by default; `allow_domains` opts out one exact domain at a time.
- **It does not persist state, phone home or write files.** No module imports `socket`,
  `ssl`, `urllib`, `http` or `requests`.
- **It does not defeat obfuscation.** The ten regexes match ASCII literals; a
  Unicode-confusable separator or a base64-wrapped value passes. egresswall assumes a buggy
  tool, not an adversarial one.

## How it is tested

413 collected tests, on CPython 3.11, 3.12 and 3.13, on ubuntu-latest and macos-latest;
`./scripts/check.sh` runs exactly what CI runs. Every detector has a positive and a
negative case, and a payload carrying the most text a policy allows screens in under a
second in each of six adversarial shapes, so a test fails if matching stops being cheap.
The proxy is driven against a real MCP server process, including a 200-call conversation
that would surface a deadlock and 44 hand-written hostile servers, one per test function.
`tests/test_readme_truth.py` executes every command block in the README marked runnable and
compares the output; `tests/test_comparison_truth.py` holds every quotation, star count,
licence and release date on the comparison page to an archived copy of the response it came
from, offline.

## Where it came from

Extracted from [RegLineage](https://github.com/Alex-lop/RegLineage), a capability-lease
runtime for AI data access, where this screen sat on two boundaries: the one facing the
language model and the one facing the MCP client. The rule that a payload is refused rather
than redacted, the reason-code vocabulary and the forbidden-key list are that project's.
This package replaces the ambiguous regexes with unambiguous ones, adds explicit size
limits, adds six secret detectors, and narrows the governance-vocabulary exemption.

## What else does this

One line each; the full both-directions table is on [compare](../compare.md). Every figure
below comes from a page or API response fetched **2026-08-30**, checked in under the
package's `docs/evidence/`.

| Tool | What it does that `egresswall` does not | Source |
| --- | --- | --- |
| Presidio (`data-privacy-stack/presidio`, ~10.7k★, MIT, `2.2.364` 2026-07-22) | Far broader entity coverage, NLP context awareness, multiple languages, image redaction — and it produces a rewritten copy. | [github.com/data-privacy-stack/presidio](https://github.com/data-privacy-stack/presidio) |
| LLM Guard (`protectai/llm-guard`, ~3.2k★, MIT, **archived**) | Many more scanner classes and a de-anonymize round trip — as a frozen snapshot; the repository is archived. | [github.com/protectai/llm-guard](https://github.com/protectai/llm-guard) |
| Snyk Agent Scan (`snyk/agent-scan`, ~3.0k★, Apache-2.0, `v0.6.0` 2026-08-19) | Discovers every MCP config and skill on a machine and checks tool *descriptions* for poisoning. It scans components, not traffic. | [github.com/snyk/agent-scan](https://github.com/snyk/agent-scan) |
| MCP Gateway (`lasso-security/mcp-gateway`, ~380★, MIT, `v1.2.0` 2026-01-21) | A full multi-server gateway with a plugin system — and it masks the token and lets the response through. | [github.com/lasso-security/mcp-gateway](https://github.com/lasso-security/mcp-gateway) |
| Guardrails AI (`guardrails-ai/guardrails`, ~7.3k★, Apache-2.0, `v0.11.0` 2026-08-14) | A large validator hub, structured generation with re-asking, a server mode — and it will raise rather than repair, on **LLM text** in an application you are writing. | [github.com/guardrails-ai/guardrails](https://github.com/guardrails-ai/guardrails) |
| Claude Code permissions and hooks | Real permission gating on the call itself, per-tool matchers, and the whole hook lifecycle. | [code.claude.com](https://code.claude.com/docs/en/hooks) |
| OpenAI moderation endpoint | Semantic harm classification across 13 categories — none of them personal data, credentials or API keys, and it returns flags rather than a decision. | [developers.openai.com](https://developers.openai.com/api/docs/guides/moderation) |

**When not to use it.** You want the response to keep flowing with the sensitive parts
removed — use MCP Gateway or Presidio. You need names or free-text PII recognised in prose
— use Presidio; ten regexes are not an NER model. Your risk is a poisoned tool description
rather than a value coming back — use Snyk Agent Scan. You need an HTTP or SSE MCP
transport — egresswall's proxy is stdio only today.
