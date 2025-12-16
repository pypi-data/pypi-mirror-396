# SPDX-License-Identifier: MIT
"""Logging configuration utilities."""

from __future__ import annotations

import logging
import sys
from typing import Any, Dict


class _SensitiveFormatter(logging.Formatter):
    """Formatter that removes obvious tokens from logs."""

    def format(self, record: logging.LogRecord) -> str:
        if isinstance(record.args, dict):
            record.args = self._sanitize_dict(record.args)
        elif isinstance(record.args, tuple):
            record.args = tuple(self._sanitize(value) for value in record.args)
        return super().format(record)

    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {key: self._sanitize(value) for key, value in data.items()}

    def _sanitize(self, value: Any) -> Any:
        if isinstance(value, str) and "pat_" in value:
            return value[:10] + "…" + value[-4:]
        return value


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger with a basic structured format."""

    handler = logging.StreamHandler(sys.stderr)
    formatter = _SensitiveFormatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(handler)
