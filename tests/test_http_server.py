"""Acceptance checks for the separately hosted Streamable HTTP transport."""

from __future__ import annotations

import asyncio
import json
import os
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import httpx
import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from ai_governance_assistant.http_server import create_http_app

FIXTURES = Path(__file__).parent / "fixtures" / "acceptance_scenarios.json"
API_KEY = "synthetic-ci-api-key"


def test_http_server_fails_closed_without_an_api_key():
    with pytest.raises(ValueError, match="AI_GOVERNANCE_API_KEY"):
        create_http_app("")


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@contextmanager
def _http_server():
    port = _free_port()
    environment = {
        **os.environ,
        "AI_GOVERNANCE_API_KEY": API_KEY,
        "AI_GOVERNANCE_HOST": "127.0.0.1",
        "AI_GOVERNANCE_PORT": str(port),
    }
    process = subprocess.Popen(
        [sys.executable, "-m", "ai_governance_assistant.http_server"],
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        for _ in range(100):
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                raise AssertionError(f"HTTP server stopped early:\n{stdout}\n{stderr}")
            try:
                with urlopen(f"{base_url}/readyz", timeout=0.2) as response:
                    if response.status == 200:
                        break
            except OSError:
                time.sleep(0.05)
        else:
            raise AssertionError("HTTP server did not become ready")
        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def test_http_probes_are_public_but_mcp_requires_api_key():
    with _http_server() as base_url:
        with urlopen(f"{base_url}/healthz") as response:
            assert json.load(response) == {"status": "ok"}

        try:
            urlopen(Request(f"{base_url}/mcp", method="POST"))
        except HTTPError as error:
            assert error.code == 401
        else:
            raise AssertionError("MCP endpoint accepted a request without an API key")


async def _run_http_journey(base_url: str) -> None:
    assessment = json.loads(FIXTURES.read_text())["internal_assistant"]
    async with httpx.AsyncClient(headers={"x-api-key": API_KEY}) as client:
        async with streamable_http_client(
            f"{base_url}/mcp", http_client=client
        ) as (read, write, _):
            async with ClientSession(read, write) as session:
                initialized = await session.initialize()
                assert "fictional or synthetic" in initialized.instructions
                listed = await session.list_tools()
                assert len(listed.tools) == 6
                result = await session.call_tool(
                    "assess_ai_system", {"assessment": assessment}
                )
                assert not result.isError
                payload = json.loads(result.content[0].text)
                assert payload["decision"]["final_tier"] == "tier_3"
                provenance = payload["decision"]["framework_source"]
                assert provenance["library_version"] == "1.1.0"
                assert provenance["status"] == "loaded"


def test_streamable_http_exposes_the_same_governance_service():
    with _http_server() as base_url:
        asyncio.run(_run_http_journey(base_url))
