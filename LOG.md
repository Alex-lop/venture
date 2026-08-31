# LOG — daily: done / learned / next (newest on top)

## 2026-08-30 (Sunday) — session 1: Phase 0 → Phase 2, red-teamed, in one day

**Done (all read-only research, code reading, and drafting; nothing sent, nothing spent, no accounts created)**
- Renamed the brief to `CLAUDE.md`; filled §0 with everything inferable and the Northeastern/MA policy research (primary sources); `assets/` gitignored; 12 public repos cloned.
- **Phase 0** → `ASSETS.md`, `STRENGTHS.md`. Every test suite run (1,229 + 408 + 238 pass). Headline: the seatbelts are real; the engines are demo-ware; no PDF pipeline, no crawler, nothing deployed, no second user ever.
- **Phase 1** → 24 dossiers in `ideas/` (14 from the brief, 9 asset-suggested, 1 red-team-requested), each with verbatim complaints, pricing, reachability, kill criteria and rubric scores; **every dossier adversarially verified** (quotes re-fetched, load-bearing claims checked, scores challenged); 6 competitor deep-dives; ranking in `ideas/README.md`.
- **A1 sweep** → 3 finders, 14 vetters: Algora's public board no longer exists; 14/14 skips; best EV $7/hr. Recorded in the A1 dossier.
- **First customer-facing artifact** → the 2026-W36 Massachusetts filings digest: 320 filings across 30 towns, hand-compiled by 9 collectors with robots.txt respected and homeowners anonymized. Kept as proof of method after B was killed. The rows are held privately (session 2, redactor); the public method record is `ventures/ma-filing-feed/samples/README.md`.
- **Phase 2** → `DECISION.md` v1 → red-teamed by three adversaries → v2 → the two follow-ups they demanded came back and killed B and B′ → **v3 (final for day 1)**.
- **C started** → `ventures/c-measurement/corpus/`: 14,417 agent-trailered merged PRs → 23 qualifying repos; funnel and biases documented.
- **Outreach** → `outreach/queue.md` (12 A-track companies with their own job-post quotes; September calendar), `outreach/crm.csv`; approval queued as ASK-009. **`ASKS.md`: nine ASKs**, ASK-007 (visa/co-op) first.
- `WEEKLY.md` week-0 review; `LEDGER.md` at $0.

**Learned**
- `gh` on this machine was authenticated as **a different person's GitHub account, not Alex's** — no GitHub writes until ASK-001 (**resolved 2026-08-30**: `gh api user` → `Alex-lop`); a secret is committed in plaintext in that account's public repository and only its owner can rotate it (ASK-002; specifics in `private/THIRD-PARTY.md`). `AC-Washing-Well@commit-changes` publishes CS2800 coursework (ASK-003).
- The brief's defaults are dead on the evidence (A1 saturated, B4 free incumbents, C1's analogue shut down). Every asset-derived dev-tool idea has a free implementation shipped in the last eight weeks. What survives verification is either physical/local or paid-on-delivery — and the red team showed even those need a real budget event, not a loud thread.
- **B died to the state's own data**: the EEA portal's free NOI API (applicant, address, resource areas, decision date; one-day lag; 18–55 days before the agenda). The Cursor "budget event" behind A's v1 wedge was refuted by the primary source (shutoff 2026-11-12; `/init` `/import` `/doctor` do the migration free).
- Two independent tests of the provenance thesis failed in opposite directions (r2: pain, no budget; r3: budget, no pain). Stop testing it.
- Research-process limits worth remembering: reddit.com 403s everything; ContractorTalk/G2/TrustRadius/Upwork/Fiverr/bls.gov 403; mass.gov 403s non-browsers (use Wayback or the EEA portal); WebSearch budget exhausts at 200 calls per agent session; Capterra/Trustpilot/Indeed/HN Algolia/GitHub/BBB/PissedConsumer/vendor pricing pages work; GitHub search doesn't honour phrase quoting; CivicClerk's OData pages at 15 rows regardless of `$top`.

**Next (session 2, once Alex answers ASK-001…009)**
- Alex: ASK-007 first; Venture Café Thu 2026-09-03 (opener in `outreach/queue.md`); send the A follow-ups within 24 h.
- Agent: widen the C corpus to ≥10 stars and script the 100-repo base-build pilot (the study's real falsifier); draft the free-autopsy runbook (agentrc + `/doctor` + `cc-safety-net` + the three-invariants read) so each session is repeatable; weekly 10-minute A1 screen; nothing on B unless an autopsied team asks for it.
- Repo hygiene once ASK-004 clears: LICENSE copyright lines, graphene-site LICENSE, the `/bin/ps` deployment defect.
