"""Authenticated Streamable HTTP transport for hosted MCP clients."""

from __future__ import annotations

import os
import secrets
from collections.abc import Awaitable, Callable
from typing import Any

import uvicorn
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from .server import create_server
from .tools import GovernanceTools

ASGIApp = Callable[
    [
        dict[str, Any],
        Callable[..., Awaitable[Any]],
        Callable[..., Awaitable[Any]],
    ],
    Awaitable[None],
]


class ApiKeyMiddleware:
    """Require a shared API key for MCP while leaving probes unauthenticated."""

    def __init__(self, app: ASGIApp, api_key: str) -> None:
        if not api_key:
            raise ValueError("AI_GOVERNANCE_API_KEY must be configured")
        self.app = app
        self.api_key = api_key

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[..., Awaitable[Any]],
        send: Callable[..., Awaitable[Any]],
    ) -> None:
        if scope["type"] != "http" or scope.get("path") in {"/healthz", "/readyz"}:
            await self.app(scope, receive, send)
            return

        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        supplied = headers.get(b"x-api-key", b"").decode("utf-8", errors="ignore")
        if not secrets.compare_digest(supplied, self.api_key):
            response = JSONResponse({"detail": "Unauthorized"}, status_code=401)
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


async def health(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


def create_http_app(
    api_key: str,
    tools: GovernanceTools | None = None,
) -> ASGIApp:
    server = create_server(
        tools,
        streamable_http_path="/mcp",
        stateless_http=True,
        max_request_body_size=1_048_576,
    )
    app = server.streamable_http_app()
    app.routes.extend(
        [
            Route("/healthz", health, methods=["GET"]),
            Route("/readyz", health, methods=["GET"]),
        ]
    )
    return ApiKeyMiddleware(app, api_key)


def main() -> None:
    api_key = os.environ.get("AI_GOVERNANCE_API_KEY", "")
    app = create_http_app(api_key)
    host = os.environ.get("AI_GOVERNANCE_HOST", "0.0.0.0")
    port = int(os.environ.get("AI_GOVERNANCE_PORT", os.environ.get("PORT", "8000")))
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
