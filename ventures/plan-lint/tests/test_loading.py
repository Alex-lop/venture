"""Loading plans and policies: JSON always, YAML behind the optional extra."""

from __future__ import annotations

import json
import os
import re
import sys

import pytest
import yaml

from agent_plan_lint import DocumentError, load_plan, load_policy
from agent_plan_lint.loading import MAX_DOCUMENT_BYTES
from conftest import plan as _plan
from conftest import policy as _policy


def _write(directory, name: str, model) -> str:
    path = directory / name
    path.write_text(json.dumps(model.model_dump(mode="json")), encoding="utf-8")
    return str(path)


def test_a_mapping_loads_without_touching_the_filesystem() -> None:
    assert load_policy(_policy().model_dump(mode="json")) == _policy()
    assert load_plan(_plan().model_dump(mode="json")) == _plan()


def test_json_round_trips_through_a_file(tmp_path) -> None:
    assert load_policy(_write(tmp_path, "policy.json", _policy())) == _policy()
    assert load_plan(_write(tmp_path, "plan.json", _plan())) == _plan()


def test_yaml_round_trips_when_the_extra_is_installed(tmp_path) -> None:
    path = tmp_path / "plan.yaml"
    path.write_text(yaml.safe_dump(_plan().model_dump(mode="json"), sort_keys=True))

    assert load_plan(path) == _plan()


def test_yaml_refuses_duplicate_keys_and_aliases(tmp_path) -> None:
    duplicate = tmp_path / "duplicate.yaml"
    duplicate.write_text("mission_id: one\nmission_id: two\n")
    aliased = tmp_path / "aliased.yaml"
    aliased.write_text("base: &anchor\n  mission_id: one\nmerged:\n  <<: *anchor\n")

    with pytest.raises(DocumentError, match="duplicate key"):
        load_plan(duplicate)
    with pytest.raises(DocumentError, match="anchors or aliases"):
        load_plan(aliased)


@pytest.mark.parametrize(
    "text",
    (
        "policy_id: &pid demo\nrepo_id: *pid\n",
        "policy_id: demo\nallowed_read_globs: &globs [src/**]\nallowed_write_globs: *globs\n",
        "policy_id: &unused demo\n",
        "tasks:\n  - &task {task_id: a}\n  - *task\n",
    ),
)
def test_yaml_anchors_and_aliases_are_refused_where_they_are_produced(tmp_path, text: str) -> None:
    """An alias is resolved by the composer and never reaches a tag constructor.

    A reviewer reads `repo_id: *pid` and the validator reads `repo_id: demo`,
    which is the parser differential the duplicate-key guard exists to close.
    """

    path = tmp_path / "aliased.yaml"
    path.write_text(text)

    with pytest.raises(DocumentError, match="anchors or aliases"):
        load_policy(path)


def test_a_named_pipe_is_refused_rather_than_read(tmp_path) -> None:
    """A FIFO with a writer that never closes would block the read forever."""

    path = tmp_path / "plan.json"
    os.mkfifo(path)

    with pytest.raises(DocumentError, match="not a regular file"):
        load_plan(path)


def test_a_directory_says_what_is_wrong_with_it(tmp_path) -> None:
    with pytest.raises(DocumentError, match="not a regular file"):
        load_plan(tmp_path)


def test_yaml_without_the_extra_says_how_to_install_it(tmp_path, monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "yaml", None)
    path = tmp_path / "plan.yaml"
    path.write_text("mission_id: one\n")

    with pytest.raises(DocumentError, match=r"pip install 'agent-plan-lint\[yaml\]'"):
        load_plan(path)


@pytest.mark.parametrize(
    ("name", "text", "expected"),
    (
        ("plan.json", "{not json", "not valid JSON"),
        ("plan.json", "[1, 2]", "must contain a mapping"),
        ("plan.yaml", "a: [1, 2\n", "not valid YAML"),
    ),
)
def test_unparseable_documents_carry_one_reason(tmp_path, name, text, expected) -> None:
    path = tmp_path / name
    path.write_text(text)

    with pytest.raises(DocumentError, match=expected):
        load_plan(path)


def test_a_missing_file_is_a_document_error(tmp_path) -> None:
    with pytest.raises(DocumentError, match="cannot read"):
        load_plan(tmp_path / "absent.json")


def test_an_oversized_document_is_refused_before_parsing(tmp_path) -> None:
    path = tmp_path / "plan.json"
    path.write_bytes(b"x" * (MAX_DOCUMENT_BYTES + 1))

    with pytest.raises(DocumentError, match="larger than"):
        load_plan(path)


def test_an_unknown_field_names_itself(tmp_path) -> None:
    document = {**_plan().model_dump(mode="json"), "budget": 3}

    with pytest.raises(DocumentError, match="unknown field budget"):
        load_plan(document)


def test_an_invalid_value_names_its_location() -> None:
    document = _policy().model_dump(mode="json")
    document["base_sha"] = "not-a-sha"

    with pytest.raises(DocumentError, match="policy is invalid: base_sha"):
        load_policy(document)


@pytest.mark.parametrize("literal", ("NaN", "Infinity", "-Infinity"))
def test_json_refuses_the_non_json_literals_cpython_accepts(tmp_path, literal: str) -> None:
    """Another language's reader refuses these, so this one does too."""

    path = tmp_path / "constant.json"
    path.write_text(f'{{"revision": {literal}}}')

    with pytest.raises(DocumentError, match="non-JSON literal"):
        load_plan(path)


def test_json_refuses_duplicate_keys(tmp_path) -> None:
    """`json.loads` is last-key-wins, which makes the text and the meaning disagree."""

    path = tmp_path / "duplicate.json"
    path.write_text('{"mission_id": "one", "mission_id": "two"}')

    with pytest.raises(DocumentError, match="duplicate key"):
        load_plan(path)


@pytest.mark.parametrize(
    ("name", "text"),
    (
        ("deep.json", '{"a":' * 10_000 + "1" + "}" * 10_000),
        ("deep.yaml", "[" * 5_000 + "]" * 5_000),
    ),
)
def test_a_document_nested_too_deeply_is_a_document_error(tmp_path, name, text) -> None:
    """A 60 KB document exhausts the parser's stack well inside MAX_DOCUMENT_BYTES."""

    path = tmp_path / name
    path.write_text(text)

    assert len(text) < MAX_DOCUMENT_BYTES
    with pytest.raises(DocumentError, match="nested too deeply"):
        load_plan(path)


@pytest.mark.skipif(not os.path.exists("/dev/zero"), reason="needs a POSIX character device")
def test_an_endless_source_is_refused_by_name_rather_than_read() -> None:
    """Only a regular file is read, so an endless device never reaches the parser."""

    with pytest.raises(DocumentError, match="not a regular file"):
        load_plan("/dev/zero")


@pytest.mark.parametrize(
    ("name", "text"),
    (
        ("plan.json", '{"schema_version": ' + "9" * 4_301 + "}"),
        ("plan.yaml", "schema_version: " + "9" * 4_301 + "\n"),
    ),
)
def test_a_number_the_interpreter_refuses_is_a_document_error(tmp_path, name, text) -> None:
    """CPython caps integer-string conversion at 4300 digits, and the parser raises a plain ValueError.

    Neither `json.JSONDecodeError` nor `yaml.YAMLError` covers that, so the
    load used to die with a traceback and the wrong exit status on a 4 KB file.
    """

    path = tmp_path / name
    path.write_text(text)

    assert len(text) < MAX_DOCUMENT_BYTES
    with pytest.raises(DocumentError, match="not valid (JSON|YAML)"):
        load_plan(path)


def test_a_yaml_refusal_never_echoes_the_line_that_failed(tmp_path) -> None:
    """`MarkedYAMLError.__str__` quotes the offending source line, credentials included.

    A plan that fails to parse would print its own content to stderr and into
    `--format json`, which is the harm the credential-shape scan exists to
    prevent -- and the scan cannot help, because the document never reaches a
    model. The refusal says what and where, and quotes nothing.
    """

    path = tmp_path / "plan.yaml"
    path.write_text('mission_id: m\ntoken: "AKIAIOSFODNN7EXAMPLE and ghp_0123456789abcdefghij\nrevision: 1\n')

    with pytest.raises(DocumentError) as raised:
        load_plan(path)

    message = str(raised.value)
    assert "the document is not valid YAML" in message
    assert re.search(r"at line \d+, column \d+", message), message
    assert "AKIAIOSFODNN7EXAMPLE" not in message
    assert "ghp_" not in message


def test_a_path_the_platform_cannot_represent_is_a_document_error() -> None:
    """`open` raises `ValueError`, not `OSError`, for a name with an embedded NUL."""

    with pytest.raises(DocumentError, match="cannot read"):
        load_plan("plan\x00.json")


@pytest.mark.parametrize(
    "text",
    (
        "? [1, 2]\n: v\n",
        "? {a: 1}\n: v\n",
        "a:\n  ? [1]\n  : v\n",
        "? !!set {a}\n: v\n",
    ),
)
def test_a_complex_yaml_mapping_key_is_a_document_error(tmp_path, text: str) -> None:
    """A non-scalar key used to reach `key in seen` and die with `TypeError: unhashable type`.

    The duplicate-key guard hashes the constructed key before PyYAML's own
    `found unhashable key` can fire, so the document escaped the except tuple
    entirely: a traceback on stderr, exit 1 rather than 2, and nothing on
    stdout under `--format json`.
    """

    path = tmp_path / "complex.yaml"
    path.write_text(text)

    with pytest.raises(DocumentError, match="non-string mapping key|not valid YAML"):
        load_plan(path)
    with pytest.raises(DocumentError, match="non-string mapping key|not valid YAML"):
        load_policy(path)


# ---------------------------------------------------------------------------
# The parse branches fail closed: they name no exception type they must predict.
# ---------------------------------------------------------------------------

#: The 27 documents that used to leave `load_plan` as an `AttributeError`, a
#: `KeyError` or an `IndexError`. Every one is a tag PyYAML's own
#: `SafeConstructor` accepts and then cannot convert, which is a failure inside a
#: constructor rather than in the parser -- so `yaml.YAMLError` never covered it.
#: Generated from the tags and the values, so the shapes are the count.
UNCONVERTIBLE_TAGGED_SCALARS = tuple(
    f'a: {tag} "{value}"\n'
    for tag, values in (
        (
            "!!timestamp",
            ("not-a-time", "x", "", "abc def", "tomorrow", "2026-13-99", "now", "++", "2026/08/31", "-"),
        ),
        (
            "!!bool",
            ("x", "", "maybe", "2", "yes please", "TRUEish", "nope", "0x1", "y ", "vrai", "si", "on/off", "tru", ","),
        ),
        ("!!int", ("", "-")),
        ("!!float", ("",)),
    )
    for value in values
)


@pytest.mark.parametrize("text", UNCONVERTIBLE_TAGGED_SCALARS)
def test_a_tag_whose_value_cannot_be_converted_is_a_document_error(tmp_path, text: str) -> None:
    """A library consumer catching `DocumentError` used to get a traceback instead.

    Through the CLI it was worse: the `main` safety net turned it into
    `internal error: AttributeError` on stderr with nothing on stdout, so
    `--format json` printed no JSON at all on a documented exit-2 path.
    """

    assert len(UNCONVERTIBLE_TAGGED_SCALARS) == 27
    path = tmp_path / "tagged.yaml"
    path.write_text(text)

    with pytest.raises(DocumentError, match="not valid YAML"):
        load_plan(path)
    with pytest.raises(DocumentError, match="not valid YAML"):
        load_policy(path)


def test_no_tagged_scalar_leaves_the_loader_as_anything_but_a_document_error(tmp_path) -> None:
    """The adversarial sweep the enumerated except tuple kept failing.

    Every standard YAML tag against every value that is nonsense for some of
    them: 252 documents, none of which may leave `load_plan` as anything but a
    `Plan` or a `DocumentError`. Three rounds of review each found one more
    exception type to add to a tuple; this asserts the property those rounds
    were sampling instead.
    """

    tags = ("!!str", "!!bool", "!!int", "!!float", "!!timestamp", "!!binary")
    tags += ("!!null", "!!seq", "!!map", "!!set", "!!omap", "!!pairs")
    values = ("", "-", "+", ".", "0x", "not-a-time", "x", "y ", "2026-13-99", "∞", ",")
    values += ("[", "{", "*", "&", "!", "%", "@", "0b2", "1e", "tru")
    path = tmp_path / "fuzz.yaml"
    escaped = []

    for tag in tags:
        for value in values:
            path.write_text(f'a: {tag} "{value}"\n')
            try:
                load_plan(path)
            except DocumentError:
                continue
            except Exception as error:  # noqa: BLE001 - that is what is being asserted about
                escaped.append((tag, value, type(error).__name__))

    assert len(tags) * len(values) == 252
    assert escaped == []


def test_an_unpredicted_json_failure_is_still_a_document_error(tmp_path, monkeypatch) -> None:
    """The JSON branch names no type either, and reports only the type it caught.

    An exception the branch did not predict has a message nobody has checked for
    the document's own text, so the refusal carries the type name and nothing
    else -- the same rule the YAML branch follows to keep a credential in an
    unparseable plan out of the CI log.
    """

    from agent_plan_lint import loading

    def _boom(*arguments: object, **keywords: object) -> object:
        raise LookupError("a message quoting sk-live-0123456789abcdef")

    monkeypatch.setattr(loading.json, "loads", _boom)
    path = tmp_path / "plan.json"
    path.write_text("{}")

    with pytest.raises(DocumentError, match="not valid JSON: LookupError") as raised:
        load_plan(path)

    assert "sk-live" not in str(raised.value)


def test_a_source_that_is_not_a_path_or_a_mapping_is_a_document_error() -> None:
    """`Path(source)` raises `TypeError`, which the read branch used not to name."""

    with pytest.raises(DocumentError, match="cannot read"):
        load_plan(b"plan.json")
