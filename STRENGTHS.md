# STRENGTHS — what this principal plus this agent can build faster than most

**Written:** 2026-08-30, from `ASSETS.md` and the §0 facts available (§0 is mostly blank; "strengths" below are inferred from ~230K LOC of shipped code, not from self-report — Alex should correct them).

## Specific, evidenced strengths

1. **Provable-agent infrastructure.** Fencing tokens, hash-bound records, compare-and-swap git refs, offline-verifiable audit capsules, differential base-vs-candidate verification, value-level egress firewalls, preview→digest→confirm approval. Four repos, ~7 weeks, all tested (1,229 + 408 + 238 tests pass today). The readers found *no exact open-source equivalent* for the Graphene seatbelt or the RegLineage lease runtime; the Nemisis claim matrix **does** have equivalents (SWE-bench's FAIL_TO_PASS/PASS_TO_PASS grading; `jittest`), so its value is as a measurement instrument, not a product. This is the one thing Alex can build faster than a funded team, because it is already built.
2. **Evidence-first engineering discipline.** Doc-truth tests that fail the build when a README overclaims; installed-artifact probes; parity scripts for the topologies the dev machine is not; a public postmortem falsifying his own benchmark. This is a *sellable credential* with technical buyers and auditors, and it is rare.
3. **MCP servers, hardened.** Three independent implementations (Graphene 9-tool, RegLineage zero-dep dual-handshake, X-Scraper read-only). Forged-argument rejection, response screening, loopback trust boundaries.
4. **Sandboxed execution of untrusted code on macOS and Docker.** Seatbelt SBPL profiles, PID-reuse-safe process ownership, hermetic git. Deep, correct, low-level.
5. **Durable local-first state on SQLite.** Event-sourced stores, WAL + full sync, idempotency keys, hash-chained events, schema-ledger digests, a real job queue with leases and fair scheduling.
6. **Python 3.11–3.13 + uv + pydantic/dataclasses + pytest**, and dependency-free browser JS. Node/TypeScript is workable (Graft was read and run fluently) but there is no TS product of Alex's own.
7. **Running coding agents in anger, at scale, with a paper trail.** The Desktop shows 2.8 GB of parallel experiment lanes with contract/convergence reports; Graphene exists because he hit the problems. **He is the user** for anything in the "agent governance" space.
8. **Boston, physically.** Northeastern sits between Longwood and the Financial District; MA is 351 town-level jurisdictions whose planning boards meet in public; NAIOP MA (~1,800 members), AGC MA, MAIA (~1,000 agencies), and CONECT are within a T ride. Free legal clinics (IP CO-LAB, Community Business Clinic) and a non-dilutive Gap Fund (IDEA, up to $30k) are on campus. No remote SaaS founder has this.

## Concrete "we can ship this in days" list

| Thing | From | Agent-days |
|---|---|---|
| MCP egress/PII firewall as a pip package | RegLineage `agent/egress.py` + `mcp_runtime` | 5–8 |
| ~~OSS library: safely apply + verify LLM-written diffs~~ (killed — see ASSETS §3) → the non-discriminating-tests measurement study | Nemisis differential runner over a density-selected public corpus | 5–8 |
| Read-only MCP gateway over a customer's SQLite/DuckDB | X-Scraper `_ReadOnlyStorage` | 8–12 |
| AI-change provenance receipt (capsule) as a CLI + verifier | Graphene `capsule.py` + `local_result.py` + `workspace_audit.py` | 10–15 |
| Plan/policy validator ("lint your agent's plan") | Graphene `validation.py` | 3–5 |
| Differential PR verification as a GitHub check (one repo) | Nemisis + Graphene sandbox | 20–32 |
| Hand-compiled municipal filing digest (no crawler) | nothing — research + drafting | 1–2 per issue |
| Marketing-claims-bound-to-evidence GitHub Action | graphene-site `refresh.py` | 8–12 |

## Weaknesses to design around (evidenced)

- **No document/PDF extraction pipeline exists.** RegLineage's "PDF pipeline" is 70 lines of `str.find`. Any B6-style paperwork product starts from zero on the extraction half.
- **No crawler.** X-Scraper's capture is login-gated Playwright. B1 needs `civic-scraper` or new adapters.
- **Nothing has ever been deployed to a cloud, and no second user has ever run any of it.** 0 stars on Graphene. Distribution is unproven; the code is not.
- **Prose for judges, not customers.** Every README needs a rewrite of the top-of-funnel voice.
- **Weak/absent stacks:** Go, Rust, C/C++, Java, mobile, GPU. (The bounty sweep confirmed the two biggest uncontested pots were Go and Rust.)
- **Hours.** 12/week. Every plan in `ideas/` is scored on the principal's hours, not the agent's.
- **Relationships.** A 20-year-old has no 12-year client relationships (the A2 dossier's central finding). In-person Boston presence is the substitute.

## What "fit" means in the dossier scores

Fit = 5 when the wedge is a subset of code that passes tests today (agent-governance, MCP guardrails, provenance). Fit = 3 when the domain is new but the shape is familiar (SQL/dbt lineage, read-only data gateways, snapshot/diff monitoring). Fit = 1–2 when the core is document extraction, phone/voice, or a crawler — none of which exist here.
