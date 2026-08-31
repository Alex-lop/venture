# SIGNALS.md — adoption and inbound tracking

Week 0 baseline established **2026-08-30**. Every later weekly entry is a diff against this file's
Week 0 table. Owned by the standing `signal-watcher` agent (CLAUDE.md §5, Wave 4).

## What is tracked

| Signal | Source | Why |
|---|---|---|
| Stars / forks / watchers / open issues | `gh api users/Alex-lop/repos` | the §9 whole-plan gate (≥500 combined stars) |
| 14-day traffic views + clones (count / uniques) | `gh api repos/.../traffic/{views,clones}` | distribution, not just capability — the v2 thesis |
| Issues and PRs opened by non-owner accounts, last 60 days | `gh api search/issues` | the §9 "≥3 issues from strangers" per-package gate; **bot PRs do not count** |
| PyPI downloads/month per released package | `pypistats` (nothing released yet) | the §9 "≥500 downloads/month" gate |
| Unsolicited inbound contacts (email / DM / issue from a stranger) | principal reports them; details live in `private/` | the §9 I gate (≥5 by 2026-10-31) |

## The gates, in numbers (CLAUDE.md §9)

- **Per released package, within 6 weeks of its release:** ≥ 50 stars **OR** ≥ 500 downloads/month **OR** ≥ 3 issues from strangers. Missed → maintain only; effort moves to the next package.
- **Inbound:** ≥ 5 unsolicited inbound contacts by **2026-10-31**. Missed → `inbound-channel-mapper` re-runs against observed data.
- **Re-open rule (Track P):** ≥ 2 **independent** inbound parties ask to pay for the **same** capability. Until then the B slot stays empty. No exceptions.
- **Whole plan, 2026-11-30:** a paying party, **or** ≥ 500 combined stars, **or** a paid role/co-op offer that resulted from the work.

Counting rules: a bot account (dependabot and friends) is never a stranger and never an inbound contact.
A fork of someone else's repo is excluded from the stars total. Clone counts include CI and agent
traffic and are treated as a floor-quality signal only, never as adoption.

## Measurement commands (run these, verbatim, each week)

```sh
# repo table
gh api users/Alex-lop/repos --paginate \
  --jq '.[] | [.name, .stargazers_count, .forks_count, .watchers_count, .open_issues_count, .pushed_at, .fork] | @tsv'

# 14-day traffic (needs push access; the principal's login has it — record 403 if it appears)
for r in Graphene RegLineage Nemisis X-Scraper graphene-site Alex_Lopez_Website; do
  for t in views clones; do
    echo -n "$r $t: "; gh api repos/Alex-lop/$r/traffic/$t --jq '[.count,.uniques]|@tsv'
  done
done

# non-owner issues/PRs in the window (count only; never record a stranger's login in a tracked file)
gh api "search/issues?q=repo:Alex-lop/<repo>+created:>YYYY-MM-DD" \
  --jq '.items[] | select(.user.login != "Alex-lop") | [(.pull_request != null), .user.type] | @tsv'

# PyPI downloads — no packages published yet; run this from the first release onward
pypistats recent <package-name> --json     # and: pypistats overall <package-name> --last-months 1
```

## Week 0 baseline — 2026-08-30

Repos owned by Alex-lop (forks excluded from totals; measured 2026-08-30 with the commands above).

| Repo | Stars | Forks | Watchers | Open issues | Last push | Views 14d (total/uniq) | Clones 14d (total/uniq) | Non-owner issues/PRs since 2026-07-01 |
|---|---|---|---|---|---|---|---|---|
| Graphene | 0 | 0 | 0 | 0 | 2026-08-29 | 9 / 6 | 598 / 117 | 2 PRs, both bot accounts (0 human) |
| RegLineage | 3 | 0 | 3 | 0 | 2026-08-10 | 0 / 0 | 8 / 8 | 0 |
| Nemisis | 0 | 0 | 0 | 0 | 2026-08-30 | 0 / 0 | 0 / 0 | 0 |
| X-Scraper | 0 | 0 | 0 | 1 | 2026-08-20 | 4 / 2 | 211 / 42 | 1 PR, bot account (0 human) |
| graphene-site | 0 | 0 | 0 | 0 | 2026-08-28 | 0 / 0 | 50 / 24 | 0 |
| Alex_Lopez_Website | 0 | 0 | 0 | 1 | 2026-08-21 | 0 / 0 | 45 / 25 | 1 PR, bot account (0 human) |
| AC-Washing-Well | 0 | 0 | 0 | 0 | 2026-07-09 | not tracked | not tracked | not measured |
| AgenticCinemaFramework | 0 | 0 | 0 | 0 | 2026-08-13 | not tracked | not tracked | not measured |
| Alex-lop (profile) | 0 | 0 | 0 | 0 | 2026-08-10 | not tracked | not tracked | not measured |
| Final_project | 0 | 0 | 0 | 0 | 2024-04-19 | not tracked | not tracked | not measured |
| Final_test | 0 | 0 | 0 | 1 | 2026-07-25 | not tracked | not tracked | 1 open PR, bot account |
| Image_to_Characters | 0 | 0 | 0 | 0 | 2026-07-27 | not tracked | not tracked | not measured |
| The-Greater-Stake | 0 | 0 | 0 | 0 | 2026-02-23 | not tracked | not tracked | not measured |
| venture | 0 | 0 | 0 | 0 | 2026-08-31 | not tracked | not tracked | not measured |
| Graft (fork) | 0 | 0 | 0 | 0 | 2026-08-21 | — | — | excluded (fork) |
| Scweet (fork) | 0 | 0 | 0 | 1 | 2026-07-25 | — | — | excluded (fork); 1 open PR, bot |
| pydantic-crash-course (fork) | 0 | 0 | 0 | 0 | 2026-01-24 | — | — | excluded (fork) |

**Week 0 totals (non-fork):** stars **3** (all RegLineage) · forks **0** · watchers **3** ·
issues/PRs from human strangers **0** · PyPI packages published **0** · downloads **0** ·
unsolicited inbound contacts **0**.

Traffic notes: no 403 on any `/traffic/` call — the active `gh` login has push access to all six.
Views are near zero everywhere; the large clone counts (Graphene 598/117, X-Scraper 211/42) are
inconsistent with 9 and 4 page views respectively and are read as automated traffic, not adoption.
UNVERIFIED: the origin of those clones — GitHub's traffic API does not expose it.

Distance to gates at Week 0: 497 stars short of the 500-star whole-plan gate; 5 inbound contacts
short of the 2026-10-31 gate; 0 of 1 packages released against the S gate (Session 2 + 7 days).

## Inbound log

Every unsolicited contact goes here on the day it arrives. Company-level description only — no
person's name, handle, email or employer-identifying detail in this file; those go in `private/`
(CLAUDE.md §2). Value tag: `paid-signal` (asked what it costs) / `pilot` / `technical` / `noise`.

| Date | Channel | Company-level description | Value tag | Draft reply |
|---|---|---|---|---|
| _(none yet)_ | | | | |

Two rows tagged `paid-signal` from independent parties naming the same capability fires the §9
re-open rule and spawns `signal-dossier-writer`.

## Weekly entries

Each entry: date, the diff against the previous week's totals, gate status, and any action the
diff triggers. Week 0 is the baseline; the first weekly entry is due 2026-09-06.

**Interim 2026-08-31 04:35 EDT (session 2b; not a weekly entry):** non-fork stars 3 (unchanged) ·
stranger issues/PRs since 08-24 **0** (the one non-owner item, Graphene #6, is imgbot[bot] — bots never count) ·
packages released **0** · downloads **0** · inbound **0**. Gate distance unchanged. No action triggered.
