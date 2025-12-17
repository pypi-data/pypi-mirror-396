# SPDX-License-Identifier: MIT
"""Factory functions to instantiate all tools."""

from __future__ import annotations

from typing import List

from fenix_mcp.application.tool_base import Tool
from fenix_mcp.infrastructure.context import AppContext

from .health import HealthTool
from .initialize import InitializeTool
from .intelligence import IntelligenceTool
from .productivity import ProductivityTool
from .knowledge import KnowledgeTool
from .user_config import UserConfigTool


def build_tools(context: AppContext) -> List[Tool]:
    """Instantiate all available tools."""

    return [
        HealthTool(context),
        InitializeTool(context),
        IntelligenceTool(context),
        ProductivityTool(context),
        KnowledgeTool(context),
        UserConfigTool(context),
    ]
