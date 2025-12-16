# SPDX-License-Identifier: MIT
"""Shared context dependency injected into tools."""

from __future__ import annotations

from dataclasses import dataclass
from logging import Logger

from fenix_mcp.infrastructure.config import Settings
from fenix_mcp.infrastructure.fenix_api.client import FenixApiClient


@dataclass(slots=True)
class AppContext:
    """Runtime dependencies shared by tools."""

    settings: Settings
    logger: Logger
    api_client: FenixApiClient
