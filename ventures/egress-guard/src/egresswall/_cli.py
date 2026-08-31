"""The egresswall command line: check, hook, proxy."""

from __future__ import annotations

import argparse
import json
import sys
from typing import IO, Any

from . import NAME, __version__
from ._core import (
    MAX_REPORT_CHARS,
    MAX_REPORTED,
    MAX_VIOLATION_CHARS,
    PAYLOAD_TOO_DEEP,
    Policy,
    Violation,
    _safe_label,
    _trimmed,
    check,
    loads,
)
from ._proxy import run_proxy

#: The report bounds live in _core because the proxy applies them too: its
#: JSON-RPC error and its drop log carry a path the server chose, exactly like
#: this report does. Re-exported here because that is where they are documented.
__all__ = ["MAX_REPORTED", "MAX_REPORT_CHARS", "MAX_VIOLATION_CHARS", "build_parser", "main"]


def _listed(violations: list[Violation]) -> tuple[list[Violation], int]:
    """The violations a report may list, trimmed, and how many it left out."""
    listed = [_trimmed(item) for item in violations[:MAX_REPORTED]]
    return listed, len(violations) - len(listed)


def _load_policy(path: str | None) -> Policy:
    return Policy.from_file(path) if path else Policy()


def _report(source: str, violations: list[Violation], fmt: str, out: IO[str]) -> int:
    listed, hidden = _listed(violations)
    if fmt == "json":
        payload = {
            "source": source,
            "blocked": bool(violations),
            "violations": [item.to_dict() for item in listed],
            "truncated": hidden,
        }
        out.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return 1 if violations else 0
    if not violations:
        out.write(f"CLEAN: {source}\n")
        return 0
    out.write(f"BLOCKED: {source}\n")
    for item in listed:
        out.write(f"  {item}\n")
    if hidden:
        out.write(f"  (+{hidden} more)\n")
    plural = "" if len(violations) == 1 else "s"
    out.write(f"{len(violations)} violation{plural}\n")
    return 1


def _cmd_check(args: argparse.Namespace, out: IO[str], err: IO[str]) -> int:
    try:
        payload: Any = loads(sys.stdin.read() if args.file == "-" else _read(args.file))
    except RecursionError:
        err.write(f"{NAME}: cannot read {args.file}: payload nests too deep to parse\n")
        return 2
    except (OSError, ValueError, OverflowError) as exc:
        err.write(f"{NAME}: cannot read {args.file}: {exc}\n")
        return 2
    return _report(args.file, check(payload, _load_policy(args.policy)), args.format, out)


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _cmd_hook(args: argparse.Namespace, out: IO[str], err: IO[str]) -> int:
    """PostToolUse hook: exit 2 and report on stderr when tool_response violates."""
    # Input the hook could not parse is input it could not screen, so both
    # branches refuse: exit 2 is the code Claude Code shows to the model, and
    # exit 1 would be a silent non-blocking error.
    try:
        event = loads(sys.stdin.read())
    except RecursionError:
        err.write(f"{NAME}: {PAYLOAD_TOO_DEEP} at tool_response: ")
        err.write("the hook input nests too deep to parse and was not screened.\n")
        err.write("Do not repeat this call and do not restate the value.\n")
        return 2
    except (ValueError, OverflowError) as exc:
        # Not "is not JSON": a number past this interpreter's digit limit is
        # valid JSON that CPython will not convert, and the operator chasing it
        # should be looking at the interpreter, not at the server.
        err.write(f"{NAME}: the hook input could not be parsed and was not screened ({exc}).\n")
        err.write("Do not repeat this call and do not restate the value.\n")
        return 2
    if not isinstance(event, dict):
        # A PostToolUse event is an object. Anything else is a shape this hook
        # does not know how to find a tool response in, so it is input that was
        # not screened -- the same refusal as input that would not parse. Only a
        # real event with no `tool_response` (a PreToolUse one) passes.
        err.write(f"{NAME}: the hook input is not a JSON object and was not screened.\n")
        err.write("Do not repeat this call and do not restate the value.\n")
        return 2
    if "tool_response" not in event:
        return 0
    policy = _load_policy(args.policy)
    violations = check(event["tool_response"], policy, where="tool_response")
    if not violations:
        return 0
    # The tool name comes from the server, so it is bounded like any other
    # name it chose: a tool named after a row would put the row in the log.
    tool = _safe_label(str(event.get("tool_name", "")), policy, "<tool>")
    err.write(f"{NAME}: {tool} returned a value that must not leave the boundary.\n")
    listed, hidden = _listed(violations)
    for item in listed:
        err.write(f"  {item}\n")
    if hidden:
        err.write(f"  (+{hidden} more)\n")
    err.write("Do not repeat this call and do not restate the value.\n")
    return 2


def _cmd_proxy(args: argparse.Namespace, out: IO[str], err: IO[str]) -> int:
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        err.write(f"{NAME}: proxy needs a server command, e.g. {NAME} proxy -- my-server\n")
        return 2
    return run_proxy(command, _load_policy(args.policy), stderr=err)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=NAME,
        description=(
            "Block agent tool responses that carry identifiers, secrets or denied "
            "fields. egresswall never redacts and never rewrites a payload: a "
            "violating payload is refused whole."
        ),
    )
    parser.add_argument("--version", action="version", version=f"{NAME} {__version__}")
    # Hidden, and before the subcommand: `egresswall --traceback check f.json`.
    # It exists so a bug report can carry a real traceback; nothing a user is
    # meant to reach for, so it is not in --help.
    parser.add_argument("--traceback", action="store_true", help=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(dest="command_name", required=True)

    check_parser = subparsers.add_parser(
        "check", help="screen a JSON file; exit 1 if it would be blocked"
    )
    check_parser.add_argument("file", help="path to a JSON file, or - for stdin")
    check_parser.add_argument("--policy", help="path to a policy JSON file")
    check_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="text for a person, json for a pipeline (default: text)",
    )
    check_parser.set_defaults(handler=_cmd_check)

    hook_parser = subparsers.add_parser(
        "hook", help="Claude Code PostToolUse hook; reads the hook JSON on stdin"
    )
    hook_parser.add_argument("--policy", help="path to a policy JSON file")
    hook_parser.set_defaults(handler=_cmd_hook)

    proxy_parser = subparsers.add_parser("proxy", help="run an MCP stdio server behind the screen")
    proxy_parser.add_argument("--policy", help="path to a policy JSON file")
    proxy_parser.add_argument(
        "command", nargs=argparse.REMAINDER, help="-- followed by the server command"
    )
    proxy_parser.set_defaults(handler=_cmd_proxy)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args, sys.stdout, sys.stderr))
    except Exception as exc:
        # Every way this CLI can fail ends the same way: one line on stderr and
        # exit 2. A traceback is noise in an MCP server log and in a CI
        # transcript, and its frames carry the payload's own field names -- the
        # values this package exists to keep out of a log. `--traceback` puts
        # the real one back when a bug needs reporting.
        if args.traceback:
            raise
        sys.stderr.write(f"{NAME}: {str(exc) or type(exc).__name__}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
