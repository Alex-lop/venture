# guardrail-checkup next to the tools you already have

Figures fetched **2026-08-31**; every quotation and number on this page is checked against a
copy of its source under [`docs/evidence/`](evidence/), and `tests/test_comparison_truth.py`
fails if a quotation is not in one of those files. Re-fetch with
`python3 scripts/refresh_evidence.py`, which exits non-zero if a source stopped saying what
this page says it says.

**Install the incumbents.** `/doctor` ships with the agent and prints read-only installation
diagnostics. `cc-safety-net` blocks destructive Git and file system commands before a tool call
runs. Each is better than anything this package would write for you at the thing it does, and
the second of them enforces. This one reports, and the report is what you read before deciding
what to enforce.

## The three you will meet first

| | What it does | Adoption (2026-08-31) | What it does not do |
|---|---|---|---|
| **Claude Code `/doctor`** | "Run a setup checkup that diagnoses issues and can fix them. Checks installation health, including duplicate or leftover installs, PATH problems, and unparseable settings files." Further down its own list, it also "trims checked-in CLAUDE.md files by cutting content Claude could derive from the codebase". From the terminal, `claude doctor` "prints read-only installation diagnostics without starting a session." | Bundled with Claude Code | Diagnoses the *installation*. It does not read your `db/` directory or your git history, and it does not know which of your paths an agent should never write. |
| **`kenryu42/cc-safety-net`** | "A pre-execution guard for AI coding agents. It blocks destructive Git and file system commands, plus common attempts to access sensitive files, before a tool call runs." | 1,517 stars, 75 forks, 0 open issues, last push 2026-08-31, MIT | Blocks a *generic* set of dangerous commands. A generic tool has two settings — allow and block — because it has never read your repository. The setting that is right for your build cache is wrong for your fixtures. |
| **`microsoft/agentrc`** | "Get your repo ready for AI." — its own description, and all this page will say about it: the only source checked in for it is the repository metadata below, and that says what it is for, not what it emits. | 1,037 stars, 93 forks, 56 open issues, last push 2026-08-26, MIT | Not characterised here. Read its README before you decide between them; this page does not describe a tool it has not fetched a source for. |

## The one-line difference

`/doctor` diagnoses the *installation* and offers to trim your `CLAUDE.md`. `cc-safety-net`
blocks a *generic* list of destructive commands before a tool call runs. This package instead
reads your git history and `CODEOWNERS` and hands back what is enforced today, what a generic
scorer will get wrong about you specifically, and up to three ranked places a hook may pay for
itself. That is what this one does, and it
enforces none of it.

That difference is thin. This package is not defended by capability; it is defended by being
the artifact you run first, and by being honest about the other three in the report it
writes.

## What this one deliberately does not do

- **No readiness score, no grade, no percentage for your repository.** §3 of the report is a
  judgement about your code and a number would launder it into something it is not. The report
  heads §3 *Invariant candidates*, says a human confirms or replaces them, and names the ones
  whose only evidence is a path match. The number §3 prints beside each candidate is the
  evidence tally that section defines, not a rating.
- **No enforcement.** It writes a hook; it never installs one. It writes a policy; it never
  applies one. Every draft goes to the directory you name with `--emit-dir`, and the tool
  refuses to write anywhere inside the repository it read.
- **No model call, no network.** The report is deterministic: the same commit, with
  `SOURCE_DATE_EPOCH` set, produces the same bytes apart from the command line the report
  records. Without `SOURCE_DATE_EPOCH` the date line moves and nothing else does. That is also
  why §3 cannot read your architecture, and the report says so.
- **It does not run the tools it names.** §2 of the report is the falsifier list to have
  ready when *you* run them, built from your own files, with the command that disproves each
  claim. `guardrail-checkup` starts no `npx` and opens no socket.

## Where it sits with the sibling packages

`agent-plan-lint` validates a plan against a policy. `egresswall` screens what a tool hands
back. `guardrail-checkup` is the thing you run before you have either: when their signature
keys are absent it drafts a starter policy, when an MCP configuration exists it drafts a
screened copy, and it applies neither.
