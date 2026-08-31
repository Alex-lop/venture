"""`python -m guardrail_checkup` is the console script."""

from __future__ import annotations

import sys

from ._cli import main

if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    sys.exit(main())
