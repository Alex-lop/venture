# Outreach queue

Nothing here is sent by the agent. Every item is a draft for Alex to send (RED action — see ASK-009 once this batch is complete). Each entry: the company, its own published channel, why this company, the message. No individual is named here — per-company contacts live in `private/outreach/named-targets.md`. Newest on top. Track sends in `private/outreach/crm.csv` (moved out of the tracked tree: it is a list of named people).

**Batch #1 status:** DRAFTED — 12 A-track companies (free-autopsy invitation, no price). **The B-track calls below are WITHDRAWN** (Track B killed 2026-08-30 by the EEA-portal finding — `DECISION.md` v3); they are kept as a record and as a ready list if the B slot ever re-opens on a wetlands signal. Nothing sent. Approval = ASK-009 (A only). Per `DECISION.md` v2: **no price is named anywhere in this batch.**

---

## Package launches — agent-plan-lint and egresswall (drafted 2026-08-31; post only after the PyPI upload and final verification)

> **Release-time re-sync performed 2026-09-01:** both released-source READMEs and demos were re-read; the frozen counts are 488 / 675 / 49; section-anchor cites, repository and docs URLs, the live study URL, self-imposed venue budgets, and egresswall's `mcp-name:` line are filled below. The repo-only egresswall demo now starts with the explicit clone command, and `mcp-server` applies to egresswall only. Re-run the final verification immediately before posting.

**Status: DRAFTED, SOURCE-READY. Nothing sent, nothing posted.** Source repositories and v0.1.0 tags are live for [agent-plan-lint](https://github.com/Alex-lop/agent-plan-lint) and [egresswall](https://github.com/Alex-lop/egresswall). Counts, docs URLs, the [study URL](https://alex-lop.github.io/guardposts/study.html), and egresswall's `mcp-name:` line are filled. PyPI remains blocked by ASK-015. The only unresolved launch placeholders are `{PYPI_URL}` and `{CONTACT_EMAIL}`; final verification remains required immediately before posting. The agent posts nothing (`CLAUDE.md` §2 RED); the principal posts every item. **No price and no hosted tier appears anywhere here** — Changelog News bars us outright if we look commercial ("🚫 Commercial products/services. Sponsorship is your path.", `research/channels.md:32`) — and nothing names a person.

**Truth rule.** Every capability sentence below is a README sentence with a test behind it: `ventures/plan-lint/README.md` = **PL**, `ventures/egress-guard/README.md` = **EW**. Both READMEs are held to their code by `tests/test_readme_truth.py` (PL §How it is tested, EW §How it is tested), which is what makes citing them worth anything. **AI-assistance disclosure is in every draft and is not optional.** Tone is `outreach/track-h/opener.md`: what it does, what it never does, what is unproven, and "nothing yet" when asked what it sells.

**Cites are section anchors, not line numbers (changed 2026-08-31).** A cite is a README section heading — `(PL §What it does not do)` — with the load-bearing phrase quoted where an exact sentence carries the claim, so a cite is checked with `grep -nF '<phrase>' README.md` rather than by counting lines. Every line cite this section used to carry had gone stale inside a day while other agents edited the same files: PL drifted +1 from line 57 (a `<!-- claim: ... -->` marker was inserted), EW drifted +19 to +47, so `EW:284` — cited here for the test count — had come to land on a sentence about not persisting state. Headings survive that. plan-lint's suite pins its own heading list (`tests/test_readme_truth.py::test_the_readme_has_exactly_the_sections_this_file_checks`); egresswall's does not, so an EW anchor that stops matching is the signal to re-read that section before posting, not to guess a line. `scripts/check-launch-cites.py` is the mechanical form of that rule: it re-reads both READMEs, asserts every heading cited here still exists and every quoted phrase is still on one line, and exits non-zero otherwise.

**The release counts are filled from the frozen READMEs (changed 2026-09-01):** 488 plan-lint tests, 675 egresswall tests and 49 hostile servers. The drafts previously read "364 tests" for plan-lint and "368 tests, 38 hostile servers" for egresswall and all three were false: while they were being verified the real counts moved 406 → 408 → 411 and 368 → 405 → 413, and the packages' own doc-truth tests were failing on exactly those claims. A wrong test count in a Show HN is the first thing a hostile reader checks. §C row 0b re-confirms them before posting.

**The rules that govern both HN posts.** All quoted from `research/channels.md` §4.1, which quotes https://news.ycombinator.com/showhn.html as fetched 2026-08-30 (`:83`; that file's verification appendix marks each quoted rule below VERIFIED, rows 6, 8, 9, 10 and 14 at `:282-291`).

- "Please don't ask friends to upvote or comment. That's not ok on HN." (`:94`) — no upvote request, no seeding, no coordinated comments.
- On topic for a package: "things people can run on their computers" (`:86`), and `pip install` clears the venue's other test, "Please make it easy for users to try your thing out, ideally without barriers such as signups or emails" (`:90`).
- "The project should be non-trivial. **Don't post quickly-generated one-offs; anybody can do that now.** Share something that is deeply personal and interesting to you. Explain how and why." (`:88`) — satisfied by what each package is: an extraction from a system that already ran it, with its provenance section and its suite (PL §Where it came from, EW §Where it came from). AI-assisted and disclosed is not the same as quickly generated; §A.4 and §B.6 are the "how and why".
- "The project must be something you've worked on personally and which you're around to discuss." (`:89`) — this is what the disclosed "I reviewed every line … the mistakes are mine" sentence answers, and what the ~4-hour comment window is for. It is also why the principal posts and replies, and the agent never does (`CLAUDE.md` §2 RED).
- "one Show HN per package, not per release" (`:96`) — this one is `channels.md`'s own operational consequence, not a sentence on showhn.html; it is quoted here as the file states it.
- **Agent's scheduling judgement, not a venue rule:** space the two Show HNs 2–4 days apart so they do not compete for the same readers. Nothing in `channels.md` §4.1 — which quotes showhn.html's rules in full at `:85-94` — says anything about posting frequency or two Show HNs in one day.

---

## A. agent-plan-lint

### A.1 Show HN — title (70 chars, cap is 80) and first comment

> Show HN: agent-plan-lint – reject an agent's plan before anything runs

> Your coding agent proposes a plan; your project has a policy. This decides, statically, whether the plan fits inside the policy before anything runs — dependency cycles, writes outside the allowed paths, two parallel tasks writing the same file, success criteria the agent would grade itself on, attempt budgets that do not add up — and exits non-zero with a typed code per finding (PL opening: "exits non-zero with a typed code per finding").
>
> Sixty seconds, from a clean install:
>
> ```
> $ pip install agent-plan-lint
> $ git clone https://github.com/Alex-lop/agent-plan-lint && cd agent-plan-lint/demo
> $ agent-plan-lint check plan-bad.json --policy policy.json
> invalid: 4 issues in plan-bad.json
>   criterion_model_assertion [criterion-checkout-works]: a model assertion cannot verify a success criterion
>   cycle: task dependency graph contains a cycle
>   parallel_write_conflict: tasks work-api, work-models overlap write scope: app/api.py
>   write_path_not_allowed [work-tests]: write path is forbidden: docs/guide.md
> exit status: 1
>
> $ agent-plan-lint check plan-good.json --policy policy.json
> ok: plan-good.json is within policy.json
> order: work-api -> work-models -> work-tests -> assemble -> verify
> exit status: 0
> ```
>
> That is `demo/OUTPUT.txt` verbatim; `tests/test_cli.py` compares the demo script's output to it byte for byte, so it fails if this stops being true (PL §How it is tested: "the demo script's output compared byte").
>
> What it never does: it does not execute, spawn or sandbox anything — there is no subprocess in the package. It does not open a socket. It does not read the files your plan names, only the plan and policy documents you point it at. No `--fix`, no `--watch`, no plugin system, no config file — the policy document is the configuration (PL §What it does not do). Exit 0 in policy, 1 out of policy, 2 when a document cannot be loaded, the command line is wrong, or the tool itself fails unexpectedly — so it drops into CI or an admission hook as-is (PL §60 seconds: "so it drops into CI or an admission hook as-is").
>
> Where it came from: the plan admission gate out of Graphene, my publication-control layer for parallel coding agents, ported with its issue codes and its tests (PL §Where it came from). 488 tests on CPython 3.11/3.12/3.13, Ubuntu and macOS (PL §How it is tested); one runtime dependency, pydantic (PL §How it is tested: "The only runtime dependency is `pydantic>=2.7`").
>
> What is unproven: nobody but me has run this on a real plan, and I have no evidence that the findings it reports correlate with agent failures you would actually have suffered — that is what I want out of posting it. The `plan-lint` package on PyPI had the idea first and owns that name and that console script, which is why this one is `agent-plan-lint` (`docs/comparison.md` §The one direct predecessor: "the same idea, published first"). The full comparison — OPA/Rego, Cedar, Kyverno, LangGraph, CrewAI, Claude Code hooks, Cursor rules — is at https://alex-lop.github.io/guardposts/. It cannot tell you whether the plan is a *good idea*; it checks a plan against a policy and nothing else (PL §What it does not do: "It does not know whether the work is a good idea").
>
> Written with AI assistance (Claude Code). I reviewed every line, the tests are why I trust it, and the mistakes are mine.

### A.2 Newsletters

**PyCoder's Weekly** — https://pycoders.com/submissions → "Submit Your Link »", $0, and "we cannot guarantee to feature every submitted link" (`research/channels.md:33`). **Blurb, 60 words (cap 60):**

> agent-plan-lint statically validates a coding agent's proposed plan against a project policy before it runs: dependency cycles, writes outside the allowed paths, two parallel tasks writing one file, success criteria the model grades itself on. 36 typed codes, non-zero exit, one dependency. Extracted from a parallel-agent control plane. Apache-2.0. Written with AI assistance (Claude Code), reviewed by me. {PYPI_URL} https://github.com/Alex-lop/agent-plan-lint

**Changelog News** — https://changelog.com/news/submit, $0. "Submitting your own work is also encouraged"; "🚫 How-to's and tutorials."; "🚫 Commercial products/services. Sponsorship is your path."; "Do your best to convince us why something is newsworthy." (`research/channels.md:32`). No tutorial framing, no product, lead with the gap. **Blurb, 80 words (cap 80):**

> Coding agents now write a plan before the code, and nothing checks the plan. agent-plan-lint checks it statically: cycles, writes outside the allowed paths, two parallel tasks fighting over one file, success criteria the model would grade itself on. 36 typed codes, non-zero exit, drops into CI. Extracted from a control plane for parallel agents; every claim in its README is asserted against the code by a test. Apache-2.0. Written with AI assistance (Claude Code), reviewed by me. {PYPI_URL} https://github.com/Alex-lop/agent-plan-lint

*Cites for both blurbs, as anchors: PL opening (what it catches); PL §What it catches ("`agent-plan-lint codes` prints them with their meanings" — the block under it prints 36); PL §60 seconds (exit status and CI); PL §How it is tested (one runtime dependency, and the README held to the code by tests); PL §Where it came from (extracted from Graphene). The 36 is re-checked at §C row 0b with everything else countable.*

### A.3 Bluesky thread — 4 posts, measured with the real URLs substituted and `488` standing in for a 3-digit count: 295 / 264 / 228 / 287 of 300

> **1/** agent-plan-lint is on PyPI. Your coding agent proposes a plan; your project has a policy. It decides statically whether the plan fits inside the policy, before anything runs, and exits non-zero with a typed code per finding.
>
> pip install agent-plan-lint
> {PYPI_URL}

> **2/** What it catches: dependency cycles, writes outside the allowed paths, two parallel tasks writing the same file, success criteria the model would grade itself on, attempt budgets that do not add up. 36 codes; `agent-plan-lint codes` prints them with their meanings.

> **3/** What it does not do: no subprocess, no socket, no --fix, no config file, no daemon. It does not read the files your plan names. It cannot tell you whether the work is a good idea. It checks a plan against a policy, nothing else.

> **4/** Extracted from Graphene, my publication-control layer for parallel coding agents. 488 tests on CPython 3.11-3.13, plus a suite that fails when the README claims something no test backs. Written with AI assistance (Claude Code), reviewed by me.
> https://github.com/Alex-lop/agent-plan-lint

*Cites, as anchors: PL opening; PL §What it catches (the 36 codes); PL §What it does not do (the does-not-do list, and "It does not know whether the work is a good idea"); PL §How it is tested (488, the CI matrix, and the README-truth suite); PL §Where it came from.*

### A.4 "Why this exists" — one paragraph, for the docs site and any reply that asks

> I build the seatbelt layer for coding agents, and a plan is the cheapest place to catch a mistake: after it runs you are reading a diff, before it runs you are reading a document. This package is that gate, lifted out of a larger control plane and made to stand alone. It is a package and not a service because I have nothing to sell you — the measurement I am actually running is separate and public (https://alex-lop.github.io/guardposts/study.html), and it asks how often a merged agent PR's own tests pass on the commit it branched from, which is the same worry one layer later. If the gate is wrong about your plan, open an issue or mail {CONTACT_EMAIL}; that is the whole business model today. It was written with AI assistance (Claude Code) and reviewed line by line; the repo says so too.

---

## B. egresswall

### B.1 Show HN — title (75 chars) and first comment

> Show HN: egresswall – refuse an agent tool response instead of redacting it

> When an agent's tool hands back a customer's email address, an API key, or a record your policy never approved, egresswall refuses the whole response instead of redacting it. A redacted response still means your tool assembled the value, put it on the wire, and something downstream had to be trusted to remove it; a refused one never left the tool boundary. There is no redaction mode and it will not grow one (EW opening: "by refusing the whole response instead of redacting it", "egresswall has no redaction mode").
>
> Sixty seconds — `pip install egresswall`, then clone the repository because the wheel does not ship `demo/`. Both blocks below are executed, not typed. The first is section 2 of `demo/OUTPUT.txt`, which `tests/test_readme_truth.py::test_the_demo_script_still_prints_what_output_txt_records` re-runs and compares; the second is the second runnable block of the README, which the same file executes and compares to what is printed there (EW §How it is tested: "executes every command block in this README marked runnable"):
>
> ```
> $ git clone https://github.com/Alex-lop/egresswall && cd egresswall
> $ egresswall check demo/leaky.json --policy demo/policy.json
> BLOCKED: demo/leaky.json
>   RAW_IDENTIFIER at response.customer.contact_email: the email detector matched
>   RAW_IDENTIFIER at response.customer.national_id: the ssn detector matched
>   DENIED_FIELD_PATH at response.patient.mrn: denied field 'patient.mrn' carries a value
>   FORBIDDEN_KEY at response.integration.api_key: field name 'api_key' is forbidden by policy
>   SECRET_MATERIAL at response.integration.api_key: the openai_key detector matched
>   FORBIDDEN_VALUE at response.note: a forbidden literal value was assembled
> 6 violations
> exit status: 1
> ```
>
> In front of a live MCP server the client gets an error naming the reason and the path, never the value, and neither the server nor the client had to change (EW §60 seconds):
>
> ```
> $ printf '%s\n' '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"lookup_customer"}}' | egresswall proxy --policy demo/policy.json -- python3 demo/fake_mcp_server.py
> {"jsonrpc":"2.0","id":2,"error":{"code":-32001,"message":"egresswall blocked this result: RAW_IDENTIFIER at tools/call.result.content[0].text","data":{"code":"RAW_IDENTIFIER","path":"tools/call.result.content[0].text","detail":"the email detector matched"}}}
> ```
>
> One screening core, three surfaces: the MCP stdio proxy, a Claude Code `PostToolUse` hook, and a CI check. Zero runtime dependencies, Python 3.11+ (EW opening: "Zero runtime dependencies, Python 3.11+, one screening core and three places to put it").
>
> What it never does: it does not redact, mask or rewrite — no `--redact`, no `--mask`, no `--fix`. It does not screen tool inputs. It does not recognise names, addresses or free-text PII — ten regexes, no model, no network call, no training data. It does not speak HTTP or SSE; the proxy is newline-delimited JSON-RPC over stdio. It does not persist state, phone home or write files. And it does not stop a Claude Code tool call: the hook runs after the tool ran, so it gets the violation into the transcript and the model's context, not ahead of the value — only the proxy refuses a value before its reader sees it. (Every sentence there is a bullet of EW §What it does not do; the hook's limit is also EW §Putting it in front of your agent, which quotes Claude Code's own exit-code table — "Shows stderr to Claude; the tool already ran".)
>
> What is unproven, and where it breaks: it does not defeat obfuscation — the ten regexes match ASCII literals, so a Unicode-confusable separator or a base64-wrapped value passes, and it assumes a buggy tool rather than an adversarial one (EW §What it does not do: "It does not defeat obfuscation"). The defaults are deliberately blunt: a response with a field called `rows` is refused until you decide it should not be (EW §What it catches: "Those defaults are deliberately blunt"). And no one but me has run it against a production tool.
>
> Where it came from: extracted from RegLineage, my capability-lease runtime for AI data access, where this screen sat on the model-facing and MCP-facing boundaries (EW §Where it came from). 675 tests, including 49 hand-written hostile MCP servers, one per test function (EW §How it is tested). How it compares to Presidio, LLM Guard, Snyk Agent Scan, Lasso's MCP Gateway, Guardrails AI and Claude Code's own permissions is at https://alex-lop.github.io/guardposts/; the short version is that most of them detect and then rewrite.
>
> Written with AI assistance (Claude Code). I reviewed every line and the mistakes are mine.

### B.2 Newsletters (mechanics and quoted rules as in §A.2)

**PyCoder's Weekly — blurb, 60 words (cap 60):**

> egresswall screens what an agent's tools hand back — email addresses, SSNs, API keys, denied fields — and refuses the whole response instead of redacting it. Three surfaces over one core: MCP stdio proxy, Claude Code hook, CI check. Zero dependencies, ten regex detectors, no model. Apache-2.0. Written with AI assistance (Claude Code), reviewed by me. {PYPI_URL} https://github.com/Alex-lop/egresswall

**Changelog News — blurb, 78 words (cap 80):**

> Almost every tool in this space detects and then rewrites. egresswall refuses instead: when an agent's tool response carries a raw identifier, secret material, or a denied field, the whole payload is blocked and the MCP client gets a JSON-RPC error naming the reason and the path, never the value. A redacted response still means the value was assembled and put on the wire. Zero runtime dependencies, Apache-2.0. Written with AI assistance (Claude Code), reviewed by me. {PYPI_URL} https://github.com/Alex-lop/egresswall

*Cites for both blurbs, as anchors: EW opening (refuse, not redact; three surfaces, zero dependencies, 3.11+); EW §What it catches (the reason codes); EW §60 seconds (the JSON-RPC error names the path, never the value); EW §What it does not do ("Ten regular expressions", no model, no network call); EW §How it is tested (README held to the code by tests).*

### B.3 MCP Registry publishing checklist — step 1 (the `mcp-name:` README line) is **done** in the released source; the remaining steps wait on or follow the PyPI upload

The registry verifies PyPI ownership by reading the README: "The MCP Registry verifies ownership of PyPI packages by checking for the existence of an `mcp-name: $SERVER_NAME` string in the package README (which becomes the package description on PyPI). The string may be hidden in a comment, but the `$SERVER_NAME` portion **MUST** match the server name from `server.json`." (`research/channels.md:105`; server-name form `io.github.username/database-query-mcp`, same line.)

1. **DONE in the v0.1.0 released source** — `ventures/egress-guard/README.md` carries `mcp-name: io.github.Alex-lop/egresswall`, so the token will be inside the README used as the PyPI description. Confirm the namespace's capitalisation with `mcp-publisher` before publishing — the token and `server.json` must match exactly, and only the tool can say which spelling it accepts.
2. **One judgement call first:** egresswall is a proxy *in front of* an MCP server, not a server. The registry is permissive — "We only remove illegal content, malware, spam, and completely broken servers", spam being "A server that doesn't do anything but provide a fixed response with some marketing copy" (`:105`) — so this is not a spam risk, but decide deliberately whether it is listed as a server or only linked from awesome-mcp-servers.
3. Rebuild and upload to PyPI from source that already contains step 1 (`tests/test_packaging.py` builds the wheel, installs it into a throwaway venv and runs the console script — EW §How it is tested: "runs `uv build`, installs the wheel into a throwaway virtualenv").
4. `mcp-publisher init` → `mcp-publisher login github` → `mcp-publisher publish`; the CLI is "installed from GitHub releases or `brew install mcp-publisher`" (`:105`).
5. Expect "currently in preview. Breaking changes or data resets may occur before general availability." (`:105`) — build nothing on the listing persisting.
6. Nothing more for the mirrors: PulseMCP's submit page is paused and says "if you have a server to share, publish it to the Official MCP Registry… we will pick it up automatically once we are back" (`:106`); Glama auto-indexes from GitHub and only 4.1% of its 80,479 listings are "Claimed", so claiming is a five-minute differentiator — account needed, so ASK (`:107`, `:180`).

### B.4 punkpeye/awesome-mcp-servers PR

Rules from the repo's own CONTRIBUTING.md (`research/channels.md:110`; re-fetched 2026-08-31, unchanged): "Contributions are welcome and encouraged!" · "**If you are an automated agent, we have a streamlined process for merging agent PRs. Just add `🤖🤖🤖` to the end of the PR title to opt-in. Merging your PR will be fast-tracked.**" · "Alphabetical order: Maintain alphabetical order within each category" · "One server per line" · and for a new entry: "The server name, linked to its repository. · A brief description of the server's functionality. · Categorize the server appropriately under the relevant section."

Section `### 🔒 Security`; legend emoji from the README, re-fetched today: `🐍` Python codebase, `🏠` Local Service. PR title `Add egresswall to Security 🤖🤖🤖` — the `🤖🤖🤖` is the required disclosure here, not decoration (`CLAUDE.md` §2, `research/channels.md:179`). One line, in the list's format:

```
- [Alex-lop/egresswall](https://github.com/Alex-lop/egresswall) 🐍 🏠 - Value-level egress firewall for MCP tool responses. Screens every server message whole and refuses it — there is no redaction mode — when it carries a raw identifier, secret material, a forbidden field name or a denied field path; the client gets a JSON-RPC error naming the reason and the path, never the value. Zero runtime dependencies. `pip install egresswall`
```

Place it at `Alex-lop`'s alphabetical position in that section. (The section as fetched today is not actually sorted; follow the stated rule, not the file.)

### B.5 Bluesky thread — 4 posts, measured with the real URLs and 3-digit / 2-digit counts standing in for `675` / `49`: 291 / 282 / 274 / 290 of 300

> **1/** egresswall is on PyPI. When an agent's tool hands back a customer's email address, an API key, or a record your policy never approved, it refuses the whole response instead of redacting it. Zero runtime dependencies, Python 3.11+.
>
> pip install egresswall
> {PYPI_URL}

> **2/** Why refuse rather than redact: a redacted response still means your tool assembled the value, put it on the wire, and something downstream had to be trusted to remove it. A refused response means it never left the tool boundary. There is no redaction mode and there will not be one.

> **3/** Three places to put one screening core: an MCP stdio proxy (the client gets a JSON-RPC error naming the reason and the path, never the value), a Claude Code PostToolUse hook, and a CI check. The honest limit: the hook runs after the tool ran. Only the proxy stops the value.

> **4/** Ten regexes, no model, no network call. It does not defeat obfuscation; it assumes a buggy tool, not an adversarial one. Extracted from RegLineage. 675 tests, 49 hostile MCP servers among them. Written with AI assistance (Claude Code), reviewed by me.
> https://github.com/Alex-lop/egresswall

*Cites, as anchors: EW opening (refuse not redact; zero dependencies, 3.11+); EW §60 seconds; EW §Putting it in front of your agent, with EW §What it does not do (the hook runs after the tool ran); EW §What it does not do (ten regexes; does not defeat obfuscation); EW §How it is tested (675, 49); EW §Where it came from.*

### B.6 "Why this exists" — one paragraph

> The teams I want to be useful to are running agents next to governed data, and the failure they describe is not a jailbreak — it is a tool that answered honestly with one field too many. Everything on the shelf detects and then rewrites, which leaves you trusting the rewriter; this refuses instead, at the value, at the transport, and reports the path rather than the value so the log is safe to keep. It came out of a lease runtime where that rule already existed, and it is a package and not a service because there is nothing here to sell — the measurement I am running asks the same question from the other end (https://alex-lop.github.io/guardposts/study.html): whether the checks we put around agent work actually discriminate. If it blocks something it should not, that is an issue I want to read — the repo's Issues, or {CONTACT_EMAIL}. It was written with AI assistance (Claude Code) and reviewed line by line; the repo says so too.

---

## C. Posting order and timing

Order is `research/channels.md:201-207` — "By 2026-09-06: PyPI release #1 with `mcp-name` token, GitHub topics set, registry publish… By 2026-09-13: Show HN for package #1; same week, PyCoder's + Changelog submissions; awesome-mcp-servers PR" — i.e. **registry → HN → newsletters**. The thing being tested is one dated gate: **Track I, ≥3 unsolicited public-artifact contacts by 2026-10-31, excluding prior 1:1 and Track H contacts** (`CLAUDE.md` §9). Every item carries the same reply address, repo Issues plus the principal's public email, because a contact with no channel back cannot be counted (`:207`). That is why all four newsletter blurbs carry a repository URL next to `{PYPI_URL}` — a blurb with only a PyPI link has no native reply channel — and why `{CONTACT_EMAIL}` remains a placeholder in §A.4 and §B.6.

| # | When | Channel | What | Gatekeeper | How its contribution is measured |
|---|---|---|---|---|---|
| 0 | before any upload | egresswall README | `mcp-name:` token (§B.3.1) | none | completed in the released source; re-check before upload with `grep mcp-name README.md` |
| 0b | after the package is frozen, before each of #4 and #5 | the drafts above | re-confirm 488 / 675 / 49 from the released READMEs, then re-grep every `§`-anchored quote with `python3 scripts/check-launch-cites.py` | none | blocks the post; done = that script exits 0, and in a clean venv, `pytest --collect-only -q \| grep -c ::` equals the README's own count equals the number in the draft, `agent-plan-lint codes \| wc -l` still prints 36. Each README's own count is pinned by its suite (PL `test_every_console_block_prints_what_the_readme_shows`, EW `test_the_readme_test_count_matches_the_suite` and `test_the_readme_hostile_server_count_matches_the_suite`), so a disagreement is a package bug: fix the README and re-freeze, never edit the number in the draft |
| 1 | by 2026-09-06 | PyPI | `agent-plan-lint`, then `egresswall` | none | `pypistats recent <pkg>` weekly into `SIGNALS.md` as telemetry; downloads cannot satisfy the operative v4 package gate |
| 2 | same day | GitHub topics | `claude-code` on both repos; `mcp-server` on egresswall only | none | 14-day views/clones diff in `SIGNALS.md`; `mcp-server` is the only findable topic (`:176`) |
| 3 | same day | Official MCP Registry | egresswall only (§B.3) | none | listing exists; Glama/PulseMCP pickup checked at 2 weeks. No per-contact attribution — record as UNMEASURABLE, not as zero |
| 4 | by 2026-09-13 | Show HN | agent-plan-lint (§A.1) | none, but ~4h of attention | strongest per-contact signal: comments and issues opened within 48h, logged in the `SIGNALS.md` inbound table with channel `hn` |
| 5 | +2–4 days after #4 | Show HN | egresswall (§B.1) | same | same. "one Show HN per package, not per release" (`:96`); the 2–4 day gap is the agent's scheduling judgement, not a venue rule — no fetched HN rule mentions posting frequency |
| 6 | week of #4 | PyCoder's Weekly | both blurbs | editorial, "cannot guarantee" | inclusion is visible in the issue; downloads step that week, or it did nothing |
| 7 | week of #4 | Changelog News | both blurbs | editorial, notified only on publication | same. A rejection is silent, so absence at 3 weeks counts as no |
| 8 | week of #4 | awesome-mcp-servers PR | §B.4, title ends `🤖🤖🤖` | maintainer review | merged / not merged, then referral traffic in the 14-day views+clones diff |
| 9 | after #4–#5 land | Bluesky | §A.3, §B.5 | none | the one channel where the principal's own network amplifies without a gatekeeper (`:199`); count replies, not likes |
| 10 | held | Console.dev, LibHunt, Claude Code plugin marketplace | — | account/ASK, or needs a live quickstart | out of this batch; re-open if #4–#8 produce fewer than 2 contacts |

**What "measured" means.** Each item gets a row in the `SIGNALS.md` inbound log on the day it goes out, and every contact it produces gets a row tagged with the channel above and a value tag (`paid-signal` / `pilot` / `technical` / `noise`). A bot account is never a stranger and never an inbound contact; neither prior 1:1 outreach nor Track H counts toward this public-artifact gate. Two `paid-signal` rows from independent parties naming the same capability fire the §9 re-open rule. If 2026-10-31 arrives under 3 qualifying contacts, what was wrong is the ranking in `research/channels.md:171-185` — an explicit hypothesis, not a finding ("Conversion rate for both is **UNVERIFIED**", `:4`) — and `inbound-channel-mapper` re-runs against these observed numbers.

**Deliberately not in this batch:** every Discord (MCP Contributor Discord — "Service or product marketing - Keep discussions vendor-neutral", `research/channels.md:73`; Python Discord rule 6 — "Do not post unapproved advertising.", `:74`, where a showcase post needs staff approval first). **r/Python and every other subreddit: UNVERIFIED** — `reddit.com/robots.txt` is `Disallow: /`, so no rule text could be fetched and none is quoted here; the principal must read each sidebar in a browser before posting anything there (`:98-99`).

---

## Track M study — launch drafts (2026-08-31, **revised after the red-team pass**)

**Status:** DRAFTED, LINK-READY at https://alex-lop.github.io/guardposts/study.html. Nothing sent. The principal posts every item below; the agent posts
nothing (`CLAUDE.md` §2 RED). **No price and no pitch appears anywhere in this section** —
Changelog News rejects commercial products outright ("🚫 Commercial products/services.
Sponsorship is your path.", `research/channels.md` §1), and the study is not a product.

**What is being launched:** the Track M study — `ventures/c-measurement/study/WRITEUP.md`,
`SUMMARY.md`, `DATASET-CARD.md`, the two result CSVs and the instrument (`runner.py`,
`analysis.py`). The public URL is live and every study link below is ready:
https://alex-lop.github.io/guardposts/study.html.

**Revised 2026-08-31.** Three red teams reviewed the write-up; `WRITEUP.md` §Red-team pass
lists every objection and its disposition. Four things changed in these drafts and **must not
be reverted**: (1) the headline is now the **pre-registered** quantity — the PR's own
*newly-added* tests, 1 of 99 — with the all-touched-tests number as context; (2) the
"well-maintained tail / the selection biases toward 0" line is **withdrawn** (the built repos
have *fewer* stars than the unbuilt ones); (3) the 74.0% is no longer described as "the PR
added the module too" (that is 15.4%; 58.6% is collateral breakage of pre-existing tests);
(4) nothing claims a property is **specific to agents** — there is no human-PR control arm.

**The four numbers every draft must keep together** (from `python3 analysis.py`): **1 of 99**
resolved PRs added tests that all already pass on base (Wilson 95% [0.2%, 5.5%]; 0 of 41 on
`fix` PRs); **0 of 99** ship an entirely non-discriminating test file set, which is **0 of 25
repositories, [0.0%, 13.3%]** once clustering is respected; **10.5%** of the tests these PRs
*add* are `PASS_TO_PASS` against **78.0%** of all tests in the files they touch; and **58.6%**
of the `FAIL_TO_PASS` evidence is a pre-existing test collaterally broken by the patch, not a
new module. A draft that quotes one without the others is dishonest in one direction or the
other and must not be posted.

**Sequencing.** SRE Weekly and Changelog News both prefer published-first, no embargo
(`research/channels.md` §1). Post to HN, then submit to the newsletters the same day; arXiv
is on its own clock (see the endorsement gate below).

### 1. Hacker News — **regular submission, not a Show HN**

Show HN excludes reading material — "Off topic: blog posts, sign-up pages, newsletters,
lists, and other reading material. Those can't be tried out, so can't be Show HNs. Make a
regular submission instead." (`research/channels.md:87`). So: normal submit form, no "Show
HN:" prefix. `news.ycombinator.com/robots.txt` sets `Crawl-delay: 30`; the principal is
posting by hand, so it does not apply, but nothing automated touches HN either way.

**Title (79 characters, HN's cap is 80):**

> We ran 107 merged AI-agent PRs' own tests against the commit they branched from

*Alternate (72 chars), if a number reads better:* `1 of 99 merged AI-agent PRs added only
tests that already passed on base`

*(The pre-revision title — "0 of 99 merged AI-agent PRs had every test pass on base; 78% of
tests did" — is withdrawn: it led with the non-pre-registered bar and paired it with a
number computed on a different denominator.)*

**First comment (post immediately after submitting, then stay for the comment window —
`DECISION.md` §4 budgets +4 h for a launch's comments):**

> Author here. The question was narrow: when a coding agent opens a PR and the PR gets
> merged, do the tests it added actually distinguish the code before the change from the code
> after it? SWE-bench answers that during dataset construction and throws the answer away, so
> I ran it as the measurement instead. It is BSG-VA's replay (arXiv:2607.28871) applied to
> merged real-world PRs rather than benchmark rollouts.
>
> Method: take each merged PR's own test files, apply only those files to the PR's base
> commit, install from the repo's lockfile, run them twice on base and twice on the merge
> commit in a container with the network off, and classify every test id as FAIL_TO_PASS /
> PASS_TO_PASS / UNRESOLVED. 107 PRs, 25 Python repos, 99 reached a verdict.
>
> The number I pre-registered was about the tests each PR *adds*. 1 of the 99 added only
> tests that already passed at its base commit — Wilson 95% [0.2%, 5.5%], and 0 of 41 on
> fix-titled PRs. Under a looser bar (zero discriminating tests anywhere in the files the PR
> touched, new or pre-existing) it is 0 of 99 — but those 99 PRs sit in 25 repos, and with
> the repo as the unit that is 0 of 25, [0.0%, 13.3%]. Quote the wider one.
>
> The interesting part is what the tests are made of. 78.0% of all the test ids in the files
> these PRs touch pass on base and candidate alike — but 90.9% of those ids are pre-existing
> tests being re-run. Restricted to the tests the PRs actually added, only 10.5% pass on both
> sides. And of the evidence that does discriminate, only 15.4% is "the PR added the module,
> so the test could not import at base"; 58.6% is a pre-existing *passing* test that the PR's
> own test patch broke by adding an import. I had that backwards in an earlier draft; the
> crosstab that catches it is in the write-up and in the published CSVs.
>
> What it is not: a population estimate. The 25 repos are the ones whose base commit installs
> from a lockfile and runs its suite offline — 25 of 60. I originally called that "the
> well-maintained tail" and claimed the selection biased the result toward zero. That claim
> is withdrawn: the repos that built have a median 64 stars against 351 for the ones that
> did not, identical agent-PR volume, and a near-identical lock-kind mix. The filter selects
> small single-lockfile projects, and I cannot tell you which way the residual bias runs.
>
> It is also **not** a claim about agents specifically — there is no human-PR control arm
> here. The nearest published one (arXiv:2601.21194) finds human and human-agent PRs include
> tests at comparable rates, 40.0% vs 42.9%. And 92 of 107 PRs carry one trailer family, so
> it is not a per-agent comparison either. A trailer proves an agent was involved, not that
> the agent wrote the tests that landed.
>
> It does not contradict "All Smoke, No Alarm" (arXiv:2606.18168), which found 80.2% of agent
> test patches have weak or no explicit oracle signals *statically*. Different axis, and
> different denominator — the number to put beside 80.2% is my 10.5%, not my 78.0%.
>
> Instrument, both CSVs, the method with every known limit, and a script that reprints every
> number are in the repo, including a section that lists all 25 red-team objections against
> this write-up with what I fixed, what I acknowledged, and the one I rejected. The dataset
> carries no author, login, email, PR title or PR body — only repo, PR number, SHAs, test ids
> and outcomes.
>
> Disclosure: built and written with heavy AI assistance; I designed the method, reviewed the
> instrument, and I am accountable for every number. I also keep two commercial concepts in
> the same repo that a *positive* finding would have helped; the finding went the other way.
> Happy to be told what is wrong with it.

### 2. Bluesky thread (6 posts, each ≤300 characters)

Post 1/6 carries the link; the rest are replies in order. Measured lengths with a 36-character
URL substituted for `https://alex-lop.github.io/guardposts/study.html`: 268, 246, 254, 251, 243, 264. Bluesky counts a link as its
full text, so a URL longer than ~70 characters breaks post 1 — shorten it or move it to 6/6.

> **1/6** I ran the tests from 107 merged AI-agent pull requests against the commit each PR
> branched from, to ask whether they could have caught anything. 25 Python repos, 99 reached a
> verdict. Not a comparison to human PRs — no control arm. https://alex-lop.github.io/guardposts/study.html

> **2/6** The pre-registered number is about the tests each PR *adds*: 1 of 99 added only
> tests that already passed at its base commit. Wilson 95% [0.2%, 5.5%]. On fix-titled PRs,
> 0 of 41. The strong form of "agents write tests that can't fail" fails here.

> **3/6** Looser bar — zero discriminating tests anywhere in the files the PR touched — is
> 0 of 99. But those PRs sit in 25 repos, and two PRs of one repo supply 50.5% of the discriminating rows.
> With the repo as the unit it's 0 of 25, [0.0%, 13.3%]. Use that one.

> **4/6** The other direction: 78.0% of all test ids in the touched files pass on both sides
> — but 90.9% of those ids are pre-existing tests being re-run. Restricted to the tests these
> PRs actually *added*, only 10.5% pass on both. That's the honest comparison.

> **5/6** And I had the mechanism backwards in a draft. Only 15.4% of the discriminating
> evidence is "the PR added the module so the test couldn't import at base." 58.6% is a
> pre-existing *passing* test broken by an import the PR's own test patch added.

> **6/6** Caveats: 25 repos, chosen because their base installs from a lockfile and runs
> offline. I called that the well-maintained tail; withdrawn — they have *fewer* stars than
> the ones that failed to build. Method, CSVs, red-team log: https://alex-lop.github.io/guardposts/study.html

### 3. PyCoder's Weekly and Changelog News — submission blurb

Both take the same text. PyCoder's: https://pycoders.com/submissions → "Submit Your Link »"
($0, "we want to hear from you about projects you are working on … and articles you want to
share"). Changelog News: https://changelog.com/news/submit ($0, free account; "Submitting
your own work is also encouraged"; no how-tos, no commercial products). Both are weekly and
notify only on publication. **Title:** *Do merged AI-agent PRs ship tests that could have
caught anything?* **URL:** `https://alex-lop.github.io/guardposts/study.html`

> A differential-execution study of 107 merged, agent-trailered pull requests across 25 public
> Python repositories: each PR's own test files are applied to the PR's base commit, run twice
> there and twice on the merge commit in an offline container, and classified in SWE-bench's
> FAIL_TO_PASS / PASS_TO_PASS vocabulary. Of the 99 PRs that reached a verdict, exactly one
> added tests that all already passed at its base commit (Wilson 95% [0.2%, 5.5%]); under the
> looser bar of "no discriminating test anywhere in the touched files" it is 0 of 99, or 0 of
> 25 repositories once clustering is respected. But only 10.5% of the tests these PRs *add*
> pass on both sides, against 78.0% of every test in the files they touch — and 58.6% of the
> discriminating evidence turns out to be a pre-existing passing test broken by an import the
> PR's own test patch added, not a newly-arrived module. Open dataset, open instrument, every
> published number reproducible by one script, and a section listing all 25 objections three
> red teams raised against the write-up with each one's disposition. Written with AI
> assistance, disclosed in the post.

### 4. arXiv cs.SE — abstract, and the gate in front of it

**The gate, verbatim from `research/channels.md:135`:** "arXiv requires that users be
endorsed before submitting their first paper to arXiv or a new category." Endorsement needs
either a claimed co-authored paper *plus* an institutional address, or a personal endorsement
from an established arXiv author — and "**A .edu address alone does not clear the gate for a
first-time author with no claimed paper.**" arXiv also warns that "it is inappropriate to
email large numbers of potential endorsers at once."

**Consequences already recorded, not re-argued here:** `DECISION.md` §3 dates the endorsement
request at **2026-09-19** and declares the arXiv path dead if no endorser has replied in
writing by **2026-09-26**; §1.7 puts the endorser **outside Northeastern**, because
university contact is RED (`CLAUDE.md` §2). **Nothing in this section asks the agent to
contact anyone.** If the gate does not clear, the study still ships as an open dataset
release and the HN, Bluesky and newsletter drafts above are unaffected.

**Abstract (one paragraph, 262 words, 1,681 characters — under arXiv's 1,920 limit):**

> Coding agents now open a large share of pull requests on public repositories, and roughly
> half of those that touch code under test also change tests (49.6%, arXiv:2607.18057;
> 42.9% include tests at all, arXiv:2601.21194). Whether those tests could have caught
> anything has been measured statically, or dynamically on benchmark rollouts, or discarded
> as a by-product of benchmark construction. We apply BSG-VA's base/candidate replay to
> merged real-world pull requests. For 107 merged PRs carrying a verbatim coding-agent
> trailer, across 25 public Python repositories whose base commit installs from its lockfile
> and runs its suite offline, we apply each PR's own test files to the PR's base commit and
> execute them twice on base and twice on the merge commit, classifying every PR-touched test
> id as FAIL_TO_PASS, PASS_TO_PASS, or UNRESOLVED. Ninety-nine PRs reach a verdict. One added
> only tests that already pass at its base commit (1/99, Wilson 95% CI [0.2%, 5.5%]; 0/41 on
> fix-titled PRs); under the looser criterion of no discriminating test anywhere in the
> touched files, 0/99, which is 0 of 25 repositories, [0.0%, 13.3%], with the repository as
> the unit. The tests these PRs add are mostly discriminating (10.5% PASS_TO_PASS) while the
> files they touch are mostly not (78.0%), and 58.6% of FAIL_TO_PASS evidence is a
> pre-existing passing test collaterally broken by the patch. We release the instrument, both
> datasets, and the funnel, and we report the selection's covariates rather than assuming its
> direction. To our knowledge no prior work reports this rate with its denominator on merged
> agent PRs; our absence search is arXiv-metadata-dominant and we state its limits.

### Not in this section (deliberately)

- **No Show HN.** `research/channels.md:87` excludes reading material; a study is reading
  material even though the instrument is runnable.
- **No Reddit or Lobsters draft.** Both are robots-excluded, so their rules could not be read
  today and are UNVERIFIED (`research/channels.md` §0). Drafting for rules we could not fetch
  is how a submission gets removed.
- **No price, no service, no hosted anything.** Changelog News bars it and the study is not
  for sale.
- **No individual named anywhere**, including no endorser candidate — the arXiv item names a
  gate and a date, not a person.
- **No claim that any of this is specific to agents.** There is no human-PR control arm in
  the study, so no draft may say or imply one.

---

## A — free "agent autopsy" (unpriced experiment; gate: 5 accepted by 2026-09-30)

### In the room (Venture Café Cambridge, Thursdays 4:30–8 pm) — the 20-second version
> I'm Alex, CS at Northeastern. I've spent the summer running parallel coding agents on my own repos with fences and audit trails — about 230K lines of it, all tested. I'm doing free 60-minute "agent autopsies" for a handful of engineering leads: you pick a repo, I run Microsoft's free readiness checker and Claude Code's `/doctor` on it live, and then I show you the three places in *your* codebase where an agent will do something you'd never let a junior do — the invariants worth a hook. No pitch, no price; I'm collecting what breaks. Want one?


### September calendar for A (verified from the organizers' pages, 2026-08-30)
| Date | Event | Why / note |
|---|---|---|
| **Thu 2026-09-03**, 4:30 pm | Venture Café Cambridge — "Uncertainty Principle: AI, Quantum, and the Tools Reshaping Work" (CIC, 1 Broadway) | The right room, five days after the Cursor news. Skip AI Tinkerers the same night (GTM theme). |
| Thu 2026-09-10 | Venture Café — "University of Tsukuba Night" | Low value for this thesis; optional. |
| **Thu 2026-09-17**, 6–8:30 pm | **"AI Native Dev Boston: Inside the Dark Factory"** — AI Security Engineers community, at Snyk, 100 Summer St | Collides with Venture Café; **take the meetup** — it targets teams already shipping with coding agents. Registration via the Luma link on the meetup page. |
| Thu 2026-09-24 | Venture Café — Thursday Gathering | Second Venture Café night (capacity rule: two per month). |
| Thu 2026-10-01 | **Boston AI Week @ Venture Café** | Hold. |

### Follow-up email (send within 24 h of meeting someone) — template
**Subject:** the autopsy — 60 min, your repo, no pitch

> Hi {first name},
>
> Good to meet you at Venture Café on Thursday. As promised: a free 60-minute agent autopsy on {repo or team}.
>
> What happens: on a call, on a throwaway clone you control, I run `microsoft/agentrc` (free, Microsoft's readiness scorer — it will tell you your Python repo has no linter, which is the fun part), Claude Code's `/doctor` on your `CLAUDE.md`/`AGENTS.md` if you have one, and `cc-safety-net`. Then the part no tool does: I read your codebase for an hour beforehand and bring the three repo-specific invariants I'd put a hook on — the "never write raw SQL outside `db/`" kind, not the "don't `rm -rf`" kind. You keep the notes. If nothing's useful, you've lost an hour and I've learned something.
>
> Two slots next week: {slot 1}, {slot 2}. Reply with a repo (read-only is fine) and one thing your agents keep getting wrong.
>
> Alex
> _(CS+Math, Northeastern '28 · {github link} — the fenced-agent control plane and the patch-verification engine are both there, with the tests)_

**Why this works:** every claim is demonstrable in the meeting; the free tools are named honestly (the red team's point); the deliverable named is the one thing no free tool ships. **Why this person:** filled per target below.

### Named A targets — 12 Boston/Cambridge companies whose own job posts name Claude Code / Cursor / Codex as internal tooling (read-only research; contacts are the companies' own published role emails or contact forms only — no individual is named; the per-company people the research found are in `private/outreach/named-targets.md`)

| # | Company | Area · size | Published channel | Why now (their own job post) | Evidence | Fit |
|---|---|---|---|---|---|---|
| 1 | **Hi Marley** | Boston, MA · ~100 employees; ~30-40 engineers; all 11 | https://www.himarley.com/contact-us/ | Clearest org-wide adopter found in Boston. Principal AI Product Engineer req: 'You live in Claude Code, Codex, and Cursor.' Sr. IT Systems Engineer req: 'Provision and manage access to Claude, ChatGPT, and Cursor; support colleagues who are building and runnin | [post](https://www.himarley.com/job-openings?gh_jid=7773714003) | 5 |
| 2 | **CloudZero** | Boston, MA · ~150 employees; ~50 engineers; 8 of 15 o | https://www.cloudzero.com/contact/ | Double exposure. Internally: Senior IT Operations Engineer (Boston) req says 'You reach for Claude Code, Claude Desktop, or ChatGPT before problem-solving manually'; Senior CloudOps Engineer (Boston) wants 'an appetite for frontier AI models such as Claude, Co | [post](https://jobs.ashbyhq.com/cloudzero/4ad891a4-8e60-4bc9-9dfd-a0a7a895a865) | 5 |
| 3 | **Reprise** | Boston, MA · ~80 employees; ~30 engineers | https://www.reprise.com/contact | Most explicit public statement of pipeline-level agent adoption found in Boston, in their own job post: 'We have aggressively used AI to change our entire build pipeline to use agent-driven recursive development cycles and we are starting to do the same on our | [post](https://jobs.ashbyhq.com/reprise/4d6b5343-170f-4ed0-8488-440acac01f32) | 4 |
| 4 | **Suno** | Cambridge, MA (Harvard Square HQ) · ~150 employees; ~50 engineers; 12 of 62  | https://jobs.ashbyhq.com/suno | They have stood up a named internal function for exactly this decision. Senior/Staff SWE, AI Engineering: 'One, AI Leverage, empowers engineers and other teams to move faster at scale with agentic tools.' Staff/Senior SWE Platform: 'Build shared infrastructure | [post](https://jobs.ashbyhq.com/suno/9e6da9b6-8562-4d9e-ae8e-c3319f76bdba) | 4 |
| 5 | **Lumafield** | Cambridge / Boston, MA (plus Everett, MA · ~200 employees; ~60 engineers; 8 of 16 o | info@lumafield.com | Agentic coding tools are a stated hiring bar even for customer-facing engineers: 'Comfortable using agentic coding tools (Claude Code, Cursor, or similar) to build tools and automations. You don't need to be a software engineer, but you should be someone who r | [post](https://jobs.lever.co/lumafield/181866d7-ffa5-4e12-b25c-aa4f1fd0bb11) | 4 |
| 6 | **Kodex** | Boston, MA (YC S21 · 30 employees per YC directory; ~15 engin | https://www.kodexglobal.com/contact | Only YC Boston company (2021+ batches) that cleared the evidence bar. Their engineering req states both the practice and the guardrail: 'We leverage AI-assisted, agentic development. We use these tools to move faster, but never ship code we can't explain, test | [post](https://jobs.ashbyhq.com/kodex/31e53827-080b-4266-945c-950005486081) | 4 |
| 7 | **Tulip Interfaces** | Somerville, MA · ~250 employees; Somerville engineering ~ | hello@tulip.co | Actively hiring a dedicated developer-experience function for agents: 'AI Enablement Engineer - Developer Experience' and 'Developer Experience Engineer' reqs both in Somerville, plus a Budapest twin. Their embedded SWE req names the tools directly - 'Experien | [post](https://tulip.co/careers/job-posting/?gh_jid=7820441003) | 4 |
| 8 | **Jellyfish** | Boston, MA (HQ · ~180 employees; ~55 engineers | hello@jellyfish.co | Two reasons. Internally, their Staff Data Engineer req calls for someone to 'spearhead development of internal tooling and agentic workflows that meaningfully accelerate engineering velocity across the org.' Commercially, they ship Jellyfish AI Impact, the pro | [post](https://jobs.ashbyhq.com/jellyfish/255c6eee-7ab8-431b-a007-4b637dccee40) | 3 |
| 9 | **Fairmarkit** | Boston, MA · ~100 employees; ~30 engineers; 4 of 7 op | https://www.fairmarkit.com/careers | Standing up a greenfield agent team in Boston right now: 'Agentic AI Engineer (Boston, Hybrid)' - 'Fairmarkit is building a brand new AI and Agentic business line from scratch, and we're assembling a small, elite founding team around it. This is one of the fir | [post](https://job-boards.greenhouse.io/fairmarkit/jobs/6111188004) | 3 |
| 10 | **Lila Sciences** | Cambridge, MA · Cambridge software + data platform group | https://job-boards.greenhouse.io/lilasciences | Names the exact tools as a hiring requirement: Staff Engineer, Data Platform - 'Proficiency with AI-assisted development tools (Cursor, Claude Code, or similar) and ability to incorporate them effectively into day-to-day engineering work.' They also have a Cam | [post](https://job-boards.greenhouse.io/lilasciences/jobs/4222065009) | 3 |
| 11 | **EverQuote** | Cambridge, MA · ~350 employees - engineering is ABOVE th | https://careers.everquote.com | Two Cambridge engineering reqs name the stack explicitly. Senior Full Stack Engineer II: 'proficiency in using AI coding tools (e.g., Claude Code, Copilot) in the full software development lifecycle, including designing, generating code, testing, monitoring an | [post](https://careers.everquote.com/job/?gh_jid=7670496003) | 3 |
| 12 | **ClearGov** | Boston area (Wellesley, MA HQ) - but pla · ~120 employees; ~35 engineers | info@cleargov.com | The most complete tool list of any board surveyed: Sr. Software Engineer - Platform asks for 'Experience using AI-assisted development tools such as Cursor, Windsurf, Claude Code, GitHub Copilot, CodeRabbit, Greptile, or similar.' A team that lists six tools h | [post](https://job-boards.greenhouse.io/cleargov/jobs/4371916009) | 2 |

**Personalization line per company:** quote their own job post — e.g. *"your Principal AI Product Engineer req says 'you live in Claude Code, Codex, and Cursor' — that's the setup I autopsy."* Do **not** reference the HN Cursor thread: it is pseudonymous and names no Boston company (verified).

**Caveats from the research:** WebSearch was exhausted, so this list comes from Greenhouse/Ashby/Lever job-board APIs across ~66 Boston boards; the YC Boston 2021+ directory does NOT support the thesis (51 active companies, mostly biotech/hardware; ~11 software firms in band, only Kodex cleared the evidence bar). EverQuote and Tulip are above the 5–50 band; ClearGov's platform team is in Calgary. Cold email to a CTO is the weakest channel here — the plan is to meet people at Venture Café first and use these as the follow-up/warm list.


---

## B — practitioner calls — **WITHDRAWN 2026-08-30** (B killed before sending; kept as a record)

**One question, asked of firms already named in this week's sample digest:** *"Does a material share of your work arrive after a Notice of Intent is already on a Conservation Commission agenda — from a party not already on the filing? Or are you always the one who filed it?"* Secondary: *"Do you use BLDUP, masspublicnotices.org, or a town's Notify Me emails today, and what do they miss?"*

### Email — template (Alex sends; no attachment; the sample is offered, not pushed)
**Subject:** quick question from a Northeastern student about how wetlands work gets awarded

> Hi {first name},
>
> I'm a CS student at Northeastern doing a small research project on Massachusetts conservation-commission filings. This week I compiled every ConCom and planning-board agenda item across 30 Greater Boston towns — {firm} shows up on {N} of them ({town}, {date}, {address}), which is why I'm writing to you rather than to a directory.
>
> I have one honest question and it decides whether the project is useful to anyone or just interesting to me: **when a Notice of Intent hits an agenda, is the wetlands scientist / engineer already hired — or does work still get awarded after that point (peer review, replication, monitoring, a consultant swap)?**
>
> Fifteen minutes on the phone would answer it. In return I'll send you the full 30-town compilation for this week, free, whatever you say. {slot 1} or {slot 2}?
>
> Alex Lopez
> Northeastern University, CS + Math '28

### Named B targets — 15 firms from read-only research (firms only; contact = the firm's own published business channel; no individual is named here — the per-firm people are in `private/outreach/named-targets.md`; no social-network scraping)

**Call first (the kill/revive test — pick three, answers decide B on 2026-09-15):**

| # | Firm | Town | Type | Published channel | Size | Named this week | Evidence | Why this firm |
|---|---|---|---|---|---|---|---|---|
| 1 | **Environmental Consulting & Restoration, LLC (ECR)** (fit 5) | Plymouth | wetlands + restoration | https://ecrwetlands.com/contact-us/ (form; site 403s non-browsers — verify live) | 4–6 | Named on the agenda as the representative of record ("Representative: (individual), ECR") — NOI, 1 Sycamore Lane, DEP 034-1569, Hingham ConCom 2026-08-31 | [agenda](https://www.hingham-ma.gov/AgendaCenter/ViewFile/Agenda/_08312026-11227) | Four-person shop that says on its own team page it partners with engineering/survey firms to win work; restoration + delineation + permitting is exactly the digest's section 0 |
| 2 | **Goddard Consulting LLC** (fit 5) | Northborough | wetlands | info@goddardconsultingllc.com (site footer) / contact form | 8–15 | Wetlands consultant of record, NOI, 281 Main Street, Reading — continued hearing, Reading ConCom 2026-08-26 | [agenda](https://www.readingma.gov/DocumentCenter/View/24619/2026-08-26-Conservation-Commission-Agenda) | Pure-play wetlands consultancy, four MA offices, no product of its own; every NOI in the digest is one of their jobs or a competitor's |
| 3 | **EBT Environmental Consultants, Inc.** (fit 5) | North Oxford | wetlands | no company-level channel published — the only published contact is a personal address (withheld; see `private/outreach/named-targets.md`) | 1–3 | Environmental consultant of record — "Pleasant View Trust c/o EBT Environmental Consultants, DEP 95-1025", NOI, 167-171 Pleasant St, Ashland ConCom 2026-08-24 | [agenda](https://www.ashlandmass.com/AgendaCenter/ViewFile/Agenda/_08242026-7950) | Est. 1986, one or two people, works "as a subcontractor to engineering, survey and architectural firms" (their words) — the persona the B thesis needs, and the one most likely to say the vendor is always already on the filing |
| 4 | **Chongris Engineering LLC** (fit 5) | Andover | septic / stormwater civil | https://chongrisengineering.com/contact/ (form; the other published address is a personal one, withheld) | 1–5 | Civil engineer of record (base survey), Brookline 2026-08-26; and Wellesley Design Review Board, 15 Lathrop Road Large House Review, 2026-09-02 | [agenda](https://wellesleyma.gov/AgendaCenter/ViewFile/Agenda/_09022026-9582) | Headline is "Fast Permitting. Short Lead Times." — a firm that sells on permit velocity is the one most likely to value permit visibility |
| 5 | **Reed Land Surveying, Inc.** (fit 5) | Lakeville | survey | no company-level channel published — the only published address is a personal one (withheld) | 4–8 | Surveyor of record on a Reading conservation item, 2026-08-26 | [agenda](https://www.readingma.gov/DocumentCenter/View/24619/2026-08-26-Conservation-Commission-Agenda) | Their site names their buyers — civil engineers, developers, GCs, site contractors — i.e. the applicants in this digest; an Order of Conditions today is a stakeout job in six weeks (the post-filing scope question, in their own business) |
| 6 | **Continental Land Survey, LLC (C&L)** (fit 5) | Franklin / Needham | survey | survey@clsurveyma.com (printed on the agenda itself) | 1–2 | Land surveyor of record, Wellesley Design Review Board, 15 Lathrop Road (LHR-26-06), 2026-09-02 | [agenda](https://wellesleyma.gov/AgendaCenter/ViewFile/Agenda/_09022026-9582) | One-surveyor shop whose listed service area (~50 MetroWest/South Shore towns) nearly matches the digest's coverage |

**Hold (send only if B survives the first three calls):**

| # | Firm | Town | Type | Published channel | Size | Named this week | Evidence | Why this firm |
|---|---|---|---|---|---|---|---|---|
| 7 | **LEC Environmental Consultants, Inc.** (fit 4) | Wakefield / Plymouth | wetlands | northlec@lecenvironmental.com; marketing@lecenvironmental.com (published; site is http-only) | 20–30 | Named of record in the sample (see digest §5) | see digest §5 | Mid-size wetlands firm with a published marketing address — the least cold of the wetlands set |
| 8 | **Merrill Engineers and Land Surveyors** (fit 4) | Hanover | civil + survey | https://merrillinc.com/contact/ (form has a "Service(s) I can provide Merrill" option) | 40–60 | Named of record in the sample | see digest §5 | Vendor-inbound path exists on their own site |
| 9 | **Highpoint Engineering, Inc.** (fit 4) | Dedham | civil / stormwater | https://highpointeng.com/contact/ | 15–20 | Named of record in the sample (Needham ×2) | see digest §5 | Sells Permit Expediting and Stormwater Inspections as service lines — already monetises permit navigation; fastest possible sale or the clearest "we already track this" |
| 10 | **Water & Wetland** (fit 4) | South Grafton | aquatic / wetland restoration | no company-level channel published — the only published address is a personal one (withheld) | 10–20 | — | — | Restoration contractor: the persona most likely to be hired AFTER an Order of Conditions (replication/monitoring) — a direct test of the post-filing-scope question |
| 11 | **Field Resources, Inc.** (fit 4) | Needham | survey | office@fieldresources.net (published; http-only) | 5–15 | Named of record in the sample | see digest §5 | Needham-based; sample density is high there |
| 12 | **Green Seal Environmental, LLC** (fit 4) | Canton (project) | environmental engineering | in person — Canton Planning Board 2026-09-02 (the only public evidence is the agenda itself) | unknown | Named on Canton PB agenda 2026-09-02 | see digest | Meet at the hearing, not by email |
| 13 | **Beals and Thomas, Inc.** (fit 3) | Southborough | civil / survey / wetland science | mail@bealsandthomas.com | 50–70 | Named of record in the sample (Needham) | see digest §5 | Larger; likely already served — useful as a "what do you use today" call |
| 14 | **Activitas, Inc.** (fit 3) | Dedham | landscape + civil | admin@activitas.com | ~13 | Named of record in the sample (Reading) | see digest §5 | Adjacent persona |
| 15 | **Horsley Witten Group, Inc.** (fit 3) | Sandwich | stormwater / environmental | hwinfo@horsleywitten.com | 80–100 | — | — | Too large for the wedge; a good "what do you use today" reference call |

**Personalization line per firm** (drops into the `{firm} shows up on {N} of them` sentence): use the "Named this week" cell verbatim, with the agenda link.

**Research notes:** none of the 15 shows any BLDUP/Dodge/ConstructConnect reference on its site; Highpoint sells permit expediting; Merrill's contact form has a vendor-inbound option; ECR's site 403s non-browser clients (re-check live); EBT publishes no company-level mailbox — its only published contact is a personal ISP address, so it has no usable public channel for this purpose. Excluded: firms with no usable web presence (McCarty, Choubah, Connorstone) and national firms already served (VHB, Weston & Sampson, CDM Smith, Kimley-Horn, TRC, Foth, Wright-Pierce, Epsilon, Control Point).

---

## Not in this batch (deliberately)
- No sales email to the 45 firms in `private/outreach/crm.csv` — the red team showed the lead-feed thesis is unproven and the sample was still advertising a price and a field it can't deliver (both fixed). Nothing goes to them until the three calls come back.
- No message to BLDUP — but see `DECISION.md` open questions: an informational interview there is worth more than a crawler.
