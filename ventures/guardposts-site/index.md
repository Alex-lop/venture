---
layout: default
title: guardposts
---

[study](study.md) · [agent-plan-lint](packages/agent-plan-lint.md) · [egresswall](packages/egresswall.md) · [guardrail-checkup](packages/guardrail-checkup.md) · [compare](compare.md) · [about](about.md)

# guardposts

Small, tested guardrails for coding and data agents. Each one was extracted from a
working system rather than designed for a slide: `agent-plan-lint` is the plan
admission gate out of [Graphene](https://github.com/Alex-lop/Graphene), and
`egresswall` is the tool-response screen out of
[RegLineage](https://github.com/Alex-lop/RegLineage). Apache-2.0, Python 3.11+, no
service to sign up for.

**Nothing here is for sale.** There is no hosted tier, no waitlist, no pricing page,
and no email address on this site. If you want to reach me, open a GitHub issue.

## The three packages

| Package | What it decides | Status |
| --- | --- | --- |
| [`agent-plan-lint`](packages/agent-plan-lint.md) | Does this proposed agent plan fit inside this project's policy — before anything runs? Exits non-zero with a typed code per finding. | 0.1.0 — [source released](https://github.com/Alex-lop/agent-plan-lint) (tag `v0.1.0`); release in progress; install lines appear here when the PyPI upload lands |
| [`egresswall`](packages/egresswall.md) | Does this MCP tool response carry an identifier, a secret or a denied field? If so it is refused whole, never redacted. | 0.1.0 — [source released](https://github.com/Alex-lop/egresswall) (tag `v0.1.0`); release in progress; install lines appear here when the PyPI upload lands |
| [`guardrail-checkup`](packages/guardrail-checkup.md) | Run it on your own repo, get the six-section report of what an agent could do here that nothing stops. | 0.1.0 working copy, in verification; not released |

All three exist as complete working copies — tests, a runnable demo script, a captured
`OUTPUT.txt` of what that script printed, and a comparison page each. `agent-plan-lint`'s
source is released at [`Alex-lop/agent-plan-lint`](https://github.com/Alex-lop/agent-plan-lint) (tag `v0.1.0`); its package-index
upload is pending the principal's action. `guardrail-checkup`'s working copy is in the public
monorepo, checkpointed mid-verification:
[`ventures/guardrail-checkup/`](https://github.com/Alex-lop/venture/tree/main/ventures/guardrail-checkup).
`egresswall`'s source is released at [`Alex-lop/egresswall`](https://github.com/Alex-lop/egresswall) (tag `v0.1.0`); its
package-index upload is pending the principal's action. **Nothing is installable yet:** each install line appears here when its upload lands, and the
`guardrail-checkup` tree can still change.

## The study

**Do merged agent-written pull requests ship tests that could have caught anything?**
107 merged, agent-trailered PRs across 25 public Python repositories. Each PR's own test
files were applied to the PR's **base** commit, run twice there and twice on the merge
commit, and every test id classified in SWE-bench's vocabulary.

The pre-registered claim — that a meaningful share of these PRs add tests that already
passed on the old code — **is refuted.** Exactly **1 of 99** resolved PRs added test ids
that all passed at base (95% Wilson interval [0.2%, 5.5%]). The separate per-test figure
is that **10.5%** of the ids these PRs actually *added* are `PASS_TO_PASS`.

[Read the one page, with the intervals, the limits and the three reproduce
commands →](study.md)

## What ships when

The dated commitments, and what happens if each one misses, are on the
[about page](about.md). The short version: `agent-plan-lint` first, then `egresswall`,
then `guardrail-checkup` if the first two earn it; the study published to a named venue
or an arXiv cs.SE identifier by **2026-10-10**, not merely pushed to a repository.

The order is itself falsifiable. If fewer than three agent runtimes outside my own repos
emit a machine-readable plan document before execution by **2026-09-05**, then
`agent-plan-lint` is an accessory to one system rather than a package, and `egresswall`
becomes release #1.

## "So what do you sell?"

The answer I have written down to give in person, when the first of these happens. The
first session is **Thu 2026-09-03**; none has been held yet, so this is a script and not a
record:

> Nothing yet. The autopsy is free and there's no version of it I'm charging for today —
> what I have is the study I'm running and the guardrail code on GitHub, and I'm doing
> these sessions to find out what teams would actually want built.

*(`outreach/track-h/opener.md`, written 2026-08-30. Since then the measurement run
itself has finished — see the [study](study.md) — and it is not yet published anywhere.)*

## Getting in touch

**GitHub issues, on the repository the thing lives in.** That is the only channel. No
email address, no form, no newsletter, no analytics on this site. Issues, pull requests
and discussions from people I have never met are the signal I am actually watching for,
so a bug report is worth more to me than a compliment.
