"""guardrail-checkup: the six-section agent-guardrail report for one repository.

    from guardrail_checkup import checkup

    result, composed = checkup("/path/to/repo")
    print(result.head, [item.slug for item in result.candidates])

Deterministic, offline, read-only. It opens no socket, calls no model, runs
nothing from the repository it reads, and writes nothing inside it.
"""

from __future__ import annotations

from ._compose import (
    CANDIDATE_LIMIT,
    FIXTURE_SAMPLE,
    SIGNATURE_SCAN_BYTES,
    SIGNATURE_SCAN_FILES,
    Composition,
    compose,
    emit,
    hook_script,
    one_line_test,
    policy_globs,
    settings_snippet,
    starter_policy,
    wrapped_mcp,
)
from ._report import MONDAY_LIMIT, SECTIONS, render_json, render_markdown, run_date
from ._scan import (
    AGENT_FILE_LIMIT,
    CATEGORIES,
    CHURN_GLOBS,
    CODEOWNERS_BONUS,
    HEURISTIC_BASE,
    HISTORY_COMMITS,
    HISTORY_PATHS,
    LANGUAGE_ROWS,
    LINE_BUDGET,
    MAX_READ_BYTES,
    OWNER_LIMIT,
    READ_ONLY_GIT,
    READ_ONLY_GIT_CONFIG,
    REGRESSION_WEIGHT,
    SERVER_ROWS,
    SETTINGS_FILES,
    SKIP_DIRECTORIES,
    SNIFF_BYTES,
    WORKFLOW_LIMIT,
    WRITE_TOOLS,
    Candidate,
    Finding,
    Repair,
    Scan,
    md,
    scan,
    servers_of,
)

#: The distribution name, the console-script name and the name --version prints.
NAME = "guardrail-checkup"
__version__ = "0.1.0"


def checkup(
    path: str, max_files: int = 20_000, policy_path: str = "/etc/egresswall/policy.json"
) -> tuple[Scan, Composition]:
    """Read one repository and compose the siblings' results. Writes nothing."""

    result = scan(path, max_files)
    return result, compose(result, policy_path)


__all__ = [
    "AGENT_FILE_LIMIT",
    "CANDIDATE_LIMIT",
    "CATEGORIES",
    "CHURN_GLOBS",
    "CODEOWNERS_BONUS",
    "FIXTURE_SAMPLE",
    "HEURISTIC_BASE",
    "HISTORY_COMMITS",
    "HISTORY_PATHS",
    "LANGUAGE_ROWS",
    "LINE_BUDGET",
    "MAX_READ_BYTES",
    "MONDAY_LIMIT",
    "NAME",
    "OWNER_LIMIT",
    "READ_ONLY_GIT",
    "READ_ONLY_GIT_CONFIG",
    "REGRESSION_WEIGHT",
    "SECTIONS",
    "SERVER_ROWS",
    "SETTINGS_FILES",
    "SIGNATURE_SCAN_BYTES",
    "SIGNATURE_SCAN_FILES",
    "SKIP_DIRECTORIES",
    "SNIFF_BYTES",
    "WORKFLOW_LIMIT",
    "WRITE_TOOLS",
    "Candidate",
    "Composition",
    "Finding",
    "Repair",
    "Scan",
    "__version__",
    "checkup",
    "compose",
    "emit",
    "hook_script",
    "md",
    "one_line_test",
    "policy_globs",
    "render_json",
    "render_markdown",
    "run_date",
    "scan",
    "servers_of",
    "settings_snippet",
    "starter_policy",
    "wrapped_mcp",
]
