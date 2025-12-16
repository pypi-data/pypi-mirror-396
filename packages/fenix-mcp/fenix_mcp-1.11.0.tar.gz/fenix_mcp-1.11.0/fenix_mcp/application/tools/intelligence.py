# SPDX-License-Identifier: MIT
"""Intelligence tool implementation (memories and smart operations)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator

from fenix_mcp.application.presenters import text
from fenix_mcp.application.tool_base import (
    MERMAID_HINT,
    CategoryStr,
    DateTimeStr,
    MarkdownStr,
    TagStr,
    TitleStr,
    Tool,
    ToolRequest,
    UUIDStr,
)
from fenix_mcp.domain.intelligence import IntelligenceService, build_metadata
from fenix_mcp.infrastructure.context import AppContext


class IntelligenceAction(str, Enum):
    def __new__(cls, value: str, description: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    SMART_CREATE = (
        "memory_smart_create",
        "Creates intelligent memories with similarity analysis.",
    )
    QUERY = ("memory_query", "Lists memories applying filters and text search.")
    GET = ("memory_get", "Gets memory details and content by ID.")
    SIMILARITY = ("memory_similarity", "Finds memories similar to a base content.")
    CONSOLIDATE = (
        "memory_consolidate",
        "Consolidates multiple memories into a primary one.",
    )
    UPDATE = ("memory_update", "Updates fields of an existing memory.")
    DELETE = ("memory_delete", "Removes a memory by ID.")
    HELP = ("memory_help", "Shows supported actions and their uses.")

    @classmethod
    def choices(cls) -> List[str]:
        return [member.value for member in cls]

    @classmethod
    def formatted_help(cls) -> str:
        lines = [
            "| **Action** | **Description** |",
            "| --- | --- |",
        ]
        for member in cls:
            lines.append(f"| `{member.value}` | {member.description} |")
        return "\n".join(lines)


ACTION_FIELD_DESCRIPTION = (
    "Intelligence action to execute. Use one of the values: "
    + ", ".join(
        f"`{member.value}` ({member.description.rstrip('.')})."
        for member in IntelligenceAction
    )
)


class IntelligenceRequest(ToolRequest):
    action: IntelligenceAction = Field(description=ACTION_FIELD_DESCRIPTION)
    title: Optional[TitleStr] = Field(default=None, description="Memory title.")
    content: Optional[MarkdownStr] = Field(
        default=None, description=f"Memory content/text (Markdown).{MERMAID_HINT}"
    )
    metadata: Optional[MarkdownStr] = Field(
        default=None,
        description="Structured memory metadata (pipe format, compact toml, etc.).",
    )
    context: Optional[str] = Field(default=None, description="Additional context.")
    source: Optional[str] = Field(default=None, description="Memory source.")
    importance: Optional[str] = Field(
        default=None,
        description="Memory importance level (low, medium, high, critical).",
    )
    include_content: bool = Field(
        default=False,
        description="Return full memory content? Set true to include the full text.",
    )
    include_metadata: bool = Field(
        default=False,
        description="Return full memory metadata? Set true to include the raw field.",
    )
    tags: Optional[List[TagStr]] = Field(
        default=None,
        description='Memory tags. REQUIRED for create. Format: JSON array of strings, e.g.: ["tag1", "tag2"]. Do not use a single string.',
        json_schema_extra={"example": ["tag1", "tag2", "tag3"]},
    )

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v: Any) -> Optional[List[str]]:
        """Validate and normalize tags field."""
        if v is None or v == "":
            return None

        # If it's already a list, return as is
        if isinstance(v, (list, tuple, set)):
            return [str(item).strip() for item in v if str(item).strip()]

        # If it's a string, try to parse as JSON
        if isinstance(v, str):
            try:
                import json

                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except (json.JSONDecodeError, TypeError):
                pass

            # If JSON parsing fails, treat as comma-separated string
            return [item.strip() for item in v.split(",") if item.strip()]

        # For any other type, convert to string and wrap in list
        return [str(v).strip()] if str(v).strip() else None

    limit: int = Field(default=20, ge=1, le=100, description="Result limit.")
    offset: int = Field(default=0, ge=0, description="Pagination offset.")
    query: Optional[str] = Field(default=None, description="Search term.")
    category: Optional[CategoryStr] = Field(
        default=None, description="Category for filtering."
    )
    date_from: Optional[DateTimeStr] = Field(
        default=None, description="Start date filter (ISO 8601)."
    )
    date_to: Optional[DateTimeStr] = Field(
        default=None, description="End date filter (ISO 8601)."
    )
    threshold: float = Field(
        default=0.8, ge=0, le=1, description="Minimum similarity threshold."
    )
    max_results: int = Field(
        default=5, ge=1, le=20, description="Maximum similar memories."
    )
    memory_ids: Optional[List[UUIDStr]] = Field(
        default=None, description="Memory IDs for consolidation (UUIDs)."
    )
    strategy: str = Field(default="merge", description="Consolidation strategy.")
    time_range: str = Field(default="month", description="Time window for analytics.")
    group_by: str = Field(default="category", description="Grouping for analytics.")
    id: Optional[UUIDStr] = Field(default=None, description="Memory ID (UUID).")
    documentation_item_id: Optional[UUIDStr] = Field(
        default=None, description="Related documentation ID (UUID)."
    )
    mode_id: Optional[UUIDStr] = Field(
        default=None, description="Related mode ID (UUID)."
    )
    rule_id: Optional[UUIDStr] = Field(
        default=None, description="Related rule ID (UUID)."
    )
    work_item_id: Optional[UUIDStr] = Field(
        default=None, description="Related work item ID (UUID)."
    )
    sprint_id: Optional[UUIDStr] = Field(
        default=None, description="Related sprint ID (UUID)."
    )


class IntelligenceTool(Tool):
    name = "intelligence"
    description = "Fenix Cloud intelligence operations (memories and smart operations)."
    request_model = IntelligenceRequest

    def __init__(self, context: AppContext):
        self._context = context
        self._service = IntelligenceService(context.api_client, context.logger)

    async def run(self, payload: IntelligenceRequest, context: AppContext):
        action = payload.action
        if action is IntelligenceAction.HELP:
            return await self._handle_help()
        if action is IntelligenceAction.SMART_CREATE:
            return await self._handle_smart_create(payload)
        if action is IntelligenceAction.QUERY:
            return await self._handle_query(payload)
        if action is IntelligenceAction.GET:
            return await self._handle_get(payload)
        if action is IntelligenceAction.SIMILARITY:
            return await self._handle_similarity(payload)
        if action is IntelligenceAction.CONSOLIDATE:
            return await self._handle_consolidate(payload)
        if action is IntelligenceAction.UPDATE:
            return await self._handle_update(payload)
        if action is IntelligenceAction.DELETE:
            return await self._handle_delete(payload)
        return text(
            "❌ Invalid action for intelligence.\n\nChoose one of the values:\n"
            + "\n".join(f"- `{value}`" for value in IntelligenceAction.choices())
        )

    async def _handle_smart_create(self, payload: IntelligenceRequest):
        if not payload.title or not payload.content:
            return text("❌ Provide title and content to create a memory.")

        if not payload.metadata or not payload.metadata.strip():
            return text("❌ Provide metadata to create a memory.")

        if not payload.source or not payload.source.strip():
            return text("❌ Provide source to create a memory.")

        try:
            normalized_tags = _ensure_tag_sequence(payload.tags)
        except ValueError as exc:
            return text(f"❌ {exc}")

        if not normalized_tags or len(normalized_tags) == 0:
            return text("❌ Provide tags to create a memory.")

        memory = await self._service.smart_create_memory(
            title=payload.title,
            content=payload.content,
            metadata=payload.metadata,
            context=payload.context,
            source=payload.source,
            importance=payload.importance,
            tags=normalized_tags,
        )
        lines = [
            "🧠 **Memory created successfully!**",
            f"ID: {memory.get('memoryId') or memory.get('id', 'N/A')}",
            f"Action: {memory.get('action') or 'created'}",
            f"Similarity: {format_percentage(memory.get('similarity'))}",
            f"Tags: {', '.join(memory.get('tags', [])) or 'Automatic'}",
            f"Category: {memory.get('category') or 'Automatic'}",
        ]
        return text("\n".join(lines))

    async def _handle_query(self, payload: IntelligenceRequest):
        memories = await self._service.query_memories(
            limit=payload.limit,
            offset=payload.offset,
            query=payload.query,
            tags=payload.tags,
            include_content=payload.include_content,
            include_metadata=payload.include_metadata,
            modeId=payload.mode_id,
            ruleId=payload.rule_id,
            workItemId=payload.work_item_id,
            sprintId=payload.sprint_id,
            documentationItemId=payload.documentation_item_id,
            category=payload.category,
            dateFrom=payload.date_from,
            dateTo=payload.date_to,
            importance=payload.importance,
        )
        if not memories:
            return text("🧠 No memories found.")
        body = "\n\n".join(_format_memory(mem) for mem in memories)
        return text(f"🧠 **Memories ({len(memories)}):**\n\n{body}")

    async def _handle_get(self, payload: IntelligenceRequest):
        if not payload.id:
            return text("❌ Provide the memory ID to get details.")
        memory = await self._service.get_memory(
            payload.id, include_content=True, include_metadata=True
        )
        return text(_format_memory(memory, show_content=True))

    async def _handle_similarity(self, payload: IntelligenceRequest):
        if not payload.content:
            return text("❌ Provide the base content to compare similarity.")
        memories = await self._service.similar_memories(
            content=payload.content,
            threshold=payload.threshold,
            max_results=payload.max_results,
        )
        if not memories:
            return text("🔍 No similar memories found.")
        body = "\n\n".join(
            f"🔍 **{mem.get('title', 'Untitled')}**\n   Similarity: {format_percentage(mem.get('finalScore'))}\n   ID: {mem.get('memoryId', 'N/A')}"
            for mem in memories
        )
        return text(f"🔍 **Similar memories ({len(memories)}):**\n\n{body}")

    async def _handle_consolidate(self, payload: IntelligenceRequest):
        if not payload.memory_ids or len(payload.memory_ids) < 2:
            return text("❌ Provide at least 2 memory IDs to consolidate.")
        result = await self._service.consolidate_memories(
            memory_ids=payload.memory_ids,
            strategy=payload.strategy,
        )
        lines = [
            "🔄 **Consolidation complete!**",
            f"Primary memory: {result.get('primary_memory_id', 'N/A')}",
            f"Consolidated: {result.get('consolidated_count', 'N/A')}",
            f"Action executed: {result.get('action', 'N/A')}",
        ]
        return text("\n".join(lines))

    async def _handle_update(self, payload: IntelligenceRequest):
        if not payload.id:
            return text("❌ Provide the memory ID for update.")
        existing = await self._service.get_memory(
            payload.id, include_content=False, include_metadata=True
        )
        try:
            normalized_tags = _ensure_tag_sequence(payload.tags)
        except ValueError as exc:
            return text(f"❌ {exc}")
        metadata = build_metadata(
            payload.metadata,
            importance=payload.importance,
            tags=normalized_tags,
            source=payload.source,
            existing=existing.get("metadata") if isinstance(existing, dict) else None,
        )
        update_fields: Dict[str, Any] = {
            "title": payload.title,
            "content": payload.content,
            "metadata": metadata,
            "tags": normalized_tags,
            "documentation_item_id": payload.documentation_item_id,
            "mode_id": payload.mode_id,
            "rule_id": payload.rule_id,
            "work_item_id": payload.work_item_id,
            "sprint_id": payload.sprint_id,
            "importance": payload.importance,
        }
        memory = await self._service.update_memory(payload.id, **update_fields)
        return text(
            "\n".join(
                [
                    "✅ **Memory updated!**",
                    f"ID: {memory.get('id', payload.id)}",
                    f"Title: {memory.get('title', 'N/A')}",
                    f"Priority: {memory.get('priority_score', 'N/A')}",
                ]
            )
        )

    async def _handle_delete(self, payload: IntelligenceRequest):
        if not payload.id:
            return text("❌ Provide the memory ID to remove.")
        await self._service.delete_memory(payload.id)
        return text(f"🗑️ Memory {payload.id} removed successfully.")

    async def _handle_help(self):
        return text(
            "📚 **Available actions for intelligence**\n\n"
            + IntelligenceAction.formatted_help()
        )


def _format_memory(memory: Dict[str, Any], *, show_content: bool = False) -> str:
    lines = [
        f"🧠 **{memory.get('title', 'Untitled')}**",
        f"ID: {memory.get('id', memory.get('memoryId', 'N/A'))}",
        f"Category: {memory.get('category', 'N/A')}",
        f"Tags: {', '.join(memory.get('tags', [])) or 'None'}",
        f"Importance: {memory.get('importance', 'N/A')}",
        f"Accesses: {memory.get('access_count', 'N/A')}",
    ]
    if show_content and memory.get("content"):
        lines.append("")
        lines.append("**Content:**")
        lines.append(memory.get("content"))
    return "\n".join(lines)


def format_percentage(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value * 100:.1f}%"


def _ensure_tag_sequence(raw: Optional[Any]) -> Optional[List[str]]:
    if raw is None or raw == "":
        return None
    if isinstance(raw, (list, tuple, set)):
        result = [str(item).strip() for item in raw if str(item).strip()]
        return result or None
    if isinstance(raw, str):
        # Try to parse as JSON array first
        try:
            import json

            parsed = json.loads(raw)
            if isinstance(parsed, list):
                result = [str(item).strip() for item in parsed if str(item).strip()]
                return result or None
        except (json.JSONDecodeError, TypeError):
            pass

        raise ValueError(
            "The `tags` field must be sent as a JSON array, for example: "
            '["tag1", "tag2"].'
        )
    return [str(raw).strip()]
