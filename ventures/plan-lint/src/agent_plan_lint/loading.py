"""Reading a plan or a policy off disk, or out of a dict already in memory.

JSON needs nothing beyond the standard library. YAML is optional: install the
`yaml` extra to read `.yaml` / `.yml` documents.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .models import Plan, ProjectPolicy

__all__ = ["MAX_DOCUMENT_BYTES", "DocumentError", "load_plan", "load_policy"]

# A plan is bounded by its own model; this is the outer guard so a hostile
# document cannot be expanded before pydantic ever sees it.
MAX_DOCUMENT_BYTES = 1_048_576

_YAML_SUFFIXES = {".yaml", ".yml"}


class DocumentError(ValueError):
    """The document is not a plan or a policy this version accepts."""


def _first_reason(error: ValidationError) -> str:
    """One readable line, not a pydantic dump."""

    first = error.errors()[0]
    location = ".".join(str(item) for item in first["loc"]) or "document"
    if first["type"] == "extra_forbidden":
        return f"unknown field {location}"
    return f"{location}: {first['msg']}"


def _no_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """JSON's `object_pairs_hook`: last-key-wins is a parser differential.

    `json.loads` silently keeps the last of two identical keys, so a document
    can say one thing to this validator and another to any other reader. The
    YAML branch refuses duplicates for the same reason.
    """

    seen: set[str] = set()
    for key, _ in pairs:
        if key in seen:
            raise DocumentError(f"duplicate key {key!r} in the document")
        seen.add(key)
    return dict(pairs)


def _no_json_constants(name: str) -> Any:
    """JSON's `parse_constant`: `NaN` and `Infinity` are CPython, not JSON.

    A Go, Rust or strict-JavaScript reader of the same file refuses them, which
    is the parser differential `_no_duplicate_pairs` exists to close, and
    `canonical_json_bytes` already refuses them on the way out.
    """

    raise DocumentError(f"the document may not contain the non-JSON literal {name}")


def _parse_yaml(text: str) -> Any:
    try:
        import yaml
    except ModuleNotFoundError as error:  # pragma: no cover - exercised in tests
        name = __package__.replace("_", "-") if __package__ else "agent-plan-lint"
        raise DocumentError(f"YAML documents need the yaml extra: pip install '{name}[yaml]'") from error

    class _StrictLoader(yaml.SafeLoader):
        """SafeLoader that refuses duplicate keys and YAML anchors and aliases.

        PyYAML's default is last-key-wins, which would silently drop half of an
        edit; an alias in a contract document is a way to make the text and the
        meaning disagree.

        Anchors and aliases are resolved by the composer and never reach a tag
        constructor, so they are refused here, where they are produced. The two
        tag constructors below still cover the `<<` merge key and the `=` value
        key, which are mapping keys rather than aliases.
        """

        def compose_node(self, parent: Any, index: Any) -> Any:
            event = self.peek_event()
            if isinstance(event, yaml.events.AliasEvent) or getattr(event, "anchor", None):
                raise DocumentError("the document may not use YAML anchors or aliases")
            return super().compose_node(parent, index)

    def _no_duplicate_keys(loader: Any, node: Any) -> dict[Any, Any]:
        seen: set[str] = set()
        for key_node, _ in node.value:
            key = loader.construct_object(key_node, deep=True)
            # YAML allows a list, a dict or a set as a mapping key. A plan and a
            # policy have string keys only, and the `key in seen` below hashes
            # what it is given, so an unhashable key used to leave this function
            # as a `TypeError` -- past the except tuple, a traceback, exit 1.
            # It is refused here, by name, where it is produced.
            if not isinstance(key, str):
                raise DocumentError("the document may not use a non-string mapping key")
            if key in seen:
                raise DocumentError(f"duplicate key {key!r} in the document")
            seen.add(key)
        return loader.construct_mapping(node, deep=True)

    def _no_alias(_loader: Any, _node: Any) -> None:
        raise DocumentError("the document may not use YAML anchors or aliases")

    _StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicate_keys)
    for tag in ("tag:yaml.org,2002:value", "tag:yaml.org,2002:merge"):
        _StrictLoader.add_constructor(tag, _no_alias)
    try:
        return yaml.load(text, Loader=_StrictLoader)
    except DocumentError:
        # The duplicate-key and alias guards above already say what is wrong.
        raise
    except RecursionError as error:
        # A deeply nested document exhausts the composer's stack. That is a
        # document this version will not load, not a crash of the caller.
        raise DocumentError("the document is nested too deeply to load") from error
    except Exception as error:  # noqa: BLE001 - failing closed is the point
        # No exception type is named, deliberately. `yaml.YAMLError` is only the
        # parser; anything raised inside a *constructor* escapes it, and
        # enumerating those was fail-open by construction -- each round of
        # review found one more (a 4301-digit integer as `ValueError`, an
        # exponent out of range as `OverflowError`, an unhashable mapping key as
        # `TypeError`, then `!!timestamp "not-a-time"` as `AttributeError`,
        # `!!bool "x"` as `KeyError`, `!!int ""` as `IndexError`). Everything out
        # of `yaml.load` is by definition a document this version cannot read,
        # which is a refusal rather than a traceback out of `load_plan`.
        #
        # `str(error)` is never interpolated: `MarkedYAMLError.__str__` embeds a
        # snippet of the offending source line, so a plan that fails to parse
        # would print its own content -- a credential included -- into the CI log
        # this package refuses credential-shaped text to keep them out of. The
        # problem and its coordinates say what and where without quoting the
        # buffer.
        mark = getattr(error, "problem_mark", None)
        where = f" at line {mark.line + 1}, column {mark.column + 1}" if mark is not None else ""
        problem = getattr(error, "problem", None) or type(error).__name__
        raise DocumentError(f"the document is not valid YAML: {problem}{where}") from error


def _document(source: str | os.PathLike[str] | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(source, Mapping):
        return dict(source)
    try:
        path = Path(source)
        # A read from a FIFO blocks until the writer supplies the cap or
        # closes, so a validator pointed at a named pipe or a process
        # substitution would hang rather than fail. Only a regular file is
        # read; a directory, a device and a pipe are all refused by name here.
        if path.exists() and not path.is_file():
            raise DocumentError(f"{path} is not a regular file")
        with path.open("rb") as handle:
            # One byte past the cap: enough to know it is over, never the whole
            # file. A multi-gigabyte file costs the cap, not its size.
            raw = handle.read(MAX_DOCUMENT_BYTES + 1)
    except DocumentError:
        raise
    except (OSError, ValueError, ArithmeticError) as error:
        # Not only the missing file: a name with an embedded NUL raises
        # `ValueError` out of `open`, and a name the platform cannot represent
        # raises out of `Path`. All of them are "this document is unreadable".
        raise DocumentError(f"cannot read {source}: {getattr(error, 'strerror', None) or error}") from error
    except Exception as error:  # noqa: BLE001 - failing closed is the point
        # Same rule as the two parse branches: a source this version cannot open
        # is a refusal naming what happened, not a traceback -- `Path(source)`
        # on a value that is neither a string nor a path raises `TypeError`.
        raise DocumentError(f"cannot read {source!r}: {type(error).__name__}") from error
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise DocumentError(f"{path} is larger than {MAX_DOCUMENT_BYTES} bytes")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise DocumentError(f"{path} is not UTF-8 text") from error
    if path.suffix.lower() in _YAML_SUFFIXES:
        document = _parse_yaml(text)
    else:
        try:
            document = json.loads(
                text,
                object_pairs_hook=_no_duplicate_pairs,
                parse_constant=_no_json_constants,
            )
        except DocumentError:
            # The duplicate-key and non-JSON-literal guards say what is wrong.
            raise
        except RecursionError as error:
            # `json.loads` recurses per nesting level, so a 60 KB document can
            # exhaust the stack well inside MAX_DOCUMENT_BYTES.
            raise DocumentError(f"{path} is nested too deeply to load") from error
        except (ValueError, ArithmeticError) as error:
            # `json.JSONDecodeError` is a `ValueError` and the ordinary case;
            # the scanner also raises a plain one for an integer literal past
            # CPython's 4300-digit int-string limit, and an `OverflowError`
            # for an exponent out of range. Every one of them is a document
            # this version will not load, not a crash of the caller.
            raise DocumentError(f"{path} is not valid JSON: {error}") from error
        except Exception as error:  # noqa: BLE001 - failing closed is the point
            # As in `_parse_yaml`: an exception this branch did not predict is
            # still a document this version will not load. Only the type name is
            # reported, because an unpredicted exception's message is not known
            # to be free of the document's own text.
            raise DocumentError(f"{path} is not valid JSON: {type(error).__name__}") from error
    if not isinstance(document, dict):
        raise DocumentError(f"{path} must contain a mapping")
    return document


def load_policy(source: str | os.PathLike[str] | Mapping[str, Any]) -> ProjectPolicy:
    """Load a project policy from a JSON/YAML file path or a mapping."""

    try:
        return ProjectPolicy.model_validate(_document(source))
    except ValidationError as error:
        raise DocumentError(f"policy is invalid: {_first_reason(error)}") from error


def load_plan(source: str | os.PathLike[str] | Mapping[str, Any]) -> Plan:
    """Load a plan from a JSON/YAML file path or a mapping."""

    try:
        return Plan.model_validate(_document(source))
    except ValidationError as error:
        raise DocumentError(f"plan is invalid: {_first_reason(error)}") from error
