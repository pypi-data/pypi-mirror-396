# SPDX-License-Identifier: MIT
"""Domain helpers for productivity (TODO) operations."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from fenix_mcp.infrastructure.fenix_api.client import FenixApiClient, FenixApiError


def _ensure_iso_datetime(value: str) -> str:
    """Convert common datetime formats to ISO 8601."""

    value = value.strip()
    if not value:
        raise ValueError("Data vazia.")
    try:
        if len(value) == 10:
            dt = datetime.strptime(value, "%Y-%m-%d")
            return dt.isoformat()
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.isoformat()
    except ValueError as exc:  # pragma: no cover
        raise ValueError(
            "Formato de data inválido. Use YYYY-MM-DD ou ISO completo (ex: 2024-12-31T23:59:59Z)."
        ) from exc


class ProductivityService:
    """Async facade around the Fênix API for TODO management."""

    def __init__(self, api_client: FenixApiClient, logger):
        self._api = api_client
        self._logger = logger

    async def create_todo(
        self,
        *,
        title: str,
        content: str,
        status: str,
        priority: str,
        category: Optional[str],
        tags: Iterable[str],
        due_date: str,
    ) -> Dict[str, Any]:
        payload = {
            "title": title,
            "content": content,
            "status": status,
            "priority": priority,
            "category": category,
            "tags": list(tags),
            "dueDate": _ensure_iso_datetime(due_date),
        }
        return await self._call(self._api.create_todo_item, _strip_none(payload))

    async def list_todos(
        self,
        *,
        limit: int,
        offset: int,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params = {
            "limit": limit,
            "offset": offset,
            "status": status,
            "priority": priority,
            "category": category,
        }
        result = await self._call(self._api.list_todo_items, **_strip_none(params))
        return self._coerce_list(result, keys=("todo_items", "items", "todos"))

    async def get_todo(self, todo_id: str) -> Dict[str, Any]:
        return await self._call(self._api.get_todo_item, todo_id)

    async def update_todo(self, todo_id: str, **fields) -> Dict[str, Any]:
        if "due_date" in fields and fields["due_date"]:
            fields["dueDate"] = _ensure_iso_datetime(fields.pop("due_date"))
        payload = _strip_none(fields)
        if not payload:
            raise ValueError("Nenhum campo foi informado para atualização.")
        return await self._call(self._api.update_todo_item, todo_id, payload)

    async def delete_todo(self, todo_id: str) -> None:
        await self._call(self._api.delete_todo_item, todo_id)

    async def stats(self) -> Dict[str, Any]:
        return await self._call(self._api.get_todo_stats) or {}

    async def search(
        self, query: str, *, limit: int, offset: int
    ) -> List[Dict[str, Any]]:
        # API atual não expõe paginação no endpoint de busca, mas mantemos
        # assinatura para possível suporte futuro.
        result = await self._call(self._api.search_todo_items, query=query)
        return self._coerce_list(result, keys=("todo_items", "items", "todos"))

    async def overdue(self) -> List[Dict[str, Any]]:
        result = await self._call(self._api.list_todo_overdue)
        return self._coerce_list(result, keys=("todo_items", "items", "todos"))

    async def upcoming(self, *, days: Optional[int] = None) -> List[Dict[str, Any]]:
        result = await self._call(self._api.list_todo_upcoming, days=days)
        return self._coerce_list(result, keys=("todo_items", "items", "todos"))

    async def categories(self) -> List[str]:
        payload = await self._call(self._api.get_todo_categories)
        return _coerce_str_list(payload, fallback_key="categories")

    async def tags(self) -> List[str]:
        payload = await self._call(self._api.get_todo_tags)
        return _coerce_str_list(payload, fallback_key="tags")

    async def _call(self, func, *args, **kwargs):
        try:
            return await asyncio.to_thread(func, *args, **kwargs)
        except FenixApiError:
            raise
        except Exception as exc:  # pragma: no cover
            if self._logger:
                self._logger.error("Erro acessando a API do Fênix: %s", exc)
            raise

    @staticmethod
    def _coerce_list(value: Any, *, keys: Iterable[str]) -> List[Dict[str, Any]]:
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            for key in keys:
                data = value.get(key)
                if isinstance(data, list):
                    return data
            data = value.get("data")
            if isinstance(data, list):
                return data
            # alguns endpoints retornam dict com 'data' contendo outro dict
            if isinstance(data, dict):
                for key in keys:
                    nested = data.get(key)
                    if isinstance(nested, list):
                        return nested
        return []

    @staticmethod
    def format_todo(item: Dict[str, Any], *, show_content: bool = False) -> str:
        lines = [
            f"📋 **{item.get('title', 'No title')}**",
            f"ID: {item.get('id', 'N/A')}",
            f"Status: {item.get('status', 'unknown')}",
            f"Priority: {item.get('priority', 'unknown')}",
            f"Category: {item.get('category') or 'not set'}",
            f"Due date: {format_date(item.get('dueDate') or item.get('due_date'))}",
        ]
        if show_content and item.get("content"):
            lines.append("")
            lines.append("**Content:**")
            lines.append(item.get("content"))
        return "\n".join(lines)


def _strip_none(data: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in data.items() if value not in (None, "")}


def _coerce_str_list(value: Any, *, fallback_key: str) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, dict):
        data = value.get(fallback_key) or value.get("data")
        if isinstance(data, list):
            return [str(item) for item in data]
    return []


def format_date(value: Optional[str]) -> str:
    if not value:
        return "not set"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return value
