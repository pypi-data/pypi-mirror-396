# SPDX-License-Identifier: MIT
"""Lightweight MCP server implementation backed by the tool registry."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

from fenix_mcp.application.tool_registry import ToolRegistry, build_default_registry
from fenix_mcp.infrastructure.context import AppContext


class McpServerError(RuntimeError):
    pass


@dataclass(slots=True)
class SimpleMcpServer:
    context: AppContext
    registry: ToolRegistry
    session_id: str

    def set_personal_access_token(self, token: Optional[str]) -> None:
        self.context.api_client.update_token(token)

    async def handle(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        method = request.get("method")
        request_id = request.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "logging": {}},
                    "serverInfo": {"name": "fenix_cloud_mcp_py", "version": "0.1.0"},
                    "sessionId": self.session_id,
                },
            }

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": self.registry.list_definitions()},
            }

        if method == "tools/call":
            params = request.get("params") or {}
            name = params.get("name")
            arguments = params.get("arguments") or {}

            if not name:
                raise McpServerError("Missing tool name in tools/call payload")

            result = await self.registry.execute(name, arguments, self.context)

            return {"jsonrpc": "2.0", "id": request_id, "result": result}

        if method == "notifications/initialized":
            # Notifications do not require a response
            return None

        raise McpServerError(f"Unsupported method: {method}")


def build_server(context: AppContext) -> SimpleMcpServer:
    registry = build_default_registry(context)
    return SimpleMcpServer(
        context=context,
        registry=registry,
        session_id=str(uuid.uuid4()),
    )
