# SPDX-License-Identifier: MIT
"""Domain helpers for knowledge operations aligned with the Fênix Cloud API."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from fenix_mcp.infrastructure.fenix_api.client import FenixApiClient


def _strip_none(data: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in data.items() if value not in (None, "")}


def _format_date(value: Optional[str]) -> str:
    if not value:
        return "não definido"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        return value


def _ensure_list(value: Any) -> List[Dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        data = value.get("data")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
    return []


def _ensure_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        data = value.get("data")
        if isinstance(data, dict):
            return data
        return value
    return {}


@dataclass(slots=True)
class KnowledgeService:
    api: FenixApiClient
    logger: Any

    async def _call(self, func, *args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    async def _call_list(self, func, *args, **kwargs) -> List[Dict[str, Any]]:
        result = await self._call(func, *args, **kwargs)
        return _ensure_list(result)

    async def _call_dict(self, func, *args, **kwargs) -> Dict[str, Any]:
        result = await self._call(func, *args, **kwargs)
        return _ensure_dict(result)

    # ------------------------------------------------------------------
    # Work items
    # ------------------------------------------------------------------
    async def work_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_dict(self.api.create_work_item, _strip_none(payload))

    async def work_list(self, **filters: Any) -> List[Dict[str, Any]]:
        return await self._call_list(self.api.list_work_items, **_strip_none(filters))

    async def work_get(self, work_id: str) -> Dict[str, Any]:
        return await self._call_dict(self.api.get_work_item, work_id)

    async def work_get_by_key(self, key: str) -> Dict[str, Any]:
        return await self._call_dict(self.api.get_work_item_by_key, key)

    async def work_assign_to_me(self, work_id: str) -> Dict[str, Any]:
        return await self._call_dict(self.api.assign_work_item_to_me, work_id)

    async def work_mine(
        self, *, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        return await self._call_list(
            self.api.get_work_items_mine, limit=limit, offset=offset
        )

    async def work_update(
        self, work_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self._call_dict(
            self.api.update_work_item, work_id, _strip_none(payload)
        )

    async def work_delete(self, work_id: str) -> None:
        await self._call(self.api.delete_work_item, work_id)

    async def work_backlog(self) -> List[Dict[str, Any]]:
        return await self._call_list(self.api.list_work_items_backlog)

    async def work_search(
        self,
        *,
        query: str,
        limit: int,
        item_type: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assignee_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        return await self._call_list(
            self.api.search_work_items,
            query=query,
            limit=limit,
            item_type=item_type,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
            tags=tags,
        )

    async def work_analytics(self) -> Dict[str, Any]:
        return await self._call(self.api.get_work_items_analytics) or {}

    async def work_velocity(self, *, sprints_count: int) -> Dict[str, Any]:
        return (
            await self._call(
                self.api.get_work_items_velocity,
                sprints_count=sprints_count,
            )
            or {}
        )

    async def work_by_sprint(self, *, sprint_id: str) -> List[Dict[str, Any]]:
        return await self._call_list(
            self.api.list_work_items_by_sprint, sprint_id=sprint_id
        )

    async def work_burndown(self, *, sprint_id: str) -> Dict[str, Any]:
        return (
            await self._call(self.api.get_work_items_burndown, sprint_id=sprint_id)
            or {}
        )

    async def work_by_epic(self, *, epic_id: str) -> List[Dict[str, Any]]:
        return await self._call(self.api.list_work_items_by_epic, epic_id=epic_id) or []

    async def work_epic_progress(self, *, epic_id: str) -> Dict[str, Any]:
        return (
            await self._call(self.api.get_work_items_epic_progress, epic_id=epic_id)
            or {}
        )

    async def work_by_board(self, *, board_id: str) -> List[Dict[str, Any]]:
        return await self._call_list(
            self.api.list_work_items_by_board, board_id=board_id
        )

    async def work_children(self, work_id: str) -> List[Dict[str, Any]]:
        return await self._call_list(self.api.get_work_item_children, work_id)

    async def work_move(self, work_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call(self.api.move_work_item, work_id, _strip_none(payload))

    async def work_update_status(
        self, work_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self._call(
            self.api.update_work_item_status, work_id, _strip_none(payload)
        )

    async def work_move_to_board(
        self, work_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self._call(
            self.api.move_work_item_to_board, work_id, _strip_none(payload)
        )

    async def work_link(self, work_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call(self.api.link_work_item, work_id, _strip_none(payload))

    async def work_assign_to_sprint(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call(
            self.api.assign_work_items_to_sprint, _strip_none(payload)
        )

    async def work_bulk_update(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call(self.api.bulk_update_work_items, _strip_none(payload))

    async def work_bulk_create(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        return await self._call_list(
            self.api.bulk_create_work_items, _strip_none(payload)
        )

    # ------------------------------------------------------------------
    # Work boards
    # ------------------------------------------------------------------
    async def board_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call(self.api.create_work_board, _strip_none(payload))

    async def board_list(self, **filters: Any) -> List[Dict[str, Any]]:
        result = await self._call(self.api.list_work_boards, **_strip_none(filters))
        return _ensure_list(result)

    async def board_list_by_team(self) -> List[Dict[str, Any]]:
        result = await self._call(self.api.list_work_boards_by_team)
        return _ensure_list(result)

    async def board_favorites(self) -> List[Dict[str, Any]]:
        result = await self._call(self.api.list_favorite_work_boards)
        return _ensure_list(result)

    async def board_search(self, *, query: str, limit: int) -> List[Dict[str, Any]]:
        result = await self._call(
            self.api.search_work_boards,
            query=query,
            limit=limit,
        )
        return _ensure_list(result)

    async def board_recent(self, *, limit: int) -> List[Dict[str, Any]]:
        result = await self._call(self.api.list_recent_work_boards, limit=limit)
        return _ensure_list(result)

    async def board_get(self, board_id: str) -> Dict[str, Any]:
        result = await self._call(self.api.get_work_board, board_id)
        return _ensure_dict(result)

    async def board_update(
        self, board_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self._call(
            self.api.update_work_board, board_id, _strip_none(payload)
        )

    async def board_delete(self, board_id: str) -> None:
        await self._call(self.api.delete_work_board, board_id)

    async def board_analytics(self, board_id: str) -> Dict[str, Any]:
        return await self._call(self.api.get_work_board_analytics, board_id) or {}

    async def board_columns(self, board_id: str) -> List[Dict[str, Any]]:
        result = await self._call(self.api.list_work_board_columns, board_id)
        return _ensure_list(result)

    async def board_toggle_favorite(
        self, board_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self._call(
            self.api.toggle_work_board_favorite, board_id, _strip_none(payload)
        )

    async def board_clone(
        self, board_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self._call(
            self.api.clone_work_board, board_id, _strip_none(payload)
        )

    async def board_reorder(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call(self.api.reorder_work_boards, _strip_none(payload))

    async def board_column_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call(self.api.create_work_board_column, _strip_none(payload))

    async def board_column_reorder(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call(
            self.api.reorder_work_board_columns, _strip_none(payload)
        )

    async def board_column_get(self, column_id: str) -> Dict[str, Any]:
        return await self._call(self.api.get_work_board_column, column_id)

    async def board_column_update(
        self, column_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self._call(
            self.api.update_work_board_column, column_id, _strip_none(payload)
        )

    async def board_column_delete(self, column_id: str) -> None:
        await self._call(self.api.delete_work_board_column, column_id)

    # ------------------------------------------------------------------
    # Sprints
    # ------------------------------------------------------------------
    async def sprint_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call(self.api.create_sprint, _strip_none(payload))

    async def sprint_list(self, **filters: Any) -> List[Dict[str, Any]]:
        return await self._call_list(self.api.list_sprints, **_strip_none(filters))

    async def sprint_get(self, sprint_id: str) -> Dict[str, Any]:
        return await self._call_dict(self.api.get_sprint, sprint_id)

    async def sprint_update(
        self, sprint_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self._call(self.api.update_sprint, sprint_id, _strip_none(payload))

    async def sprint_delete(self, sprint_id: str) -> None:
        await self._call(self.api.delete_sprint, sprint_id)

    async def sprint_list_by_team(self) -> List[Dict[str, Any]]:
        return await self._call_list(self.api.list_sprints_by_team)

    async def sprint_recent(self, *, limit: int) -> List[Dict[str, Any]]:
        return await self._call(self.api.list_recent_sprints, limit=limit) or []

    async def sprint_search(self, *, query: str, limit: int) -> List[Dict[str, Any]]:
        return await self._call_list(
            self.api.search_sprints,
            query=query,
            limit=limit,
        )

    async def sprint_active(self) -> Dict[str, Any]:
        return await self._call(self.api.get_active_sprint) or {}

    async def sprint_velocity(self) -> Dict[str, Any]:
        return await self._call(self.api.get_sprints_velocity) or {}

    async def sprint_burndown(self) -> Dict[str, Any]:
        return await self._call(self.api.get_sprints_burndown) or {}

    async def sprint_work_items(self, sprint_id: str) -> List[Dict[str, Any]]:
        return await self._call_list(self.api.get_sprint_work_items, sprint_id)

    async def sprint_add_work_items(
        self, sprint_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self._call(
            self.api.add_work_items_to_sprint, sprint_id, _strip_none(payload)
        )

    async def sprint_remove_work_items(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call(
            self.api.remove_work_items_from_sprint, _strip_none(payload)
        )

    async def sprint_analytics(self, sprint_id: str) -> Dict[str, Any]:
        return await self._call(self.api.get_sprint_analytics, sprint_id) or {}

    async def sprint_capacity(self, sprint_id: str) -> Dict[str, Any]:
        return await self._call(self.api.get_sprint_capacity, sprint_id) or {}

    async def sprint_start(
        self, sprint_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self._call(self.api.start_sprint, sprint_id, _strip_none(payload))

    async def sprint_complete(
        self, sprint_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self._call(
            self.api.complete_sprint, sprint_id, _strip_none(payload)
        )

    async def sprint_cancel(self, sprint_id: str) -> Dict[str, Any]:
        return await self._call(self.api.cancel_sprint, sprint_id)

    # ------------------------------------------------------------------
    # Modes and rules
    # ------------------------------------------------------------------
    async def mode_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = await self._call(self.api.create_mode, _strip_none(payload))
        # API returns { message, mode } - extract mode
        if isinstance(result, dict) and "mode" in result:
            return result["mode"]
        return result or {}

    async def mode_list(
        self,
        *,
        include_rules: Optional[bool] = None,
        return_description: Optional[bool] = None,
        return_metadata: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        return (
            await self._call(
                self.api.list_modes,
                include_rules=include_rules,
                return_description=return_description,
                return_metadata=return_metadata,
            )
            or []
        )

    async def mode_get(
        self,
        mode_id: str,
        *,
        return_description: Optional[bool] = None,
        return_metadata: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return await self._call(
            self.api.get_mode,
            mode_id,
            return_description=return_description,
            return_metadata=return_metadata,
        )

    async def mode_update(
        self, mode_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        result = await self._call(self.api.update_mode, mode_id, _strip_none(payload))
        # API returns { message, mode } - extract mode
        if isinstance(result, dict) and "mode" in result:
            return result["mode"]
        return result or {}

    async def mode_delete(self, mode_id: str) -> None:
        await self._call(self.api.delete_mode, mode_id)

    async def mode_rule_add(self, mode_id: str, rule_id: str) -> Dict[str, Any]:
        return await self._call(self.api.add_mode_rule, mode_id, rule_id)

    async def mode_rule_remove(self, mode_id: str, rule_id: str) -> None:
        await self._call(self.api.remove_mode_rule, mode_id, rule_id)

    async def mode_rules(self, mode_id: str) -> List[Dict[str, Any]]:
        return await self._call(self.api.list_rules_by_mode, mode_id) or []

    async def mode_rules_for_rule(self, rule_id: str) -> List[Dict[str, Any]]:
        return await self._call(self.api.list_modes_by_rule, rule_id) or []

    async def rule_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = await self._call(self.api.create_rule, _strip_none(payload))
        # API returns { message, rule } - extract rule
        if isinstance(result, dict) and "rule" in result:
            return result["rule"]
        return result or {}

    async def rule_list(
        self,
        *,
        return_description: Optional[bool] = None,
        return_metadata: Optional[bool] = None,
        return_modes: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        return (
            await self._call(
                self.api.list_rules,
                return_description=return_description,
                return_metadata=return_metadata,
                return_modes=return_modes,
            )
            or []
        )

    async def rule_get(
        self,
        rule_id: str,
        *,
        return_description: Optional[bool] = None,
        return_metadata: Optional[bool] = None,
        return_modes: Optional[bool] = None,
    ) -> Dict[str, Any]:
        return await self._call(
            self.api.get_rule,
            rule_id,
            return_description=return_description,
            return_metadata=return_metadata,
            return_modes=return_modes,
        )

    async def rule_update(
        self, rule_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        result = await self._call(self.api.update_rule, rule_id, _strip_none(payload))
        # API returns { message, rule } - extract rule
        if isinstance(result, dict) and "rule" in result:
            return result["rule"]
        return result or {}

    async def rule_delete(self, rule_id: str) -> None:
        await self._call(self.api.delete_rule, rule_id)

    # ------------------------------------------------------------------
    # Documentation
    # ------------------------------------------------------------------
    async def doc_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_dict(
            self.api.create_documentation_item, _strip_none(payload)
        )

    async def doc_list(self, **filters: Any) -> List[Dict[str, Any]]:
        result = await self._call(
            self.api.list_documentation_items, **_strip_none(filters)
        )
        return _ensure_list(result)

    async def doc_get(self, doc_id: str, **filters: Any) -> Dict[str, Any]:
        result = await self._call(
            self.api.get_documentation_item, doc_id, **_strip_none(filters)
        )
        return _ensure_dict(result)

    async def doc_update(self, doc_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_dict(
            self.api.update_documentation_item, doc_id, _strip_none(payload)
        )

    async def doc_delete(self, doc_id: str) -> None:
        await self._call(self.api.delete_documentation_item, doc_id)

    async def doc_roots(self) -> List[Dict[str, Any]]:
        result = await self._call(self.api.list_documentation_roots)
        return _ensure_list(result)

    async def doc_recent(self, *, limit: int) -> List[Dict[str, Any]]:
        result = await self._call(
            self.api.list_documentation_recent,
            limit=limit,
        )
        return _ensure_list(result)

    async def doc_analytics(self) -> Dict[str, Any]:
        result = await self._call(self.api.get_documentation_analytics)
        return _ensure_dict(result)

    async def doc_children(self, doc_id: str) -> List[Dict[str, Any]]:
        return await self._call_list(self.api.get_documentation_children, doc_id)

    async def doc_tree(self, doc_id: str) -> Dict[str, Any]:
        return await self._call(self.api.get_documentation_tree, doc_id) or {}

    async def doc_full_tree(self) -> Dict[str, Any]:
        return await self._call(self.api.get_documentation_full_tree) or {}

    async def doc_move(self, doc_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_dict(
            self.api.move_documentation_item, doc_id, _strip_none(payload)
        )

    async def doc_publish(self, doc_id: str) -> Dict[str, Any]:
        return await self._call_dict(self.api.publish_documentation_item, doc_id)

    async def doc_version(self, doc_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_dict(
            self.api.create_documentation_version, doc_id, _strip_none(payload)
        )

    async def doc_duplicate(
        self, doc_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self._call_dict(
            self.api.duplicate_documentation_item, doc_id, _strip_none(payload)
        )


__all__ = [
    "KnowledgeService",
    "_strip_none",
    "_format_date",
]
