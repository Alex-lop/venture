#!/usr/bin/env python3
"""A 40-line MCP stdio server used by the demo and the proxy tests.

``cohort_summary`` returns an aggregate. ``lookup_customer`` returns a row that
should never have left the tool boundary. Neither the client nor this server
knows about egresswall; the proxy sits between them.
"""

from __future__ import annotations

import json
import sys

RESULTS = {
    "cohort_summary": {"cohort_size": 25, "week_2_abandonment_rate": "0.7200"},
    "lookup_customer": {
        "ticket": "SUP-4417",
        "contact_email": "member-88231@northgate-clinic.test",
    },
}


def handle(message: dict) -> dict | None:
    request_id = message.get("id")
    if request_id is None:
        return None
    method = message.get("method")
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "demo-support-tools", "version": "0.1.0"},
            },
        }
    if method == "tools/call":
        name = (message.get("params") or {}).get("name")
        payload = RESULTS.get(name)
        if payload is None:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "unknown tool"},
            }
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(payload, sort_keys=True)}],
                "isError": False,
            },
        }
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": "Method not found"},
    }


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        response = handle(json.loads(line))
        if response is not None:
            sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
