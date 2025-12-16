# SPDX-License-Identifier: MIT
"""Registry that keeps the mapping between tool names and instances."""

from __future__ import annotations

from typing import Dict, Iterable, List

from fenix_mcp.application.tool_base import Tool, ToolResponse
from fenix_mcp.infrastructure.context import AppContext


class ToolRegistry:
    """Lookup table for tool execution."""

    def __init__(self, tools: Iterable[Tool]):
        self._tools: Dict[str, Tool] = {}
        for tool in tools:
            if tool.name in self._tools:
                raise ValueError(f"Duplicate tool name detected: {tool.name}")
            self._tools[tool.name] = tool

    def list_definitions(self) -> List[dict]:
        return [tool.schema() for tool in self._tools.values()]

    async def execute(
        self, name: str, arguments: dict, context: AppContext
    ) -> ToolResponse:
        try:
            tool = self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool '{name}'") from exc
        return await tool.execute(arguments, context)


def build_default_registry(context: AppContext) -> ToolRegistry:
    from fenix_mcp.application.tools import build_tools

    tools = build_tools(context)
    return ToolRegistry(tools)
