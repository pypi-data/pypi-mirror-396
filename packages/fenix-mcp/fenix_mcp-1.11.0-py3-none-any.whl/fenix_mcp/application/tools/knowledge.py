# SPDX-License-Identifier: MIT
"""Knowledge tool implementation updated for the expanded Fênix API."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from fenix_mcp.application.presenters import text
from fenix_mcp.application.tool_base import (
    MERMAID_HINT,
    CategoryStr,
    DateTimeStr,
    DescriptionStr,
    EmojiStr,
    LanguageStr,
    MarkdownStr,
    TagStr,
    TitleStr,
    Tool,
    ToolRequest,
    UUIDStr,
    VersionStr,
    sanitize_null,
    sanitize_null_list,
)
from fenix_mcp.domain.knowledge import KnowledgeService, _format_date
from fenix_mcp.infrastructure.context import AppContext


class KnowledgeAction(str, Enum):
    def __new__(cls, value: str, description: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    # Work items
    WORK_CREATE = (
        "work_create",
        "Creates a work item with title, status and optional links. Use parent_key (e.g., DVPT-0001) to set parent.",
    )
    WORK_LIST = (
        "work_list",
        "Lists work items with status, priority and context filters.",
    )
    WORK_GET = (
        "work_get",
        "Gets full details of a work item by ID or key (e.g., DVPT-0001).",
    )
    WORK_UPDATE = (
        "work_update",
        "Updates allowed fields of an existing work item (title, description, priority, story_points, tags, due_date).",
    )
    WORK_BACKLOG = ("work_backlog", "Lists backlog items for a team.")
    WORK_SEARCH = (
        "work_search",
        "Searches work items by text with additional filters.",
    )
    WORK_ANALYTICS = ("work_analytics", "Returns consolidated work item metrics.")
    WORK_BY_BOARD = ("work_by_board", "Lists work items associated with a board.")
    WORK_BY_SPRINT = ("work_by_sprint", "Lists work items associated with a sprint.")
    WORK_BY_EPIC = ("work_by_epic", "Lists work items associated with an epic.")
    WORK_CHILDREN = (
        "work_children",
        "Lists child work items of a parent item by ID or key (e.g., DVPT-0001).",
    )
    WORK_STATUS_UPDATE = (
        "work_status_update",
        "Updates only the status of a work item.",
    )
    WORK_ASSIGN_SPRINT = (
        "work_assign_sprint",
        "Assigns work items to a sprint.",
    )
    WORK_ASSIGN_TO_ME = (
        "work_assign_to_me",
        "Assigns a work item to the current user.",
    )
    WORK_MINE = (
        "work_mine",
        "Lists work items assigned to the current user. Automatically excludes items with status 'done' or 'cancelled'. Supports pagination via limit and offset parameters.",
    )
    WORK_BULK_CREATE = (
        "work_bulk_create",
        "Creates multiple work items atomically with hierarchy. Use temp_id as temporary identifier and parent_temp_id to reference parent in the same batch, or parent_key to reference an existing work item (e.g., TEMA-0056). Cannot use both parent_temp_id and parent_key on the same item. Example: [{temp_id:'epic-1', title:'My Epic', item_type:'epic', work_category:'backend'}, {temp_id:'task-1', parent_temp_id:'epic-1', title:'My Task', item_type:'task', work_category:'backend'}] or [{temp_id:'task-1', parent_key:'TEMA-0056', title:'My Task', item_type:'task', work_category:'backend'}]",
    )

    # Boards
    BOARD_LIST = ("board_list", "Lists available boards with optional filters.")
    BOARD_BY_TEAM = ("board_by_team", "Lists boards for a specific team.")
    BOARD_FAVORITES = ("board_favorites", "Lists boards marked as favorites.")
    BOARD_GET = ("board_get", "Gets board details by ID.")
    BOARD_COLUMNS = ("board_columns", "Lists columns configured for a board.")

    # Sprints
    SPRINT_LIST = ("sprint_list", "Lists available sprints with optional filters.")
    SPRINT_BY_TEAM = ("sprint_by_team", "Lists sprints associated with a team.")
    SPRINT_ACTIVE = ("sprint_active", "Gets the active sprint for a team.")
    SPRINT_GET = ("sprint_get", "Gets sprint details by ID.")
    SPRINT_WORK_ITEMS = (
        "sprint_work_items",
        "Lists work items linked to a sprint.",
    )

    # Modes
    MODE_CREATE = ("mode_create", "Creates a mode with content and optional metadata.")
    MODE_LIST = ("mode_list", "Lists registered modes.")
    MODE_GET = ("mode_get", "Gets full details of a mode.")
    MODE_UPDATE = ("mode_update", "Updates properties of an existing mode.")
    MODE_DELETE = ("mode_delete", "Removes a mode.")
    MODE_RULE_ADD = ("mode_rule_add", "Associates a rule with a mode.")
    MODE_RULE_REMOVE = (
        "mode_rule_remove",
        "Removes the association of a rule with a mode.",
    )
    MODE_RULES = ("mode_rules", "Lists rules associated with a mode.")

    # Rules
    RULE_CREATE = ("rule_create", "Creates a rule with content and metadata.")
    RULE_LIST = ("rule_list", "Lists registered rules.")
    RULE_GET = ("rule_get", "Gets rule details.")
    RULE_UPDATE = ("rule_update", "Updates an existing rule.")
    RULE_DELETE = ("rule_delete", "Removes a rule.")

    # Documentation - Navigation workflow: doc_full_tree -> doc_children -> doc_get
    DOC_CREATE = (
        "doc_create",
        "Creates a documentation item. Requires doc_emoji for page, api_doc, and guide types.",
    )
    DOC_LIST = (
        "doc_list",
        "Lists documentation items. Use doc_full_tree for hierarchical view.",
    )
    DOC_GET = (
        "doc_get",
        "Reads document content by ID. Get the ID from doc_full_tree or doc_children first.",
    )
    DOC_UPDATE = ("doc_update", "Updates a documentation item.")
    DOC_DELETE = ("doc_delete", "Removes a documentation item.")
    DOC_ROOTS = (
        "doc_roots",
        "Lists root folders. Use doc_children to navigate inside.",
    )
    DOC_RECENT = ("doc_recent", "Lists recently accessed documents.")
    DOC_ANALYTICS = ("doc_analytics", "Returns document analytics.")
    DOC_CHILDREN = (
        "doc_children",
        "Lists child documents of a folder by ID. Use this to navigate into folders.",
    )
    DOC_TREE = ("doc_tree", "Retrieves tree starting from a specific document.")
    DOC_FULL_TREE = (
        "doc_full_tree",
        "Retrieves complete documentation tree. Start here to find documents.",
    )
    DOC_MOVE = ("doc_move", "Moves a document to another parent.")
    DOC_PUBLISH = ("doc_publish", "Changes publication status of a document.")
    DOC_VERSION = ("doc_version", "Generates or retrieves a document version.")
    DOC_DUPLICATE = ("doc_duplicate", "Duplicates an existing document.")

    HELP = ("knowledge_help", "Shows available actions and their uses.")

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


ACTION_FIELD_DESCRIPTION = "Knowledge action. Choose one of the values: " + ", ".join(
    f"`{member.value}` ({member.description.rstrip('.')})."
    for member in KnowledgeAction
)


_ALLOWED_DOC_TYPES = {
    "folder",
    "page",
    "api_doc",
    "guide",
}


class KnowledgeRequest(ToolRequest):
    action: KnowledgeAction = Field(description=ACTION_FIELD_DESCRIPTION)
    id: Optional[UUIDStr] = Field(
        default=None, description="Primary resource ID (UUID)."
    )
    limit: int = Field(default=20, ge=1, le=100, description="Result limit.")
    offset: int = Field(
        default=0, ge=0, description="Pagination offset (when supported)."
    )
    board_id: Optional[UUIDStr] = Field(
        default=None, description="Associated board ID (UUID)."
    )
    sprint_id: Optional[UUIDStr] = Field(
        default=None, description="Associated sprint ID (UUID)."
    )
    epic_id: Optional[UUIDStr] = Field(
        default=None, description="Associated epic ID (UUID)."
    )
    query: Optional[str] = Field(default=None, description="Filter/search term.")
    return_content: Optional[bool] = Field(
        default=None, description="Return full content."
    )
    return_description: Optional[bool] = Field(
        default=None, description="Return full description."
    )
    return_metadata: Optional[bool] = Field(
        default=None, description="Return full metadata."
    )

    # Work item fields
    work_key: Optional[str] = Field(
        default=None,
        description="Work item key (e.g., DVPT-0001). Use this instead of id for work_get and work_children.",
    )
    work_title: Optional[TitleStr] = Field(default=None, description="Work item title.")
    work_description: Optional[MarkdownStr] = Field(
        default=None, description=f"Work item description (Markdown).{MERMAID_HINT}"
    )
    work_type: Optional[str] = Field(
        default="task",
        description="Work item type (epic, feature, story, task, subtask, bug).",
    )
    work_status: Optional[str] = Field(
        default=None,
        description="Work item status ID (UUID of TeamStatus).",
    )
    work_priority: Optional[str] = Field(
        default=None,
        description="Work item priority (critical, high, medium, low).",
    )
    work_category: Optional[str] = Field(
        default=None,
        description="Work item category/discipline. REQUIRED for work_create. Values: backend, frontend, mobile, fullstack, devops, infra, platform, sre, database, security, data, analytics, ai_ml, qa, automation, design, research, product, project, agile, support, operations, documentation, training, architecture, planning, development.",
    )
    story_points: Optional[int] = Field(
        default=None, ge=0, le=100, description="Story points (0-100)."
    )
    assignee_id: Optional[UUIDStr] = Field(
        default=None, description="Assignee ID (UUID)."
    )
    parent_id: Optional[UUIDStr] = Field(
        default=None,
        description="Parent item ID (UUID). Prefer using parent_key instead.",
    )
    parent_key: Optional[str] = Field(
        default=None,
        description="Parent item key (e.g., DVPT-0001). Use this to set the parent of a work item.",
    )
    work_due_date: Optional[DateTimeStr] = Field(
        default=None, description="Work item due date (ISO 8601)."
    )
    work_tags: Optional[List[TagStr]] = Field(
        default=None, description="Work item tags."
    )
    work_item_ids: Optional[List[UUIDStr]] = Field(
        default=None,
        description="List of work item IDs for batch operations (UUIDs).",
    )
    work_items: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description=(
            "List of work items for bulk create (max 50). Each item requires: "
            "temp_id (your temporary ID like 'epic-1', 'task-a'), title, item_type, work_category. "
            "Use parent_temp_id to set parent from same batch (e.g., parent_temp_id:'epic-1'), "
            "OR parent_key to set parent from existing work item (e.g., parent_key:'TEMA-0056'). "
            "Cannot use both parent_temp_id and parent_key on the same item. "
            "Optional: description, priority (low/medium/high/critical), story_points, tags, due_date. "
            'Example: [{"temp_id":"e1", "title":"Epic", "item_type":"epic", "work_category":"backend"}, '
            '{"temp_id":"t1", "parent_temp_id":"e1", "title":"Task", "item_type":"task", "work_category":"backend"}]'
        ),
    )

    # Mode fields
    mode_id: Optional[UUIDStr] = Field(
        default=None, description="Related mode ID (UUID)."
    )
    mode_name: Optional[TitleStr] = Field(default=None, description="Mode name.")
    mode_description: Optional[DescriptionStr] = Field(
        default=None, description="Mode description."
    )
    mode_content: Optional[MarkdownStr] = Field(
        default=None, description="Mode content (Markdown)."
    )
    mode_is_default: Optional[bool] = Field(
        default=None, description="Indicates if the mode is default."
    )
    mode_metadata: Optional[MarkdownStr] = Field(
        default=None, description="Mode metadata for AI processing."
    )

    # Rule fields
    rule_id: Optional[UUIDStr] = Field(
        default=None, description="Related rule ID (UUID)."
    )
    rule_name: Optional[TitleStr] = Field(default=None, description="Rule name.")
    rule_description: Optional[DescriptionStr] = Field(
        default=None, description="Rule description."
    )
    rule_content: Optional[MarkdownStr] = Field(
        default=None, description="Rule content (Markdown)."
    )
    rule_is_default: Optional[bool] = Field(default=None, description="Default rule.")
    rule_metadata: Optional[MarkdownStr] = Field(
        default=None, description="Rule metadata for AI processing."
    )

    # Documentation fields
    doc_title: Optional[TitleStr] = Field(
        default=None, description="Documentation title."
    )
    doc_description: Optional[DescriptionStr] = Field(
        default=None, description="Documentation description."
    )
    doc_content: Optional[MarkdownStr] = Field(
        default=None, description=f"Documentation content (Markdown).{MERMAID_HINT}"
    )
    doc_status: Optional[str] = Field(
        default=None,
        description="Documentation status (draft, review, published, archived).",
    )
    doc_type: Optional[str] = Field(
        default=None,
        description="Documentation type. Values: folder, page, api_doc, guide.",
    )
    doc_language: Optional[LanguageStr] = Field(
        default=None, description="Documentation language (e.g.: pt, en, pt-BR)."
    )
    doc_parent_id: Optional[UUIDStr] = Field(
        default=None, description="Parent document ID (UUID)."
    )
    doc_owner_id: Optional[UUIDStr] = Field(
        default=None, description="Owner ID (UUID)."
    )
    doc_reviewer_id: Optional[UUIDStr] = Field(
        default=None, description="Reviewer ID (UUID)."
    )
    doc_version: Optional[VersionStr] = Field(
        default=None, description="Document version (e.g.: 1.0, 2.1.3)."
    )
    doc_category: Optional[CategoryStr] = Field(default=None, description="Category.")
    doc_tags: Optional[List[TagStr]] = Field(default=None, description="Tags.")
    doc_position: Optional[int] = Field(
        default=None, ge=0, description="Desired position when moving documents."
    )
    doc_emoji: Optional[EmojiStr] = Field(
        default=None,
        description="Emoji displayed with the document. REQUIRED for page, api_doc, and guide types (not required for folder).",
    )
    doc_emote: Optional[EmojiStr] = Field(
        default=None, description="Alias for emoji, kept for compatibility."
    )
    doc_keywords: Optional[List[TagStr]] = Field(
        default=None, description="Keywords for search."
    )
    doc_is_public: Optional[bool] = Field(
        default=None, description="Whether the document is public."
    )


class KnowledgeTool(Tool):
    name = "knowledge"
    description = "Fenix Cloud knowledge operations (Work Items, Boards, Sprints, Modes, Rules, Docs)."
    request_model = KnowledgeRequest

    def __init__(self, context: AppContext):
        self._context = context
        self._service = KnowledgeService(context.api_client, context.logger)

    async def run(self, payload: KnowledgeRequest, context: AppContext):
        action = payload.action
        if action is KnowledgeAction.HELP:
            return await self._handle_help()
        if action.value.startswith("work_"):
            return await self._run_work(payload)
        if action.value.startswith("board_"):
            return await self._run_board(payload)
        if action.value.startswith("sprint_"):
            return await self._run_sprint(payload)
        if action.value.startswith("mode_"):
            return await self._run_mode(payload)
        if action.value.startswith("rule_"):
            return await self._run_rule(payload)
        if action.value.startswith("doc_"):
            return await self._run_doc(payload)
        return text(
            "❌ Invalid action for knowledge.\n\nChoose one of the values:\n"
            + "\n".join(f"- `{value}`" for value in KnowledgeAction.choices())
        )

    # ------------------------------------------------------------------
    # Work items
    # ------------------------------------------------------------------
    async def _run_work(self, payload: KnowledgeRequest):
        action = payload.action
        if action is KnowledgeAction.WORK_CREATE:
            if not payload.work_title:
                return text("❌ Provide work_title to create the item.")
            if not payload.work_category:
                return text(
                    "❌ Provide work_category to create the item. Values: backend, frontend, mobile, fullstack, devops, infra, platform, sre, database, security, data, analytics, ai_ml, qa, automation, design, research, product, project, agile, support, operations, documentation, training, architecture, planning, development."
                )

            # Resolve parent_key to parent_id if provided
            parent_id = payload.parent_id
            if payload.parent_key and not parent_id:
                parent_work = await self._service.work_get_by_key(payload.parent_key)
                parent_id = parent_work.get("id")

            work = await self._service.work_create(
                {
                    "title": payload.work_title,
                    "description": payload.work_description,
                    "item_type": payload.work_type,
                    "status_id": payload.work_status,
                    "priority": payload.work_priority,
                    "work_category": payload.work_category,
                    "story_points": payload.story_points,
                    "assignee_id": payload.assignee_id,
                    "sprint_id": payload.sprint_id,
                    "parent_id": parent_id,
                    "due_date": payload.work_due_date,
                    "tags": payload.work_tags,
                }
            )
            return text(_format_work(work, header="✅ Work item created"))

        if action is KnowledgeAction.WORK_LIST:
            items = await self._service.work_list(
                limit=payload.limit,
                offset=payload.offset,
                priority=payload.work_priority,
                type=payload.work_type,
                assignee=payload.assignee_id,
                sprint=payload.sprint_id,
            )
            if not items:
                return text("🎯 No work items found.")
            body = "\n\n".join(_format_work(item) for item in items)
            return text(f"🎯 **Work items ({len(items)}):**\n\n{body}")

        if action is KnowledgeAction.WORK_GET:
            # Support both id and work_key
            if payload.work_key:
                work = await self._service.work_get_by_key(payload.work_key)
            elif payload.id:
                work = await self._service.work_get(payload.id)
            else:
                return text("❌ Provide id or work_key to get the work item.")
            return text(
                _format_work(work, header="🎯 Work item details", show_description=True)
            )

        if action is KnowledgeAction.WORK_UPDATE:
            # Resolve work_key to id if needed
            work_id = payload.id
            if payload.work_key and not work_id:
                work_item = await self._service.work_get_by_key(payload.work_key)
                work_id = work_item.get("id")
            if not work_id:
                return text("❌ Provide id or work_key to update the work item.")

            # Only allow safe fields to be updated via MCP
            # Excluded: item_type, status_id, assignee_id, sprint_id, parent_id, work_category
            work = await self._service.work_update(
                work_id,
                {
                    "title": payload.work_title,
                    "description": payload.work_description,
                    "priority": payload.work_priority,
                    "story_points": payload.story_points,
                    "due_date": payload.work_due_date,
                    "tags": payload.work_tags,
                },
            )
            return text(_format_work(work, header="✅ Work item updated"))

        if action is KnowledgeAction.WORK_ASSIGN_TO_ME:
            # Resolve work_key to id if needed
            work_id = payload.id
            if payload.work_key and not work_id:
                work_item = await self._service.work_get_by_key(payload.work_key)
                work_id = work_item.get("id")
            if not work_id:
                return text("❌ Provide id or work_key to assign the work item.")
            work = await self._service.work_assign_to_me(work_id)
            return text(_format_work(work, header="✅ Work item assigned to you"))

        if action is KnowledgeAction.WORK_MINE:
            items = await self._service.work_mine(
                limit=payload.limit,
                offset=payload.offset,
            )
            if not items:
                return text("🎯 No work items assigned to you.")
            body = "\n\n".join(_format_work(item) for item in items)
            return text(f"🎯 **Your work items ({len(items)}):**\n\n{body}")

        if action is KnowledgeAction.WORK_BACKLOG:
            items = await self._service.work_backlog()
            if not items:
                return text("📋 Backlog empty.")
            body = "\n\n".join(_format_work(item) for item in items)
            return text(f"📋 **Backlog ({len(items)}):**\n\n{body}")

        if action is KnowledgeAction.WORK_SEARCH:
            query = sanitize_null(payload.query)
            if not query:
                return text("❌ Provide query to search work items.")
            items = await self._service.work_search(
                query=query,
                limit=payload.limit,
                item_type=payload.work_type,
                status=payload.work_status,
                priority=payload.work_priority,
                assignee_id=payload.assignee_id,
                tags=payload.work_tags,
            )
            if not items:
                return text("🔍 No work items found.")
            body = "\n\n".join(_format_work(item) for item in items)
            return text(f"🔍 **Results ({len(items)}):**\n\n{body}")

        if action is KnowledgeAction.WORK_ANALYTICS:
            analytics = await self._service.work_analytics()
            lines = ["📊 **Work Items Analytics**"]
            for key, value in analytics.items():
                lines.append(f"- {key}: {value}")
            return text("\n".join(lines))

        if action is KnowledgeAction.WORK_BY_BOARD:
            if not payload.board_id:
                return text("❌ Provide board_id to list items.")
            items = await self._service.work_by_board(board_id=payload.board_id)
            if not items:
                return text("🗂️ No work items for the specified board.")
            body = "\n\n".join(_format_work(item) for item in items)
            return text(f"🗂️ **Board items ({len(items)}):**\n\n{body}")

        if action is KnowledgeAction.WORK_BY_SPRINT:
            if not payload.sprint_id:
                return text("❌ Provide sprint_id to list items.")
            items = await self._service.work_by_sprint(sprint_id=payload.sprint_id)
            if not items:
                return text("🏃 No items linked to the specified sprint.")
            body = "\n\n".join(_format_work(item) for item in items)
            return text(f"🏃 **Sprint work items ({len(items)}):**\n\n{body}")

        if action is KnowledgeAction.WORK_BY_EPIC:
            if not payload.epic_id:
                return text("❌ Provide epic_id to list items.")
            items = await self._service.work_by_epic(epic_id=payload.epic_id)
            if not items:
                return text("📦 No items linked to the specified epic.")
            body = "\n\n".join(_format_work(item) for item in items)
            return text(f"📦 **Epic work items ({len(items)}):**\n\n{body}")

        if action is KnowledgeAction.WORK_CHILDREN:
            # Support both id and work_key
            work_id = payload.id
            if payload.work_key and not work_id:
                work_item = await self._service.work_get_by_key(payload.work_key)
                work_id = work_item.get("id")
            if not work_id:
                return text("❌ Provide id or work_key to list children.")
            items = await self._service.work_children(work_id)
            if not items:
                return text("👶 No child items found.")
            body = "\n\n".join(_format_work(item) for item in items)
            return text(f"👶 **Child work items ({len(items)}):**\n\n{body}")

        if action is KnowledgeAction.WORK_STATUS_UPDATE:
            # Resolve work_key to id if needed
            work_id = payload.id
            if payload.work_key and not work_id:
                work_item = await self._service.work_get_by_key(payload.work_key)
                work_id = work_item.get("id")
            if not work_id:
                return text("❌ Provide id or work_key to update status.")
            if not payload.work_status:
                return text("❌ Provide work_status (status_id) to update.")
            work = await self._service.work_update_status(
                work_id,
                {"status_id": payload.work_status},
            )
            return text(_format_work(work, header="✅ Status updated"))

        if action is KnowledgeAction.WORK_ASSIGN_SPRINT:
            if not payload.sprint_id:
                return text("❌ Provide sprint_id to assign items.")
            if not payload.work_item_ids:
                return text("❌ Provide work_item_ids with the list of IDs.")
            await self._service.work_assign_to_sprint(
                {
                    "sprint_id": payload.sprint_id,
                    "work_item_ids": payload.work_item_ids,
                }
            )
            count = len(payload.work_item_ids)
            return text(f"✅ {count} work item(s) assigned to sprint.")

        if action is KnowledgeAction.WORK_BULK_CREATE:
            if not payload.work_items:
                return text(
                    "❌ Provide work_items array. Each item requires: temp_id, title, item_type, work_category. "
                    "Optional: parent_temp_id OR parent_key (not both), description, priority, story_points, tags, due_date."
                )
            if len(payload.work_items) > 50:
                return text("❌ Maximum 50 items per bulk create.")

            # Validate required fields
            for i, item in enumerate(payload.work_items):
                if not item.get("temp_id"):
                    return text(f"❌ Item {i}: missing temp_id.")
                if not item.get("title"):
                    return text(f"❌ Item {i}: missing title.")
                if not item.get("item_type"):
                    return text(f"❌ Item {i}: missing item_type.")
                if not item.get("work_category"):
                    return text(f"❌ Item {i}: missing work_category.")
                if item.get("parent_temp_id") and item.get("parent_key"):
                    return text(
                        f"❌ Item {i}: cannot have both parent_temp_id and parent_key. Use one or the other."
                    )

            items = await self._service.work_bulk_create({"items": payload.work_items})

            # Format response as hierarchical tree
            lines = [f"✅ **{len(items)} work items created**", ""]

            # Build tree structure
            items_by_id: Dict[str, Dict[str, Any]] = {}
            children_map: Dict[str, List[str]] = {}
            root_ids: List[str] = []

            for item in items:
                item_id = item.get("id", "")
                items_by_id[item_id] = item
                parent_id = item.get("parent_id")
                if parent_id and parent_id in items_by_id:
                    if parent_id not in children_map:
                        children_map[parent_id] = []
                    children_map[parent_id].append(item_id)
                else:
                    root_ids.append(item_id)

            def format_tree_node(
                item_id: str, prefix: str = "", is_last: bool = True
            ) -> List[str]:
                """Format a node and its children as tree lines."""
                node_lines: List[str] = []
                item = items_by_id.get(item_id, {})
                key = item.get("key", "")
                title = item.get("title", "Untitled")
                item_type = item.get("item_type", "unknown")

                # Determine connector
                if prefix == "":
                    connector = ""
                    child_prefix = ""
                else:
                    connector = "└── " if is_last else "├── "
                    child_prefix = prefix + ("    " if is_last else "│   ")

                node_lines.append(f"{prefix}{connector}{item_type}: {key} - {title}")

                # Process children
                child_ids = children_map.get(item_id, [])
                for i, child_id in enumerate(child_ids):
                    is_last_child = i == len(child_ids) - 1
                    node_lines.extend(
                        format_tree_node(child_id, child_prefix, is_last_child)
                    )

                return node_lines

            # Format root items and their children
            for i, root_id in enumerate(root_ids):
                lines.extend(format_tree_node(root_id))
                if i < len(root_ids) - 1:
                    lines.append("")  # Add blank line between root trees

            # Summary by type
            type_counts: Dict[str, int] = {}
            for item in items:
                item_type = item.get("item_type", "unknown")
                type_counts[item_type] = type_counts.get(item_type, 0) + 1

            lines.append("")
            lines.append("**Summary by type:**")
            for item_type, count in sorted(type_counts.items()):
                lines.append(f"- {item_type}: {count}")

            return text("\n".join(lines))

        return text(
            "❌ Unsupported work item action.\n\nChoose one of the values:\n"
            + "\n".join(
                f"- `{value}`"
                for value in KnowledgeAction.choices()
                if value.startswith("work_")
            )
        )

    # ------------------------------------------------------------------
    # Boards
    # ------------------------------------------------------------------
    async def _run_board(self, payload: KnowledgeRequest):
        action = payload.action
        if action is KnowledgeAction.BOARD_LIST:
            boards = await self._service.board_list(
                limit=payload.limit, offset=payload.offset
            )
            if not boards:
                return text("🗂️ No boards found.")
            body = "\n\n".join(_format_board(board) for board in boards)
            return text(f"🗂️ **Boards ({len(boards)}):**\n\n{body}")

        if action is KnowledgeAction.BOARD_BY_TEAM:
            boards = await self._service.board_list_by_team()
            if not boards:
                return text("🗂️ No boards registered for the team.")
            body = "\n\n".join(_format_board(board) for board in boards)
            return text(f"🗂️ **Team boards ({len(boards)}):**\n\n{body}")

        if action is KnowledgeAction.BOARD_FAVORITES:
            boards = await self._service.board_favorites()
            if not boards:
                return text("⭐ No favorite boards registered.")
            body = "\n\n".join(_format_board(board) for board in boards)
            return text(f"⭐ **Favorite boards ({len(boards)}):**\n\n{body}")

        if action is KnowledgeAction.BOARD_GET:
            if not payload.board_id:
                return text("❌ Provide board_id to get details.")
            board = await self._service.board_get(payload.board_id)
            return text(_format_board(board, header="🗂️ Board details"))

        if action is KnowledgeAction.BOARD_COLUMNS:
            if not payload.board_id:
                return text("❌ Provide board_id to list columns.")
            columns = await self._service.board_columns(payload.board_id)
            if not columns:
                return text("📊 Board has no columns registered.")
            body = "\n".join(
                f"- {col.get('name', 'Unnamed')} (ID: {col.get('id')})"
                for col in columns
            )
            return text(f"📊 **Board columns:**\n{body}")

        return text(
            "❌ Unsupported board action.\n\nChoose one of the values:\n"
            + "\n".join(
                f"- `{value}`"
                for value in KnowledgeAction.choices()
                if value.startswith("board_")
            )
        )

    # ------------------------------------------------------------------
    # Sprints
    # ------------------------------------------------------------------
    async def _run_sprint(self, payload: KnowledgeRequest):
        action = payload.action
        if action is KnowledgeAction.SPRINT_LIST:
            sprints = await self._service.sprint_list(
                limit=payload.limit, offset=payload.offset
            )
            if not sprints:
                return text("🏃 No sprints found.")
            body = "\n\n".join(_format_sprint(sprint) for sprint in sprints)
            return text(f"🏃 **Sprints ({len(sprints)}):**\n\n{body}")

        if action is KnowledgeAction.SPRINT_BY_TEAM:
            sprints = await self._service.sprint_list_by_team()
            if not sprints:
                return text("🏃 No sprints registered for the team.")
            body = "\n\n".join(_format_sprint(sprint) for sprint in sprints)
            return text(f"🏃 **Team sprints ({len(sprints)}):**\n\n{body}")

        if action is KnowledgeAction.SPRINT_ACTIVE:
            sprint = await self._service.sprint_active()
            if not sprint:
                return text("⏳ No active sprint at the moment.")
            return text(_format_sprint(sprint, header="⏳ Active sprint"))

        if action is KnowledgeAction.SPRINT_GET:
            if not payload.sprint_id:
                return text("❌ Provide sprint_id to get details.")
            sprint = await self._service.sprint_get(payload.sprint_id)
            return text(_format_sprint(sprint, header="🏃 Sprint details"))

        if action is KnowledgeAction.SPRINT_WORK_ITEMS:
            if not payload.sprint_id:
                return text("❌ Provide sprint_id to list items.")
            items = await self._service.sprint_work_items(payload.sprint_id)
            if not items:
                return text("🏃 No items linked to the specified sprint.")
            body = "\n\n".join(_format_work(item) for item in items)
            return text(f"🏃 **Sprint items ({len(items)}):**\n\n{body}")

        return text(
            "❌ Unsupported sprint action.\n\nChoose one of the values:\n"
            + "\n".join(
                f"- `{value}`"
                for value in KnowledgeAction.choices()
                if value.startswith("sprint_")
            )
        )

    # ------------------------------------------------------------------
    # Modes
    # ------------------------------------------------------------------
    async def _run_mode(self, payload: KnowledgeRequest):
        action = payload.action
        if action is KnowledgeAction.MODE_CREATE:
            if not payload.mode_name:
                return text("❌ Provide mode_name to create the mode.")
            mode = await self._service.mode_create(
                {
                    "name": payload.mode_name,
                    "description": payload.mode_description,
                    "content": payload.mode_content,
                    "is_default": payload.mode_is_default,
                    "metadata": payload.mode_metadata,
                }
            )
            return text(_format_mode(mode, header="✅ Mode created"))

        if action is KnowledgeAction.MODE_LIST:
            modes = await self._service.mode_list(
                include_rules=payload.return_metadata,
                return_description=payload.return_description,
                return_metadata=payload.return_metadata,
            )
            if not modes:
                return text("🎭 No modes found.")
            body = "\n\n".join(_format_mode(mode) for mode in modes)
            return text(f"🎭 **Modes ({len(modes)}):**\n\n{body}")

        if action is KnowledgeAction.MODE_GET:
            if not payload.mode_id:
                return text("❌ Provide mode_id to get details.")
            mode = await self._service.mode_get(
                payload.mode_id,
                return_description=payload.return_description,
                return_metadata=payload.return_metadata,
            )
            # Buscar rules associadas ao mode
            associations = await self._service.mode_rules(payload.mode_id)
            rules = [assoc.get("rule", assoc) for assoc in associations]

            # Formatar resposta com rules (incluindo content)
            output = _format_mode(mode, header="🎭 Mode details", show_content=True)
            if rules:
                rules_parts = []
                for r in rules:
                    rule_text = f"### 📋 {r.get('name', 'Unnamed')}\n"
                    rule_text += f"ID: {r.get('id')}\n"
                    if r.get("content"):
                        rule_text += f"\n{r.get('content')}"
                    rules_parts.append(rule_text)
                output += f"\n\n**Rules ({len(rules)}):**\n\n" + "\n\n---\n\n".join(
                    rules_parts
                )
            return text(output)

        if action is KnowledgeAction.MODE_UPDATE:
            if not payload.mode_id:
                return text("❌ Provide mode_id to update.")
            mode = await self._service.mode_update(
                payload.mode_id,
                {
                    "name": payload.mode_name,
                    "description": payload.mode_description,
                    "content": payload.mode_content,
                    "is_default": payload.mode_is_default,
                    "metadata": payload.mode_metadata,
                },
            )
            return text(_format_mode(mode, header="✅ Mode updated"))

        if action is KnowledgeAction.MODE_DELETE:
            if not payload.mode_id:
                return text("❌ Provide mode_id to remove.")
            await self._service.mode_delete(payload.mode_id)
            return text(f"🗑️ Mode {payload.mode_id} removed.")

        if action is KnowledgeAction.MODE_RULE_ADD:
            if not payload.mode_id or not payload.rule_id:
                return text("❌ Provide mode_id and rule_id to associate.")
            link = await self._service.mode_rule_add(payload.mode_id, payload.rule_id)
            return text(
                "\n".join(
                    [
                        "🔗 **Rule associated with mode!**",
                        f"Mode: {link.get('modeId', payload.mode_id)}",
                        f"Rule: {link.get('ruleId', payload.rule_id)}",
                    ]
                )
            )

        if action is KnowledgeAction.MODE_RULE_REMOVE:
            if not payload.mode_id or not payload.rule_id:
                return text("❌ Provide mode_id and rule_id to remove the association.")
            await self._service.mode_rule_remove(payload.mode_id, payload.rule_id)
            return text("🔗 Association removed.")

        if action is KnowledgeAction.MODE_RULES:
            if payload.mode_id:
                associations = await self._service.mode_rules(payload.mode_id)
                context_label = f"mode {payload.mode_id}"
                # API retorna [{id, mode_id, rule_id, rule: {...}}] - extrair rule
                items = [assoc.get("rule", assoc) for assoc in associations]
            elif payload.rule_id:
                associations = await self._service.mode_rules_for_rule(payload.rule_id)
                context_label = f"rule {payload.rule_id}"
                # API retorna [{id, mode_id, rule_id, mode: {...}}] - extrair mode
                items = [assoc.get("mode", assoc) for assoc in associations]
            else:
                return text("❌ Provide mode_id or rule_id to list associations.")
            if not items:
                return text("🔗 No associations found.")
            body = "\n".join(
                f"- {item.get('name', 'Unnamed')} (ID: {item.get('id')})"
                for item in items
            )
            return text(f"🔗 **Associations for {context_label}:**\n{body}")

        return text(
            "❌ Unsupported mode action.\n\nChoose one of the values:\n"
            + "\n".join(
                f"- `{value}`"
                for value in KnowledgeAction.choices()
                if value.startswith("mode_")
            )
        )

    # ------------------------------------------------------------------
    # Rules
    # ------------------------------------------------------------------
    async def _run_rule(self, payload: KnowledgeRequest):
        action = payload.action
        if action is KnowledgeAction.RULE_CREATE:
            if not payload.rule_name or not payload.rule_content:
                return text("❌ Provide rule_name and rule_content.")
            rule = await self._service.rule_create(
                {
                    "name": payload.rule_name,
                    "description": payload.rule_description,
                    "content": payload.rule_content,
                    "is_default": payload.rule_is_default,
                    "metadata": payload.rule_metadata,
                }
            )
            return text(_format_rule(rule, header="✅ Rule created"))

        if action is KnowledgeAction.RULE_LIST:
            rules = await self._service.rule_list(
                return_description=payload.return_description,
                return_metadata=payload.return_metadata,
                return_modes=payload.return_metadata,
            )
            if not rules:
                return text("📋 No rules found.")
            body = "\n\n".join(_format_rule(rule) for rule in rules)
            return text(f"📋 **Rules ({len(rules)}):**\n\n{body}")

        if action is KnowledgeAction.RULE_GET:
            if not payload.rule_id:
                return text("❌ Provide rule_id to get details.")
            rule = await self._service.rule_get(
                payload.rule_id,
                return_description=payload.return_description,
                return_metadata=payload.return_metadata,
                return_modes=payload.return_metadata,
            )
            return text(_format_rule(rule, header="📋 Rule details", show_content=True))

        if action is KnowledgeAction.RULE_UPDATE:
            if not payload.rule_id:
                return text("❌ Provide rule_id to update.")
            rule = await self._service.rule_update(
                payload.rule_id,
                {
                    "name": payload.rule_name,
                    "description": payload.rule_description,
                    "content": payload.rule_content,
                    "is_default": payload.rule_is_default,
                    "metadata": payload.rule_metadata,
                },
            )
            return text(_format_rule(rule, header="✅ Rule updated"))

        if action is KnowledgeAction.RULE_DELETE:
            if not payload.rule_id:
                return text("❌ Provide rule_id to remove.")
            await self._service.rule_delete(payload.rule_id)
            return text(f"🗑️ Rule {payload.rule_id} removed.")

        return text(
            "❌ Unsupported rule action.\n\nChoose one of the values:\n"
            + "\n".join(
                f"- `{value}`"
                for value in KnowledgeAction.choices()
                if value.startswith("rule_")
            )
        )

    # ------------------------------------------------------------------
    # Documentation
    # ------------------------------------------------------------------
    async def _run_doc(self, payload: KnowledgeRequest):
        action = payload.action
        if action is KnowledgeAction.DOC_CREATE:
            if not payload.doc_title:
                return text("❌ Provide doc_title to create the documentation.")
            if payload.doc_type and payload.doc_type not in _ALLOWED_DOC_TYPES:
                allowed = ", ".join(sorted(_ALLOWED_DOC_TYPES))
                return text(
                    "❌ Invalid doc_type. Use one of the supported values: " + allowed
                )
            # Emoji is required for page, api_doc, guide (not for folder)
            doc_type = sanitize_null(payload.doc_type) or "page"
            emoji = sanitize_null(payload.doc_emoji or payload.doc_emote)
            if doc_type != "folder" and not emoji:
                return text(
                    "❌ Provide doc_emoji to create documentation. "
                    "Emoji is required for page, api_doc, and guide types."
                )
            doc = await self._service.doc_create(
                {
                    "title": payload.doc_title,
                    "description": sanitize_null(payload.doc_description),
                    "content": sanitize_null(payload.doc_content),
                    "status": sanitize_null(payload.doc_status),
                    "doc_type": sanitize_null(payload.doc_type),
                    "language": sanitize_null(payload.doc_language),
                    "parent_id": sanitize_null(payload.doc_parent_id),
                    "owner_user_id": sanitize_null(payload.doc_owner_id),
                    "reviewer_user_id": sanitize_null(payload.doc_reviewer_id),
                    "version": sanitize_null(payload.doc_version),
                    "category": sanitize_null(payload.doc_category),
                    "tags": sanitize_null_list(payload.doc_tags),
                    "emoji": sanitize_null(payload.doc_emoji or payload.doc_emote),
                    "keywords": sanitize_null_list(payload.doc_keywords),
                    "is_public": payload.doc_is_public,
                }
            )
            return text(_format_doc(doc, header="✅ Documentation created"))

        if action is KnowledgeAction.DOC_LIST:
            docs = await self._service.doc_list(
                limit=payload.limit,
                offset=payload.offset,
                returnContent=payload.return_content,
            )
            if not docs:
                return text("📄 No documentation found.")
            body = "\n\n".join(_format_doc(doc) for doc in docs)
            return text(f"📄 **Documents ({len(docs)}):**\n\n{body}")

        if action is KnowledgeAction.DOC_GET:
            if not payload.id:
                return text("❌ Provide the documentation ID.")
            doc = await self._service.doc_get(payload.id)
            return text(
                _format_doc(doc, header="📄 Documentation details", show_content=True)
            )

        if action is KnowledgeAction.DOC_UPDATE:
            if not payload.id:
                return text("❌ Provide the documentation ID.")
            if payload.doc_type and payload.doc_type not in _ALLOWED_DOC_TYPES:
                allowed = ", ".join(sorted(_ALLOWED_DOC_TYPES))
                return text(
                    "❌ Invalid doc_type. Use one of the supported values: " + allowed
                )
            doc = await self._service.doc_update(
                payload.id,
                {
                    "title": sanitize_null(payload.doc_title),
                    "description": sanitize_null(payload.doc_description),
                    "content": sanitize_null(payload.doc_content),
                    "status": sanitize_null(payload.doc_status),
                    "doc_type": sanitize_null(payload.doc_type),
                    "language": sanitize_null(payload.doc_language),
                    "parent_id": sanitize_null(payload.doc_parent_id),
                    "owner_user_id": sanitize_null(payload.doc_owner_id),
                    "reviewer_user_id": sanitize_null(payload.doc_reviewer_id),
                    "version": sanitize_null(payload.doc_version),
                    "category": sanitize_null(payload.doc_category),
                    "tags": sanitize_null_list(payload.doc_tags),
                    "emoji": sanitize_null(payload.doc_emoji or payload.doc_emote),
                    "keywords": sanitize_null_list(payload.doc_keywords),
                    "is_public": payload.doc_is_public,
                },
            )
            return text(_format_doc(doc, header="✅ Documentation updated"))

        if action is KnowledgeAction.DOC_DELETE:
            if not payload.id:
                return text("❌ Provide the documentation ID.")
            await self._service.doc_delete(payload.id)
            return text(f"🗑️ Documentation {payload.id} removed.")

        if action is KnowledgeAction.DOC_ROOTS:
            docs = await self._service.doc_roots()
            if not docs:
                return text("📚 No roots found.")
            body = "\n".join(
                f"- {doc.get('title', 'Untitled')} (ID: {doc.get('id')})"
                for doc in docs
            )
            return text(f"📚 **Documentation roots:**\n{body}")

        if action is KnowledgeAction.DOC_RECENT:
            docs = await self._service.doc_recent(
                limit=payload.limit,
            )
            if not docs:
                return text("🕒 No recent documentation found.")
            body = "\n\n".join(_format_doc(doc) for doc in docs)
            return text(f"🕒 **Recent documents ({len(docs)}):**\n\n{body}")

        if action is KnowledgeAction.DOC_ANALYTICS:
            analytics = await self._service.doc_analytics()
            lines = ["📊 **Documentation Analytics**"]
            for key, value in analytics.items():
                lines.append(f"- {key}: {value}")
            return text("\n".join(lines))

        if action is KnowledgeAction.DOC_CHILDREN:
            if not payload.id:
                return text("❌ Provide the documentation ID.")
            docs = await self._service.doc_children(payload.id)
            if not docs:
                return text("📄 No children registered for the specified document.")
            body = "\n".join(
                f"- {doc.get('title', 'Untitled')} (ID: {doc.get('id')})"
                for doc in docs
            )
            return text(f"📄 **Children:**\n{body}")

        if action is KnowledgeAction.DOC_TREE:
            if not payload.id:
                return text("❌ Provide the documentation ID.")
            tree = await self._service.doc_tree(payload.id)
            return text(f"🌳 **Documentation tree for {payload.id}:**\n{tree}")

        if action is KnowledgeAction.DOC_FULL_TREE:
            tree = await self._service.doc_full_tree()
            return text(f"🌳 **Full documentation tree:**\n{tree}")

        if action is KnowledgeAction.DOC_MOVE:
            if not payload.id:
                return text("❌ Provide the documentation ID.")
            if payload.doc_parent_id is None and payload.doc_position is None:
                return text("❌ Provide doc_parent_id, doc_position or both to move.")
            move_payload = {
                "new_parent_id": payload.doc_parent_id,
                "new_position": payload.doc_position,
            }
            doc = await self._service.doc_move(payload.id, move_payload)
            return text(_format_doc(doc, header="📦 Documentation moved"))

        if action is KnowledgeAction.DOC_PUBLISH:
            if not payload.id:
                return text("❌ Provide the documentation ID.")
            result = await self._service.doc_publish(payload.id)
            return text(f"🗞️ Document published: {result}")

        if action is KnowledgeAction.DOC_VERSION:
            if not payload.id:
                return text("❌ Provide the documentation ID.")
            if not payload.doc_version:
                return text(
                    "❌ Provide doc_version with the version number/identifier."
                )
            version_payload = {
                "title": payload.doc_title or f"Version {payload.doc_version}",
                "version": payload.doc_version,
                "content": payload.doc_content,
            }
            doc = await self._service.doc_version(payload.id, version_payload)
            return text(_format_doc(doc, header="🗞️ New version created"))

        if action is KnowledgeAction.DOC_DUPLICATE:
            if not payload.id:
                return text("❌ Provide the documentation ID.")
            if not payload.doc_title:
                return text("❌ Provide doc_title to name the copy.")
            doc = await self._service.doc_duplicate(
                payload.id,
                {
                    "title": payload.doc_title,
                },
            )
            return text(_format_doc(doc, header="🗂️ Document duplicated"))

        return text(
            "❌ Unsupported documentation action.\n\nChoose one of the values:\n"
            + "\n".join(
                f"- `{value}`"
                for value in KnowledgeAction.choices()
                if value.startswith("doc_")
            )
        )

    async def _handle_help(self):
        workflow_guide = """
## 📖 How to find and read a document

1. **doc_full_tree** → See complete folder structure with IDs
2. **doc_children(id)** → List contents of a specific folder
3. **doc_get(id)** → Read the document content

Example: To find "Overview" inside "Architecture" folder:
1. Call `doc_full_tree` to see all folders and documents
2. Find the folder "Architecture" and note its ID
3. Call `doc_children` with that ID to list its contents
4. Find "Overview" document and note its ID
5. Call `doc_get` with that ID to read the content

"""
        return text(
            "📚 **Available actions for knowledge**\n\n"
            + workflow_guide
            + KnowledgeAction.formatted_help()
        )


def _format_work(
    item: Dict[str, Any],
    *,
    header: Optional[str] = None,
    show_description: bool = False,
) -> str:
    lines: List[str] = []
    if header:
        lines.append(header)
        lines.append("")

    # Extract key (e.g., DVPT-0001)
    key = item.get("key", "")

    # Extract title
    title = item.get("title") or item.get("name") or "Untitled"

    # Extract type
    item_type = item.get("item_type") or item.get("type") or "unknown"

    # Extract status - prefer status object with name, fallback to status_id
    status_obj = item.get("status")
    if isinstance(status_obj, dict):
        status = status_obj.get("name", "unknown")
    else:
        status = item.get("status_id") or status_obj or "unknown"

    # Extract priority
    priority = item.get("priority") or item.get("priority_level") or "undefined"

    # Extract ID
    item_id = item.get("id", "N/A")

    # Extract assignee - check both assignee_id and assignee object
    assignee = item.get("assignee_id")
    if not assignee and item.get("assignee"):
        assignee_obj = item.get("assignee", {})
        assignee = assignee_obj.get("name") or assignee_obj.get("id")
    if not assignee:
        assignee = "N/A"

    # Format title line with key if available
    if key:
        lines.append(f"🎯 **[{key}] {title}**")
    else:
        lines.append(f"🎯 **{title}**")

    lines.extend(
        [
            f"ID: {item_id}",
            f"Type: {item_type}",
            f"Status: {status}",
            f"Priority: {priority}",
            f"Assignee: {assignee}",
        ]
    )

    # Add key as separate line if present (for easy reference)
    if key:
        lines.append(f"Key: {key}")

    if item.get("due_date") or item.get("dueDate"):
        lines.append(
            f"Due date: {_format_date(item.get('due_date') or item.get('dueDate'))}"
        )
    if item.get("tags"):
        tags = item.get("tags", [])
        if tags:
            lines.append(f"Tags: {', '.join(tags)}")

    # Show description only when explicitly requested (e.g., work_get)
    if show_description and item.get("description"):
        lines.append("")
        lines.append("**Description:**")
        lines.append(item.get("description"))

    return "\n".join(lines)


def _format_board(board: Dict[str, Any], header: Optional[str] = None) -> str:
    lines: List[str] = []
    if header:
        lines.append(header)
        lines.append("")
    lines.extend(
        [
            f"🗂️ **{board.get('name', 'Unnamed')}**",
            f"ID: {board.get('id', 'N/A')}",
            f"Team: {board.get('team_id', 'N/A')}",
            f"Columns: {len(board.get('columns', []))}",
        ]
    )
    return "\n".join(lines)


def _format_sprint(sprint: Dict[str, Any], header: Optional[str] = None) -> str:
    lines: List[str] = []
    if header:
        lines.append(header)
        lines.append("")
    lines.extend(
        [
            f"🏃 **{sprint.get('name', 'Unnamed')}**",
            f"ID: {sprint.get('id', 'N/A')}",
            f"Status: {sprint.get('status', 'N/A')}",
            f"Team: {sprint.get('team_id', 'N/A')}",
        ]
    )
    if sprint.get("start_date") or sprint.get("startDate"):
        lines.append(
            f"Start: {_format_date(sprint.get('start_date') or sprint.get('startDate'))}"
        )
    if sprint.get("end_date") or sprint.get("endDate"):
        lines.append(
            f"End: {_format_date(sprint.get('end_date') or sprint.get('endDate'))}"
        )
    return "\n".join(lines)


def _format_mode(
    mode: Dict[str, Any],
    *,
    header: Optional[str] = None,
    show_content: bool = False,
) -> str:
    lines: List[str] = []
    if header:
        lines.append(header)
        lines.append("")
    lines.extend(
        [
            f"🎭 **{mode.get('name', 'Unnamed')}**",
            f"ID: {mode.get('id', 'N/A')}",
            f"Default: {mode.get('is_default', False)}",
        ]
    )
    if mode.get("description"):
        lines.append(f"Description: {mode['description']}")
    if show_content and mode.get("content"):
        lines.append("")
        lines.append("**Content:**")
        lines.append(mode.get("content"))
    return "\n".join(lines)


def _format_rule(
    rule: Dict[str, Any],
    *,
    header: Optional[str] = None,
    show_content: bool = False,
) -> str:
    lines: List[str] = []
    if header:
        lines.append(header)
        lines.append("")
    lines.extend(
        [
            f"📋 **{rule.get('name', 'Unnamed')}**",
            f"ID: {rule.get('id', 'N/A')}",
            f"Default: {rule.get('is_default', False)}",
        ]
    )
    if rule.get("description"):
        lines.append(f"Description: {rule['description']}")
    if show_content and rule.get("content"):
        lines.append("")
        lines.append("**Content:**")
        lines.append(rule.get("content"))
    return "\n".join(lines)


def _format_doc(
    doc: Dict[str, Any],
    *,
    header: Optional[str] = None,
    show_content: bool = False,
) -> str:
    lines: List[str] = []
    if header:
        lines.append(header)
        lines.append("")
    lines.extend(
        [
            f"📄 **{doc.get('title') or doc.get('name', 'Untitled')}**",
            f"ID: {doc.get('id', 'N/A')}",
            f"Status: {doc.get('status', 'N/A')}",
            f"Team: {doc.get('team_id', 'N/A')}",
        ]
    )
    if doc.get("updated_at") or doc.get("updatedAt"):
        lines.append(
            f"Updated at: {_format_date(doc.get('updated_at') or doc.get('updatedAt'))}"
        )

    # Show content only when explicitly requested (e.g., doc_get)
    if show_content and doc.get("content"):
        lines.append("")
        lines.append("**Content:**")
        lines.append(doc.get("content"))

    return "\n".join(lines)


__all__ = ["KnowledgeTool", "KnowledgeAction"]
