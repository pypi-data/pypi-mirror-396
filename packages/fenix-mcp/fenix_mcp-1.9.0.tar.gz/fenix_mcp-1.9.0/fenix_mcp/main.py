# SPDX-License-Identifier: MIT
"""CLI entry point for the Fênix MCP server."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
from contextlib import AsyncExitStack

from fenix_mcp.infrastructure.config import Settings, load_settings
from fenix_mcp.infrastructure.context import AppContext
from fenix_mcp.infrastructure.logging import configure_logging
from fenix_mcp.infrastructure.fenix_api.client import FenixApiClient
from fenix_mcp.interface.mcp_server import build_server
from fenix_mcp.interface.transports import TransportFactory


def _normalize_pat(token: str | None) -> str | None:
    if token is None:
        return None
    value = token.strip()
    if value.lower().startswith("bearer "):
        value = value[7:].strip()
    return value or None


async def _run_async(pat_token: str | None) -> None:
    """Async bootstrap so we can support both STDIO and HTTP/SSE transports."""

    settings: Settings = load_settings()
    configure_logging(level=settings.log_level)

    logger = logging.getLogger("fenix_mcp.main")
    settings_payload = settings.model_dump(mode="python")
    settings_payload["api_url"] = str(settings.api_url)
    logger.info(
        "Loaded configuration: transport=%s api_url=%s http=%s:%s",
        settings.transport_mode,
        settings_payload["api_url"],
        settings.http_host,
        settings.http_port,
    )

    token = _normalize_pat(pat_token) or _normalize_pat(os.getenv("FENIX_PAT_TOKEN"))

    if token:
        logger.debug("Using PAT token (length=%s)", len(token))
    else:
        logger.debug("No PAT token provided; relying on Authorization headers")

    api_client = FenixApiClient(
        base_url=str(settings.api_url),
        personal_access_token=token,
        timeout=settings.http_timeout,
    )

    context = AppContext(
        settings=settings,
        logger=logging.getLogger("fenix_mcp"),
        api_client=api_client,
    )

    async with AsyncExitStack() as stack:
        server = build_server(context=context)
        transport = await TransportFactory(settings, logger=logger).create(
            stack=stack, server=server
        )
        logger.info("Fênix MCP server started (mode=%s)", transport.name)
        await transport.serve_forever()


def run() -> None:
    """Entry point used by scripts."""

    parser = argparse.ArgumentParser(description="Fênix MCP server")
    parser.add_argument(
        "--pat",
        dest="pat_token",
        default=None,
        help="Personal Access Token for the Fênix API (with or without 'Bearer ').",
    )
    args = parser.parse_args()

    try:
        asyncio.run(_run_async(args.pat_token))
    except KeyboardInterrupt:
        logging.getLogger("fenix_mcp.main").info("Fênix MCP server interrupted by user")


if __name__ == "__main__":
    run()
