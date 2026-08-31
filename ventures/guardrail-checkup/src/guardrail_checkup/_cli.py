"""The command line. Exit 0 when the report was written; 2 on usage or IO errors."""

from __future__ import annotations

import argparse
import contextlib
import os
import shlex
import sys
from importlib import metadata
from pathlib import Path

from . import NAME, __version__
from ._compose import CANDIDATE_LIMIT, compose, emit
from ._report import render_json, render_markdown, run_date
from ._scan import scan

__all__ = ["build_parser", "main"]

#: The default listing cap. A repository larger than this is reported with the
#: cap named rather than read to the end.
DEFAULT_MAX_FILES = 20_000

#: What the emitted MCP suggestion names as egresswall's policy file. A
#: placeholder for the reader to replace: this tool writes no egresswall policy.
POLICY_PLACEHOLDER = "/etc/egresswall/policy.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=NAME,
        description=(
            "Read one repository and write the six-section agent-guardrail report: what is enforced, what a "
            "generic scorer will get wrong here, and up to three invariant candidates worth a hook. Offline, "
            "deterministic, read-only, no model call."
        ),
    )
    parser.add_argument("--version", action="version", version=f"{NAME} {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="check one repository and write a report")
    run.add_argument("path", metavar="PATH", help="the repository to read; never modified")
    run.add_argument(
        "--out", required=True, metavar="REPORT.md", help="where to write the report; must be outside PATH"
    )
    run.add_argument(
        "--emit-dir",
        metavar="DIR",
        help="where to write the drafted policy, hooks and MCP suggestion; must be outside PATH",
    )
    run.add_argument("--format", choices=("md", "json"), default="md", help="report format (default: md)")
    run.add_argument(
        "--max-files",
        type=int,
        default=DEFAULT_MAX_FILES,
        metavar="N",
        help=f"listing cap (default: {DEFAULT_MAX_FILES})",
    )
    return parser


def _refuse(target: Path, repository: Path, label: str) -> str | None:
    """Why this tool will not write to `target`, or None when it will.

    Two reasons. The path *resolves* inside the repository under inspection; or
    it is a second name for a file that already exists, which the first test
    cannot see -- a hard link resolves to itself, so `drafts/report.md` hard-
    linked to `repo/keep.md` is outside the repository by every path comparison
    and is the same bytes on disk.

    `os.path.realpath`, the same call the scan uses, is what makes the first
    test see a symlink: `--emit-dir drafts` with `drafts/starter-policy.json` a
    symlink to `<repo>/CLAUDE.md` is outside the repository by every lexical
    comparison, and `write_text` follows the link and edits the checkout. It is
    `realpath` rather than `Path.resolve` because two links pointing at each
    other make `resolve` raise instead of answering.
    """

    real = Path(os.path.realpath(target))
    if real == repository or repository in real.parents:
        return f"{NAME}: {label} {target} is inside {repository}; this tool never writes to the repository it reads"
    if target.is_file() and target.stat().st_nlink > 1:
        return f"{NAME}: {label} {target} is a hard link to another file; this tool never overwrites one"
    return None


def _versions() -> dict[str, str]:
    out = {NAME: __version__}
    for name in ("agent-plan-lint", "egresswall"):
        try:
            out[name] = metadata.version(name)
        except metadata.PackageNotFoundError:  # pragma: no cover - source tree without install
            out[name] = "0+unknown"
    return out


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    given = arguments.path
    repository = Path(given).resolve()
    if not repository.is_dir():
        print(f"{NAME}: {given} is not a directory", file=sys.stderr)
        return 2

    out = Path(arguments.out).resolve()
    emit_dir = Path(arguments.emit_dir).resolve() if arguments.emit_dir else None
    checked = [(out, "--out"), *([(emit_dir, "--emit-dir")] if emit_dir is not None else [])]
    for target, label in checked:
        problem = _refuse(target, repository, label)
        if problem is not None:
            print(problem, file=sys.stderr)
            return 2

    if arguments.max_files < 1:
        print(f"{NAME}: --max-files must be at least 1", file=sys.stderr)
        return 2

    try:
        result = scan(given, arguments.max_files)
        composed = compose(result, POLICY_PLACEHOLDER)
        if emit_dir is not None:
            emit_dir.mkdir(parents=True, exist_ok=True)
            for name in sorted(composed.drafts):
                problem = _refuse(emit_dir / name, repository, "--emit-dir target")
                if problem is not None:
                    print(problem, file=sys.stderr)
                    return 2
            emit(composed.drafts, emit_dir)
        command = " ".join([NAME, *(shlex.quote(item) for item in (argv if argv is not None else sys.argv[1:]))])
        render = render_json if arguments.format == "json" else render_markdown
        body = render(
            result, composed, command, _versions(), arguments.emit_dir, run_date(os.environ.get("SOURCE_DATE_EPOCH"))
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
    except ImportError as error:
        # A partial environment: one of the two siblings is not installed. One
        # line, and exit 2 like every other error -- never the 1 this tool
        # promises not to return.
        print(f"{NAME}: {error}", file=sys.stderr)
        return 2
    except Exception as error:
        # The belt behind every guard in _scan: a repository is untrusted input,
        # and no shape it can take may produce a traceback or exit 1. This tool
        # reports; a reader who gets exit 1 from it would think it gated.
        print(f"{NAME}: {type(error).__name__}: {error}", file=sys.stderr)
        return 2

    drafted = f", {len(composed.drafts)} draft(s) in {arguments.emit_dir}" if emit_dir is not None else ""
    summary = (
        f"{NAME}: wrote {arguments.out} — {len(result.findings)} inventory finding(s), "
        f"{len(result.candidates[:CANDIDATE_LIMIT])} invariant candidate(s){drafted}"
    )
    # The report is on disk by here, so the promise is already kept and nothing
    # this line does may take it back. Unflushed, the write landed in CPython's
    # shutdown flush instead -- after `main` returned, past every guard above --
    # so `guardrail-checkup run . --out R.md | head` printed a BrokenPipeError
    # traceback and exited 120 on a run that had succeeded. Flushing here puts
    # that failure inside the contract; the devnull descriptor then keeps the
    # interpreter's own flush at exit quiet.
    try:
        print(summary)
        sys.stdout.flush()
    except Exception:
        # A reader that closed the pipe (`| head`), or a caller that ran this
        # with no stdout at all (`1>&-`, where `sys.stdout` is None), has not
        # failed a run whose report is on disk -- and a line about it on stderr
        # would be noise in exactly the pipelines that cause it. The devnull
        # descriptor keeps the interpreter's own flush at exit quiet too.
        with contextlib.suppress(Exception):
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    return 0
