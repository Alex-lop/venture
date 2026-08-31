"""The stdio proxy, exercised against demo/fake_mcp_server.py."""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from egresswall import Policy
from egresswall._core import SCHEMA_KEYS
from egresswall._proxy import (
    BLOCKED_CODE,
    MAX_LINE_BYTES,
    PARSE_ERROR_CODE,
    SCHEMA_METHODS,
    _lines,
    _schema_keys,
    screen_message,
)

REQUESTS = [
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {}},
    },
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "cohort_summary"}},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "lookup_customer"}},
]


def drive(repo_root: Path, requests: list[dict], policy: str | None = None) -> list[dict]:
    args = [sys.executable, "-m", "egresswall._cli", "proxy"]
    if policy:
        args += ["--policy", policy]
    args += ["--", sys.executable, "demo/fake_mcp_server.py"]
    done = subprocess.run(
        args,
        input="".join(json.dumps(item) + "\n" for item in requests),
        capture_output=True,
        text=True,
        cwd=repo_root,
        timeout=60,
    )
    assert done.returncode == 0, done.stderr
    return [json.loads(line) for line in done.stdout.splitlines() if line.strip()]


def test_the_proxy_passes_clean_traffic_through_unchanged(repo_root: Path) -> None:
    responses = drive(repo_root, REQUESTS)
    assert [item["id"] for item in responses] == [1, 2, 3]
    assert responses[0]["result"]["serverInfo"]["name"] == "demo-support-tools"
    assert json.loads(responses[1]["result"]["content"][0]["text"]) == {
        "cohort_size": 25,
        "week_2_abandonment_rate": "0.7200",
    }


def test_the_proxy_replaces_a_violating_result_with_a_jsonrpc_error(repo_root: Path) -> None:
    blocked = drive(repo_root, REQUESTS)[2]
    assert "result" not in blocked
    assert blocked["error"]["code"] == BLOCKED_CODE
    assert blocked["error"]["message"] == (
        "egresswall blocked this result: RAW_IDENTIFIER at tools/call.result.content[0].text"
    )
    assert blocked["error"]["data"]["code"] == "RAW_IDENTIFIER"
    assert "member-88231@northgate-clinic.test" not in json.dumps(blocked)


def test_the_proxy_survives_a_long_conversation_without_deadlocking(repo_root: Path) -> None:
    requests = [REQUESTS[0]]
    for index in range(200):
        name = "lookup_customer" if index % 2 else "cohort_summary"
        requests.append(
            {"jsonrpc": "2.0", "id": index + 2, "method": "tools/call", "params": {"name": name}}
        )
    responses = drive(repo_root, requests)
    assert len(responses) == 201
    assert sum("error" in item for item in responses) == 100


def test_the_proxy_exits_with_the_server_exit_code(repo_root: Path) -> None:
    done = subprocess.run(
        [
            sys.executable,
            "-m",
            "egresswall._cli",
            "proxy",
            "--",
            sys.executable,
            "-c",
            "import sys; sys.exit(7)",
        ],
        input="",
        capture_output=True,
        text=True,
        cwd=repo_root,
        timeout=60,
    )
    assert done.returncode == 7


class TestScreenMessage:
    """The contract is (what to forward, why it was not): "clean" is not None.

    A server message that *is* ``null`` is a JSON value that screens clean, so
    the payload alone cannot say whether a message was cleared or dropped.
    """

    def test_only_the_result_of_a_screened_method_is_replaced(self) -> None:
        message = {"jsonrpc": "2.0", "id": 1, "result": {"api_key": "x"}}
        blocked, violation = screen_message(message, Policy(), "tools/call", 1)
        assert blocked["error"]["data"]["path"] == "tools/call.result.api_key"
        assert violation.path == "tools/call.result.api_key"

    def test_a_clean_error_is_untouched(self) -> None:
        message = {"jsonrpc": "2.0", "id": 1, "error": {"code": -1, "message": "no"}}
        assert screen_message(message, Policy(), "tools/call") == (message, None)

    def test_a_message_that_is_json_null_screens_clean_and_is_not_a_drop(self) -> None:
        """None as the clean answer and None as "drop it" used to be one value."""
        assert screen_message(None, Policy(), "response") == (None, None)

    def test_a_violating_error_object_is_replaced_whole(self) -> None:
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -1, "message": "no such row", "data": {"ssn": "412-88-7690"}},
        }
        blocked, _ = screen_message(message, Policy(), "tools/call", 1)
        assert blocked["error"]["message"] == (
            "egresswall blocked this error payload: FORBIDDEN_KEY at tools/call.error.data.ssn"
        )
        assert "412-88-7690" not in json.dumps(blocked)

    def test_a_clean_message_with_neither_a_result_nor_an_error_is_untouched(self) -> None:
        message = {"jsonrpc": "2.0", "method": "notifications/message", "params": {}}
        assert screen_message(message, Policy(), "notifications/message") == (message, None)

    def test_a_violating_message_with_no_id_to_answer_on_is_dropped(self) -> None:
        """None means drop: an id the client never sent may itself be a value."""
        message = {"jsonrpc": "2.0", "id": "412-88-7690", "result": {"ok": True}}
        dropped, violation = screen_message(message, Policy(), "result")
        assert dropped is None and violation.code == "RAW_IDENTIFIER"

    def test_a_resources_read_result_is_screened_under_its_own_root(self) -> None:
        message = {"jsonrpc": "2.0", "id": 1, "result": {"contents": [{"text": "412-88-7690"}]}}
        blocked, _ = screen_message(message, Policy(), "resources/read", 1)
        assert blocked["error"]["data"]["path"] == "resources/read.result.contents[0].text"


# --- regressions found by the red team ---------------------------------------

LEAK = '{"content":[{"type":"text","text":"victim@example.com"}]}'


def drive_script(
    tmp_path: Path, body: str, requests: str, timeout: int = 60, policy: str | None = None
):
    """Run the proxy in front of a hand-written server and return the completed process."""
    server = tmp_path / "server.py"
    server.write_text("import json, os, sys, time\n" + body)
    args = [sys.executable, "-m", "egresswall._cli", "proxy"]
    if policy:
        args += ["--policy", policy]
    return subprocess.run(
        [*args, "--", sys.executable, str(server)],
        input=requests,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


CALL = '{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{}}\n'

ECHO = """
for line in sys.stdin:
    if not line.strip():
        continue
    m = json.loads(line)
    {emit}
    sys.stdout.flush()
"""


def blocked_ids(done: subprocess.CompletedProcess) -> list:
    out = [json.loads(line) for line in done.stdout.splitlines() if line.strip()]
    return [item["id"] for item in out if "error" in item]


def test_a_server_message_reusing_the_request_id_does_not_disarm_the_screen(
    tmp_path: Path,
) -> None:
    """JSON-RPC ids are per-direction: a server ping may reuse the id of a live call."""
    emit = (
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":m["id"],"method":"ping"})+"\\n");'
        "sys.stdout.write(json.dumps"
        '({"jsonrpc":"2.0","id":m["id"],"result":' + LEAK + '})+"\\n")'
    )
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    assert "victim@example.com" not in done.stdout
    assert blocked_ids(done) == [7]


def test_a_batched_response_array_is_screened(tmp_path: Path) -> None:
    emit = (
        "sys.stdout.write(json.dumps"
        '([{"jsonrpc":"2.0","id":m[0]["id"] if isinstance(m,list) else m["id"],'
        '"result":' + LEAK + '}])+"\\n")'
    )
    done = drive_script(tmp_path, ECHO.format(emit=emit), "[" + CALL.strip() + "]\n")
    assert "victim@example.com" not in done.stdout
    batch = json.loads(done.stdout.strip())
    assert isinstance(batch, list) and batch[0]["error"]["code"] == BLOCKED_CODE


def test_an_id_echoed_with_a_different_json_type_is_still_screened(tmp_path: Path) -> None:
    emit = (
        "sys.stdout.write(json.dumps"
        '({"jsonrpc":"2.0","id":str(m["id"]),"result":' + LEAK + '})+"\\n")'
    )
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    assert "victim@example.com" not in done.stdout
    assert blocked_ids(done) == ["7"]


def test_a_result_for_a_request_the_proxy_never_saw_is_still_screened(tmp_path: Path) -> None:
    """Screened either way: a clean one is forwarded, a violating one is dropped."""
    body = (
        "sys.stdout.write(json.dumps"
        '({"jsonrpc":"2.0","id":99,"result":' + LEAK + '})+"\\n")\n'
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":98,"result":{"ok":True}})+"\\n")\n'
        "sys.stdout.flush()\n"
    )
    done = drive_script(tmp_path, body, "")
    assert "victim@example.com" not in done.stdout
    assert "victim@example.com" not in done.stderr
    assert [json.loads(line)["id"] for line in done.stdout.splitlines() if line.strip()] == [98]
    assert "dropped a server message" in done.stderr


@pytest.mark.parametrize("token", ["NaN", "1e999", "-1e999"])
def test_a_number_this_interpreter_cannot_re_emit_is_refused_not_forwarded(
    tmp_path: Path, token: str
) -> None:
    """`NaN` and `Infinity` are not JSON: forwarding one makes the proxy the bad speaker.

    `json.loads` accepts both and `json.dumps` writes them back as bare tokens,
    so a message a strict client could read went out as one it cannot. The
    value is refused on the client's own id instead.
    """
    emit = (
        'sys.stdout.write(\'{"jsonrpc":"2.0","id":%s,"result":{"temp":' + token + '}}\' % m["id"]'
        ' + "\\n")'
    )
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    assert done.returncode == 0, done.stderr
    answer = json.loads(done.stdout.strip())
    assert answer["id"] == 7
    assert answer["error"]["data"]["code"] == "PAYLOAD_TOO_LARGE"
    for bad in ("NaN", "Infinity"):
        assert bad not in done.stdout


def test_a_non_utf8_byte_from_the_server_does_not_take_the_proxy_down(tmp_path: Path) -> None:
    body = 'os.write(1, b\'{"jsonrpc":"2.0","id":7,"result":{"t":"\\xff\\xfe"}}\\n\')\n'
    done = drive_script(tmp_path, body, CALL)
    assert done.returncode == 0, done.stderr
    assert json.loads(done.stdout.strip())["id"] == 7


def test_an_oversized_server_message_is_refused_rather_than_dropped(tmp_path: Path) -> None:
    emit = (
        "sys.stdout.write(json.dumps"
        '({"jsonrpc":"2.0","id":m["id"],"result":{"t":"x"*(9*1024*1024)}})+"\\n")'
    )
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL, timeout=120)
    answer = json.loads(done.stdout.strip())
    assert answer["id"] == 7
    assert answer["error"]["data"]["code"] == "PAYLOAD_TOO_LARGE"


def test_a_non_json_server_line_is_answered_rather_than_dropped(tmp_path: Path) -> None:
    emit = 'sys.stdout.write(\'{"jsonrpc":"2.0","id":%s,"result":\' % m["id"] + "not json\\n")'
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    answer = json.loads(done.stdout.strip())
    assert answer["id"] == 7 and answer["error"]["code"] == PARSE_ERROR_CODE


def test_the_proxy_never_leaves_the_server_running(tmp_path: Path) -> None:
    """The server closes stdout but keeps running; the proxy must still reap it."""
    pid_file = tmp_path / "pid"
    body = (
        f'open({str(pid_file)!r}, "w").write(str(os.getpid()))\n'
        'sys.stdout.write(\'{"jsonrpc":"2.0","id":7,"result":{"ok":true}}\\n\')\n'
        "sys.stdout.flush()\n"
        "os.close(1)\n"
        "time.sleep(120)\n"
    )
    done = drive_script(tmp_path, body, CALL, timeout=60)
    assert json.loads(done.stdout.strip())["id"] == 7
    pid = int(pid_file.read_text())
    for _ in range(50):
        try:
            os.kill(pid, 0)
        except OSError:
            return
        time.sleep(0.1)
    raise AssertionError(f"the server process {pid} outlived the proxy")


def test_a_violating_error_from_the_server_never_reaches_the_client(tmp_path: Path) -> None:
    """A server that puts the row in error.data is leaking it just the same."""
    emit = (
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":m["id"],"error":'
        '{"code":-32000,"message":"lookup failed for victim@example.com",'
        '"data":{"ssn":"412-88-7690","api_key":"AKIAIOSFODNN7EXAMPLE"}}})+"\\n")'
    )
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    for value in ("victim@example.com", "412-88-7690", "AKIAIOSFODNN7EXAMPLE"):
        assert value not in done.stdout, value
    answer = json.loads(done.stdout.strip())
    assert answer["id"] == 7
    assert answer["error"]["code"] == BLOCKED_CODE
    assert answer["error"]["data"]["code"] == "RAW_IDENTIFIER"


def test_a_violating_server_notification_is_dropped_and_the_reason_logged(tmp_path: Path) -> None:
    """notifications/message is the MCP logging channel; a logged row is still a row."""
    emit = (
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","method":"notifications/message",'
        '"params":{"level":"info","data":"row: victim@example.com"}})+"\\n");'
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","method":"notifications/progress",'
        '"params":{"progress":1}})+"\\n");'
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":m["id"],"result":{"ok":True}})+"\\n")'
    )
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    assert "victim@example.com" not in done.stdout
    assert "victim@example.com" not in done.stderr
    assert "RAW_IDENTIFIER at notifications/message.params.data" in done.stderr
    out = [json.loads(line) for line in done.stdout.splitlines() if line.strip()]
    assert [item.get("method", item.get("id")) for item in out] == ["notifications/progress", 7]


def test_an_oversized_line_never_echoes_an_id_the_client_did_not_send(tmp_path: Path) -> None:
    """The id is scraped from an unscreened line, so it may itself be a value."""
    emit = (
        'sys.stdout.write(\'{"jsonrpc":"2.0","result":{"customer":{"id":\''
        '\'"member-88231@northgate-clinic.test","pad":"\' + "x"*(9*1024*1024) + \'"}},\''
        ' + \'"id":%s}\' % json.dumps(m["id"]) + "\\n")'
    )
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL, timeout=180)
    assert "member-88231@northgate-clinic.test" not in done.stdout
    assert "member-88231@northgate-clinic.test" not in done.stderr
    # The real id sits past the head, behind 9 MiB of padding, so there is no id
    # to answer on: the line is dropped and the reason goes to the proxy's stderr.
    assert done.stdout.strip() == ""
    assert "no pending client id: oversized" in done.stderr


class TestBoundedReads:
    """The line limit has to bound what is allocated, not only what is screened."""

    def test_a_line_past_the_limit_is_abandoned_as_it_arrives(self) -> None:
        stream = io.StringIO("a" * 10_000 + "\n" + '{"ok":1}\n')
        got = list(_lines(stream, 100))
        assert [len(line) for line, _ in got] == [100, 9]
        assert [oversized for _, oversized in got] == [True, False]

    def test_a_last_line_without_a_newline_is_a_whole_line(self) -> None:
        assert list(_lines(io.StringIO('{"ok":1}'), 100)) == [('{"ok":1}', False)]

    def test_an_empty_stream_ends(self) -> None:
        assert list(_lines(io.StringIO(""), 100)) == []


# --- every shape that reaches the client is screened -------------------------

VICTIM = "victim@example.com"

#: One line each: a bare JSON string, a non-string `method`, a message with no
#: recognised member, `result` and `error` together, `result` beside an extra
#: member, and a batch whose first element is not an object.
LEAKY_SHAPES = [
    json.dumps(VICTIM),
    json.dumps({"jsonrpc": "2.0", "id": 1, "method": None, "params": {"email": VICTIM}}),
    json.dumps({"jsonrpc": "2.0", "id": 1, "payload": {"email": VICTIM}}),
    json.dumps({"jsonrpc": "2.0", "id": 7, "result": {"ok": True}, "error": {"message": VICTIM}}),
    json.dumps({"jsonrpc": "2.0", "id": 7, "result": {"ok": True}, "meta": {"email": VICTIM}}),
    json.dumps([VICTIM, {"jsonrpc": "2.0", "id": 7, "result": {"ok": True}}]),
]


def test_no_server_message_shape_reaches_the_client_unscreened(tmp_path: Path) -> None:
    emit = ";".join(f'sys.stdout.write({shape!r}+"\\n")' for shape in LEAKY_SHAPES)
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    assert VICTIM not in done.stdout, done.stdout
    assert VICTIM not in done.stderr, done.stderr
    # The one message the client is waiting on is answered; the rest are dropped.
    assert blocked_ids(done) == [7]


def test_a_message_carrying_both_a_result_and_an_error_is_screened_in_both(tmp_path: Path) -> None:
    emit = (
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":m["id"],"result":{"ok":True},'
        '"error":{"message":"' + VICTIM + '"}})+"\\n")'
    )
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    assert VICTIM not in done.stdout
    assert blocked_ids(done) == [7]


def test_a_clean_message_the_proxy_does_not_recognise_is_still_forwarded(tmp_path: Path) -> None:
    """Screening everything may not turn into blocking everything."""
    emit = 'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":m["id"],"payload":{"ok":1}})+"\\n")'
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    assert json.loads(done.stdout.strip()) == {"jsonrpc": "2.0", "id": 7, "payload": {"ok": 1}}


def test_a_violating_result_for_an_id_the_client_never_sent_is_dropped_not_answered(
    tmp_path: Path,
) -> None:
    """The id of a message that violates is a server-controlled value like any other."""
    emit = (
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":"' + VICTIM + '",'
        '"result":{"ssn":"412-88-7690"}})+"\\n")'
    )
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    assert VICTIM not in done.stdout
    assert VICTIM not in done.stderr
    assert done.stdout.strip() == ""
    assert "dropped a server message" in done.stderr


def test_a_dropped_notification_never_logs_a_server_field_name(tmp_path: Path) -> None:
    emit = (
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","method":"notifications/message",'
        '"params":{"' + VICTIM + '":{"api_key":"x"}}})+"\\n")'
    )
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    assert VICTIM not in done.stdout
    assert VICTIM not in done.stderr, done.stderr
    assert "<key#0>" in done.stderr


def test_a_server_named_method_never_reaches_the_log_unbounded(tmp_path: Path) -> None:
    emit = (
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","method":"' + VICTIM + '",'
        '"params":{"ssn":"412-88-7690"}})+"\\n")'
    )
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    assert VICTIM not in done.stdout
    assert VICTIM not in done.stderr, done.stderr


# --- fix pass 4: null messages, the protocol envelope, discovery results -----


def test_a_server_message_that_is_json_null_does_not_take_the_proxy_down(tmp_path: Path) -> None:
    """`null` is a JSON value that screens clean; it used to be read as "drop it"."""
    body = (
        "sys.stdin.readline()\n"
        'sys.stdout.write("null\\n")\n'
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":7,'
        '"result":{"ssn":"412-88-7690"}})+"\\n")\n'
        "sys.stdout.flush()\n"
    )
    done = drive_script(tmp_path, body, CALL)
    assert done.returncode == 0, done.stderr
    assert "Traceback" not in done.stderr
    lines = [line for line in done.stdout.splitlines() if line.strip()]
    assert lines[0] == "null"
    assert json.loads(lines[1])["error"]["code"] == BLOCKED_CODE
    assert "412-88-7690" not in done.stdout


def test_a_batch_element_that_is_null_is_forwarded_and_the_rest_still_screened(
    tmp_path: Path,
) -> None:
    body = (
        "sys.stdin.readline()\n"
        'sys.stdout.write(json.dumps([None,{"jsonrpc":"2.0","id":7,'
        '"result":{"ssn":"412-88-7690"}}])+"\\n")\n'
        "sys.stdout.flush()\n"
    )
    done = drive_script(tmp_path, body, CALL)
    assert done.returncode == 0, done.stderr
    batch = json.loads(done.stdout.strip())
    assert batch[0] is None
    assert batch[1]["error"]["code"] == BLOCKED_CODE
    assert "412-88-7690" not in done.stdout


PROGRESS = (
    'sys.stdout.write(json.dumps({"jsonrpc":"2.0","method":"notifications/progress",'
    '"params":{"progressToken":"tok-1","progress":1,"total":2}})+"\\n");'
    'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":m["id"],"result":{"ok":True}})+"\\n")'
)


def test_a_standard_progress_notification_reaches_the_client(tmp_path: Path) -> None:
    """`progressToken` is the protocol's field name, not the tool's data.

    It normalizes to a name ending in `token`, so the default suffix rule used
    to drop every progress notification a spec-compliant server sends.
    """
    done = drive_script(tmp_path, ECHO.format(emit=PROGRESS), CALL)
    out = [json.loads(line) for line in done.stdout.splitlines() if line.strip()]
    assert [item.get("method", item.get("id")) for item in out] == ["notifications/progress", 7]
    assert out[0]["params"]["progressToken"] == "tok-1"
    assert "dropped" not in done.stderr


LIST = '{"jsonrpc":"2.0","id":5,"method":"tools/list"}\n'


def catalogue(description: str, extra: dict | None = None) -> str:
    """A tools/list result whose one tool declares three forbidden parameter names."""
    tool = {
        "name": "lookup_order",
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone": {"type": "string"},
                "rows": {"type": "integer"},
                "nextToken": {"type": "string"},
            },
        },
    }
    return json.dumps({"tools": [tool | (extra or {})], "nextCursor": "page-2"})


def emit_result(result: str) -> str:
    """One line of server source answering the pending id with ``result``."""
    return (
        f"out = {{'jsonrpc': '2.0', 'id': m['id'], 'result': json.loads({result!r})}}; "
        "sys.stdout.write(json.dumps(out) + '\\n')"
    )


def test_a_tool_schema_naming_a_forbidden_field_does_not_kill_discovery(tmp_path: Path) -> None:
    """A parameter called `phone` is a declaration; refusing it disables the server."""
    emit = emit_result(catalogue("Look up an order"))
    done = drive_script(tmp_path, ECHO.format(emit=emit), LIST)
    answer = json.loads(done.stdout.strip())
    assert answer["id"] == 5, done.stderr
    schema = answer["result"]["tools"][0]["inputSchema"]["properties"]
    assert sorted(schema) == ["nextToken", "phone", "rows"]


def test_a_discovery_result_is_still_screened_for_the_values_it_carries(tmp_path: Path) -> None:
    """Only the schema's parameter names step aside for a catalogue; nothing else does."""
    emit = emit_result(catalogue(f"Ask {VICTIM}"))
    done = drive_script(tmp_path, ECHO.format(emit=emit), LIST)
    assert VICTIM not in done.stdout
    answer = json.loads(done.stdout.strip())
    assert answer["id"] == 5
    assert answer["error"]["data"]["code"] == "RAW_IDENTIFIER"


def test_a_forbidden_field_name_outside_the_schema_still_refuses_a_catalogue(
    tmp_path: Path,
) -> None:
    """The exemption is the schema subtree, not the whole discovery result."""
    emit = emit_result(catalogue("Look up an order", {"session_id": "s-1"}))
    done = drive_script(tmp_path, ECHO.format(emit=emit), LIST)
    answer = json.loads(done.stdout.strip())
    assert answer["error"]["data"]["code"] == "FORBIDDEN_KEY"
    assert answer["error"]["data"]["path"].endswith("tools[0].session_id")


def test_a_forbidden_name_in_a_schema_is_only_exempt_for_a_discovery_result(
    tmp_path: Path,
) -> None:
    """The same shape returned by tools/call is data, and is refused."""
    emit = emit_result(catalogue("Look up an order"))
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    answer = json.loads(done.stdout.strip())
    assert answer["error"]["data"]["code"] == "FORBIDDEN_KEY"


#: The five field names the JSON-RPC and MCP specifications mandate that a
#: forbidden-name rule would otherwise refuse. One test each: without the
#: allow-list, `progressToken` ends in the default suffix `token` and every one
#: of them can be listed by an operator writing a policy for their own data.
SPEC_FIELDS = ["progressToken", "_meta", "cursor", "nextCursor", "requestId"]


@pytest.mark.parametrize("field", SPEC_FIELDS)
def test_a_protocol_field_name_never_makes_the_proxy_refuse_a_message(
    tmp_path: Path, field: str
) -> None:
    """A policy that forbids the protocol's own name may not disable the protocol."""
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"forbidden_keys": SPEC_FIELDS, "detectors": []}))
    assert Policy.from_file(policy).forbids_key(field), field
    emit = emit_result(json.dumps({field: "page-2", "ok": True}))
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL, policy=str(policy))
    answer = json.loads(done.stdout.strip())
    assert answer["result"][field] == "page-2", done.stderr
    assert "dropped" not in done.stderr


@pytest.mark.parametrize("field", SPEC_FIELDS)
def test_a_protocol_field_name_exempts_the_name_and_never_the_value(
    tmp_path: Path, field: str
) -> None:
    """Pagination is protocol; an email address inside a cursor is still a value."""
    emit = emit_result(json.dumps({field: f"page-{VICTIM}"}))
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    answer = json.loads(done.stdout.strip())
    assert VICTIM not in done.stdout
    assert answer["error"]["data"]["code"] == "RAW_IDENTIFIER", done.stderr


BIG_INT = (
    'sys.stdout.write(\'{"jsonrpc":"2.0","id":7,"result":{"n":\' + "9" * 100000 + \'}}\' + "\\n")'
)


def test_a_number_too_long_to_convert_is_named_as_a_size_not_as_bad_json(
    tmp_path: Path,
) -> None:
    """The JSON is valid; this interpreter's digit limit is what refused it."""
    done = drive_script(tmp_path, ECHO.format(emit=BIG_INT), CALL)
    answer = json.loads(done.stdout.strip())
    assert answer["id"] == 7, done.stderr
    assert answer["error"]["data"]["code"] == "PAYLOAD_TOO_LARGE"
    assert "more digits than this interpreter converts" in answer["error"]["data"]["detail"]
    assert "invalid JSON" not in done.stdout


def test_a_line_that_is_not_json_is_still_named_as_bad_json(tmp_path: Path) -> None:
    """The sharper message for one cause must not blur the message for the others."""
    emit = 'sys.stdout.write(\'{"id": 7, not json\' + "\\n")'
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    answer = json.loads(done.stdout.strip())
    assert answer["error"]["code"] == PARSE_ERROR_CODE
    assert "the server sent invalid JSON" in answer["error"]["message"]


# --- fix pass 5: one policy means one thing on all three surfaces -------------

MRN = '{"patient":{"mrn":"NG-88231"}}'


def test_the_shipped_demo_policy_gives_the_same_verdict_on_all_three_surfaces(
    repo_root: Path, tmp_path: Path
) -> None:
    """A dotted `denied_field_paths` entry used to be a silent no-op in the proxy.

    `check` and `hook` root the dotted path at the tool payload; the proxy
    screened the whole JSON-RPC envelope, so the accumulated path gained a
    `result.` prefix and never equalled the operator's entry. The same policy
    and the same body gave opposite verdicts, and the one that let the value
    through was the only surface that stops it before its reader sees it.
    """
    policy = str(repo_root / "demo" / "policy.json")
    body = tmp_path / "body.json"
    body.write_text(MRN, encoding="utf-8")

    checked = subprocess.run(
        [sys.executable, "-m", "egresswall._cli", "check", str(body), "--policy", policy],
        capture_output=True,
        text=True,
        cwd=repo_root,
        timeout=60,
    )
    assert checked.returncode == 1
    assert "DENIED_FIELD_PATH at response.patient.mrn" in checked.stdout

    hooked = subprocess.run(
        [sys.executable, "-m", "egresswall._cli", "hook", "--policy", policy],
        input=json.dumps({"tool_name": "t", "tool_response": json.loads(MRN)}),
        capture_output=True,
        text=True,
        cwd=repo_root,
        timeout=60,
    )
    assert hooked.returncode == 2
    assert "DENIED_FIELD_PATH at tool_response.patient.mrn" in hooked.stderr

    proxied = drive_script(tmp_path, ECHO.format(emit=emit_result(MRN)), CALL, policy=policy)
    answer = json.loads(proxied.stdout.strip())
    assert "NG-88231" not in proxied.stdout
    assert answer["error"]["data"]["code"] == "DENIED_FIELD_PATH"
    assert answer["error"]["data"]["path"] == "tools/call.result.patient.mrn"
    assert answer["error"]["data"]["detail"] == "denied field 'patient.mrn' carries a value"


@pytest.mark.parametrize(
    ("emit", "path"),
    [
        (
            'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":m["id"],"result":'
            + MRN
            + '})+"\\n")',
            "tools/call.result.patient.mrn",
        ),
        (
            'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":m["id"],"error":'
            '{"code":-1,"message":"no","data":' + MRN + '}})+"\\n")',
            "tools/call.error.data.patient.mrn",
        ),
    ],
)
def test_a_dotted_denied_path_fires_in_a_result_and_in_an_error(
    tmp_path: Path, emit: str, path: str
) -> None:
    """The dotted root is the payload member, whichever member carries it."""
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"denied_field_paths": ["patient.mrn"], "detectors": []}))
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL, policy=str(policy))
    answer = json.loads(done.stdout.strip())
    assert "NG-88231" not in done.stdout
    assert answer["error"]["data"]["code"] == "DENIED_FIELD_PATH"
    assert answer["error"]["data"]["path"] == path


def test_a_dotted_denied_path_fires_in_a_notifications_params(tmp_path: Path) -> None:
    """A notification's `params` is a payload member too, and roots the path the same way."""
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"denied_field_paths": ["patient.mrn"], "detectors": []}))
    emit = (
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","method":"notifications/message",'
        '"params":' + MRN + '})+"\\n")'
    )
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL, policy=str(policy))
    assert "NG-88231" not in done.stdout
    assert "NG-88231" not in done.stderr
    assert "DENIED_FIELD_PATH at notifications/message.params.patient.mrn" in done.stderr


def test_an_envelope_field_name_the_spec_does_not_define_is_still_screened(tmp_path: Path) -> None:
    """Screening the members one at a time may not stop screening the envelope."""
    emit = (
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":m["id"],"result":{"ok":1},'
        '"api_key":"x"})+"\\n")'
    )
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    answer = json.loads(done.stdout.strip())
    assert answer["error"]["data"]["code"] == "FORBIDDEN_KEY"
    assert answer["error"]["data"]["path"] == "tools/call.api_key"


# --- fix pass 5: what the README promises of every surface --------------------


def test_a_duplicate_keyed_server_line_is_refused_rather_than_screened(tmp_path: Path) -> None:
    """Last-wins parsing let a server hide a value behind a second, clean spelling."""
    emit = (
        'sys.stdout.write(\'{"jsonrpc":"2.0","id":%s,"result":'
        '{"content":"victim@example.com","content":"all clean"}}\' % json.dumps(m["id"]) + "\\n")'
    )
    done = drive_script(tmp_path, ECHO.format(emit=emit), CALL)
    assert VICTIM not in done.stdout
    assert "all clean" not in done.stdout
    answer = json.loads(done.stdout.strip())
    assert answer["id"] == 7
    assert answer["error"]["code"] == PARSE_ERROR_CODE
    assert "spells the same field twice" in answer["error"]["message"]


def test_the_proxy_error_is_bounded_however_deep_the_server_nests_the_violation(
    tmp_path: Path,
) -> None:
    """The path is a run of field names the server chose, so it is trimmed like a report."""
    from egresswall._core import MAX_VIOLATION_CHARS

    body = (
        "sys.stdin.readline()\n"
        'node = {"api_key": "x"}\n'
        "for i in range(28):\n"
        '    node = {("k%02d" % i) + "n"*56: node}\n'
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":7,"result":node})+"\\n")\n'
        "sys.stdout.flush()\n"
    )
    done = drive_script(tmp_path, body, CALL)
    answer = json.loads(done.stdout.strip())
    error = answer["error"]
    assert error["data"]["code"] == "FORBIDDEN_KEY"
    assert error["data"]["path"].endswith("...")
    assert len(error["message"]) <= MAX_VIOLATION_CHARS
    assert len(error["data"]["path"]) + len(error["data"]["detail"]) <= MAX_VIOLATION_CHARS


def test_an_empty_server_batch_is_logged_rather_than_swallowed(tmp_path: Path) -> None:
    """Forwarded, answered or logged was the contract; this shape was none of them."""
    body = (
        "sys.stdin.readline()\n"
        'sys.stdout.write("[]\\n")\n'
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":7,"result":{"ok":1}})+"\\n")\n'
        "sys.stdout.flush()\n"
    )
    done = drive_script(tmp_path, body, CALL)
    assert json.loads(done.stdout.strip())["id"] == 7
    assert "dropped an empty server batch" in done.stderr


# --- fix pass 5: every message the MCP specification defines ------------------

#: One line each of what a spec-compliant server sends, with the default policy
#: in front of it. `elicitation/create` is the one that was dropped: its
#: `requestedSchema` names the fields the user is being asked for, and `phone`,
#: `user_id` and anything ending in `token` are all ordinary things to ask for
#: and all in the default forbidden list. It is a *request*, so dropping it hung
#: the server on an answer the client was never told to send.
SPEC_MESSAGES = {
    "initialize result": {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "serverInfo": {"name": "s"},
        },
    },
    "elicitation/create": {
        "jsonrpc": "2.0",
        "id": 50,
        "method": "elicitation/create",
        "params": {
            "message": "How should we reach you?",
            "requestedSchema": {
                "type": "object",
                "properties": {
                    "phone": {"type": "string"},
                    "user_id": {"type": "string"},
                    "apiToken": {"type": "string"},
                },
            },
        },
    },
    "sampling/createMessage": {
        "jsonrpc": "2.0",
        "id": 51,
        "method": "sampling/createMessage",
        "params": {"messages": [{"role": "user", "content": {"type": "text", "text": "hi"}}]},
    },
    "roots/list": {"jsonrpc": "2.0", "id": 52, "method": "roots/list"},
    "ping": {"jsonrpc": "2.0", "id": 53, "method": "ping"},
    "notifications/message": {
        "jsonrpc": "2.0",
        "method": "notifications/message",
        "params": {"level": "info", "logger": "s", "data": "started"},
    },
    "notifications/progress": {
        "jsonrpc": "2.0",
        "method": "notifications/progress",
        "params": {"progressToken": "tok-1", "progress": 1, "total": 2},
    },
    "notifications/cancelled": {
        "jsonrpc": "2.0",
        "method": "notifications/cancelled",
        "params": {"requestId": 4, "reason": "user cancelled"},
    },
    "notifications/resources/updated": {
        "jsonrpc": "2.0",
        "method": "notifications/resources/updated",
        "params": {"uri": "file:///a.txt"},
    },
    # fix pass 6: the three list_changed notifications. The coverage sentence in
    # the README claimed them and the suite did not drive them.
    "notifications/tools/list_changed": {
        "jsonrpc": "2.0",
        "method": "notifications/tools/list_changed",
    },
    "notifications/resources/list_changed": {
        "jsonrpc": "2.0",
        "method": "notifications/resources/list_changed",
    },
    "notifications/prompts/list_changed": {
        "jsonrpc": "2.0",
        "method": "notifications/prompts/list_changed",
    },
}

#: Every message a *server* may originate under the 2025-06-18 specification:
#: four requests and seven notifications. `initialize result` is in
#: SPEC_MESSAGES as well, and is a response rather than either of those, so it
#: is not listed here. The README's coverage sentence is this set; the test
#: below is what makes the sentence true rather than aspirational.
SERVER_TO_CLIENT = frozenset(
    {
        "elicitation/create",
        "sampling/createMessage",
        "roots/list",
        "ping",
        "notifications/message",
        "notifications/progress",
        "notifications/cancelled",
        "notifications/resources/updated",
        "notifications/tools/list_changed",
        "notifications/resources/list_changed",
        "notifications/prompts/list_changed",
    }
)


def test_the_suite_drives_every_server_to_client_message_the_spec_defines() -> None:
    driven = {item["method"] for item in SPEC_MESSAGES.values() if "method" in item}
    assert driven == SERVER_TO_CLIENT, driven ^ SERVER_TO_CLIENT


@pytest.mark.parametrize("name", sorted(SPEC_MESSAGES))
def test_a_message_the_specification_defines_is_forwarded_under_the_default_policy(
    tmp_path: Path, name: str
) -> None:
    """A screen that drops the protocol is a screen nobody can leave switched on."""
    message = SPEC_MESSAGES[name]
    body = (
        "sys.stdin.readline()\n"
        f"sys.stdout.write(json.dumps({message!r})+'\\n')\n"
        "sys.stdout.flush()\n"
    )
    done = drive_script(tmp_path, body, CALL)
    assert done.stdout.strip(), f"{name} was dropped: {done.stderr}"
    assert json.loads(done.stdout.strip()) == message, done.stderr
    assert "dropped" not in done.stderr, done.stderr


def test_a_value_under_a_requested_schema_is_still_screened(tmp_path: Path) -> None:
    """The schema exemption is the declared names, never what is declared about them."""
    message = json.loads(json.dumps(SPEC_MESSAGES["elicitation/create"]))
    message["params"]["requestedSchema"]["properties"]["phone"]["description"] = f"ask {VICTIM}"
    body = (
        "sys.stdin.readline()\n"
        f"sys.stdout.write(json.dumps({message!r})+'\\n')\n"
        "sys.stdout.flush()\n"
    )
    done = drive_script(tmp_path, body, CALL)
    assert VICTIM not in done.stdout
    assert VICTIM not in done.stderr
    assert done.stdout.strip() == ""
    assert "RAW_IDENTIFIER" in done.stderr


# --- fix pass 6: what a hostile line may not do to the session ----------------

#: An id whose value carries an escaped quote. `_ID`'s string alternative stops
#: at the first inner quote, so what it cuts out of the head is the fragment
#: `"a\"` -- valid for the regex, not valid JSON.
ESCAPED_QUOTE_ID = r'"id":"a\"b"'


def test_an_unparseable_line_whose_head_holds_an_escaped_quote_id_is_dropped(
    tmp_path: Path,
) -> None:
    """_recover_id parsed a slice of a line that never parsed, and raised out of the proxy.

    The whole session went down on one malformed line: exit 2, and every call
    the client had in flight was lost. A fragment that will not parse is simply
    not a candidate id.
    """
    line = "{" + ESCAPED_QUOTE_ID + ",}"
    body = (
        "sys.stdin.readline()\n"
        f"sys.stdout.write({line!r} + '\\n')\n"
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":7,"result":{"ok":1}})+"\\n")\n'
        "sys.stdout.flush()\n"
    )
    done = drive_script(tmp_path, body, CALL)
    assert done.returncode == 0, done.stderr
    assert "Traceback" not in done.stderr
    assert "no pending client id" in done.stderr
    # The client's real call is still answered.
    assert json.loads(done.stdout.strip())["id"] == 7


def test_an_oversized_line_whose_head_holds_an_escaped_quote_id_is_dropped(
    tmp_path: Path,
) -> None:
    """The same crash arrived by the >8 MiB path, where only the head is kept."""
    head = "{" + ESCAPED_QUOTE_ID + ',"pad":"'
    body = (
        "sys.stdin.readline()\n"
        f"sys.stdout.write({head!r} + 'x' * (9 * 1024 * 1024) + '\"}}\\n')\n"
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":7,"result":{"ok":1}})+"\\n")\n'
        "sys.stdout.flush()\n"
    )
    done = drive_script(tmp_path, body, CALL)
    assert done.returncode == 0, done.stderr
    assert "Traceback" not in done.stderr
    assert "oversized" in done.stderr
    assert json.loads(done.stdout.strip())["id"] == 7


def test_a_batch_shares_one_size_budget_with_the_line_it_arrived_on(tmp_path: Path) -> None:
    """The budget was per member, so a server could multiply the documented cap.

    `max_nodes` is a bound on the message; a batch is one message on one line,
    so 40 members of 9 000 nodes each is 360 000 nodes and the line is refused
    part way through. Every member after the budget stops is refused too -- a
    stopped budget must never read as "screened clean".
    """
    members = (
        "msg = [{'jsonrpc':'2.0','method':'notifications/message',"
        "'params':{'level':'info','data':[1]*9000}} for _ in range(40)]\n"
        "msg[0] = {'jsonrpc':'2.0','id':7,'result':{'ok':1}}\n"
    )
    body = (
        "sys.stdin.readline()\n"
        + members
        + "sys.stdout.write(json.dumps(msg, separators=(',',':'))+'\\n')\n"
        "sys.stdout.flush()\n"
    )
    done = drive_script(tmp_path, body, CALL, timeout=120)
    assert done.returncode == 0, done.stderr
    assert "PAYLOAD_TOO_LARGE" in done.stderr
    forwarded = json.loads(done.stdout.strip())
    assert forwarded[0]["id"] == 7
    assert len(forwarded) < 40, "members past the line's budget were forwarded unscreened"


# --- fix pass 6: serialized JSON inside an MCP content[].text ----------------


def call_result(payload: object) -> str:
    """One line of exactly what an MCP server answers a `tools/call` with."""
    message = {
        "jsonrpc": "2.0",
        "id": 7,
        "result": {
            "content": [{"type": "text", "text": json.dumps(payload, sort_keys=True)}],
            "isError": False,
        },
    }
    return json.dumps(message, separators=(",", ":"))


@pytest.mark.parametrize(
    ("payload", "code"),
    [
        ({"rows": [{"ticket": "SUP-4417"}]}, "FORBIDDEN_KEY"),
        ({"patient": {"mrn": "NG-88231"}}, "DENIED_FIELD_PATH"),
    ],
)
def test_a_policy_name_rule_fires_inside_a_serialized_tool_payload(
    tmp_path: Path, repo_root: Path, payload: dict, code: str
) -> None:
    """MCP puts the tool's whole payload in `content[].text` as serialized JSON.

    To the screen that was one string, so `forbidden_keys` and
    `denied_field_paths` -- the two rules an operator actually configures --
    silently never fired behind the proxy. Neither payload here trips a value
    detector: only the name rules can catch them.
    """
    line = call_result(payload)
    body = f"sys.stdin.readline()\nsys.stdout.write({line!r} + '\\n')\nsys.stdout.flush()\n"
    done = drive_script(tmp_path, body, CALL, policy=str(repo_root / "demo/policy.json"))
    assert done.returncode == 0, done.stderr
    answer = json.loads(done.stdout.strip())
    assert answer["error"]["data"]["code"] == code, answer
    assert "\u2192" in answer["error"]["data"]["path"], answer["error"]["data"]["path"]
    assert answer["error"]["data"]["path"].startswith("tools/call.result.content[0].text\u2192")


def test_a_benign_serialized_tool_payload_still_reaches_the_client(
    tmp_path: Path, repo_root: Path
) -> None:
    """The rules run on the parsed document; a document that passes is forwarded whole."""
    line = call_result({"cohort_size": 25, "week_2_abandonment_rate": "0.7200"})
    body = f"sys.stdin.readline()\nsys.stdout.write({line!r} + '\\n')\nsys.stdout.flush()\n"
    done = drive_script(tmp_path, body, CALL, policy=str(repo_root / "demo/policy.json"))
    assert done.returncode == 0, done.stderr
    assert json.loads(done.stdout.strip()) == json.loads(line)
    assert done.stderr == ""


def test_the_servers_own_stderr_reaches_the_operator_unscreened(tmp_path: Path) -> None:
    """A limit the README states rather than one it leaves for a reader to find.

    The proxy screens stdout, which is where JSON-RPC lives. A tool that
    debug-logs its own payload writes it on stderr, which goes straight to the
    operator's MCP server log beside egresswall's own value-free lines.
    """
    body = (
        "sys.stdin.readline()\n"
        f"sys.stderr.write('DEBUG row=' + {VICTIM!r} + '\\n'); sys.stderr.flush()\n"
        'sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":7,"result":'
        f'{{"contact": {VICTIM!r}}}}})+"\\n")\n'
        "sys.stdout.flush()\n"
    )
    done = drive_script(tmp_path, body, CALL)
    assert done.returncode == 0, done.stderr
    assert VICTIM in done.stderr, "the documented limit"
    # The screen itself still holds: the value never reaches the client.
    assert VICTIM not in done.stdout
    assert json.loads(done.stdout.strip())["error"]["data"]["code"] == "RAW_IDENTIFIER"


# --- fix pass 7: the bound the CHANGELOG states, measured where it is claimed --

#: The largest server line the proxy accepts: `_lines` reads at most
#: MAX_LINE_BYTES characters and treats a chunk that fills the read without a
#: newline as oversized, so a line of exactly this many characters *including*
#: its newline is the last one that is screened rather than refused unread.
LARGEST_ACCEPTED = MAX_LINE_BYTES

#: The bound the CHANGELOG claims for it. It is four to five times the measured
#: time on the machines this suite runs on; it is a bound, not a benchmark.
PROXY_SECONDS = 2.0


def test_the_largest_message_the_proxy_accepts_is_screened_in_under_two_seconds(
    tmp_path: Path,
) -> None:
    """The CHANGELOG says the documented bound is measured; this is the measurement.

    The shape is the expensive one: many small strings, so the walk really
    screens text up to `max_total_length` before the budget stops it, rather
    than one huge string that is refused unscanned. The line is sized to exactly
    the largest the proxy will read, and the assertion that it comes back with
    the *budget's* reason rather than the oversized-line reason is what proves
    it was accepted and screened rather than abandoned as it arrived.
    """
    body = (
        "sys.stdin.readline()\n"
        f"n = {LARGEST_ACCEPTED}\n"
        'rows = {"r%05d" % i: "n" * 4000 for i in range(2000)}\n'
        'rows["pad"] = ""\n'
        'msg = {"jsonrpc": "2.0", "id": 7, "result": rows}\n'
        'line = json.dumps(msg, separators=(",", ":"))\n'
        'rows["pad"] = "p" * (n - len(line) - 1)\n'
        'line = json.dumps(msg, separators=(",", ":"))\n'
        "assert len(line) + 1 == n, len(line)\n"
        'sys.stdout.write(line + "\\n")\n'
        "sys.stdout.flush()\n"
    )
    started = time.monotonic()
    done = drive_script(tmp_path, body, CALL, timeout=120)
    elapsed = time.monotonic() - started
    assert done.returncode == 0, done.stderr
    answer = json.loads(done.stdout.strip())
    assert answer["id"] == 7
    assert answer["error"]["data"]["code"] == "PAYLOAD_TOO_LARGE"
    assert "max_total_length" in answer["error"]["data"]["detail"], answer["error"]["data"]
    assert elapsed < PROXY_SECONDS, f"{elapsed:.2f}s"


# --- fix pass 8: the same document behind one invisible character ------------


@pytest.mark.parametrize("prefix", ["\ufeff", "\u200b", "\u00ad", "\u0301"])
def test_one_invisible_character_cannot_turn_the_name_rules_off_behind_the_proxy(
    tmp_path: Path, repo_root: Path, prefix: str
) -> None:
    """The red team's repro, end to end, against the package's own demo policy.

    The candidate test was `\\s*[{\\[]`, which no invisible code point but
    whitespace matched, so a server prefixing its serialized payload with one
    U+FEFF got the whole of it forwarded: rc 0, empty stderr, nothing reported.
    """
    message = {
        "jsonrpc": "2.0",
        "id": 7,
        "result": {
            "content": [
                {"type": "text", "text": prefix + '{"patient":{"mrn":"NG-88231"},"rows":[]}'}
            ]
        },
    }
    line = json.dumps(message, separators=(",", ":"))
    body = f"sys.stdin.readline()\nsys.stdout.write({line!r} + '\\n')\nsys.stdout.flush()\n"
    done = drive_script(tmp_path, body, CALL, policy=str(repo_root / "demo/policy.json"))
    assert done.returncode == 0, done.stderr
    answer = json.loads(done.stdout.strip())
    assert "NG-88231" not in done.stdout
    assert answer["error"]["data"]["code"] == "DENIED_FIELD_PATH", answer
    assert answer["error"]["data"]["path"] == "tools/call.result.content[0].text\u2192patient.mrn"


# --- fix pass 9: a denied path inside a declared schema -----------------------
#
# The round-7 fix exempted a schema's declared *names* from the field-name rule
# and gated `denied_field_paths` behind the same branch, so an operator's dotted
# entry was silently off inside every catalogue and every elicitation -- and an
# elicitation is server-originated, so the untrusted side chose the exemption
# for a subtree of its own naming. Only the name rule steps aside now.

#: `denied_field_paths` an operator would actually write for a clinical tool:
#: the bare field name, and the same field under its parent.
DENIED_PATHS = {"denied_field_paths": ["mrn", "requestedSchema.patient.mrn"]}


def denied_paths_policy(tmp_path: Path) -> str:
    path = tmp_path / "denied-paths.json"
    path.write_text(json.dumps(DENIED_PATHS), encoding="utf-8")
    return str(path)


def schema_catalogue(schema: dict) -> str:
    """A tools/list result whose one tool declares ``schema`` as its input."""
    return json.dumps({"tools": [{"name": "lookup_order", "inputSchema": schema}]})


def test_a_denied_field_path_inside_a_tool_schema_still_refuses_the_catalogue(
    tmp_path: Path,
) -> None:
    """The red team's repro: `{"denied_field_paths": ["mrn"]}` and a catalogue."""
    emit = emit_result(schema_catalogue({"mrn": "NG-88231"}))
    done = drive_script(
        tmp_path, ECHO.format(emit=emit), LIST, policy=denied_paths_policy(tmp_path)
    )
    assert "NG-88231" not in done.stdout
    answer = json.loads(done.stdout.strip())
    assert answer["id"] == 5, done.stderr
    assert answer["error"]["data"]["code"] == "DENIED_FIELD_PATH", answer
    assert answer["error"]["data"]["path"] == "tools/list.result.tools[0].inputSchema.mrn"


def test_a_denied_field_path_inside_a_requested_schema_still_refuses_an_elicitation(
    tmp_path: Path,
) -> None:
    """Server-originated, so the untrusted side names the exempt method itself.

    An elicitation carries an id the server waits on, so a violating one is
    dropped rather than answered -- the reason goes to the proxy's stderr with
    no value in it.
    """
    message = {
        "jsonrpc": "2.0",
        "id": 50,
        "method": "elicitation/create",
        "params": {
            "message": "How should we reach you?",
            "requestedSchema": {"patient": {"mrn": "NG-88231"}},
        },
    }
    body = (
        "sys.stdin.readline()\n"
        f"sys.stdout.write(json.dumps({message!r})+'\\n')\n"
        "sys.stdout.flush()\n"
    )
    done = drive_script(tmp_path, body, CALL, policy=denied_paths_policy(tmp_path))
    assert done.stdout.strip() == ""
    assert "NG-88231" not in done.stderr
    assert "DENIED_FIELD_PATH" in done.stderr, done.stderr


def test_a_forbidden_name_in_a_schema_is_still_exempt_under_the_same_policy(
    tmp_path: Path,
) -> None:
    """The half of the exemption that stays: a parameter called `phone` is a
    declaration, and refusing the catalogue takes the whole server away."""
    emit = emit_result(catalogue("Look up an order"))
    done = drive_script(
        tmp_path, ECHO.format(emit=emit), LIST, policy=denied_paths_policy(tmp_path)
    )
    answer = json.loads(done.stdout.strip())
    assert "error" not in answer, answer
    schema = answer["result"]["tools"][0]["inputSchema"]["properties"]
    assert sorted(schema) == ["nextToken", "phone", "rows"]


@pytest.mark.parametrize("method", sorted(SCHEMA_METHODS))
def test_the_path_rule_runs_under_a_schema_key_in_every_exempt_method(method: str) -> None:
    """One assertion per method the exemption covers, without a subprocess.

    A forbidden *name* under the same key in the same message is still exempt,
    so this pins the split rather than just the half that was broken.
    """
    policy = Policy(denied_field_paths=frozenset({"mrn"}))
    for key in SCHEMA_KEYS:
        message = {"jsonrpc": "2.0", "id": 9, "result": {key: {"mrn": "NG-88231", "api_key": "k"}}}
        _sent, violation = screen_message(
            message, policy, method, 9, schema_keys=_schema_keys(method)
        )
        assert violation is not None, (method, key)
        assert violation.code == "DENIED_FIELD_PATH", (method, key, violation)


def test_a_method_outside_the_exempt_list_never_had_the_exemption(tmp_path: Path) -> None:
    """The control: `tools/call` returning the same shape is data, and both
    rules run over it."""
    policy = Policy(denied_field_paths=frozenset({"mrn"}))
    message = {"jsonrpc": "2.0", "id": 9, "result": {"inputSchema": {"api_key": "k"}}}
    _sent, violation = screen_message(message, policy, "tools/call", 9, schema_keys=frozenset())
    assert violation is not None and violation.code == "FORBIDDEN_KEY"
