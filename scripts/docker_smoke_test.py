#!/usr/bin/env python3
"""End-to-end smoke test for the Dockerized MCP gateway.

Builds the image, runs it with a restricted MCP_SERVERS selection and an
MCP_API_KEY, then drives a real MCP JSON-RPC session over HTTP to confirm:
bearer-token auth is enforced, only the selected tool domains are exposed,
and a real tool call succeeds. The container is always torn down, even on
failure, and its logs are printed for debugging.
"""

import json
import subprocess
import sys
import time
from typing import Any

import httpx

IMAGE = "mcp-ai-assistant-smoke-test"
CONTAINER = "mcp-ai-assistant-smoke-test"
PORT = 8765
API_KEY = "smoke-test-key"
BASE_URL = f"http://localhost:{PORT}/mcp"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def _parse_sse(text: str) -> dict[str, Any]:
    for line in text.splitlines():
        if line.startswith("data: "):
            result: dict[str, Any] = json.loads(line[len("data: ") :])
            return result
    raise ValueError(f"No SSE data line found in response: {text!r}")


def _wait_for_server(timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            httpx.post(BASE_URL, json={}, timeout=2.0)
            return
        except httpx.TransportError:
            time.sleep(1)
    raise TimeoutError("Gateway did not start listening in time")


def main() -> None:
    print("Building image...")
    _run(["docker", "build", "-t", IMAGE, "."])

    print("Starting container...")
    _run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            CONTAINER,
            "-p",
            f"{PORT}:8000",
            "-e",
            "MCP_SERVERS=weather,currency",
            "-e",
            f"MCP_API_KEY={API_KEY}",
            IMAGE,
        ]
    )

    try:
        _wait_for_server()

        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "smoke-test", "version": "1.0"},
            },
        }

        print("Checking unauthenticated request is rejected...")
        resp = httpx.post(BASE_URL, json=init_payload, headers=HEADERS, timeout=10.0)
        assert resp.status_code == 401, f"expected 401 without auth, got {resp.status_code}"

        print("Initializing authenticated session...")
        auth_headers = {**HEADERS, "Authorization": f"Bearer {API_KEY}"}
        resp = httpx.post(BASE_URL, json=init_payload, headers=auth_headers, timeout=10.0)
        assert resp.status_code == 200, f"initialize failed: {resp.status_code} {resp.text}"
        session_headers = {**auth_headers, "mcp-session-id": resp.headers["mcp-session-id"]}

        httpx.post(
            BASE_URL,
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
            headers=session_headers,
            timeout=10.0,
        )

        print("Listing tools...")
        resp = httpx.post(
            BASE_URL,
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            headers=session_headers,
            timeout=10.0,
        )
        names = {t["name"] for t in _parse_sse(resp.text)["result"]["tools"]}
        assert any(n.startswith("weather_") for n in names), f"no weather tools in {names}"
        assert any(n.startswith("currency_") for n in names), f"no currency tools in {names}"
        assert not any(n.startswith("qr_") for n in names), f"unexpected qr tools in {names}"

        print("Calling a tool...")
        resp = httpx.post(
            BASE_URL,
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "currency_convert_currency",
                    "arguments": {"amount": 100, "from_currency": "USD", "to_currency": "RUB"},
                },
            },
            headers=session_headers,
            timeout=15.0,
        )
        result = _parse_sse(resp.text)["result"]
        assert result["isError"] is False, f"tool call failed: {result}"

        print("Smoke test passed.")
    finally:
        print("--- container logs ---")
        subprocess.run(["docker", "logs", CONTAINER])
        subprocess.run(["docker", "rm", "-f", CONTAINER])


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"SMOKE TEST FAILED: {e}", file=sys.stderr)
        sys.exit(1)
