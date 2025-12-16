# SPDX-License-Identifier: MIT
"""Helpers to format MCP responses."""

from __future__ import annotations

from typing import Iterable, List

from fenix_mcp.application.tool_base import ToolResponse


def text(content: str) -> ToolResponse:
    return {"content": [{"type": "text", "text": content}]}


def bullet_list(title: str, items: Iterable[str]) -> ToolResponse:
    body_lines: List[str] = [title, ""]
    body_lines.extend(f"- {item}" for item in items)
    return text("\n".join(body_lines))


def key_value(title: str, **values: str) -> ToolResponse:
    lines = [title, ""]
    lines.extend(f"{key}: {value}" for key, value in values.items())
    return text("\n".join(lines))
