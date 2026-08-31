---
layout: default
title: About
---

[home](index.md) · [study](study.md) · [agent-plan-lint](packages/agent-plan-lint.md) · [egresswall](packages/egresswall.md) · [guardrail-checkup](packages/guardrail-checkup.md) · [compare](compare.md)

# About

Built by Alexander Lopez — `Alex-lop` on GitHub — a CS + Math student at Northeastern. The
guardrails here are not a startup and not a product line: they are the parts of larger
systems I built and kept using, pulled out one at a time, tested harder than they were
inside, and published under Apache-2.0 with an honest comparison page attached. There is
nothing for sale, no hosted tier, no waitlist, and no email address on this site; GitHub
issues on the repository a thing lives in are the whole channel. The measurement on the
[study page](study.md) exists for the same reason the packages do — it is the number I
wanted and could not find, so I ran it, and it came out against the thing it would have
been convenient for me to believe.

## The commitments, with dates

These are the operational gates from `DECISION.md` v4 §3 in the
[venture repository](https://github.com/Alex-lop/venture/blob/main/DECISION.md), copied
here because a date only counts if it is somewhere I cannot quietly move it. Each is a
number that can fail, and each has a stated consequence. When one fires, the consequence is
recorded rather than argued.

| Date | The gate | If it misses |
| --- | --- | --- |
| **2026-09-05** | Fewer than 3 agent runtimes outside my own repos emit a machine-readable plan document before execution, with a schema URL and a public example each | `agent-plan-lint` is an accessory to one system rather than a package: `egresswall` becomes release #1 and plan-lint drops to third |
| **2026-09-06** | The first package is not released and installing-and-testing from a clean clone | The wedge was too big; ship the smallest module that stands alone |
| **2026-09-13** | The second package is not released | Same |
| **2026-09-27** | The differential runner has not produced a verdict matrix for at least 20 PRs across 5 repos end to end, reproducible by one shipped script from a clean clone | The 2026-10-10 date below is abandoned on the spot and the study re-scopes to the buildability finding |
| **2026-10-03** | Fewer than 80 PRs across 20 distinct repos reach a verdict, and the headline is not stratified by who merged the PR | Published as a methods-and-instrument paper with the rate stated as a bounded observation, not a population estimate, and the abstract says so |
| **2026-10-10** | The study has no arXiv cs.SE identifier and no named, non-self-published venue acceptance. A push to a GitHub repository does not satisfy this | +2 weeks once; then publish what exists, labelled MISSED |
| **2026-10-18** | Fewer than 3 distinct non-owner accounts open an issue, PR or discussion on `agent-plan-lint` within 6 weeks of its release. Stars and downloads cannot satisfy this gate | Maintain only; effort moves to the next package |
| **2026-10-18** | A 6-week star and stranger-account count predicted on release day lands inside the prior for packages of this exact shape (0–13 stars, 0 stranger accounts) rather than the forecast | The distribution thesis is falsified for the whole family; packages 2 and 3 do not ship as packages |
| **2026-10-31** | Fewer than 3 contacts from parties with no prior in-person or 1:1 contact with me, each logged in `SIGNALS.md` with its channel and date. Track-H-originated contacts are counted separately and never toward this number | The channel ranking was wrong and gets re-run against the observed data |
| **2026-11-15** | A dominant, well-maintained incumbent for `egresswall` has appeared | `egresswall` becomes a contribution PR to that incumbent instead |
| **2026-11-30** | Fewer than 500 combined stars across the family | The open source is career capital, and it is scored as such rather than as a plan |

## AI assistance

This is disclosed rather than mentioned, because it changes how you should read everything
here. The packages, the study, and this site were built with heavy AI assistance — coding
agents wrote most of the first draft of most files, under review. Three things follow, and
they are the reason the disclosure is worth anything:

- **Every claim is bound to a check, not to a promise.** Both packages carry doc-truth
  tests: a claim in a README that no test can back fails the suite rather than being
  softened. Both comparison pages hold every quotation and star count to an archived copy of
  the page it was fetched from. The [study](study.md) reprints all of its numbers from its
  own CSVs with one command. This site has its own checker, `scripts/check_site.py`, which
  re-runs the study's analysis and binds each headline row on the study page to the line of
  that output it came from, collects both packages' own test suites (`pytest --collect-only`, no tests executed) and compares the test
  counts printed here against them, and resolves every link into the monorepo against the
  files actually tracked there.
- **The method and the numbers are mine to defend.** That sentence is in the study's own
  summary, and it is the standard here: an agent writing the draft does not move the
  responsibility for the result.
- **Where AI assistance touched someone else's material, it is disclosed there too.** Any
  open-source contribution follows the target project's own contributing and AI policy, and
  discloses assistance where that policy asks.

## Licence

Apache-2.0, Copyright 2026 Alexander Lopez, for this site and for both packages.
