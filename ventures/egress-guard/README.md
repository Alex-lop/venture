# egresswall

**Stop your agent's tools from handing back a customer's email address, an API key, or a
record your policy never approved — by refusing the whole response instead of redacting it.**

```
pip install git+https://github.com/Alex-lop/egresswall@v0.1.0
```

Zero runtime dependencies, Python 3.11+, one screening core and three places to put it: an
MCP stdio proxy, a Claude Code hook, and a CI check.
*Status: 0.1.0. PyPI publication is pending; the command above installs the exact source tag.*

Why refuse rather than redact: a redacted response still means your tool assembled the
value, put it on the wire, and something downstream had to be trusted to remove it. A
refused response means it never left the tool boundary. egresswall has no redaction mode
and will not grow one.

## 60 seconds

One tool response, one bad row. Nothing is rewritten; the whole payload is refused and the
exit status is 1:

<!-- runnable -->
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

The same screen, in front of a live MCP server the client did not have to be changed for.
The client gets a JSON-RPC error naming the reason and the path — never the value:

<!-- runnable -->
```console
$ printf '%s\n' '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"lookup_customer"}}' | egresswall proxy --policy demo/policy.json -- python3 demo/fake_mcp_server.py
{"jsonrpc":"2.0","id":2,"error":{"code":-32001,"message":"egresswall blocked this result: RAW_IDENTIFIER at tools/call.result.content[0].text","data":{"code":"RAW_IDENTIFIER","path":"tools/call.result.content[0].text","detail":"the email detector matched"}}}
```

`demo/demo.sh` exercises all three surfaces end to end (four scenarios); `demo/OUTPUT.txt`
is what it printed.

## What it catches

| Reason code | What triggers it | Example that trips it |
|---|---|---|
| `RAW_IDENTIFIER` | the `email`, `ssn` and `phone` detectors, anywhere in any string. These are shapes, not meanings: a build string like `320.451.9977` trips `phone` and an order number like `123-45-6789` trips `ssn`. Both want a separator, so `123456789` and `6175550142` pass. Drop either from `detectors` if that is your data | `"contact": "member-88231@northgate-clinic.test"` |
| `JOIN_TOKEN` | the `join_token` detector — an `hmac-sha256:` or `hmac-sha512:` prefix followed by 64 to 128 hex characters: a pseudonymous key that can re-link records | `"cohort": "hmac-sha256:abab…"` |
| `SECRET_MATERIAL` | the `private_key`, `aws_access_key`, `github_token`, `anthropic_key`, `openai_key` and `bearer_token` detectors | `"AKIAIOSFODNN7EXAMPLE"` |
| `FORBIDDEN_KEY` | a field **name** in the policy's list, or containing `credential`, `password`, `secret` or `reviewer_override`, or ending in `token`. Names are matched with case and separators removed, so `apiKey`, `api-key` and `API_KEY` are all the listed `api_key` — and so `nextToken` and `pageToken` are refused by default, which is wrong for a paginated API: set `forbidden_key_suffixes` to `[]` there | `{"apiKey": ""}` — the name alone is enough |
| `DENIED_FIELD_PATH` | a field your policy denies, matched on the bare name or the dotted path, with case and separators removed on both sides (`patient.mrn` catches `Patient.MRN`) | `{"patient": {"mrn": "NG-88231"}}` |
| `FORBIDDEN_VALUE` | a literal string your policy forbids, as a substring of any string | `"escalated per ACME-INTERNAL-CASE-9931"` |
| `PAYLOAD_TOO_DEEP` | nesting past `max_depth` — screening could not finish, so the payload is refused | 33 levels with `max_depth: 32` |
| `PAYLOAD_TOO_LARGE` | more nodes than `max_nodes`, a string over `max_string_length`, or more text in one payload than `max_total_length`; also a number this interpreter cannot render or re-emit (`NaN`, `Infinity`, an integer past its digit limit), and a message the proxy refused before it could be screened (an oversized line, or a batch member after the line's budget is spent) | a 2 MiB string with the 1 MiB default |
| `EMBEDDED_DOCUMENT_UNPARSEABLE` | a string whose first visible character is `{` or `[` — a candidate serialized document — that does not parse or is too long to parse. The field-**name** and field-**path** rules could not run over it, so it is refused rather than forwarded. A template string such as `{{name}}` and a bracketed log line such as `[INFO] ready` are candidates that do not parse, so **they are refused by default**; set `refuse_unparseable_embedded` to `false` to screen such a string as a string only | `{"total": 1, "total": 2}` — the same field twice |

Field **names** are screened as strings too, because a table keyed by an identifier is what
a lookup tool returns: `{"contacts": {"member-88231@northgate-clinic.test": "vip"}}` is a
`RAW_IDENTIFIER` on the key alone. A field name that carries a value like that is reported by
its position, `<key#3>`, and never by its text — so the report is safe to log.

**Serialized payloads are unwrapped.** MCP's `CallToolResult` carries the tool's whole answer
as JSON *text* inside `content[].text`, and a plain string has no field names in it — so a
screened string whose first visible character is `{` or `[` is parsed and screened again as
a document, under the same node, depth and text budget as the payload that carried it. Every
rule above then runs over its field names, its field paths and its values, and the path says
where the value was found:

<!-- runnable -->
```console
$ printf '{"content":[{"type":"text","text":"{\\"patient\\": {\\"mrn\\": \\"NG-88231\\"}, \\"rows\\": []}"}]}' | egresswall check - --policy demo/policy.json
BLOCKED: -
  DENIED_FIELD_PATH at response.content[0].text→patient.mrn: denied field 'patient.mrn' carries a value
  FORBIDDEN_KEY at response.content[0].text→rows: field name 'rows' is forbidden by policy
2 violations
```

The embedded document gets its own dotted root, so `patient.mrn` in a policy means the same
thing inside a `content[].text` payload as it does in the file `egresswall check` reads.

*Visible* is the whole of that test. Every code point at either end of the string that
carries no glyph is stripped before the `{`/`[` test and before the parse, so a document a
server prefixed with one is screened as a document rather than forwarded as a string. Three
sets say what that means. Unicode category C, Z or M — a byte-order mark, a zero-width or
bidi format character, a soft hyphen, a combining mark, ordinary whitespace. Every code point
with Unicode's `Default_Ignorable_Code_Point` property, transcribed into the code from
`DerivedCoreProperties.txt`, which is where the Hangul fillers `U+115F`, `U+1160`, `U+3164`
and `U+FFA0` live — they are category `Lo`, so the categories alone missed them and a payload
behind one was forwarded whole. And the code points that are in neither set and are drawn
blank anyway: `U+2800`, the empty cell of the Braille block, and `U+1D159`, the musical null
notehead. A document behind a *printable* prologue — a `)]}'` guard, a log prefix — is not a
candidate and is screened as a string only.

A candidate that does not parse is refused, not waved through. A string whose first visible
character is `{` or `[` and that then will not parse — malformed JSON, a field spelled twice,
an integer past this interpreter's digit limit, an array nested past the parser's own recursion — could not be
screened by the two rules an operator configures, so it is an
`EMBEDDED_DOCUMENT_UNPARSEABLE` violation. **Template strings are refused by default.** So
are bracketed log lines and Markdown links at the start of a string: `{{name}}`,
`{{ order.total }} is substituted at render time`, `[INFO] ready` and
`[the runbook](https://example.com)` are all candidates that do not parse, and each is a
violation wherever it appears — including a tool description in a catalogue, where refusing
the message takes the whole server away rather than one call. The trade is deliberate: a
candidate that had to *end* in the matching bracket to count would give the untrusted side a
one-character way to stop a document being one. `refuse_unparseable_embedded: false` in the
policy screens such a string as a string only, which is what the earlier behaviour was and is
the setting for a server whose text is templates and logs. A string whose first visible
character is neither `{` nor `[` is prose, is not a candidate, and is screened as a string
with no violation.

The codes are constants and a `VIOLATION_CODES` mapping, so your alerting can switch on them:

<!-- runnable -->
```console
$ python3 -c "import egresswall; print(' '.join(sorted(egresswall.VIOLATION_CODES)))"
DENIED_FIELD_PATH EMBEDDED_DOCUMENT_UNPARSEABLE FORBIDDEN_KEY FORBIDDEN_VALUE JOIN_TOKEN PAYLOAD_TOO_DEEP PAYLOAD_TOO_LARGE RAW_IDENTIFIER SECRET_MATERIAL
$ python3 -c "import egresswall; print(' '.join(sorted(egresswall.DETECTORS)))"
anthropic_key aws_access_key bearer_token email github_token join_token openai_key phone private_key ssn
$ python3 -c "import egresswall; print(' '.join(sorted(egresswall.DEFAULT_FORBIDDEN_KEYS)))"
access_key api_key arbitrary_sql auth authorization credentials customer_id database_credentials direct_identifier direct_identifiers password phone private_key query_text raw_rows reviewer_override reviewer_overrides rows secret secrets session_id sql ssn suppressed_value suppressed_values token user_id x_api_key
```

Those defaults are deliberately blunt: a response with a field called `rows` is refused
until you decide it should not be. Set `forbidden_keys` in your policy to replace the list.

## Putting it in front of your agent

**1. In the MCP client config** — the server does not change and neither does the client.
`egresswall proxy` spawns the server, forwards JSON-RPC both ways, and screens **every**
server message whole before it reaches the client: results, errors, server-originated
notifications and requests, every element of a batch, and any shape that is none of those.
A violating message that answers a call the client made is replaced with a JSON-RPC error on
that call's id. Anything else that violates — a notification such as `notifications/message`,
a request such as `sampling/createMessage`, a message answering an id the client never sent —
is dropped, with the reason on the proxy's stderr and no value in it. A result is screened
whether or not the proxy saw the request that asked for it.

A policy means the same thing on all three surfaces: `denied_field_paths` are matched from
the tool's own payload, so `patient.mrn` catches `{"patient": {"mrn": …}}` in a `result`, in
an `error`'s `data`, in a notification's `params` and in the file `egresswall check` reads,
and you never write the JSON-RPC envelope into a policy.

Two sets of field names are the protocol talking rather than a tool answering, so the
field-**name** rules do not run over them. The JSON-RPC and MCP envelope — `jsonrpc`, `id`,
`method`, `params`, `result`, `error`, `progressToken`, `_meta`, `cursor`, `nextCursor` and
`requestId` — is exempt, because `progressToken` ends in the default forbidden suffix
`token` and refusing it would drop every progress notification a compliant server sends.
Those eleven names are matched the way forbidden names are — case and separators removed —
and they are exempt wherever they appear in a server message, not only where the
specification puts them: a tool payload with its own field called `progress_token` is
exempt too. The **value** under the name is screened either way. And in a `tools/list`,
`resources/list`, `resources/templates/list`, `prompts/list` or `elicitation/create`
message, the parameter names declared under `inputSchema`, `outputSchema` and
`requestedSchema` are exempt: a tool may legitimately take a parameter called `phone` and an
elicitation may legitimately ask the user for one, and refusing the catalogue takes the
whole server away rather than one call — while refusing an elicitation, which carries an id
the server waits on, hangs the call instead. Only the field-**name** rule steps aside there.
Your `denied_field_paths` still run under a schema key, in every one of those methods: a
denied path names a field of your own boundary rather than a schema keyword, so a catalogue
or an elicitation that declares one is refused like anything else that carries it — and
`elicitation/create` is server-originated, so exempting the path rule would have let the
untrusted side pick the exemption for a subtree it named itself. Nothing else is exempt —
every **value** in those messages, a tool description included, is screened by every rule; a forbidden field
name anywhere else in a catalogue still refuses it; and the same shape returned by
`tools/call` is data, and is refused. `exempt_keys` in the policy is the same knob for a name
your own boundary defines; it exempts the name, never the value under it.

```json
{
  "mcpServers": {
    "support-tools": {
      "command": "egresswall",
      "args": ["proxy", "--policy", "/etc/egresswall/policy.json",
               "--", "python", "-m", "support_tools"]
    }
  }
}
```

**2. As a Claude Code hook** — put this in `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "mcp__.*",
        "hooks": [
          { "type": "command",
            "command": "egresswall hook --policy /etc/egresswall/policy.json" }
        ]
      }
    ]
  }
}
```

`egresswall hook` reads the hook event on stdin, screens `tool_response`, and exits 2 with
the reason on stderr. Input it cannot parse is input it could not screen, so that exits 2 too. Be clear about what that buys you. Claude Code's exit-code table lists
`PostToolUse` as non-blocking — "Shows stderr to Claude; the tool already ran"
(https://code.claude.com/docs/en/hooks, fetched 2026-08-30) — so the hook gets the violation
into the model's context and your transcript, after the value is already there. That page
also documents an `updatedToolOutput` field that "Replaces the tool's output with the provided
value before it is sent to Claude"; egresswall does not use it, because substituting a value
is a rewrite and this package does not rewrite. If you need the value stopped, use the proxy.

**3. In CI or a one-off** — `egresswall check fixture.json --policy policy.json` exits 1 on
violations, `--format json` for a machine-readable report, `-` to read stdin. `python -m
egresswall` is the same CLI, for when the console script is not on PATH.

Two things every surface does with input it cannot vouch for. A report lists at most **20**
violations and **4000** characters of them — one violation's share is 200 characters, past
which its path and its detail are truncated — and then says `(+N more)`; the count of
violations is always exact. The proxy reports one violation at a time and gives it that same
200-character share, in the JSON-RPC error it sends and in the line it logs. Both the path
and the detail are built from field names the other side chose, so an unbounded report is an
unbounded write into your log and, through the hook, into the model's context. The reason
code is never truncated. And a JSON object that spells the same key twice is refused rather
than screened: Python keeps the last spelling, so a document whose first spelling carries a
value and whose second is clean would screen clean here and leak wherever it is read
first-wins. `check` and `hook` exit 2; the proxy answers the client with a JSON-RPC parse
error instead of forwarding the line. Input that cannot be screened unambiguously has not
been screened.

## The policy file

Plain JSON, every key optional, unknown keys are a hard error so a typo cannot silently
disable a rule:

```json
{
  "denied_field_paths": ["patient.mrn", "resting_heart_rate"],
  "forbidden_values": ["ACME-INTERNAL-CASE-9931"],
  "detectors": ["email", "ssn", "aws_access_key"],
  "allow_domains": ["support.acme-corp.example"],
  "allow_tokens": ["WITHHELD"],
  "forbidden_keys": ["api_key", "ssn"],
  "forbidden_key_substrings": ["credential", "secret"],
  "forbidden_key_suffixes": ["token"],
  "exempt_keys": ["progressToken"],
  "max_depth": 32,
  "max_nodes": 100000,
  "max_string_length": 1048576,
  "max_total_length": 2097152,
  "refuse_unparseable_embedded": true
}
```

Every key the policy has is in that example. `max_total_length` is the bound that is actually
measured: screening a string costs its own length, and `max_nodes` x `max_string_length` is
not a bound anyone can wait for, so the walk stops and refuses the payload once it has
screened that much text in total. Raise it if your tools return more, and expect screening
time to rise with it. `forbidden_values` holds at most **10000** entries — a denylist is
compiled once per policy into an Aho-Corasick automaton, which reads each character of a
screened string a bounded number of times whatever the list holds and however it is shaped,
so a scan costs the length of the string and not the size of the list, the bound is on the
memory that automaton pins rather than on screening time, and a policy over it is refused
when it is loaded. `forbidden_key_substrings` reuses that automaton and
`forbidden_key_suffixes` is compiled once per policy into a reversed prefix tree; both cost
the length of the field name whatever the list holds, and neither is capped. An empty string in any of the three is refused when the policy
is loaded, because it would match everything. A `denied_field_paths` entry holds at most
**512** characters: the walk carries the accumulated path at every node only while it is
still short enough to equal a denied entry, so one very long entry buys back a cost the
screen is built to avoid. A policy over that is refused when it is loaded too.

`denied_field_paths` fires when the field is present at all: `0`, `false`, `""`, `[]` and
`{}` under a denied path are violations, because an empty field under a denied name still
says the field exists. Two things pass — a `null`, and one deliberate exemption: a value that
is one of a short, closed list of governance words is vocabulary rather than data, so
`{"mrn": "DENY"}` passes while `{"mrn": "NG-88231"}` and `{"mrn": "SMITH"}` do not.

<!-- runnable -->
```console
$ python3 -c "import egresswall; print(' '.join(sorted(egresswall.DEFAULT_GOVERNANCE_TOKENS)))"
DENIED DENY MODEL_CONTEXT_DENIED NOT_AUTHORIZED REDACTED SUPPRESSED WITHHELD
```

Add your own with `allow_tokens`; nothing else widens the list, so an upper-cased value that
is not on it — a surname, a product code — is data. The value-shape detectors still run over
all of them.

## The Python API

```python
from egresswall import EgressViolation, Policy, check, screen

policy = Policy.from_file("policy.json")

screen(result, policy, where="tools/call.result")  # raises EgressViolation, or returns result
for violation in check(result, policy):  # never raises; for reporting
    log.warning("%s at %s: %s", violation.code, violation.path, violation.detail)
```

`EgressViolation` carries `.reason`, `.path` and `.detail`. None of them, and no log line
this package produces, ever contains the offending value: a field name that is itself one is
reported as `<key#n>`, and so is a method name a server chose.

## What it does not do

- **It does not redact, mask or rewrite.** There is no `--redact` flag, no `--mask` flag and
  no `--fix` flag. A violating payload is refused whole.
- **It does not screen tool inputs.** `egresswall hook` looks at `tool_response` only.
- **It does not recognise names, addresses or free-text PII.** Ten regular expressions, all
  listed above. No model, no network call, no training data.
- **It does not speak HTTP or SSE.** The proxy is newline-delimited JSON-RPC over stdio.
- **It does not stop a Claude Code tool call.** The hook runs after the tool ran, and
  egresswall reports rather than substituting an output; only the proxy refuses a value
  before its reader sees it.
- **It does not fold the case of a `forbidden_values` entry.** The two field-**name** rules
  match with case and separators removed; `forbidden_values` matches the literal characters,
  so `ACME-INTERNAL-CASE-9931` does not catch the lowercased spelling of itself, and an
  entry written with a combining accent does not catch the precomposed one. List the
  spellings your tools actually emit.
- **It does not exempt documented placeholders.** `user@example.com` is a violation by
  default; `allow_domains` opts out one exact domain at a time (`mail.example.com` is not
  covered by `example.com`).
- **It does not persist state, phone home or write files.** Nothing survives the process:
  the proxy tracks the ids of in-flight calls in memory and forgets them when it exits. No
  module in the package imports `socket`, `ssl`, `urllib`, `http` or `requests`, and a
  `check` run leaves its working directory as it found it.
- **It does not defeat obfuscation.** The ten regexes match ASCII literals. A
  Unicode-confusable separator (`U+2024` for `.`, `U+FF20` for `@`, `U+2011` for `-`), an
  unusual separator, or a base64-wrapped value passes. Field-**name** matching has the same
  limit: it folds accents and compatibility forms — NFKD, then combining marks stripped, then
  casefold — so `API_KEY` and fullwidth `ＡＰＩ＿ＫＥＹ` are the listed `api_key`, but it does not fold one script into another, so `аpi_key`
  spelled with a Cyrillic `а` is not that name and the name rule does not fire on it. The
  value under such a name is still screened by every detector. egresswall assumes a buggy
  tool, not an adversarial one.
- **It does not screen the server's own stderr.** The proxy screens what the server writes on
  stdout, which is where JSON-RPC lives. Its stderr is passed through to yours untouched, so
  a tool that debug-logs its own payload puts that payload in your MCP server log with no
  violation and no note. Everything egresswall itself writes there is value-free; the server's
  half of that stream is not.
- **It does not fall back to string-only screening for a document it cannot parse.** A
  `content[].text` payload whose first visible character is `{` or `[` and that does not parse
  is refused as `EMBEDDED_DOCUMENT_UNPARSEABLE`, because the field-**name** and field-**path**
  rules need a document and never ran. A template string like `{{name}}` and a bracketed log
  line like `[INFO] ready` are refused by this rule under the default policy: they are
  candidates, and they do not parse. The ten detectors and `forbidden_values` do read every
  character of it first, so both reasons are reported. `refuse_unparseable_embedded: false`
  opts out and screens it as a string only. A document behind a *printable* prologue — a
  `)]}'` guard, a log prefix — is not a candidate at all, so it is screened as a string only
  whatever this flag says.
- **It does not answer every message it refuses.** A server line over 8 MiB is discarded as
  it arrives rather than held in memory, so it can be answered only when the head of it names
  a request the client is waiting on. A violating message whose id the client never sent is
  dropped too, like a violating server notification, with the reason on the proxy's stderr —
  because the id in a message that failed the screen may itself be a value.

## How it is tested

Zero runtime dependencies, two development ones (`pytest`, `ruff`). `./scripts/check.sh`
runs the checks CI runs before it installs the built wheel:

```
uv lock --check
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv build
```

CI then installs that wheel into a fresh virtualenv and runs the console script and the demo
out of it; `tests/test_packaging.py` does the same from inside the suite.

- **675 tests** (`uv run pytest --collect-only -q`), on CPython 3.11, 3.12 and 3.13, on ubuntu-latest and macos-latest.
- Every detector has a positive case and a negative case, and nine pathological inputs are
  run with every detector active, each asserting that matching finishes in under a second.
  The regexes are unambiguous, and any single string over `max_string_length` is refused
  rather than scanned, so no one string can make matching expensive. A payload carrying the
  most text a policy allows, `max_total_length`, 2 MiB by default, screens in under a second
  in each of the seven shapes the suite measures: flat rows; the deepest nesting a policy
  allows, with field names that long; a full 10000-entry `forbidden_values` list over text
  that is nothing but candidate positions for it; a denylist whose entries all share a head,
  over text made of that head, which is the shape a prefix index degenerates on; a
  10000-entry `denied_field_paths` list; full `forbidden_key_substrings` and
  `forbidden_key_suffixes` lists over a payload that is nothing but field names; and a
  payload of the longest integers this interpreter will render, because a number is screened
  as the text `str` makes of it and costs the budget that text. Nothing
  matches in any of them, so what is measured is the search. A test fails if any of them
  stops finishing in under a second.
- The CLI is tested through `subprocess`, and the proxy is driven against a real MCP server
  process (`demo/fake_mcp_server.py`) including a 200-call conversation that would surface a
  deadlock, plus 49 hand-written hostile servers, one per test function: reusing a live request
  id, batching, echoing the id as a string, returning `NaN`, writing invalid UTF-8, answering
  with 9 MiB, closing stdout and staying alive, putting the row in `error.data`, logging it
  through `notifications/message`, hiding an email address in an `id` ahead of the real one,
  keying the payload by it, naming a method after it, sending a message that is JSON `null` or
  a batch containing one, sending a number too long for this interpreter to convert, sending a
  tool catalogue whose schema declares a forbidden parameter name, sending each protocol field
  name a policy might forbid, spelling one field twice in one object, nesting a violation
  behind a run of long field names, sending an empty batch, putting an id with an escaped
  quote in the head of a line that does not parse, batching enough small members to spend the
  whole line's size budget, sending a line of exactly the largest size the proxy accepts and
  answering it in under two seconds, prefixing a serialized `content[].text` payload with an
  invisible code point, and every message shape that carries neither a `result`
  nor an `error`. Every **server-to-client** request and notification the MCP specification defines —
  four requests and seven notifications — is driven through the proxy under the default
  policy, one test each, asserting it is forwarded unchanged.
- `tests/test_readme_truth.py` executes every command block in this README marked runnable
  and compares the output to what is printed above, checks that the reason codes listed here
  are exactly the codes in the code, asserts that the "does not do" list above is true of the
  argument parser, checks the default limits and the dependency and CI-matrix claims on this
  page against `pyproject.toml` and `.github/workflows/ci.yml`, and checks that the version
  here matches `pyproject.toml`.
- Every sentence this README or `docs/comparison.md` puts in quotation marks has to appear in
  the copy of its source under `docs/evidence/`, fetched by `scripts/refresh_evidence.py`;
  `tests/test_comparison_truth.py` also checks every star count, licence, release tag and
  date on the comparison page against the API responses stored there. Both tests are offline.
- `tests/test_packaging.py` runs `uv build`, installs the wheel into a throwaway virtualenv,
  and runs the console script from it.

## Where it came from

Extracted from [RegLineage](https://github.com/Alex-lop/RegLineage), a
capability-lease runtime for AI data access, where this screen sat on two boundaries: the
one facing the language model (`src/reglineage/agent/egress.py`) and the one facing the MCP
client (`src/reglineage/mcp_runtime/server.py`). The rule that a payload is refused rather
than redacted, the reason-code vocabulary and the forbidden-key list are that project's;
its test discipline is why they are portable. This package decouples them from RegLineage's
plan model, replaces the ambiguous regexes with unambiguous ones, adds explicit size limits,
adds six secret detectors, and narrows the governance-vocabulary exemption so an uppercase
identifier like `NG-88231` is no longer mistaken for a policy word.

## Comparison with other tools

[docs/comparison.md](docs/comparison.md) — Presidio, LLM Guard, Snyk Agent Scan,
Lasso MCP Gateway, Guardrails AI, Claude Code's own permissions
and hooks, and provider content filters: what each does that this does not, and the reverse,
with star counts and dates fetched on 2026-08-30. The short version is that most of them
detect and then rewrite; the two that can refuse — Guardrails AI, and Claude Code's own
permissions — refuse at the model or at the call, not at the value a tool has returned.

## MCP Registry

The proxy is listed in the official MCP Registry under this name; the line below is the
registry's PyPI ownership check and must stay in the README that PyPI renders.

mcp-name: io.github.Alex-lop/egresswall

## License

Apache-2.0. See [LICENSE](LICENSE).
