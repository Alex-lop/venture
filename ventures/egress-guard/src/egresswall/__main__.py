"""`python -m egresswall` runs the same CLI as the console script.

A project venv's `bin/` is not always on PATH -- a CI job, a `uv run`, a
pre-commit `language: system` hook and a `.claude/settings.json` hook command
all reach for `python -m` when it is not. Without this the import error they
got was exit 1, which is the code Claude Code treats as non-blocking.
"""

from __future__ import annotations

from ._cli import main

raise SystemExit(main())
