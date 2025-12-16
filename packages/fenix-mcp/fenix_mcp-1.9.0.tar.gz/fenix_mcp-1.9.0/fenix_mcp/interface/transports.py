# SPDX-License-Identifier: MIT
"""Transport management supporting STDIO and HTTP JSON-RPC."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
import contextlib
from contextlib import AsyncExitStack
from typing import Iterable, List, Protocol

from aiohttp import web

from fenix_mcp.infrastructure.config import Settings


class Transport(Protocol):
    name: str

    async def serve_forever(self) -> None: ...


class StdIoTransport:
    name = "stdio"

    def __init__(self, server):
        self._server = server
        self._logger = logging.getLogger("fenix_mcp.transport.stdio")

    async def serve_forever(self) -> None:
        loop = asyncio.get_running_loop()
        self._logger.info("STDIO transport awaiting input")
        try:
            while True:
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    await asyncio.sleep(0.05)
                    continue

                line = line.strip()
                if not line:
                    continue

                try:
                    request = json.loads(line)
                except json.JSONDecodeError as exc:  # pragma: no cover - defensive
                    self._logger.warning(
                        "Invalid JSON received on STDIO", extra={"error": str(exc)}
                    )
                    continue

                try:
                    response = await self._server.handle(request)
                except Exception as exc:  # pragma: no cover - defensive
                    self._logger.exception("STDIO transport error")
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id") if isinstance(request, dict) else None,
                        "error": {"code": -32000, "message": str(exc)},
                    }

                if response is not None:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
        except asyncio.CancelledError:  # pragma: no cover - cancellation path
            self._logger.debug("STDIO transport cancelled")


class HttpTransport:
    name = "http"

    def __init__(self, server, host: str, port: int):
        self._server = server
        self._host = host
        self._port = port
        self._logger = logging.getLogger("fenix_mcp.transport.http")
        self._runner: web.AppRunner | None = None
        self._shutdown_event = asyncio.Event()

    async def serve_forever(self) -> None:
        await self._start()
        try:
            await self._shutdown_event.wait()
        except asyncio.CancelledError:  # pragma: no cover - cancellation path
            self._logger.debug("HTTP transport cancelled")
        finally:
            await self._cleanup()

    async def shutdown(self) -> None:
        self._shutdown_event.set()
        await self._cleanup()

    async def _start(self) -> None:
        if self._runner is not None:
            return

        app = web.Application()
        app.add_routes(
            [
                web.get("/health", self._handle_health),
                web.post("/jsonrpc", self._handle_jsonrpc),
                web.options("/jsonrpc", self._handle_options),
            ]
        )

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host=self._host, port=self._port)
        try:
            await site.start()
        except Exception:  # pragma: no cover - defensive
            self._logger.exception(
                "Failed to bind HTTP transport",
                extra={"host": self._host, "port": self._port},
            )
            raise

        self._logger.info(
            "HTTP transport listening", extra={"host": self._host, "port": self._port}
        )
        self._runner = runner

    async def _cleanup(self) -> None:
        runner, self._runner = self._runner, None
        if runner is not None:
            await runner.cleanup()

    def _with_cors(self, response: web.StreamResponse) -> web.StreamResponse:
        response.headers.setdefault("Access-Control-Allow-Origin", "*")
        response.headers.setdefault(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.setdefault("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response

    async def _handle_health(self, request: web.Request) -> web.Response:
        payload = {
            "status": "ok",
            "transport": "http",
            "sessionId": self._server.session_id,
        }
        return self._with_cors(web.json_response(payload))

    async def _handle_options(self, request: web.Request) -> web.StreamResponse:
        return self._with_cors(web.Response(status=204))

    async def _handle_jsonrpc(self, request: web.Request) -> web.StreamResponse:
        auth_header = request.headers.get("Authorization") or request.headers.get(
            "authorization"
        )
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            if token:
                self._server.set_personal_access_token(token)

        try:
            payload = await request.json()
        except Exception:  # pragma: no cover - defensive
            return self._with_cors(
                web.json_response(
                    {"error": {"code": -32700, "message": "Invalid JSON"}}, status=400
                )
            )

        self._logger.debug("JSON-RPC request payload", extra={"payload": payload})

        try:
            response = await self._server.handle(payload)
        except Exception as exc:  # pragma: no cover - defensive
            self._logger.exception("Error processing JSON-RPC request")
            return self._with_cors(
                web.json_response(
                    {"error": {"code": -32000, "message": str(exc)}}, status=500
                )
            )

        if response is None:
            return self._with_cors(web.Response(status=204))
        return self._with_cors(web.json_response(response))


class CompositeTransport:
    def __init__(self, transports: Iterable[Transport]):
        self._transports: List[Transport] = list(transports)
        self.name = "+".join(transport.name for transport in self._transports)

    async def serve_forever(self) -> None:
        tasks = [asyncio.create_task(t.serve_forever()) for t in self._transports]
        try:
            await asyncio.gather(*tasks)
        finally:
            for task in tasks:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task


class TransportFactory:
    def __init__(self, settings: Settings, logger: logging.Logger | None = None):
        self._settings = settings
        self._logger = logger or logging.getLogger("fenix_mcp.transport")

    async def create(self, *, stack: AsyncExitStack, server) -> Transport:
        transports: List[Transport] = []

        if self._settings.transport_mode in ("stdio", "both"):
            self._logger.info("Enabling STDIO transport")
            transports.append(StdIoTransport(server))

        if self._settings.transport_mode in ("http", "both"):
            self._logger.info(
                "Enabling HTTP transport",
                extra={
                    "host": self._settings.http_host,
                    "port": self._settings.http_port,
                },
            )
            http_transport = HttpTransport(
                server,
                host=self._settings.http_host,
                port=self._settings.http_port,
            )
            stack.push_async_callback(http_transport.shutdown)
            transports.append(http_transport)

        if not transports:
            raise ValueError(
                "No transport configured. Check FENIX_TRANSPORT_MODE env var."
            )

        if len(transports) == 1:
            return transports[0]

        return CompositeTransport(transports)
