#!/usr/bin/env python3
"""Re-fetch the sources docs/comparison.md and README.md quote, into docs/evidence/.

Not part of CI: refreshing an incumbent's numbers must be a deliberate act with
a diff. Every anchor below is a phrase one of those documents quotes; if a
source stops containing one, this script fails rather than writing evidence
that no longer supports the page.

It fetches two hosts over https and no others: `code.claude.com` for the two
documentation pages in PAGES, and `api.github.com` for the repository metadata
of the two projects in REPOS. `urls()` is the whole list; tests/test_comparison_truth.py
counts the distinct hosts in it against the number CONTRIBUTING.md states.

    python3 scripts/refresh_evidence.py
"""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

#: What every third-party host this script contacts sees. The sdist ships
#: scripts/, so this is the only place a URL in the released package could name
#: a repository other than this package's own -- and it must not.
UA = "guardrail-checkup-evidence/1 (+https://github.com/Alex-lop/guardrail-checkup)"

EVIDENCE = Path(__file__).resolve().parent.parent / "docs" / "evidence"

#: slug -> (url, the phrases the documents quote from it)
PAGES: dict[str, tuple[str, list[str]]] = {
    "claude-code-hooks": (
        "https://code.claude.com/docs/en/hooks",
        ["PreToolUse", "matcher", "CLAUDE_PROJECT_DIR", "tool_input", "Blocks the tool call"],
    ),
    # Every span docs/comparison.md quotes from this page, not just the two
    # words that name the command: a refresh that cannot fail on the sentences
    # the comparison row leans on is a refresh that proves nothing.
    "claude-code-commands": (
        "https://code.claude.com/docs/en/commands",
        [
            "doctor",
            "setup checkup",
            "Run a setup checkup that diagnoses issues and can fix them.",
            "Checks installation health, including duplicate or leftover installs, PATH problems, and "
            "unparseable settings files.",
            "trims checked-in CLAUDE.md files by cutting content Claude could derive from the codebase",
            "prints read-only installation diagnostics without starting a session.",
        ],
    ),
}

#: repository -> the phrases the documents quote from its metadata. An empty
#: list here would mean a refresh can never fail on what the page claims, so
#: every quoted span in docs/comparison.md's "What it does" column is listed.
REPOS: dict[str, list[str]] = {
    "microsoft/agentrc": ["Get your repo ready for AI."],
    "kenryu42/cc-safety-net": [
        "A pre-execution guard for AI coding agents.",
        "It blocks destructive Git and file system commands, plus common attempts to access sensitive files, "
        "before a tool call runs.",
    ],
}


#: Where a repository's metadata is read from. Named here rather than built at
#: the call site, so `urls()` can be the whole list and the host count cannot
#: drift from what the docstring and CONTRIBUTING.md say.
REPO_METADATA = "https://api.github.com/repos/{repository}"


def urls() -> list[str]:
    """Every URL this script requests. Two hosts, four URLs, and nothing else."""

    return [url for url, _ in PAGES.values()] + [REPO_METADATA.format(repository=item) for item in REPOS]


def fetch(url: str, accept: str = "text/html") -> str:
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    # https only, and only the URLs `urls()` lists; the module docstring names the hosts
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", "replace")


def as_text(markup: str) -> str:
    body = re.sub(r"(?is)<(script|style|svg|nav|footer)\b.*?</\1>", " ", markup)
    body = re.sub(r"(?s)<[^>]+>", " ", body)
    return re.sub(r"[ \t]+", " ", html.unescape(body)).strip()


def write(slug: str, url: str, body: str) -> Path:
    target = EVIDENCE / f"{slug}.txt"
    stamp = datetime.now(UTC).strftime("%Y-%m-%d")
    target.write_text(f"# source: {url}\n# fetched: {stamp}\n\n{body}\n", encoding="utf-8")
    return target


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    missing: list[str] = []
    for slug, (url, anchors) in PAGES.items():
        text = as_text(fetch(url))
        for anchor in anchors:
            if anchor not in text:
                missing.append(f"{slug}: {anchor!r} is no longer at {url}")
        write(slug, url, text)
    for repository, anchors in REPOS.items():
        payload = json.loads(fetch(REPO_METADATA.format(repository=repository), "application/vnd.github+json"))
        kept = {
            key: payload.get(key)
            for key in (
                "full_name",
                "description",
                "stargazers_count",
                "forks_count",
                "open_issues_count",
                "pushed_at",
                "license",
                "archived",
            )
        }
        body = json.dumps(kept, indent=2, sort_keys=True)
        for anchor in anchors:
            if anchor not in body:
                missing.append(f"{repository}: {anchor!r} is no longer in the repository metadata")
        write(repository.replace("/", "__"), REPO_METADATA.format(repository=repository), body)
    for line in missing:
        print(line, file=sys.stderr)
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
