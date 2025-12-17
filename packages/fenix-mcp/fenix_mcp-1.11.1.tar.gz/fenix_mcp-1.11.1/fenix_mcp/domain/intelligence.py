# SPDX-License-Identifier: MIT
"""Domain helpers for intelligence (memory) operations."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from fenix_mcp.infrastructure.fenix_api.client import FenixApiClient


@dataclass(slots=True)
class IntelligenceService:
    api: FenixApiClient
    logger: Any

    async def smart_create_memory(
        self,
        *,
        title: str,
        content: str,
        metadata: str,
        context: Optional[str],
        source: str,
        importance: str,
        tags: List[str],
    ) -> Dict[str, Any]:
        # Validate required parameters
        if not metadata or not metadata.strip():
            raise ValueError("metadata is required and cannot be empty")

        if not source or not source.strip():
            raise ValueError("source is required and cannot be empty")

        if not tags or not isinstance(tags, list) or len(tags) == 0:
            raise ValueError("tags is required and must be a non-empty List[str]")

        # Validate all tags are strings
        for i, tag in enumerate(tags):
            if not isinstance(tag, str) or not tag.strip():
                raise ValueError(
                    f"All tags must be non-empty strings, got {type(tag)} at index {i}"
                )

        importance_value = importance or "medium"
        metadata_str = build_metadata(
            metadata,
            importance=importance_value,
            tags=tags,
            context=context,
            source=source,
        )
        payload = {
            "title": title,
            "content": content,
            "metadata": metadata_str,
            "priority_score": _importance_to_priority(importance_value),
            "tags": tags,
        }
        return await self._call(self.api.smart_create_memory, _strip_none(payload))

    async def query_memories(self, **filters: Any) -> List[Dict[str, Any]]:
        params = _strip_none(filters)
        include_content = _coerce_bool(
            params.pop("include_content", params.pop("content", None))
        )
        include_metadata = _coerce_bool(
            params.pop("include_metadata", params.pop("metadata", None))
        )
        allowed_keys = {
            "limit",
            "offset",
            "query",
            "tags",
            "modeId",
            "ruleId",
            "workItemId",
            "sprintId",
            "documentationItemId",
            "importance",
        }
        cleaned_params = {key: params[key] for key in allowed_keys if key in params}
        return (
            await self._call(
                self.api.list_memories,
                include_content=include_content,
                include_metadata=include_metadata,
                **cleaned_params,
            )
            or []
        )

    async def similar_memories(
        self, *, content: str, threshold: float, max_results: int
    ) -> List[Dict[str, Any]]:
        payload = {
            "content": content,
            "threshold": threshold,
        }
        result = (
            await self._call(self.api.find_similar_memories, _strip_none(payload)) or []
        )
        if isinstance(result, list) and max_results:
            return result[:max_results]
        return result

    async def consolidate_memories(
        self, *, memory_ids: Iterable[str], strategy: str
    ) -> Dict[str, Any]:
        payload = {
            "memoryIds": list(memory_ids),
            "strategy": strategy,
        }
        return await self._call(self.api.consolidate_memories, payload)

    async def update_memory(self, memory_id: str, **fields: Any) -> Dict[str, Any]:
        payload = _strip_none(fields)
        if "importance" in payload:
            payload["priority_score"] = _importance_to_priority(
                payload.pop("importance")
            )
        mapping = {
            "documentation_item_id": "documentationItemId",
            "mode_id": "modeId",
            "rule_id": "ruleId",
            "work_item_id": "workItemId",
            "sprint_id": "sprintId",
        }
        for old_key, new_key in mapping.items():
            if old_key in payload:
                payload[new_key] = payload.pop(old_key)
        return await self._call(self.api.update_memory, memory_id, payload)

    async def delete_memory(self, memory_id: str) -> None:
        await self._call(self.api.delete_memory, memory_id)

    async def _call(self, func, *args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    async def get_memory(
        self,
        memory_id: str,
        *,
        include_content: bool = False,
        include_metadata: bool = False,
    ) -> Dict[str, Any]:
        return await self._call(
            self.api.get_memory,
            memory_id,
            include_content=include_content,
            include_metadata=include_metadata,
        )


def _importance_to_priority(importance: Optional[str]) -> float:
    mapping = {
        "low": 0.2,
        "medium": 0.5,
        "high": 0.7,
        "critical": 0.9,
    }
    if importance is None:
        return 0.5
    return mapping.get(importance.lower(), 0.5)


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y"}:
            return True
        if normalized in {"false", "0", "no", "n"}:
            return False
    return bool(value)


def _strip_none(data: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in data.items() if value not in (None, "")}


def build_metadata(
    explicit: str,
    *,
    importance: Optional[str],
    tags: List[str],
    context: Optional[str] = None,
    source: str,
    existing: Optional[str] = None,
) -> str:
    if explicit and explicit.strip():
        return explicit.strip()

    existing_map = _parse_metadata(existing) if existing else {}
    metadata_map: Dict[str, str] = {}

    metadata_map["t"] = existing_map.get("t", "memory")
    metadata_map["src"] = _slugify(source) if source else existing_map.get("src", "mcp")

    ctx_value = _slugify(context) if context else existing_map.get("ctx")
    if ctx_value:
        metadata_map["ctx"] = ctx_value

    priority_key = importance.lower() if importance else existing_map.get("p")
    if priority_key:
        metadata_map["p"] = priority_key

    tag_string = _format_tags(tags)
    if tag_string:
        metadata_map["tags"] = tag_string
    elif "tags" in existing_map:
        metadata_map["tags"] = existing_map["tags"]

    for key, value in existing_map.items():
        if key not in metadata_map:
            metadata_map[key] = value

    if not metadata_map:
        metadata_map["t"] = "memory"
        metadata_map["src"] = "mcp"

    return "|".join(f"{key}:{metadata_map[key]}" for key in metadata_map)


def _parse_metadata(metadata: str) -> Dict[str, str]:
    items = {}
    for entry in metadata.split("|"):
        if ":" not in entry:
            continue
        key, value = entry.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key:
            items[key] = value
    return items


def _slugify(value: Optional[str]) -> str:
    if not value:
        return ""
    sanitized = value.replace("|", " ").replace(":", " ")
    return "-".join(part for part in sanitized.split() if part).lower()


def _format_tags(tags: List[str]) -> str:
    """
    Format tags list into a comma-separated string for metadata.

    Args:
        tags: List of string tags (required)

    Returns:
        Comma-separated string of tags

    Raises:
        TypeError: If tags is not a List[str]
        ValueError: If tags is empty
    """
    if not isinstance(tags, list):
        raise TypeError(f"tags must be List[str], got {type(tags)}")

    if not tags:
        raise ValueError("tags cannot be empty")

    # Clean and validate tags
    cleaned_tags = []
    for tag in tags:
        if isinstance(tag, str) and tag.strip():
            cleaned_tags.append(tag.strip())
        else:
            raise ValueError(
                f"All tags must be non-empty strings, got {type(tag)}: {tag}"
            )

    if not cleaned_tags:
        raise ValueError("No valid tags found after cleaning")

    return ",".join(sorted(set(cleaned_tags)))
