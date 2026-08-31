"""An MCP stdio proxy that screens what the server sends before the client sees it.

The proxy spawns the real MCP server, forwards newline-delimited JSON-RPC in
both directions, and screens every server message: a ``result`` or an ``error``
that fails the policy is replaced with a JSON-RPC error naming the reason and
the path, and a server-originated ``method`` message (a notification such as
``notifications/message``, or a server request) whose ``params`` fail is dropped
with the reason logged to stderr. The value never reaches the client. Screening
is unconditional: a result is screened whether or not the proxy saw the request
that asked for it.
"""

from __future__ import annotations

import contextlib
import json
import re
import subprocess
import sys
import threading
from collections.abc import Iterator, Mapping
from dataclasses import replace
from typing import IO, Any

from . import NAME
from ._core import (
    PAYLOAD_TOO_DEEP,
    PAYLOAD_TOO_LARGE,
    SCHEMA_KEYS,
    Policy,
    Violation,
    _Budget,
    _first,
    _safe_label,
    _trimmed,
    loads,
)

#: JSON-RPC error code returned for a blocked result (implementation-defined range).
BLOCKED_CODE = -32001

#: The JSON-RPC standard code for a message the proxy could not parse.
PARSE_ERROR_CODE = -32700

#: A single JSON-RPC message longer than this is refused rather than parsed.
#: The bounded read below counts characters, so up to four times this many bytes
#: of multibyte text is held before the line is refused -- bounded, not 8 MiB.
MAX_LINE_BYTES = 8 * 1024 * 1024

#: Enough of a line's head to find its id when the body cannot be parsed.
_ID = re.compile(r'"id"\s*:\s*(-?\d+|"[^"]{0,128}")')

#: Field names JSON-RPC and MCP define for the envelope itself. They are the
#: protocol talking, not the tool answering, so the forbidden-name rules do not
#: apply to them -- `progressToken` ends in the default forbidden suffix
#: `token`, and refusing it drops the progress notifications every spec-
#: compliant server sends. The values under these names are screened as usual.
PROTOCOL_KEYS: frozenset[str] = frozenset(
    {
        "jsonrpc",
        "id",
        "method",
        "params",
        "result",
        "error",
        # The five the specification mandates by name. Each has a test: without
        # them `progressToken` and `requestId` end in the forbidden suffix
        # `token`/`id`-shaped names an operator may list, and dropping any of
        # them breaks progress reporting or pagination on a compliant server.
        "progressToken",
        "_meta",
        "cursor",
        "nextCursor",
        "requestId",
    }
)

#: The methods whose payload declares a schema rather than answering with data:
#: the four catalogues, whose entries carry an `inputSchema`/`outputSchema`, and
#: `elicitation/create`, whose `requestedSchema` names the fields the server is
#: asking the user to fill in. A tool may legitimately take a parameter called
#: `phone`, and an elicitation may legitimately ask for one, so the field-name
#: rules step aside under those keys and nowhere else in the message. One
#: declared parameter name can no longer make the whole server undiscoverable,
#: and -- because an elicitation is a *request*, carrying an id the server waits
#: on -- can no longer hang the session either. Every value under a schema, a
#: tool description included, is still screened by every rule.
#:
#: Only the *name* rule steps aside. `denied_field_paths` names a field of the
#: operator's own boundary rather than a schema keyword, so it runs under these
#: keys like anywhere else -- gating it here too switched an operator's policy
#: off for every catalogue and every elicitation, and an elicitation is
#: server-originated, so the untrusted side chose when that happened.
SCHEMA_METHODS: frozenset[str] = frozenset(
    {
        "tools/list",
        "resources/list",
        "resources/templates/list",
        "prompts/list",
        "elicitation/create",
    }
)

#: Envelope member -> the member inside it that carries the tool's payload, or
#: None when the member is the payload itself. A policy's `denied_field_paths`
#: are rooted at the tool payload in `check` and `hook`, so they are rooted there
#: in the proxy too: `patient.mrn` means the same thing on all three surfaces.
#: Screening each payload as its own document is what makes that true; the
#: reported path keeps its `tools/call.result.` prefix either way. A JSON-RPC
#: `error` is protocol as much as the envelope is -- `code` and `message` are
#: the specification's, and `data` is where the tool's own payload sits.
PAYLOAD_MEMBERS: dict[str, str | None] = {"result": None, "params": None, "error": "data"}

#: The note `_core.loads` raises when a server object spells a field twice.
_DUPLICATE_NOTE = "duplicate object key"

#: CPython refuses to convert an integer literal longer than
#: ``sys.get_int_max_str_digits()`` digits and says so in the message it raises.
#: The JSON is valid and the interpreter is the limit, so the client is told a
#: size was exceeded rather than that its server speaks bad JSON.
_INT_LIMIT_NOTE = "int_max_str_digits"

#: How much of an abandoned line is kept -- enough for _ID and nothing more.
_HEAD_CHARS = 512


def _blocked(request_id: Any, violation: Violation, what: str = "result") -> dict[str, Any]:
    """The JSON-RPC error that replaces a message, with the path bounded.

    The path and the detail are built from field names the server chose and grow
    with the depth of the payload, so this error is bounded exactly like the
    CLI's report: an unbounded one is an unbounded server-controlled write into
    the client's transcript.
    """
    item = _trimmed(violation)
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": BLOCKED_CODE,
            "message": f"{NAME} blocked this {what}: {item.code} at {item.path}",
            "data": item.to_dict(),
        },
    }


def _key(request_id: Any) -> str:
    """Ids are matched by their text, so a server that echoes 7 as "7" still matches."""
    return str(request_id)


def _batch(payload: Any) -> list[Any]:
    """A JSON-RPC message is either one object or a batch array of them."""
    return payload if isinstance(payload, list) else [payload]


def _recover_id(line: str, pending: dict[str, str], lock: threading.Lock) -> Any:
    """The client id a line answers, or None, so no call is left hanging.

    The line was never screened, so a scraped id is trusted only when the client
    itself sent it. Otherwise a payload-internal field named "id" -- the first
    "id" in the head of a hostile line -- would cross the boundary inside the
    error that blocked the payload. Every candidate in the head is tried, so a
    nested "id" ahead of the real one costs an answer to nothing.

    The slice comes out of a line that did **not** parse, so parsing it can
    fail too: `_ID`'s string alternative stops at the first inner quote, so an
    id whose value contains an escaped quote yields the fragment `"a\\"`. A
    fragment that will not parse is simply not a candidate -- raising here
    would tear down the whole session over one malformed line.
    """
    for match in _ID.finditer(line[:_HEAD_CHARS]):
        try:
            candidate = json.loads(match.group(1))
        except ValueError:
            continue
        with lock:
            if pending.pop(_key(candidate), None) is not None:
                return candidate
    return None


def _pump_requests(
    source: IO[str], sink: IO[str], pending: dict[str, str], lock: threading.Lock
) -> None:
    """Client -> server. Records the method name each request id is waiting on.

    Nothing here is screened and nothing here is rewritten: the line the client
    wrote is the line the server gets, and this parse only reads the id and the
    method off it. So it stays on ``json.loads`` rather than the duplicate-key
    refusal ``_pump_responses`` uses -- refusing to record an id would leave the
    client waiting on a call the proxy could no longer answer.
    """
    try:
        for line in source:
            if not line.strip():
                continue
            try:
                message = json.loads(line)
            except (ValueError, OverflowError, RecursionError):
                message = None
            for item in _batch(message):
                if isinstance(item, dict) and item.get("id") is not None:
                    method = item.get("method")
                    if isinstance(method, str):
                        with lock:
                            pending[_key(item["id"])] = method
            sink.write(line if line.endswith("\n") else line + "\n")
            sink.flush()
    except (BrokenPipeError, ValueError, OverflowError):
        pass
    finally:
        with contextlib.suppress(BrokenPipeError, ValueError):
            sink.close()


def _what(method: str, violation: Violation) -> str:
    """Name the member the violation is in, for the message the client reads."""
    member = violation.path[len(method) + 1 :].split(".")[0] if violation.path != method else ""
    return {"result": "result", "error": "error payload"}.get(member, "message")


def _parts(message: Any, method: str) -> Iterator[tuple[Any, str]]:
    """Each part of a server message, and the path to report violations in it under.

    A payload -- ``result``, ``params``, and the ``data`` inside an ``error`` --
    is screened as its own document, so the dotted path a policy matches starts
    at the tool's own field names. Without this an operator's ``patient.mrn``
    silently never fired behind the proxy, because the accumulated path was
    ``result.patient.mrn``, while ``check`` and ``hook`` on the same body
    blocked it.

    Every other member is screened where it sits, its own field name included,
    so a member JSON-RPC does not define still carries nothing out.
    """
    if not isinstance(message, Mapping):
        yield message, method
        return
    for key, value in message.items():
        if key not in PAYLOAD_MEMBERS:
            yield {key: value}, method
            continue
        carrier = PAYLOAD_MEMBERS[key]
        if carrier is None or not isinstance(value, Mapping):
            yield value, f"{method}.{key}"
            continue
        for name, item in value.items():
            if name == carrier:
                yield item, f"{method}.{key}.{name}"
            else:
                yield {name: item}, f"{method}.{key}"


def screen_message(
    message: Any,
    policy: Policy,
    method: str,
    request_id: Any = None,
    *,
    schema_keys: frozenset[str] = frozenset(),
    budget: _Budget | None = None,
) -> tuple[Any, Violation | None]:
    """Screen a whole server message: what to forward, and why it was not.

    Returns ``(message, None)`` when it screens clean. When it does not, the
    violation comes back with either a JSON-RPC error to send in its place --
    only when ``request_id`` is an id the client is actually waiting on -- or
    ``None`` to say there is nothing to answer and the caller must drop it,
    because the id in a violating message may itself be a value.

    The violation is returned rather than the payload alone because ``None`` is
    a JSON value: a server message that *is* ``null`` screens clean, and "clean"
    and "drop it" must not be the same answer.

    Every member is screened, not a selected one: an ``error`` beside a clean
    ``result``, a member the JSON-RPC spec does not define, a bare string and a
    batch element that is not an object all carry whatever the server put in
    them.

    The members share one size budget, so the documented caps stay a bound on
    the message rather than one on each member of it. ``budget`` is passed in
    by the caller when several messages arrive on one line -- a JSON-RPC batch
    -- so the caps bound the **line** and not each member of it: without that a
    server could multiply the documented cost by the number of members it put
    in the array, whatever the policy said.
    """
    budget = budget or _Budget()
    violation = None
    for part, where in _parts(message, method):
        if budget.stopped:
            # An earlier message on this line spent the line's budget, so this
            # one was never walked. Refusing it is the only answer that is not
            # a guess -- a stopped budget must never read as "screened clean".
            violation = Violation(
                PAYLOAD_TOO_LARGE,
                method,
                "an earlier message on this line exhausted the size budget, "
                "so this one was not screened",
            )
            break
        violation = _first(part, policy, where=where, schema_keys=schema_keys, budget=budget)
        if violation is not None:
            break
    if violation is None:
        return message, None
    if request_id is None:
        return None, violation
    return _blocked(request_id, violation, _what(method, violation)), violation


def _parse_failure(exc: Exception) -> tuple[dict[str, Any], str]:
    """The JSON-RPC error and the log note for a line the proxy could not parse."""
    if _DUPLICATE_NOTE in str(exc):
        ambiguous = {
            "code": PARSE_ERROR_CODE,
            "message": (
                f"{NAME}: the server sent an object that spells the same field twice, "
                "which cannot be screened unambiguously"
            ),
        }
        return ambiguous, "a duplicate object key"
    if _INT_LIMIT_NOTE in str(exc):
        violation = Violation(
            PAYLOAD_TOO_LARGE,
            "result",
            "the server sent a number with more digits than this interpreter converts",
        )
        return _blocked(None, violation)["error"], "a number too long to convert"
    invalid = {"code": PARSE_ERROR_CODE, "message": f"{NAME}: the server sent invalid JSON"}
    return invalid, "not JSON"


def _emit(sink: IO[str], payload: Any) -> None:
    # allow_nan off: `json.dumps` writes an infinity or a NaN back as the bare
    # token `Infinity`/`NaN`, which no strict client parses -- the proxy, not
    # the server, would be the one producing invalid JSON. _screen_scalar
    # refuses a non-finite number before it gets here, so this is the assertion
    # that it did rather than a path anything reaches.
    sink.write(json.dumps(payload, separators=(",", ":"), allow_nan=False) + "\n")
    sink.flush()


def _refuse(
    sink: IO[str],
    log: IO[str],
    line: str,
    error: dict[str, Any],
    note: str,
    pending: dict[str, str],
    lock: threading.Lock,
) -> None:
    """Answer a line the proxy would not forward, so no call is left hanging.

    The id is scraped out of a line that was never screened, so it is echoed back
    only when the client itself sent it. Otherwise a payload-internal field named
    "id" would cross the boundary inside the error that blocked the payload.
    """
    request_id = _recover_id(line, pending, lock)
    if request_id is None:
        log.write(f"{NAME}: dropped a server message with no pending client id: {note}\n")
        log.flush()
        return
    _emit(sink, {"jsonrpc": "2.0", "id": request_id, "error": error})


def _lines(source: IO[str], limit: int) -> Iterator[tuple[str, bool]]:
    """Yield ``(line, oversized)``, never holding more than ``limit`` characters.

    ``limit`` is a character count, not a byte count: text mode decodes before
    the length is known, so a line of multibyte characters costs up to four
    bytes each. The read is bounded either way, which is the point.

    Bounding the read is the point: ``for line in source`` allocates the whole
    line before anything can refuse it, so a server that sends one 4 GB line
    would take the proxy down with the limit still on. A line past the limit is
    abandoned as it arrives -- only its head is kept, and the rest is read and
    discarded until the next newline.
    """
    while True:
        chunk = source.readline(limit)
        if not chunk:
            return
        if chunk.endswith("\n") or len(chunk) < limit:
            yield chunk, False
            continue
        head = chunk[:_HEAD_CHARS]
        while True:
            rest = source.readline(limit)
            if not rest or rest.endswith("\n") or len(rest) < limit:
                break
        yield head, True


def _claim(
    item: Any, policy: Policy, pending: dict[str, str], lock: threading.Lock
) -> tuple[Any, str, frozenset[str]]:
    """The client id this message may be answered on, the root of its paths, its schema keys.

    Only a message carrying ``result`` or ``error`` answers a call, so a server
    request that reuses a live id (a ``ping``) cannot consume the entry the real
    result needs. An id the client never sent is not an id to answer on.

    A catalogue's method is the one the client asked for and comes out of
    ``pending``; a server-originated request such as ``elicitation/create``
    names its own method on the message, so neither needs the other's lookup.
    """
    if isinstance(item, dict):
        if "result" in item or "error" in item:
            request_id = item.get("id")
            with lock:
                method = pending.pop(_key(request_id), None)
            if method is not None:
                return request_id, _safe_label(method, policy, "<method>"), _schema_keys(method)
            return None, "response", frozenset()
        method = item.get("method")
        if isinstance(method, str):
            return None, _safe_label(method, policy, "<method>"), _schema_keys(method)
    return None, "response", frozenset()


def _schema_keys(method: str) -> frozenset[str]:
    return SCHEMA_KEYS if method in SCHEMA_METHODS else frozenset()


def _pump_responses(
    source: IO[str],
    sink: IO[str],
    policy: Policy,
    pending: dict[str, str],
    lock: threading.Lock,
    log: IO[str],
) -> None:
    """Server -> client. Every result, error and notification payload is screened."""
    # The envelope's own field names are the protocol's, not the tool's answer.
    envelope = replace(policy, exempt_keys=policy.exempt_keys | PROTOCOL_KEYS)
    for line, oversized in _lines(source, MAX_LINE_BYTES):
        if not line.strip():
            continue
        if oversized or len(line.encode("utf-8", "replace")) > MAX_LINE_BYTES:
            violation = Violation(
                PAYLOAD_TOO_LARGE,
                "result",
                f"the server sent a message longer than {MAX_LINE_BYTES} bytes "
                "and it was not screened",
            )
            _refuse(sink, log, line, _blocked(None, violation)["error"], "oversized", pending, lock)
            continue
        try:
            # _core.loads, not json.loads: a server object that spells the same
            # key twice means one thing to this parser and another to a
            # first-wins reader, so it is refused rather than screened -- the
            # same rule `check` and `hook` apply to a document they are handed.
            message = loads(line)
        except RecursionError:
            violation = Violation(
                PAYLOAD_TOO_DEEP, "result", "the server message nests too deep to parse"
            )
            _refuse(
                sink,
                log,
                line,
                _blocked(None, violation)["error"],
                "too deeply nested",
                pending,
                lock,
            )
            continue
        except (ValueError, OverflowError) as exc:
            error, note = _parse_failure(exc)
            _refuse(sink, log, line, error, note, pending, lock)
            continue
        screened = []
        # One budget for the line, not one per batch member: the size caps are
        # documented as a bound on the message, and the server chooses how many
        # members it puts on a line.
        budget = _Budget()
        for item in _batch(message):
            request_id, method, schema = _claim(item, policy, pending, lock)
            answer, violation = screen_message(
                item, envelope, method, request_id, schema_keys=schema, budget=budget
            )
            if violation is not None and answer is None:
                # Nothing the client is waiting on, so there is nothing to answer:
                # the reason goes to the operator's log and the message is dropped.
                # Bounded like the JSON-RPC error, and for the same reason.
                log.write(f"{NAME}: dropped a server message: {_trimmed(violation)}\n")
                log.flush()
                continue
            screened.append(answer)
        if screened:
            _emit(sink, screened if isinstance(message, list) else screened[0])
        elif isinstance(message, list) and not message:
            # An empty batch answers nothing by definition, so there is no id to
            # answer it on -- but "forwarded, answered or logged" is the whole
            # contract, and this is the one shape that would otherwise vanish.
            log.write(f"{NAME}: dropped an empty server batch\n")
            log.flush()


def run_proxy(
    command: list[str],
    policy: Policy,
    *,
    stdin: IO[str] | None = None,
    stdout: IO[str] | None = None,
    stderr: IO[str] | None = None,
) -> int:
    """Run ``command`` as an MCP stdio server behind the screen. Returns its exit code."""
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    # The command is the operator's own MCP server, taken from their client config.
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",  # a non-UTF-8 byte becomes U+FFFD and is screened, not fatal
        bufsize=1,
    )
    assert process.stdin is not None and process.stdout is not None
    pending: dict[str, str] = {}
    lock = threading.Lock()
    requests = threading.Thread(
        target=_pump_requests, args=(stdin, process.stdin, pending, lock), daemon=True
    )
    requests.start()
    try:
        _pump_responses(process.stdout, stdout, policy, pending, lock, stderr)
    finally:
        with contextlib.suppress(OSError):
            process.stdout.close()
        # No path may leave the server running: give it a moment to exit on its
        # own (the usual case), then terminate, then kill.
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    return process.wait()
