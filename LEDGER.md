# LEDGER

Hard cap: $1,000 total. Recurring burn before revenue: ≤ $40/month. Any single spend > $25 needs an ASK.

| Date | Direction | Amount | Balance | Reason | ASK ref |
|---|---|---|---|---|---|
| 2026-08-30 | — | $0.00 | $1,000.00 | Opening balance (cap) | — |

**Model/API spend by feature** (counts toward burn once a venture is live):

| Date | Venture | Feature | Provider | Cost | Notes |
|---|---|---|---|---|---|
| 2026-08-30/31 | session 2 | swarm run (Claude Code, ultracode) | Anthropic plan quota | $0 cash | ~17.8M subagent tokens across 17 workflows (~120 agents) before the docs-site and round-7 workflows; main-session usage not reported by the client. No API keys, no paid services. |
| 2026-08-31 | session 2b | swarm run (Claude Code, ultracode), second orchestrator | Anthropic plan quota | $0 cash | ~0.25M subagent tokens across 2 workflows (4 agents: clean-clone ×2, readme-pr-repairer, pr-verifier); main-session usage not reported by the client. No API keys, no paid services. |
| 2026-09-01/02 | session 3 | close, pilot repair and guardrail verification | Codex client | $0 cash | Client usage was not reported. Eight named subagent roles: release truth, pilot gap, autopsy audit, close audit, guardrail fixer, guardrail auditor, guardrail verifier and receipt audit; at most 7 concurrent slots. No API keys or paid services. |
