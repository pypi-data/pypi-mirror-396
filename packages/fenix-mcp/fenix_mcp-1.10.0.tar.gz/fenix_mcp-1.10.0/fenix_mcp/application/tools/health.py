# SPDX-License-Identifier: MIT
"""Health check tool."""

from __future__ import annotations

from fenix_mcp.application.presenters import key_value
from fenix_mcp.application.tool_base import Tool, ToolRequest
from fenix_mcp.infrastructure.context import AppContext


class _HealthRequest(ToolRequest):
    pass


class HealthTool(Tool):
    name = "fenix_health_check"
    description = "Check if Fênix Cloud Backend is healthy and accessible."
    request_model = _HealthRequest

    def __init__(self, context: AppContext):
        self._context = context

    async def run(self, payload: ToolRequest, context: AppContext):
        api_health = self._context.api_client.get_health() or {}
        return key_value(
            "Fênix Cloud Backend Health",
            status=str(api_health.get("status", "unknown")),
        )
