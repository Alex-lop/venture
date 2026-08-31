from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

FENCE = re.compile(r"```.*?```", re.S)
CODE = re.compile(r"`[^`\n]*`")
#: An editorial insertion such as "discover[s]" is the quoter's, not the source's.
INSERTION = re.compile(r"\[[^\]]{0,3}\]")


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT


def flatten(text: str) -> str:
    """Compare on words, not typography: curly quotes, emphasis and breaks are noise."""
    for curly, plain in zip("\u2019\u2018\u201c\u201d", "''\"\"", strict=True):
        text = text.replace(curly, plain)
    return INSERTION.sub("", re.sub(r"\s+", " ", text.replace("*", "").replace("`", "")))


def fullwidth(ascii_text: str) -> str:
    """The fullwidth spelling of an ASCII name, built rather than pasted.

    The literal is what the README shows and what `_fold` has to fold, but a
    file of fullwidth capitals is exactly what the linter's ambiguous-character
    rule exists to stop, so it is derived from the offset instead.
    """
    return "".join(chr(ord(char) + 0xFEE0) for char in ascii_text)


def quotations(markdown: str) -> list[str]:
    """Every double-quoted span outside code, paired left to right."""
    spans = flatten(CODE.sub("", FENCE.sub("", markdown))).split('"')
    assert len(spans) % 2 == 1, "unbalanced quotation marks"
    return [item for item in spans[1::2] if len(item) >= 12]


def evidence_corpus() -> str:
    """Every source excerpt checked in under docs/evidence/, as one flat string."""
    files = sorted((ROOT / "docs" / "evidence").glob("*.txt"))
    return flatten("\n".join(item.read_text(encoding="utf-8") for item in files))


def unquoted(markdown: str) -> list[str]:
    """The quotations in `markdown` that no checked-in source contains."""
    corpus = evidence_corpus()
    missing = []
    for quote in quotations(markdown):
        if any(part.strip(". ") not in corpus for part in quote.split(" ... ")):
            missing.append(quote)
    return missing
