"""egresswall: a value-level egress firewall for agent tool responses.

It screens a JSON payload for raw identifiers, secret material, forbidden field
names, denied field paths and forbidden literal values, and it blocks instead of
redacting -- a redacted payload hides that an unauthorized value was assembled.
"""

from __future__ import annotations

from ._core import (
    DEFAULT_DETECTORS,
    DEFAULT_FORBIDDEN_KEY_SUBSTRINGS,
    DEFAULT_FORBIDDEN_KEY_SUFFIXES,
    DEFAULT_FORBIDDEN_KEYS,
    DEFAULT_GOVERNANCE_TOKENS,
    DENIED_FIELD_PATH,
    DETECTORS,
    EMBEDDED_DOCUMENT_UNPARSEABLE,
    FORBIDDEN_KEY,
    FORBIDDEN_VALUE,
    JOIN_TOKEN,
    MAX_ALLOWED_DEPTH,
    MAX_DENIED_PATH_CHARS,
    MAX_FORBIDDEN_VALUES,
    PAYLOAD_TOO_DEEP,
    PAYLOAD_TOO_LARGE,
    RAW_IDENTIFIER,
    SECRET_MATERIAL,
    VIOLATION_CODES,
    EgressViolation,
    Policy,
    Violation,
    check,
    screen,
)

#: The distribution name, the console-script name and the name --version prints.
NAME = "egresswall"
__version__ = "0.1.0"

__all__ = [
    "DEFAULT_DETECTORS",
    "DEFAULT_FORBIDDEN_KEYS",
    "DEFAULT_FORBIDDEN_KEY_SUBSTRINGS",
    "DEFAULT_FORBIDDEN_KEY_SUFFIXES",
    "DEFAULT_GOVERNANCE_TOKENS",
    "DENIED_FIELD_PATH",
    "DETECTORS",
    "EMBEDDED_DOCUMENT_UNPARSEABLE",
    "FORBIDDEN_KEY",
    "FORBIDDEN_VALUE",
    "JOIN_TOKEN",
    "MAX_ALLOWED_DEPTH",
    "MAX_DENIED_PATH_CHARS",
    "MAX_FORBIDDEN_VALUES",
    "NAME",
    "PAYLOAD_TOO_DEEP",
    "PAYLOAD_TOO_LARGE",
    "RAW_IDENTIFIER",
    "SECRET_MATERIAL",
    "VIOLATION_CODES",
    "EgressViolation",
    "Policy",
    "Violation",
    "__version__",
    "check",
    "screen",
]
