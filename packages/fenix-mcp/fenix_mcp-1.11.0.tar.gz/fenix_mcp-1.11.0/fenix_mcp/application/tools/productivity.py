# SPDX-License-Identifier: MIT
"""Productivity tool implementation (TODO operations)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

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
from fenix_mcp.domain.productivity import ProductivityService
from fenix_mcp.infrastructure.context import AppContext


class TodoAction(str, Enum):
    def __new__(cls, value: str, description: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    CREATE = ("todo_create", "Creates a new TODO.")
    LIST = (
        "todo_list",
        "Lists TODOs. By default returns only pending and in_progress. "
        "To filter by status, use status parameter with values: pending (backlog), in_progress, completed, cancelled.",
    )
    GET = ("todo_get", "Gets TODO details and content by ID.")
    UPDATE = ("todo_update", "Updates fields of an existing TODO.")
    DELETE = ("todo_delete", "Removes a TODO by ID.")
    STATS = ("todo_stats", "Returns aggregated TODO statistics.")
    SEARCH = ("todo_search", "Searches TODOs by text term.")
    OVERDUE = ("todo_overdue", "Lists overdue TODOs.")
    UPCOMING = ("todo_upcoming", "Lists TODOs with upcoming due dates.")
    CATEGORIES = ("todo_categories", "Lists registered categories.")
    TAGS = ("todo_tags", "Lists registered tags.")
    HELP = ("todo_help", "Shows supported actions and their uses.")

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
    "Productivity action (TODO). Choose one of the values: "
    + ", ".join(
        f"`{member.value}` ({member.description.rstrip('.')})." for member in TodoAction
    )
)


class ProductivityRequest(ToolRequest):
    action: TodoAction = Field(description=ACTION_FIELD_DESCRIPTION)
    id: Optional[UUIDStr] = Field(default=None, description="TODO item ID (UUID).")
    title: Optional[TitleStr] = Field(
        default=None, description="TODO title (required for create)."
    )
    content: Optional[MarkdownStr] = Field(
        default=None,
        description=f"Markdown content (required for create).{MERMAID_HINT}",
    )
    status: Optional[str] = Field(
        default=None,
        description="TODO status. Values: pending (shown as 'backlog' in UI), in_progress, completed, cancelled.",
    )
    priority: Optional[str] = Field(
        default=None, description="TODO priority (low, medium, high, urgent)."
    )
    category: Optional[CategoryStr] = Field(
        default=None, description="Optional category."
    )
    tags: Optional[List[TagStr]] = Field(default=None, description="Tag list.")
    due_date: Optional[DateTimeStr] = Field(
        default=None, description="TODO due date (ISO 8601)."
    )
    limit: int = Field(
        default=20, ge=1, le=100, description="Result limit for list/search."
    )
    offset: int = Field(default=0, ge=0, description="Pagination offset.")
    query: Optional[str] = Field(default=None, description="Search term.")
    days: Optional[int] = Field(
        default=None, ge=1, le=30, description="Day window for upcoming."
    )


class ProductivityTool(Tool):
    name = "productivity"
    description = "Fenix Cloud productivity operations (TODOs)."
    request_model = ProductivityRequest

    def __init__(self, context: AppContext):
        self._context = context
        self._service = ProductivityService(context.api_client, context.logger)

    async def run(self, payload: ProductivityRequest, context: AppContext):
        action = payload.action
        if action is TodoAction.HELP:
            return await self._handle_help()
        if action is TodoAction.CREATE:
            return await self._handle_create(payload)
        if action is TodoAction.LIST:
            return await self._handle_list(payload)
        if action is TodoAction.GET:
            return await self._handle_get(payload)
        if action is TodoAction.UPDATE:
            return await self._handle_update(payload)
        if action is TodoAction.DELETE:
            return await self._handle_delete(payload)
        if action is TodoAction.STATS:
            return await self._handle_stats()
        if action is TodoAction.SEARCH:
            return await self._handle_search(payload)
        if action is TodoAction.OVERDUE:
            return await self._handle_overdue()
        if action is TodoAction.UPCOMING:
            return await self._handle_upcoming(payload)
        if action is TodoAction.CATEGORIES:
            return await self._handle_categories()
        if action is TodoAction.TAGS:
            return await self._handle_tags()
        return text(
            "❌ Invalid action for productivity.\n\nChoose one of the values:\n"
            + "\n".join(f"- `{value}`" for value in TodoAction.choices())
        )

    async def _handle_create(self, payload: ProductivityRequest):
        if not payload.title or not payload.content or not payload.due_date:
            return text("❌ Provide title, content and due_date to create a TODO.")
        todo = await self._service.create_todo(
            title=payload.title,
            content=payload.content,
            status=payload.status or "pending",
            priority=payload.priority or "medium",
            category=payload.category,
            tags=payload.tags or [],
            due_date=payload.due_date,
        )
        return text(self._format_single(todo, header="✅ TODO created successfully!"))

    async def _handle_list(self, payload: ProductivityRequest):
        # If no status filter provided, fetch pending and in_progress only
        if payload.status:
            todos = await self._service.list_todos(
                limit=payload.limit,
                offset=payload.offset,
                status=payload.status,
                priority=payload.priority,
                category=payload.category,
            )
        else:
            # Fetch pending and in_progress separately and merge
            pending = await self._service.list_todos(
                limit=payload.limit,
                offset=payload.offset,
                status="pending",
                priority=payload.priority,
                category=payload.category,
            )
            in_progress = await self._service.list_todos(
                limit=payload.limit,
                offset=payload.offset,
                status="in_progress",
                priority=payload.priority,
                category=payload.category,
            )
            todos = pending + in_progress
        if not todos:
            return text("📋 No TODOs found.")
        body = "\n\n".join(ProductivityService.format_todo(todo) for todo in todos)
        return text(f"📋 **TODOs ({len(todos)}):**\n\n{body}")

    async def _handle_get(self, payload: ProductivityRequest):
        if not payload.id:
            return text("❌ Provide the ID to get a TODO.")
        todo = await self._service.get_todo(payload.id)
        return text(
            self._format_single(todo, header="📋 TODO found", show_content=True)
        )

    async def _handle_update(self, payload: ProductivityRequest):
        if not payload.id:
            return text("❌ Provide the ID to update a TODO.")
        fields = {
            "title": payload.title,
            "content": payload.content,
            "status": payload.status,
            "priority": payload.priority,
            "category": payload.category,
            "tags": payload.tags,
            "due_date": payload.due_date,
        }
        todo = await self._service.update_todo(payload.id, **fields)
        return text(self._format_single(todo, header="✅ TODO updated"))

    async def _handle_delete(self, payload: ProductivityRequest):
        if not payload.id:
            return text("❌ Provide the ID to delete a TODO.")
        await self._service.delete_todo(payload.id)
        return text(f"🗑️ TODO {payload.id} removed successfully.")

    async def _handle_stats(self):
        stats = await self._service.stats()
        lines = ["📊 **TODO Statistics**"]
        for key, value in (stats or {}).items():
            lines.append(f"- {key}: {value}")
        return text("\n".join(lines))

    async def _handle_search(self, payload: ProductivityRequest):
        if not payload.query:
            return text("❌ Provide a search term (query).")
        todos = await self._service.search(
            payload.query, limit=payload.limit, offset=payload.offset
        )
        if not todos:
            return text("🔍 No TODOs found for the search.")
        body = "\n\n".join(ProductivityService.format_todo(todo) for todo in todos)
        return text(f"🔍 **Search results ({len(todos)}):**\n\n{body}")

    async def _handle_overdue(self):
        todos = await self._service.overdue()
        if not todos:
            return text("✅ No overdue TODOs at the moment.")
        body = "\n\n".join(ProductivityService.format_todo(todo) for todo in todos)
        return text(f"⏰ **Overdue TODOs ({len(todos)}):**\n\n{body}")

    async def _handle_upcoming(self, payload: ProductivityRequest):
        todos = await self._service.upcoming(days=payload.days)
        if not todos:
            return text("📅 No TODOs scheduled for the specified period.")
        body = "\n\n".join(ProductivityService.format_todo(todo) for todo in todos)
        header = f"📅 Scheduled TODOs ({len(todos)}):"
        if payload.days:
            header += f" next {payload.days} days"
        return text(f"{header}\n\n{body}")

    async def _handle_categories(self):
        categories = await self._service.categories()
        if not categories:
            return text("🏷️ No categories registered yet.")
        body = "\n".join(f"- {category}" for category in categories)
        return text(f"🏷️ **Categories in use:**\n{body}")

    async def _handle_tags(self):
        tags = await self._service.tags()
        if not tags:
            return text("🔖 No tags registered yet.")
        body = "\n".join(f"- {tag}" for tag in tags)
        return text(f"🔖 **Tags in use:**\n{body}")

    async def _handle_help(self):
        return text(
            "📚 **Available actions for productivity**\n\n"
            + TodoAction.formatted_help()
        )

    @staticmethod
    def _format_single(
        todo: Dict[str, Any], *, header: str, show_content: bool = False
    ) -> str:
        return "\n".join(
            [
                header,
                "",
                ProductivityService.format_todo(todo, show_content=show_content),
            ]
        )
