# A1 weekly bounty screen
Standing 10-minute screen (CLAUDE.md §5/§7). Four gates from `ideas/a1-bounty-engine.md` "Live sweep results" (2026-08-30).
Gates: (1) board lifetime payouts non-zero to non-maintainers; (2) <= ~3 open attempt PRs; (3) >= ~30% of last 30 merged PRs external; (4) no funder withdrawal / maintainer rewrite in thread. Expected result: nothing passes.

## 2026-08-30

Sources and statuses (all read-only, run 2026-08-30):
- `gh api 'search/issues?q=label:bounty+is:open+is:issue+created:>2026-08-23&sort=created&per_page=50'` — HTTP 200, total_count **131**.
- `gh api 'search/issues?q=label:"💎 Bounty"+is:open+is:issue+created:>2026-08-23'` — HTTP 200, total_count **0**.
- `gh api 'search/issues?q=label:"bounty:*"+is:open+is:issue+created:>2026-08-23'` — HTTP 200, total_count **0** (GitHub does not expand label globs).
- `gh api 'search/issues?q=is:open+is:issue+created:>2026-08-23+commenter:algora-pbc[bot]'` — HTTP 200, total_count **0** (no new Algora-funded issues in the window).
- `curl https://algora.io/bounties` → **404**; `https://console.algora.io/bounties` → **301**; `https://algora.io` → **200**; `https://opire.dev/home` → **200**. `https://algora.io/robots.txt` fetched, no Disallow for `*`.

Items screened: 14 newest of the 131 (`label:bounty`), all from 5 repos.

| Item | Repo age / last push / stars | Gate 1 (payouts) | Gate 2 (attempts) | Gate 3 (external merges) | Gate 4 (thread) | Result |
|---|---|---|---|---|---|---|
| relayhop/sn-monetization-runtime #756, #755, #753, #752, #751, #743, #733 | created 2026-05-02, pushed 2026-08-31, 5 stars | FAIL — no Algora/Opire board; issues are bot-generated `[radar] SN open bounty <timestamp>` self-labels | not reached | not reached | not reached | skip |
| NSPG13/agent-bounties #1262 | created 2026-07-08, pushed 2026-08-30, 13 stars | FAIL — no funding board; title `[DRAFT DIRECT]`, self-labelled | not reached | not reached | not reached | skip |
| zhangjiayang6835-cyber/bounty-plaza #952, #951 | created 2026-07-08, pushed 2026-07-12, 8 stars | FAIL — no funding board; repo unpushed for 7 weeks | not reached | not reached | not reached | skip |
| s6pa1rta3n-lab/universal_bounty_fleet #1 | created 2026-08-28, pushed 2026-08-30, 1 star | FAIL — no funding board; repo 2 days old | not reached | not reached | not reached | skip |
| OphirPay/OphirPay #393, #391, #390 | created 2026-08-01, pushed 2026-08-30, 3 stars | FAIL — no funding board; no dollar amount on the issues | not reached | not reached | not reached | skip |

Items passing all four gates: **0**.

Note: `commenter:algora-pbc[bot]` returning 0 for the window means every item in this week's `label:bounty` pool is self-applied by agent-farm repos, so gate 1 (the payout board) terminates the screen before any code is read. UNVERIFIED: whether any of these five repos has an off-GitHub funding source; not checked, gate 1 requires a public board.

next screen: 2026-09-06
