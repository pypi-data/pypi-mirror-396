# SPDX-License-Identifier: MIT
"""Configuration helpers for the Fênix MCP server."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration knobs consumed by the server."""

    api_url: str = Field(
        default="https://fenix-api-production-7619.up.railway.app",
        description="Base URL for the Fênix Cloud API.",
    )
    http_timeout: float = Field(
        default=30.0, description="Default HTTP timeout in seconds."
    )
    log_level: str = Field(default="INFO", description="Root log level.")
    transport_mode: Literal["stdio", "http", "both"] = Field(
        default="stdio",
        description="Active transport mode: stdio, http or both.",
    )
    http_host: str = Field(default="127.0.0.1", description="HTTP bind host.")
    http_port: int = Field(
        default=3000, description="HTTP port when running with network transport."
    )

    model_config = SettingsConfigDict(
        populate_by_name=True,
        env_prefix="FENIX_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @field_validator("log_level")
    @classmethod
    def _validate_level(cls, value: str) -> str:
        upper = value.upper()
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
        if upper not in allowed:
            raise ValueError(f"Invalid log level '{value}'. Allowed: {sorted(allowed)}")
        return upper

    @field_validator("api_url")
    @classmethod
    def _validate_api_url(cls, value: str) -> str:
        HttpUrl(value)
        return value


@lru_cache(maxsize=1)
def load_settings() -> Settings:
    """Load settings from environment / .env file (cached)."""

    return Settings()  # type: ignore[call-arg]
