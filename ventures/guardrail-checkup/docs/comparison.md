# guardrail-checkup next to the tools you already have

Figures fetched **2026-08-31**; every quotation and number on this page is checked against a
copy of its source under [`docs/evidence/`](evidence/), and `tests/test_comparison_truth.py`
fails if a quotation is not in one of those files. Re-fetch with
`python3 scripts/refresh_evidence.py`, which exits non-zero if a source stopped saying what
this page says it says.

**Install the incumbents.** Two of the three below are better than anything this package
would write for you, at the thing they do. They enforce. This one reports, and the report is
what you read before deciding what to enforce.

## The three you will meet first

| | What it does | Adoption (2026-08-31) | What it does not do |
|---|---|---|---|
| **Claude Code `/doctor`** | "Run a setup checkup that diagnoses issues and can fix them. Checks installation health, including duplicate or leftover installs, PATH problems, and unparseable settings files." Its headline move is subtraction: it "trims checked-in CLAUDE.md files by cutting content Claude could derive from the codebase". `claude doctor` "prints read-only installation diagnostics without starting a session." | First-party, bundled with the agent | Diagnoses the *installation*. It does not read your `db/` directory or your git history, and it does not know which of your paths an agent should never write. |
| **`kenryu42/cc-safety-net`** | "A pre-execution guard for AI coding agents. It blocks destructive Git and file system commands, plus common attempts to access sensitive files, before a tool call runs." | 1,517 stars, 75 forks, 0 open issues, last push 2026-08-31, MIT | Blocks a *generic* set of dangerous commands. A generic tool has two settings — allow and block — because it has never read your repository. The setting that is right for your build cache is wrong for your fixtures. |
| **`microsoft/agentrc`** | "Get your repo ready for AI." A readiness score and a machine-readable agent config standard. | 1,037 stars, 93 forks, 56 open issues, last push 2026-08-26, MIT | Scores. A score over a repository it does not know produces claims that are false for that repository — which is why §2 of this tool's report is a *falsifier list* built from your own files. |

## The one-line difference

Every tool above **enforces or scores**. None of them **reports**: runs once against a
repository you already have, and hands back what is enforced today, what a generic scorer
will get wrong about you specifically, and three ranked places a hook would pay for itself.

That difference is thin. `cc-safety-net` could add a `--report` flag in an afternoon. This
package is not defended by capability; it is defended by being the artifact you run first,
and by being honest about the other three in the report it writes.

## What this one deliberately does not do

- **No score, no grade, no percentage.** §3 of the report is a judgement about your code and
  a number would launder it into something it is not. The report calls its three invariants
  *candidates* and says a human confirms or replaces them.
- **No enforcement.** It writes a hook; it never installs one. It writes a policy; it never
  applies one. Every draft goes to the directory you name with `--emit-dir`, and the tool
  refuses to write anywhere inside the repository it read.
- **No model call, no network.** The report is deterministic: the same commit produces the
  same bytes. That is also why §3 cannot read your architecture, and the report says so.
- **It does not run the tools it names.** §2 of the report is the falsifier list to have
  ready when *you* run them, built from your own files, with the command that disproves each
  claim. `guardrail-checkup` starts no `npx` and opens no socket.

## Where it sits with the sibling packages

`agent-plan-lint` validates a plan against a policy. `egresswall` screens what a tool hands
back. `guardrail-checkup` is the thing you run before you have either: it finds the policy
you would have written and the servers you would have screened, drafts both, and applies
neither.
