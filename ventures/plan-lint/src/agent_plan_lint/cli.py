"""The `agent-plan-lint` command line."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from . import NAME, __version__
from .loading import DocumentError, load_plan, load_policy
from .models import Plan, ProjectPolicy, is_invisible
from .validation import ISSUE_CODES, validate_plan

__all__ = ["main"]


def _printable(value: str) -> str:
    """Text from a document or the command line, safe to put on one line.

    A model refuses `models.UNPRINTABLE` in any text, and every character
    `models.is_invisible` names in a path, when a document loads -- so what
    reaches here is a file name off the command line and the text of a load
    failure. Both classes are escaped with that one imported predicate, so a
    file name carrying a zero-width joiner or a variation selector cannot render
    as a different name in this tool's own output. Only that predicate: a
    combining mark, which a path may not carry, is visible in text and is
    printed as itself.
    """

    return "".join(f"\\u{ord(character):04x}" if is_invisible(character) else character for character in value)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=NAME,
        description=("Statically validate an agent's plan against a project policy before anything runs."),
    )
    parser.add_argument("--version", action="version", version=f"{NAME} {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser(
        "check",
        help="validate a plan against a policy (exit 0 valid, 1 issues, 2 load or usage error)",
    )
    check.add_argument("plan", help="path to the plan document (JSON, or YAML with the yaml extra)")
    check.add_argument("--policy", required=True, help="path to the project policy document")
    check.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="text (the default), or the whole validation result as JSON",
    )
    check.add_argument(
        "--strict",
        action="store_true",
        help="also reject criteria discharged by a human gate",
    )

    commands.add_parser("codes", help="list every issue code and what it means")
    commands.add_parser("schema", help="print the JSON Schema of the plan and policy documents")
    return parser


def _load_failure(error: DocumentError, document: str, output_format: str) -> int:
    """Exit 2 in the format the caller asked for, so `--format json` is JSON on every exit."""

    if output_format == "json":
        print(json.dumps({"document": document, "error": str(error)}, indent=2, sort_keys=True))
    else:
        print(f"{NAME}: {_printable(str(error))}", file=sys.stderr)
    return 2


def _check(arguments: argparse.Namespace) -> int:
    try:
        policy = load_policy(arguments.policy)
    except DocumentError as error:
        return _load_failure(error, arguments.policy, arguments.format)
    try:
        plan = load_plan(arguments.plan)
    except DocumentError as error:
        return _load_failure(error, arguments.plan, arguments.format)

    result = validate_plan(policy, plan, strict=arguments.strict)
    if arguments.format == "json":
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
    elif result.valid:
        print(f"ok: {_printable(arguments.plan)} is within {_printable(arguments.policy)}")
        print(f"order: {' -> '.join(result.topological_order)}")
    else:
        count = len(result.issues)
        print(f"invalid: {count} issue{'' if count == 1 else 's'} in {_printable(arguments.plan)}")
        for item in result.issues:
            where = f" [{_printable(item.task_id)}]" if item.task_id else ""
            print(f"  {item.code}{where}: {_printable(item.detail)}")
    return 0 if result.valid else 1


#: Undocumented, and deliberately: it is for debugging this package, not for
#: using it, so it is stripped before argparse ever sees the command line and
#: never appears in `--help`. It may sit anywhere in the arguments.
_TRACEBACK_FLAG = "--traceback"


def main(argv: Sequence[str] | None = None) -> int:
    """The one entry point, for the console script and for `python -m agent_plan_lint`.

    Every unexpected exception becomes the documented error exit and one line on
    stderr. A traceback at the user is not a diagnosis: it is this package's bug
    printed into someone else's CI log, and the exit status that comes with it
    (1) says "the plan is not within policy", which is a different and worse
    lie. `--traceback` opts back into the real exception while debugging.
    """

    argv = list(sys.argv[1:] if argv is None else argv)
    wants_traceback = _TRACEBACK_FLAG in argv
    if wants_traceback:
        argv = [argument for argument in argv if argument != _TRACEBACK_FLAG]
    try:
        return _run(argv)
    except Exception as error:  # noqa: BLE001 - the safety net is the point
        if wants_traceback:
            raise
        detail = _printable(f"{type(error).__name__}: {error}")
        print(f"{NAME}: internal error: {detail}", file=sys.stderr)
        return 2


def _run(argv: Sequence[str]) -> int:
    arguments = _parser().parse_args(argv)
    if arguments.command == "codes":
        width = max(len(code) for code in ISSUE_CODES)
        for code, meaning in ISSUE_CODES.items():
            print(f"{code.ljust(width)}  {meaning}")
        return 0
    if arguments.command == "schema":
        print(
            json.dumps(
                {
                    "plan": Plan.model_json_schema(),
                    "policy": ProjectPolicy.model_json_schema(),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    return _check(arguments)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
