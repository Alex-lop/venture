"""The six-section report. Same sections, same order as the in-person autopsy."""

from __future__ import annotations

import dataclasses
import json
import re
from datetime import UTC, datetime

from ._compose import Composition, one_line_test, settings_snippet
from ._scan import (
    CODEOWNERS_BONUS,
    HEURISTIC_BASE,
    HISTORY_COMMITS,
    HISTORY_PATHS,
    LOCKFILES,
    MAX_READ_BYTES,
    READ_ONLY_GIT,
    REGRESSION_WEIGHT,
    SKIP_DIRECTORIES,
    SNIFF_BYTES,
    Scan,
    _read,
    visible,
)

__all__ = ["SECTIONS", "render_json", "render_markdown", "run_date"]

#: The six sections, in the order the in-person session works through them. A
#: doc-truth test asserts every rendered report carries exactly these headings,
#: and none of them states a conclusion: §3 is headed "candidates" because the
#: report never claims to have found the invariants.
SECTIONS = (
    "1. Scope",
    "2. Tool results — and what they got wrong",
    "3. Invariant candidates",
    "4. Monday list",
    "5. What this did not cover",
    "6. Provenance",
)


def run_date(epoch: str | None) -> str:
    """The report's date. SOURCE_DATE_EPOCH pins it, so a demo is reproducible."""

    if epoch and epoch.strip().isdigit():
        return datetime.fromtimestamp(int(epoch), UTC).strftime("%Y-%m-%d")
    return datetime.now(UTC).strftime("%Y-%m-%d")


def _no_head(result: Scan) -> str:
    """Why a report has no commit to name. A git repository can have none yet."""

    return "this is a git repository with no commits yet" if result.is_git else "this path is not a git repository"


def _head_line(result: Scan) -> str:
    if result.head:
        return f"HEAD `{result.head[:12]}`"
    return "a git repository with no commits yet" if result.is_git else "not a git repository"


def _linter(result: Scan) -> str | None:
    for relative in result.files:
        if relative.rsplit("/", 1)[-1] in (
            "ruff.toml",
            ".ruff.toml",
            ".eslintrc",
            ".eslintrc.json",
            "eslint.config.js",
            "biome.json",
            ".flake8",
            ".golangci.yml",
        ):
            return relative
    for relative in ("pyproject.toml", "setup.cfg", "package.json"):
        if relative in result.files:
            text = _read(result.root, relative) or ""
            hit = re.search(r"(?i)\b(ruff|flake8|black|eslint|biome|prettier|pylint)\b", text)
            if hit:
                number = next(
                    (n for n, line in enumerate(text.splitlines(), 1) if hit.group(0).lower() in line.lower()), 1
                )
                return f"{relative}:{number}"
    return None


def _falsifiers(result: Scan) -> list[tuple[str, str, str]]:
    """Claim a generic scorer makes → what is true here → the command that shows it."""

    out = []
    locks = [item for item in result.files if item.rsplit("/", 1)[-1] in LOCKFILES]
    if locks:
        out.append(("“Missing package manager lockfile”", f"`{locks[0]}` is committed", f"wc -l {locks[0]}"))
    linter = _linter(result)
    if linter:
        out.append(
            (
                "“Missing linter configuration”",
                f"a linter is configured at `{linter}`",
                f"grep -n -iE 'ruff|eslint|biome|flake8|prettier' {linter.split(':')[0]}",
            )
        )
    tests = [item for item in result.files if re.search(r"(^|/)(tests?|spec)/|(^|/)test_[^/]+$|_test\.[a-z]+$", item)]
    if tests:
        out.append(
            (
                "“Testing: 0/0 (0%)”",
                f"{len(tests)} file(s) sit in a test path",
                "find . -path ./.git -prune -o -name 'test_*' -print | wc -l",
            )
        )
    return out


def _monday(result: Scan, composed: Composition, emit_dir: str | None) -> list[str]:
    """At most five actions, each naming an emitted artifact or a file to edit."""

    where = emit_dir or "the directory you pass to --emit-dir"
    items: list[str] = []
    if result.candidates:
        first = result.candidates[0]
        items.append(
            f"Read invariant candidate 1 ({first.slug}) in §3 and decide whether it is right. If it is, copy "
            f"`{where}/hooks/protect-{first.slug}.py` into `.claude/hooks/`, `chmod +x` it, and merge "
            f"`{where}/hooks/settings-{first.slug}.json` into `.claude/settings.json`."
        )
    if any(item.fact.startswith(".claude/settings.json: absent") for item in result.findings):
        items.append(
            "Create `.claude/settings.json` with the hooks block from §3. There is no hook file at all today, "
            "so every candidate in §3 has nowhere to live."
        )
    elif any("no PreToolUse hook" in item.fact for item in result.findings):
        items.append(
            "Add the §3 `PreToolUse` block to `.claude/settings.json`; today only `PostToolUse` is "
            "wired, and it runs after the write."
        )
    if "mcp-wrapped.json" in composed.drafts:
        items.append(
            f"Compare `{where}/mcp-wrapped.json` with your own MCP configuration. It is the same servers with "
            f"`egresswall proxy` in front of the {len(composed.wrapped)} that run a command line"
            + (f"; the {len(composed.unwrapped)} remote server(s) are unchanged" if composed.unwrapped else "")
            + "; nothing was applied."
        )
    if "starter-policy.json" in composed.drafts:
        items.append(
            f"Review `{where}/starter-policy.json` — a valid agent-plan-lint policy whose exclusions are the §3 "
            "candidates. Fix the write globs to the paths your agents really own, then run "
            "`agent-plan-lint check <plan.json> --policy starter-policy.json`."
        )
    if any(item.fact.startswith("secret scanning: not configured") for item in result.findings):
        items.append(
            "Add gitleaks or detect-secrets to CI or to `.pre-commit-config.yaml`. §5 explains why "
            "this tool cannot do it for you."
        )
    if any("no line both forbids something and names a path" in item.fact for item in result.findings):
        items.append(
            "Add one line to your agent instruction file naming the paths in §3 — prose is not a "
            "guardrail, but a contributor reads it."
        )
    return items[:5]


def render_markdown(
    result: Scan, composed: Composition, command: str, versions: dict[str, str], emit_dir: str | None, date: str
) -> str:
    lines: list[str] = []
    add = lines.append

    add(f"# Agent guardrail checkup — {result.root.name}")
    add("")
    add(f"Run {date} · read-only · {result.given_path} · " + _head_line(result))
    add(
        "Produced by `guardrail-checkup`, a deterministic offline reader. No model was called for anything below; "
        "every judgement in §3 is yours to make."
    )
    add("")

    # 1
    add(f"## {SECTIONS[0]}")
    add("")
    add(f"- **Repository:** `{result.given_path}`, as given on the command line")
    add(f"- **HEAD:** `{result.head}`" if result.head else f"- **HEAD:** none — {_no_head(result)}")
    add(f"- **Size:** {len(result.files):,} file(s) considered, {result.total_bytes:,} bytes on disk")
    if result.truncated:
        add(
            f"- **Listing truncated:** {result.total_files:,} paths were found and the first {result.max_files:,} in "
            "sorted order were used. Re-run with a larger `--max-files` for the rest."
        )
    add(
        "- **File list:** `git ls-files` — tracked files plus untracked files `.gitignore` does not exclude"
        if result.is_git
        else "- **File list:** a directory walk. This path is not a git repository, so `.gitignore` was not applied; "
        "the walk skipped `" + "`, `".join(SKIP_DIRECTORIES) + "`"
    )
    add("- **Language mix** (by file extension):")
    for extension, count in result.languages:
        add(f"  - `{extension}` — {count}")
    add(
        "- **Read:** the named guardrail artifacts listed in §2, every checked-in `.json` file (scanned for "
        f"agent-plan-lint's signature keys), and up to {len(composed.screened)} JSON fixture(s) screened in §2. "
        f"A file over {MAX_READ_BYTES // 2**20} MiB, or one whose first {SNIFF_BYTES // 2**10} KiB "
        "contains a NUL byte, is listed and not read."
    )
    add(
        "- **Not read:** everything else. No source file was interpreted, no test was run, no command from this "
        "repository was executed, and nothing was sent anywhere."
    )
    add("")

    # 2
    add(f"## {SECTIONS[1]}")
    add("")
    add("### Guardrail inventory — what exists, and what an agent can do because of it")
    add("")
    add("| Fact | Where | What an agent can do |")
    add("| --- | --- | --- |")
    for finding in result.findings:
        add(f"| {_cell(finding.fact)} | `{_cell(finding.where)}` | {_cell(finding.consequence)} |")
    add("")
    add("### agent-plan-lint")
    add("")
    if composed.policies or composed.plans:
        for path, status in composed.policies + composed.plans:
            add(f"- `{path}` — {status}")
        for line in composed.validations:
            add(f"  - {line}")
    else:
        add(
            "- No document in agent-plan-lint's schema was found (no `.json` file carries both "
            "`policy_id` and `allowed_write_globs`, or both `mission_id` and `tasks`)."
        )
        if "starter-policy.json" in composed.drafts:
            add("- A starter policy was drafted instead; see §4. It was **not** written into your repository.")
    if composed.unpoliceable:
        add(
            f"- {len(composed.unpoliceable)} path(s) were left out of that policy: a backslash, a control or bidi "
            "character, or a leading `./` is not something agent-plan-lint accepts as a glob — "
            + ", ".join(f"`{_cell(item)}`" for item in composed.unpoliceable[:4])
        )
    add("")
    add("### egresswall")
    add("")
    if composed.screened:
        for path, violations in composed.screened:
            if violations:
                add(f"- `{path}` — **{len(violations)} violation(s)** under egresswall's default policy:")
                for item in violations[:6]:
                    add(f"  - {item}")
            else:
                add(f"- `{path}` — clean under egresswall's default policy")
        add("")
        add(
            "A violation names a code and a path, never a value. These are checked-in fixtures; the same screen in "
            "front of a live MCP server is what stops the real answer."
        )
    else:
        add("- No checked-in JSON fixture was found to screen.")
    if "mcp-wrapped.json" in composed.drafts:
        total = len(composed.wrapped) + len(composed.unwrapped)
        add(
            f"- Your MCP configuration (`{_cell(result.mcp_config[0])}`) was rewritten as a **suggestion** with "
            f"`egresswall proxy` in front of {len(composed.wrapped)} of {total} server(s)."
            + (
                f" The {len(composed.unwrapped)} server(s) that name no command line — "
                + ", ".join(f"`{_cell(item)}`" for item in composed.unwrapped[:4])
                + " — are reached over the network and a proxy in front of a command cannot screen them, so they "
                "were copied through unchanged."
                if composed.unwrapped
                else ""
            )
            + " It was not applied; see §4."
        )
    add("")
    add("### What a generic scorer will get wrong here")
    add("")
    add(
        "**guardrail-checkup did not run any of these tools.** It contacts no network and starts no `npx`. This is "
        "the falsifier list to have ready when you do run them, built from this repository's own files:"
    )
    add("")
    falsifiers = _falsifiers(result)
    if falsifiers:
        add("| A generic readiness scorer will say | True here | Command that shows it |")
        add("| --- | --- | --- |")
        for claim, truth, command_ in falsifiers:
            add(f"| {_cell(claim)} | {_cell(truth)} | `{_cell(command_)}` |")
    else:
        add(
            "- Nothing here falsifies a generic scorer's usual claims: this repository has no "
            "lockfile, no linter configuration and no test path."
        )
    add("")

    # 3
    add(f"## {SECTIONS[2]}")
    add("")
    shown = result.candidates[:3]
    bare = [item for item in shown if item.score <= HEURISTIC_BASE]
    add(
        "**Candidates — a human confirms or replaces them.** They are ranked by evidence, not by judgement: "
        f"score = repair commits in the history that touched these paths (a commit that also touched a regression "
        f"test counts {'twice' if REGRESSION_WEIGHT == 2 else f'{REGRESSION_WEIGHT} times'}) "
        f"+ {CODEOWNERS_BONUS} if CODEOWNERS names one of them + {HEURISTIC_BASE} if the path heuristic matched at "
        "all. This tool does not know your architecture and does not claim to."
    )
    add("")
    if not shown:
        add(
            "No path here matched any of the categories this tool knows, so there is no candidate to rank. "
            "Two candidates with evidence beat three with one invented; here there are none."
        )
    else:
        if len(result.candidates) < 3:
            add(
                f"Only {len(result.candidates)} of the categories this tool knows matched any path here, so there "
                "are that many candidates and not three. The runbook's rule applies: do not invent a third."
            )
            add("")
        if bare:
            add(
                f"{'All ' if len(bare) == len(shown) else ''}{len(bare)} of these "
                f"{'is' if len(bare) == 1 else 'are'} a bare path match at score {HEURISTIC_BASE}: the path "
                "heuristic matched and nothing else did — no repair commit and no CODEOWNERS entry points at "
                "them. Equal scores are ordered by the number of matching files, then by name; that ordering is "
                "not evidence."
            )
            add("")
    for number, candidate in enumerate(shown, start=1):
        add(f"### Invariant candidate {number} — {candidate.rule}")
        add("")
        governs = "`" + "`, `".join(candidate.prefixes) + "`"
        if set(candidate.prefixes) != set(candidate.paths):
            governs += " — for example `" + "`, `".join(candidate.paths[:4]) + "`"
        add(f"- **Governs:** {governs}")
        add(f"- **Evidence (score {candidate.score}):**")
        for item in candidate.evidence:
            add(f"  - {item}")
        add(
            "- **An agent breaks it by:** reading two files nearby, inferring the pattern, and writing the change "
            "here rather than asking — which is the correct move everywhere else in this repository."
        )
        add("- **Hook** — `.claude/settings.json`:")
        add("")
        add("```json")
        add(json.dumps(settings_snippet(candidate.slug), indent=2))
        add("```")
        add("")
        add(f"  and `.claude/hooks/protect-{candidate.slug}.py` (emitted; exit 2 blocks the call):")
        add("")
        add("```python")
        add(composed.drafts.get(f"hooks/protect-{candidate.slug}.py", "").rstrip("\n"))
        add("```")
        add("")
        add(f"- **Test** (exits non-zero when a staged commit violates it): `{one_line_test(candidate.prefixes)}`")
        add("")

    # 4
    add(f"## {SECTIONS[3]}")
    add("")
    monday = _monday(result, composed, emit_dir)
    if monday:
        for number, item in enumerate(monday, start=1):
            add(f"{number}. {item}")
    else:
        add("Nothing. Every artifact this tool looks for is already in place.")
    add("")

    # 5
    add(f"## {SECTIONS[4]}")
    add("")
    add(
        "- **Branch protection and required reviews.** They live on the host, not in the checkout; "
        "this tool never asked one."
    )
    add("- **Production systems.** No credential, no VPN, no CI, no deploy, no live database was touched.")
    add(
        "- **Secrets already in history.** This reads the working tree, not every blob. Run "
        "`gitleaks detect`, `trufflehog git`, or `detect-secrets scan` for that."
    )
    add(
        "- **Runtime behaviour.** Nothing here was executed. A hook that has never run does not go "
        "on anyone's screen — run the emitted one before you trust it."
    )
    add(
        "- **Anything needing a model.** No model was called. §3 is a ranked list of places, not a "
        "reading of your architecture"
        + (
            f", and the one judgement that matters — is candidate {len(shown)} the right one — is not in this file."
            if shown
            else ", and it named none here."
        )
    )
    add(
        "- **Whether the rules that exist are followed.** Presence is checked; compliance is not. A hook is "
        "reported by its matcher, not by what it does: nothing here was executed, so a `PreToolUse` entry that "
        "only writes a log line reads exactly like one that blocks."
    )
    add("")

    # 6
    add(f"## {SECTIONS[5]}")
    add("")
    add(f"- **Tool:** `guardrail-checkup` {versions['guardrail-checkup']}")
    add(f"- **Command:** `{command}`")
    add(
        f"- **Repository commit:** `{result.head}`"
        if result.head
        else f"- **Repository commit:** none ({_no_head(result)})"
    )
    add(
        f"- **Repair commits examined:** {result.repairs}, from the last {HISTORY_COMMITS} non-merge commits"
        + (
            f". The history was sampled: the walk stopped after {HISTORY_PATHS:,} path entries, so commits older "
            "than that were not read."
            if result.history_sampled
            else ""
        )
    )
    add(
        "- **What left this machine: nothing.** This tool opens no socket and makes no model call. The git "
        "subcommands it runs are `ls-files`, `rev-parse` and `log`, all read-only. It wrote no file inside the "
        "repository it read."
    )
    add(
        f"- **Built on:** `agent-plan-lint` {versions['agent-plan-lint']} (policy and plan "
        f"validation), `egresswall` {versions['egresswall']} (fixture screening, MCP proxy suggestion)."
    )
    add(
        "- **Lineage:** the plan gate comes from Graphene's admission validator and the screen from RegLineage's "
        "egress firewall, both the author's own prior work, extracted and re-tested as packages."
    )
    add(
        "- **AI assistance:** this tool was written with AI assistance. **This report was not** — it is deterministic "
        "output from the files listed in §1, and re-running the command above on the same commit produces it again "
        "byte for byte."
    )
    add(
        "- **No guarantee** is made about anything not listed in §1. The third-party tools named in "
        "§2 are unaffiliated with this one."
    )
    add("")
    return "\n".join(lines)


def _cell(text: str) -> str:
    """One table cell. Nothing in it may end the row, the table or the section.

    The strings in a cell come from the repository under inspection, so a
    newline here would let a checkout close the table and write its own
    headings underneath. `visible` turns every control character into a visible
    escape; the `|` is this renderer's own delimiter.
    """

    return visible(text).replace("|", "\\|")


def render_json(
    result: Scan, composed: Composition, command: str, versions: dict[str, str], emit_dir: str | None, date: str
) -> str:
    document = {
        "schema": "guardrail-checkup/1",
        "date": date,
        "scope": {
            "given_path": result.given_path,
            "head": result.head,
            "is_git": result.is_git,
            "files": len(result.files),
            "total_files": result.total_files,
            "truncated": result.truncated,
            "total_bytes": result.total_bytes,
            "languages": [{"extension": item, "files": count} for item, count in result.languages],
            "read": result.read,
            "unread": result.unread,
        },
        "inventory": [dataclasses.asdict(item) for item in result.findings],
        "composition": composed.to_dict(),
        "falsifiers": [
            {"claim": claim, "truth": truth, "command": command_} for claim, truth, command_ in _falsifiers(result)
        ],
        "candidates": [dataclasses.asdict(item) for item in result.candidates[:3]],
        "monday": _monday(result, composed, emit_dir),
        "not_covered": [
            "branch protection and required reviews",
            "production systems",
            "secrets already in git history",
            "runtime behaviour",
            "anything needing a model",
            "whether existing rules are followed",
        ],
        "provenance": {
            "command": command,
            "versions": versions,
            "left_the_machine": "nothing",
            "git_subcommands": list(READ_ONLY_GIT),
            "repair_commits": result.repairs,
            "ai_assistance": (
                "the tool was written with AI assistance; this report is deterministic output, not model output"
            ),
        },
    }
    return json.dumps(document, indent=2, sort_keys=False) + "\n"
