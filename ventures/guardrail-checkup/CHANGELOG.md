# Changelog

All notable changes to this project are documented here.
This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-31

The first release. There is no earlier version to have changed from, so this
entry describes what the release contains and what was decided during its
review.

### Added

- `guardrail-checkup run PATH --out REPORT.md` writes a six-section report over
  one repository: Scope, Tool results and what they got wrong, The three
  invariants, Monday list, What this did not cover, Provenance. The sections and
  their order are the ones the in-person session's runbook fixes, so the two
  deliverables are interchangeable.
- A guardrail inventory over `CLAUDE.md`, `AGENTS.md`, `.cursorrules`,
  `.cursor/rules`, `.github/copilot-instructions.md`, `GEMINI.md`,
  `.claude/settings.json` hooks, `.mcp.json` / `claude_desktop_config.json` /
  `.claude/mcp.json` servers, `.pre-commit-config.yaml`, installed `.git/hooks`,
  `CODEOWNERS`, `.github/workflows/`, secret-scanning configuration, lockfiles
  and test layout. Every finding carries the `file:line` it came from and one
  line naming what an agent can do because of it.
- Three ranked invariant candidates from path heuristics, from repair commits in
  `git log`, and from `CODEOWNERS`, each with a `PreToolUse` hook that blocks
  writes to the path and a one-line test. The report labels them candidates and,
  when fewer than three have evidence, says so rather than inventing a third.
- Composition with the sibling packages: `agent-plan-lint` validates any
  checked-in policy or plan document and drafts a starter policy when there is
  none; `egresswall` screens a sample of checked-in JSON fixtures and the MCP
  configuration is rewritten with `egresswall proxy` in front of each server, as
  a suggestion.
- `--emit-dir` for the drafted policy, hooks and MCP suggestion; `--format json`
  for the same report as a document; `--max-files` for the listing cap.

### Decided during the build

- **The tool never writes into the repository it reads.** `--out` and
  `--emit-dir` are refused with exit 2 if either resolves inside `PATH`. The
  only subprocess in the package is `git`, restricted to `ls-files`,
  `rev-parse` and `log` by an assertion in the wrapper; `tests/test_readonly.py`
  asserts that over the AST of every shipped module, along with the absence of
  any import that could reach the network or a model provider.
- **Exit status is 0 whenever the report was written, and 2 on a usage or IO
  error. It is never 1.** This tool reports; it does not gate. The sibling
  packages exit 1 on a finding because they are gates.
- **No score, no grade, no percentage.** Section 3 is a judgement about the
  reader's code, and a number would launder it into something it is not.
- **The report is deterministic.** The same commit produces the same bytes;
  `SOURCE_DATE_EPOCH` pins the date, and the path is printed as given rather
  than resolved, so a report can be diffed and a demo can be checked in.
- **Section 2 does not run the tools it names.** It emits the falsifier list —
  the claims a generic readiness scorer makes, next to what is true in this
  repository and the command that shows it — because running `npx` would break
  the offline promise and because the falsifiers are what the reader needs.
- The history heuristic weighs a repair commit double when the same commit
  touched a test path named for a regression. The first draft matched
  `\bregress` with a word boundary, which never fired on `test_regression_x.py`;
  the boundary is gone and `tests/test_scan.py` covers it.

### Pre-release scaffolding

- `[tool.uv.sources]` in `pyproject.toml` resolves `agent-plan-lint` and
  `egresswall` from the sibling working copies, because neither is on PyPI yet.
  **The release deletes that table and re-locks**, so the declared PyPI ranges
  `agent-plan-lint>=0.1,<1` and `egresswall>=0.1,<1` are what a user resolves.
  `tests/test_packaging.py` fails if the table is present and this note is not.
