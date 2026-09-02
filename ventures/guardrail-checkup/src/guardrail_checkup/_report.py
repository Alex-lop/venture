"""The six-section report. Same sections, same order as the in-person autopsy."""

from __future__ import annotations

import dataclasses
import json
import re
import shlex
from datetime import UTC, datetime

from ._compose import (
    CANDIDATE_LIMIT,
    EXCLUSION_GLOBS,
    SIGNATURE_SCAN_BYTES,
    SIGNATURE_SCAN_FILES,
    Composition,
    one_line_test,
    settings_snippet,
)
from ._scan import (
    CODEOWNERS_BONUS,
    HEURISTIC_BASE,
    HISTORY_COMMITS,
    HISTORY_PATHS,
    LOCKFILES,
    MAX_READ_BYTES,
    QUOTED_WIDTH,
    READ_ONLY_GIT,
    REGRESSION_WEIGHT,
    SETTINGS_FILES,
    SKIP_DIRECTORIES,
    SNIFF_BYTES,
    TEST_PATH,
    Scan,
    _bar,
    _code,
    _read,
    _record,
    md,
)

__all__ = ["MONDAY_LIMIT", "SECTIONS", "render_json", "render_markdown", "run_date"]

#: How many actions the Monday list carries, at most.
MONDAY_LIMIT = 5

#: The manifests the falsifier list opens looking for a linter, on top of the
#: linter's own configuration files. §1 names them, because it reads them.
LINTER_MANIFESTS = ("pyproject.toml", "setup.cfg", "package.json")

#: How many servers §2's egresswall paragraph names as examples. It was the one
#: cut in the report that did not announce itself: four of five thousand servers
#: were listed, the sentence ended in a full stop, and it read as the whole set.
EXAMPLES = 4

#: The three tools §5 says this one does not replace, each with one fact from
#: the file under `docs/evidence/` that carries it -- `/doctor` and
#: `cc-safety-net` from their own words, `agentrc` from its own description,
#: which is all any source checked in for it says. `docs/comparison.md` claims
#: this package is "honest about the other three in the report it writes"; it
#: was honest about them on that page and the report named none of them, so the
#: sentence was false until this list existed. tests/test_scan.py greps a
#: rendered report for every phrase here, and tests/test_comparison_truth.py
#: holds each one against its evidence file.
NOT_REPLACED = (
    ("Claude Code's `/doctor`", "prints read-only installation diagnostics without starting a session"),
    (
        "`kenryu42/cc-safety-net`",
        "blocks destructive Git and file system commands, plus common attempts to access sensitive files, "
        "before a tool call runs",
    ),
    ("`microsoft/agentrc`", "Get your repo ready for AI."),
)


def _and_more(total: int) -> str:
    """The clause a cut list needs. Every other cap in this report announces itself."""

    return f" and {total - EXAMPLES:,} more" if total > EXAMPLES else ""


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
    for relative in result.all_files or result.files:
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
    for relative in LINTER_MANIFESTS:
        if relative in (result.all_files or result.files):
            text = _record(result, relative, _read(result.root, relative)) or ""
            hit = re.search(r"(?i)\b(ruff|flake8|black|eslint|biome|prettier|pylint)\b", text)
            if hit:
                number = next(
                    (n for n, line in enumerate(text.splitlines(), 1) if hit.group(0).lower() in line.lower()), 1
                )
                return f"{relative}:{number}"
    return None


def _capped(result: Scan) -> str:
    """The clause a conclusion drawn off the `--max-files` slice has to carry.

    The ranking reads the capped listing, so "No path here matched any of the
    categories this tool knows" is a statement about the first N paths and not
    about the repository. The inventory's name-based lookups and the signature
    scan read the whole listing; symlink inspection and §3 stay inside the cap.
    """

    if not result.truncated:
        return ""
    return (
        f" Listing capped at {result.max_files:,}; {result.total_files - result.max_files:,} file(s) were not "
        "scanned for a candidate path, so this ranking reads the first "
        f"{result.max_files:,} paths in sorted order and no other."
    )


def _falsifiers(result: Scan) -> list[tuple[str, str, str]]:
    """Claim a generic scorer makes → what is true here → the command that shows it.

    Every path in a command here is `shlex.quote`d. The reader is invited to
    paste these lines into a shell, and a filename is repository-controlled
    text: `a;id>PWNED;x/uv.lock` is a legal directory name.
    """

    listing = result.all_files or result.files
    out = []
    locks = [item for item in listing if item.rsplit("/", 1)[-1] in LOCKFILES]
    if locks:
        out.append(
            ("“Missing package manager lockfile”", f"{_code(locks[0])} is committed", f"wc -l {shlex.quote(locks[0])}")
        )
    linter = _linter(result)
    if linter:
        out.append(
            (
                "“Missing linter configuration”",
                f"a linter is configured at {_code(linter)}",
                "grep -n -iE 'ruff|eslint|biome|flake8|prettier' " + shlex.quote(linter.split(":")[0]),
            )
        )
    # The same TEST_PATH the inventory counts with: two copies of this
    # expression let one report state two different numbers of test files.
    tests = [item for item in listing if TEST_PATH.search(item)]
    if tests:
        out.append(("“Testing: 0/0 (0%)”", f"{len(tests)} file(s) sit in a test path", _test_command(result)))
    return out


def _test_command(result: Scan) -> str:
    """The command that prints the figure printed beside it, over the listing §1 names.

    The shipped one was `find . -path ./.git -prune -o -name 'test_*' -print | wc -l`.
    It pruned the literal `./.git` and nothing else, so it walked `.venv/` and
    `__pycache__/`, and it counted files *named* `test_*` where the cell beside
    it counts files *in a test path*: on the checkout the pinned transcript
    records it printed 65 against a cell that said 13, and on a repository whose
    `.venv` holds vendored suites, 605 against 148. A command a report sells as the
    one that disproves a claim may not print a different number from the claim,
    so both halves come from one place now -- the file list §1 states, and
    `TEST_PATH` itself, written out for `grep -E`.
    """

    pattern = shlex.quote(TEST_PATH.pattern)
    if result.is_git:
        return f"git ls-files --cached --others --exclude-standard | grep -cE {pattern}"
    # Not a checkout: the listing is `os.walk` minus SKIP_DIRECTORIES, so the
    # find has to prune the same names or it counts a vendored suite too.
    prune = " -o ".join(f"-name {shlex.quote(item)}" for item in SKIP_DIRECTORIES)
    return f"find . \\( {prune} \\) -prune -o -type f -print | grep -cE {pattern}"


def _monday(result: Scan, composed: Composition, emit_dir: str | None) -> list[str]:
    """At most MONDAY_LIMIT actions, each naming an emitted artifact or a file to edit."""

    # With no `--emit-dir` there is no directory to name, so the sentence changes
    # rather than the noun: the fallback used to be concatenated into a path
    # inside a code span, producing text that could not be copied.
    where = emit_dir or "DIR"
    unwritten = "" if emit_dir else " Re-run with `--emit-dir DIR` to write it; this run wrote no draft."
    items: list[str] = []
    if result.candidates:
        first = result.candidates[0]
        items.append(
            f"Read invariant candidate 1 ({first.slug}) in §3 and decide whether it is right. If it is, copy "
            f"{_code(f'{where}/hooks/protect-{first.slug}.py')} into `.claude/hooks/`, `chmod +x` it, and merge "
            f"{_code(f'{where}/hooks/settings-{first.slug}.json')} into `.claude/settings.json`." + unwritten
        )
    settings_absent = [item for item in result.findings if item.fact.endswith(": absent") and "settings" in item.fact]
    # The sentence about PostToolUse asserts that a PostToolUse hook exists, so
    # it may only be written when the inventory found one.
    post = any("PostToolUse entr" in item.fact for item in result.findings)
    pre = any("no PreToolUse hook" in item.fact for item in result.findings)
    if len(settings_absent) == len(SETTINGS_FILES):
        items.append(
            "Create `.claude/settings.json` with the hooks block from §3. Neither settings file exists in this "
            "repository today, so every candidate in §3 has nowhere to live."
        )
    elif pre and post:
        items.append(
            "Add the §3 `PreToolUse` block to `.claude/settings.json`; the only hook this repository checks in "
            "is a `PostToolUse` one, and it runs after the write."
        )
    elif pre:
        items.append(
            "Add the §3 `PreToolUse` block to `.claude/settings.json`; the settings file in this repository "
            "wires no hook of either kind."
        )
    if "mcp-wrapped.json" in composed.drafts:
        items.append(
            f"Compare {_code(f'{where}/mcp-wrapped.json')} with your own MCP configuration. It is the same "
            f"servers with `egresswall proxy` in front of the {len(composed.wrapped)} it could wrap"
            + (f"; {len(composed.unwrapped)} it could not are unchanged" if composed.unwrapped else "")
            + (f"; {len(composed.already)} already run a screen" if composed.already else "")
            + f"; nothing was applied. Its `--policy` names `{composed.policy_path}`, a placeholder — point it at "
            "an egresswall policy you write, because this tool writes none." + unwritten
        )
    if "starter-policy.json" in composed.drafts:
        items.append(
            f"Review {_code(f'{where}/starter-policy.json')} — a valid agent-plan-lint policy whose exclusions "
            "are the §3 candidates. Fix the write globs to the paths your agents really own, then run "
            "`agent-plan-lint check <plan.json> --policy starter-policy.json`." + unwritten
        )
    if any(item.fact.startswith("secret scanning: not configured") for item in result.findings):
        items.append(
            "Add gitleaks or detect-secrets to CI or to `.pre-commit-config.yaml`. §5 explains why "
            "this tool cannot do it for you."
        )
    # The file, not "your agent instruction file": every other item on this list
    # names a path, and the row that produced this branch already knows one.
    prose = next(
        (item for item in result.findings if "no line both forbids something and names a path" in item.fact), None
    )
    if prose is not None:
        items.append(
            f"Add one line to {_code(prose.where.rsplit(':', 1)[0])} naming the paths in §3 — prose is not a "
            "guardrail, but a contributor reads it."
        )
    return items[:MONDAY_LIMIT]


def render_markdown(
    result: Scan, composed: Composition, command: str, versions: dict[str, str], emit_dir: str | None, date: str
) -> str:
    lines: list[str] = []
    add = lines.append

    add(f"# Agent guardrail checkup — {md(result.root.name)}")
    add("")
    # A code span, like §1 and §6: the path is copyable in all three, and a
    # directory name carrying a newline or a backtick -- what a hostile archive
    # creates on extraction -- can neither open a heading nor close the span.
    add(f"Run {date} · read-only · {_code(result.given_path)} · " + _head_line(result))
    add(
        "Produced by `guardrail-checkup`, a deterministic offline reader. No model was called for anything below; "
        "every judgement in §3 is yours to make."
    )
    add("")

    # 1
    add(f"## {SECTIONS[0]}")
    add("")
    add(f"- **Repository:** {_code(result.given_path)}, as given on the command line")
    add(f"- **HEAD:** `{result.head}`" if result.head else f"- **HEAD:** none — {_no_head(result)}")
    # Apparent size, not blocks: a 10 GiB sparse file occupies nothing and
    # `st_size` still reports 10 GiB, so "on disk" would be the wrong words.
    add(f"- **Size:** {len(result.files):,} file(s) considered, {result.total_bytes:,} bytes (apparent size)")
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
    add(
        f"- **Language mix** (by file extension), the {len(result.languages)} most common of {result.extensions}:"
        if result.extensions > len(result.languages)
        else "- **Language mix** (by file extension):"
    )
    for extension, count in result.languages:
        add(f"  - {_code(extension)} — {count}")
    add(
        "- **Read:** the named guardrail artifacts listed in §2, `" + "`, `".join(LINTER_MANIFESTS) + "` (for the "
        "linter falsifier), every checked-in `.json` file the signature scan reached before its "
        f"{SIGNATURE_SCAN_BYTES // 2**20} MiB and {SIGNATURE_SCAN_FILES:,} file budgets were spent, and up "
        f"to {len(composed.screened)} JSON fixture(s) screened in §2. "
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
        # The fact and the consequence carry repository text that `_scan`
        # escaped where it was interpolated; escaping them again is the defect
        # `md`'s docstring names.
        add(f"| {finding.fact} | {_bar(_code(finding.where))} | {finding.consequence} |")
    add("")
    add("### agent-plan-lint")
    add("")
    if composed.policies or composed.plans:
        for path, status in composed.policies + composed.plans:
            # `status` carries a sibling's own message for a document it
            # refused, and that message quotes the document.
            add(f"- {_code(path)} — {md(status, QUOTED_WIDTH)}")
        for line in composed.validations:
            # A code span, not `md`: the line opens with a filename out of the
            # checkout and closes with the plan's own write path, and both read
            # as themselves inside one. This was the last repository-controlled
            # string in the report that passed neither door.
            add(f"  - {_code(line)}")
    else:
        # Not a flat "none was found" when the scan stopped early: the row is
        # the one the `.cursor/rules` fan-out gets, saying how many were listed
        # and not read, because an absence over unread files is not one.
        add(
            f"- No document in agent-plan-lint's schema was found in the `.json` files that were read, and "
            f"{composed.signature_skipped:,} more were listed and not read: the signature scan stops after "
            f"{SIGNATURE_SCAN_BYTES // 2**20} MiB of JSON."
            if composed.signature_skipped
            else "- No document in agent-plan-lint's schema was found (no `.json` file carries both "
            "`policy_id` and `allowed_write_globs`, or both `mission_id` and `tasks`)."
        )
        if "starter-policy.json" in composed.drafts:
            add("- A starter policy was drafted instead; see §4. It was **not** written into your repository.")
            if composed.exclusions_cut:
                add(
                    f"- Its exclusions are drawn from the first {EXCLUSION_GLOBS} candidate path globs in sorted order "
                    f"({composed.exclusions_cut:,} more were cut). Review that cut before using the policy."
                )
            # The one cap in this package that decides what an emitted file
            # *grants* rather than what a row says. A repository whose repair
            # commits touched a hundred directories was handed a policy denying
            # writes in thirty-six of them, and nothing anywhere said so.
            if result.churn_cut:
                add(
                    f"- Its write globs come from the {len(result.churn)} most-churned directories "
                    f"({result.churn_cut:,} more were cut). A directory that is not a write glob is one the "
                    "policy denies writes in, so add the ones your agents own before you use it."
                )
    if composed.unpoliceable:
        add(
            f"- {len(composed.unpoliceable)} path(s) were left out of that policy: agent-plan-lint's own path type "
            "refuses each of them as a glob — " + ", ".join(_code(item) for item in composed.unpoliceable[:4])
        )
    add("")
    add("### egresswall")
    add("")
    if composed.screened:
        for path, violations in composed.screened:
            if violations:
                add(f"- {_code(path)} — **{len(violations)} violation(s)** under egresswall's default policy:")
                for item in violations[:6]:
                    # egresswall names a code and a path out of the fixture, and
                    # the fixture is a file the inspected repository wrote.
                    add(f"  - {_code(item)}")
            else:
                add(f"- {_code(path)} — clean under egresswall's default policy")
        add("")
        add(
            "A violation names a code and a path, never a value. These are checked-in fixtures; the same screen in "
            "front of a live MCP server is what stops the real answer."
        )
    else:
        add("- No checked-in JSON fixture was found to screen.")
    if "mcp-wrapped.json" in composed.drafts:
        total = len(composed.wrapped) + len(composed.unwrapped) + len(composed.already)
        add(
            f"- Your MCP configuration ({_code(result.mcp_config[0])}) was rewritten as a **suggestion** with "
            f"`egresswall proxy` in front of {len(composed.wrapped)} of {total} server(s)."
            + (
                f" {len(composed.already)} of them already run one of the known screens and were left alone — "
                + ", ".join(_code(item) for item in composed.already[:EXAMPLES])
                + _and_more(len(composed.already))
                + "."
                if composed.already
                else ""
            )
            + (
                f" {len(composed.unwrapped)} were copied through unchanged: "
                + "; ".join(f"{_code(name)} — {reason}" for name, reason in composed.unwrapped[:EXAMPLES])
                + _and_more(len(composed.unwrapped))
                + "."
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
            add(f"| {claim} | {_bar(truth)} | {_bar(_code(command_))} |")
    else:
        add(
            "- Nothing here falsifies a generic scorer's usual claims: this repository has no "
            "lockfile, no linter configuration and no test path."
        )
    add("")

    # 3
    add(f"## {SECTIONS[2]}")
    add("")
    shown = result.candidates[:CANDIDATE_LIMIT]
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
            "Two candidates with evidence beat three with one invented; here there are none." + _capped(result)
        )
        # The blank line every other section boundary in this file has: without
        # it the paragraph runs straight into `## 4.` on the next line.
        add("")
    else:
        if result.truncated:
            add(_capped(result).strip())
            add("")
        if len(result.candidates) < 3:
            add(
                f"Only {len(result.candidates)} of the categories this tool knows matched a path here, so it "
                f"names {len(result.candidates)} candidate(s) and not three. The runbook's rule applies: do not "
                "invent a third."
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
        # A bullet, not a table cell: `_bar`'s `|` escape belongs to a row, and
        # putting it in a shell line the reader copies would break the pipe.
        governs = ", ".join(_code(item) for item in candidate.prefixes)
        if set(candidate.prefixes) != set(candidate.paths):
            governs += " — for example " + ", ".join(_code(item) for item in candidate.paths[:4])
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
        # The script carries repository-controlled path text, so the fence has
        # to be longer than any backtick run inside it.
        script = composed.drafts.get(f"hooks/protect-{candidate.slug}.py", "").rstrip("\n")
        fence = "`" * max(3, max((len(run) for run in re.findall(r"`+", script)), default=0) + 1)
        add(f"{fence}python")
        add(script)
        add(fence)
        add("")
        add("- **Test** (exits non-zero when a staged commit violates it): " + _code(one_line_test(candidate.prefixes)))
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
    # No candidate number here: this section may not single one out. `len(shown)`
    # was used as an index and so always named the last, lowest-ranked one.
    add(
        "- **Anything needing a model.** No model was called. §3 is a ranked list of places, not a "
        "reading of your architecture"
        + (
            ", and the judgement — whether these are the right places — is not in this file."
            if shown
            else ", and it named none here."
        )
    )
    add(
        "- **Hooks configured outside this checkout.** The inventory reads `.claude/settings.json` and "
        "`.claude/settings.local.json`. A hook in `~/.claude/settings.json`, in an enterprise policy, or in "
        "an installed plugin is on the machine and not in this repository, and was not read."
    )
    add(
        "- **Whether the rules that exist are followed.** Presence is checked; compliance is not. A hook is "
        "reported by its matcher, not by what it does: nothing here was executed, so a `PreToolUse` entry that "
        "only writes a log line reads exactly like one that blocks."
    )
    # The three tools this one does not replace, named in the report rather than
    # only on the comparison page: the page claims the report is honest about
    # them, and a claim about this file has to be true in this file.
    add(
        "- **What the three tools next to this one do.** None of them ran here, and this replaces none of "
        f"them. {NOT_REPLACED[0][0]} “{NOT_REPLACED[0][1]}”. {NOT_REPLACED[1][0]} “{NOT_REPLACED[1][1]}”. "
        f"{NOT_REPLACED[2][0]} says only “{NOT_REPLACED[2][1]}” — its own description, and this report "
        "characterises it no further. The first two are better at those jobs than anything here; install "
        "them. This one reports, and the report is what you read before deciding what to enforce."
    )
    add("")

    # 6
    add(f"## {SECTIONS[5]}")
    add("")
    add(f"- **Tool:** `guardrail-checkup` {versions['guardrail-checkup']}")
    # A code span, and through `_code`: the command line carries the path as it
    # was typed, and a directory name holding a newline would otherwise close
    # the span and write its own heading underneath.
    add(f"- **Command:** {_code(command)}")
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
        "§2 and §5 are unaffiliated with this one."
    )
    add("")
    return "\n".join(lines)


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
        "candidates": [dataclasses.asdict(item) for item in result.candidates[:CANDIDATE_LIMIT]],
        "monday": _monday(result, composed, emit_dir),
        "not_covered": [
            "branch protection and required reviews",
            "production systems",
            "secrets already in git history",
            "runtime behaviour",
            "hooks configured outside this checkout",
            "anything needing a model",
            "whether existing rules are followed",
            "what the three tools named in §5 do",
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
