# SPDX-License-Identifier: MIT
"""Domain helpers for user configuration documents."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from fenix_mcp.infrastructure.fenix_api.client import FenixApiClient


def _strip_none(data: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in data.items() if value not in (None, "")}


class UserConfigService:
    def __init__(self, api: FenixApiClient):
        self._api = api

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        payload = _strip_none(data)
        result = await asyncio.to_thread(self._api.create_user_core_document, payload)
        # API returns { message, document } - extract document
        if isinstance(result, dict) and "document" in result:
            return result["document"]
        return result or {}

    async def list(
        self, *, returnContent: Optional[bool] = None, **_: Any
    ) -> List[Dict[str, Any]]:
        return (
            await asyncio.to_thread(
                self._api.list_user_core_documents,
                return_content=bool(returnContent),
            )
            or []
        )

    async def get(
        self, doc_id: str, *, returnContent: Optional[bool] = None, **_: Any
    ) -> Dict[str, Any]:
        return await asyncio.to_thread(
            self._api.get_user_core_document,
            doc_id,
            return_content=bool(returnContent),
        )

    async def update(self, doc_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        payload = _strip_none(data)
        result = await asyncio.to_thread(
            self._api.update_user_core_document, doc_id, payload
        )
        # API returns { message, document } - extract document
        if isinstance(result, dict) and "document" in result:
            return result["document"]
        return result or {}

    async def delete(self, doc_id: str) -> None:
        await asyncio.to_thread(self._api.delete_user_core_document, doc_id)
