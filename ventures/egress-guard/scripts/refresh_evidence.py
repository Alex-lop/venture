#!/usr/bin/env python3
"""Re-fetch the sources docs/comparison.md cites and rewrite docs/evidence/.

Not part of CI: refreshing the numbers must be a deliberate act with a diff.
Every anchor below is a sentence docs/comparison.md quotes; if a source stops
containing one, this script fails rather than writing evidence that no longer
supports the page.

    python3 scripts/refresh_evidence.py
"""

from __future__ import annotations

import html
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

#: What every third-party host this script contacts sees. The sdist ships
#: scripts/, so this is the only place a URL in the released package could name
#: a repository other than this package's own -- and it must not.
UA = "egresswall-evidence/1 (+https://github.com/Alex-lop/egresswall)"

#: The categories docs/comparison.md enumerates, in the order the response lists them.
MODERATION_CATEGORIES = (
    "sexual",
    "sexual/minors",
    "harassment",
    "harassment/threatening",
    "hate",
    "hate/threatening",
    "illicit",
    "illicit/violent",
    "self-harm",
    "self-harm/intent",
    "self-harm/instructions",
    "violence",
    "violence/graphic",
)
EVIDENCE = Path(__file__).resolve().parent.parent / "docs" / "evidence"
WINDOW = 600

REPOS = [
    "data-privacy-stack/presidio",
    "protectai/llm-guard",
    "snyk/agent-scan",
    "lasso-security/mcp-gateway",
    "guardrails-ai/guardrails",
]

#: slug -> (url, anchors quoted by docs/comparison.md)
PAGES: dict[str, tuple[str, list[str]]] = {
    "presidio-readme": (
        "https://api.github.com/repos/data-privacy-stack/presidio/readme",
        [
            "Presidio is moving to a new home",
            "Context aware, pluggable and customizable PII de-identification service",
            "identification and anonymization modules for private entities in text",
        ],
    ),
    "llm-guard-readme": (
        "https://api.github.com/repos/protectai/llm-guard/readme",
        [
            "The Security Toolkit for LLM Interactions",
            "sanitization, detection of harmful language, prevention of data leakage",
        ],
    ),
    "agent-scan-readme": (
        "https://api.github.com/repos/snyk/agent-scan/readme",
        [
            "a security scanning tool to both scan and inspect the supply chain",
            "scan MCP servers, tools, prompts, resources, and skills",
        ],
    ),
    "mcp-gateway-readme": (
        "https://api.github.com/repos/lasso-security/mcp-gateway/readme",
        [
            "Intercepts requests and responses to sanitize sensitive information",
            "will automatically mask the sensitive token in the response",
        ],
    ),
    "guardrails-readme": (
        "https://api.github.com/repos/guardrails-ai/guardrails/readme",
        [
            "intercept the inputs and outputs of LLMs",
            "discontinuing its hosted remote inferencing",
            # the comparison page's claim that Guardrails can refuse rather than repair
            "OnFailAction.EXCEPTION",
        ],
    ),
    "claude-code-hooks": (
        "https://code.claude.com/docs/en/hooks",
        [
            "Shows stderr to Claude; the tool already ran",
            "Replaces the tool",  # updatedToolOutput
            "For redaction or transformation use cases",
        ],
    ),
    "openai-moderation": (
        "https://developers.openai.com/api/docs/guides/moderation",
        [
            "Use the results to enforce your application",
            # Every flag the comparison page enumerates, so a taxonomy that gains
            # or loses a category fails this refresh instead of being rewritten.
            *(f'"{name}" :' for name in MODERATION_CATEGORIES),
        ],
    ),
}


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8", "replace")
    if url.endswith("/readme"):
        import base64

        body = base64.b64decode(json.loads(body)["content"]).decode("utf-8", "replace")
        # Drop markdown emphasis so a quotation of the prose matches the source
        # even where the source bolds a word inside the sentence.
        body = re.sub(r"[*`_]", "", body)
    elif "<html" in body[:2000].lower():
        body = re.sub(r"<(script|style).*?</\1>", " ", body, flags=re.S | re.I)
        body = html.unescape(re.sub(r"<[^>]+>", " ", body))
    return re.sub(r"[ \t]+", " ", body)


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    missing: list[str] = []
    pending: list[tuple[Path, str]] = []
    for slug, (url, anchors) in PAGES.items():
        text = fetch(url)
        parts = [f"# source: {url}\n# fetched: {today}\n"]
        spans: list[list[int]] = []
        for anchor in anchors:
            index = text.find(anchor)
            if index < 0:
                missing.append(f"{slug}: {anchor!r}")
                continue
            spans.append([max(0, index - WINDOW), index + WINDOW])
        merged: list[list[int]] = []
        for start, end in sorted(spans):  # overlapping windows are one excerpt
            if merged and start <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])
        parts.extend(text[start:end].strip() for start, end in merged)
        pending.append((EVIDENCE / f"{slug}.txt", "\n\n---\n\n".join(parts) + "\n"))
    for repo in REPOS:
        meta = json.loads(fetch(f"https://api.github.com/repos/{repo}"))
        try:
            release = json.loads(fetch(f"https://api.github.com/repos/{repo}/releases/latest"))
        except Exception:  # a repo may have no release
            release = {}
        record = {
            "fetched": today,
            "full_name": meta["full_name"],
            "archived": meta["archived"],
            "stargazers_count": meta["stargazers_count"],
            "license": (meta.get("license") or {}).get("spdx_id"),
            "pushed_at": meta["pushed_at"],
            "tag_name": release.get("tag_name"),
            "published_at": release.get("published_at"),
        }
        name = repo.replace("/", "__") + ".json"
        pending.append((EVIDENCE / name, json.dumps(record, indent=2, sort_keys=True) + "\n"))
    if missing:
        # Nothing is written: evidence that no longer supports the page must not
        # replace evidence that does, or the failure below is the only trace.
        print("MISSING ANCHORS (the comparison page cites text the source no longer has):")
        for item in missing:
            print("  " + item)
        return 1
    for path, body in pending:
        path.write_text(body, encoding="utf-8")
        print(f"wrote {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
