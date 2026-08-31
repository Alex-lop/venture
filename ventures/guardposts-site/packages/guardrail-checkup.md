---
layout: default
title: guardrail-checkup
---

[home](../index.md) · [study](../study.md) · [agent-plan-lint](agent-plan-lint.md) · [egresswall](egresswall.md) · [compare](../compare.md) · [about](../about.md)

# guardrail-checkup

**In design. Not built. There is no code, no repository and no date.** This page exists so
that the shape is written down in public before anything is promised about it, and so that
anyone who wants a different shape can say so in an issue while it is still cheap.

The idea: run it on your own repository and get back a report of the places where an agent
could confidently do the wrong plausible thing, and what would stop each one. It is the
self-serve version of a manual session I have written a runbook for and have not yet run
with anyone — which is why the report shape below is specified and the tool is not.

## The six-section report shape

Taken from `outreach/track-h/runbook.md` §3, where it is the deliverable of the manual
version. Marked **UNVERIFIED, not built** in that file, and it is marked that here too.

1. **Scope** — what was read, what was *not* read (no production, no CI, no data), how
   long, and who was in the room.
2. **Tool results, and what they got wrong** — the verbatim output of the free tools that
   already exist, next to the claims that are false for this specific repository, each with
   the command that disproves it.
3. **The three invariants** — a rule in one sentence; the paths it governs; the specific
   wrong-but-plausible move that breaks it; whether it has already happened, with a
   file and line, or "no prior violation found"; a hook snippet; and one command that exits
   non-zero when the rule is violated.
4. **The Monday list** — ordered, each item under 30 minutes, free things first.
5. **What this did not cover** — no runtime, no CI, one hour, one pair of eyes.
6. **Provenance** — tool versions and dates; the tools are third-party and unaffiliated;
   the report makes no guarantee about anything not actually run.

## What it will not be

- Not a score, a grade or a percentage. Section 3 is a judgement about *your* code, and a
  number would launder it into something it is not.
- Not a scanner that reports every rule it knows. The generic tools already do that, and
  section 2 exists because their output is frequently wrong about a specific repository.
- Not a hosted service, and not the free tier of one.
- Not a promise. If [`agent-plan-lint`](agent-plan-lint.md) and [`egresswall`](egresswall.md)
  do not earn their own dated gates on the [about page](../about.md), this is not built at all,
  and that decision gets written down here rather than quietly dropped.

If you want this, or want it to be something else, the useful thing is an issue on
[`Alex-lop/venture`](https://github.com/Alex-lop/venture/issues) saying what your repository
would need. That is the whole feedback channel; there is no email address on this site.
