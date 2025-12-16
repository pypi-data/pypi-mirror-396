# SPDX-License-Identifier: MIT
"""User configuration tool implementation."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from fenix_mcp.application.presenters import text
from fenix_mcp.application.tool_base import (
    MarkdownStr,
    TitleStr,
    Tool,
    ToolRequest,
    UUIDStr,
)
from fenix_mcp.domain.user_config import UserConfigService, _strip_none
from fenix_mcp.infrastructure.context import AppContext


class UserConfigAction(str, Enum):
    def __new__(cls, value: str, description: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    CREATE = ("create", "Creates a new user core document.")
    LIST = ("list", "Lists documents with optional pagination.")
    GET = ("get", "Gets details of a specific document.")
    UPDATE = ("update", "Updates fields of an existing document.")
    DELETE = ("delete", "Removes a document.")
    HELP = ("help", "Shows available actions and their uses.")

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


ACTION_FIELD_DESCRIPTION = "Action to execute. Choose one of the values: " + ", ".join(
    f"`{member.value}` ({member.description.rstrip('.')})."
    for member in UserConfigAction
)


class UserConfigRequest(ToolRequest):
    action: UserConfigAction = Field(description=ACTION_FIELD_DESCRIPTION)
    id: Optional[UUIDStr] = Field(default=None, description="Document ID (UUID).")
    name: Optional[TitleStr] = Field(default=None, description="Document name.")
    content: Optional[MarkdownStr] = Field(
        default=None, description="Content in Markdown/JSON."
    )
    mode_id: Optional[UUIDStr] = Field(
        default=None, description="Associated mode ID (UUID)."
    )
    is_default: Optional[bool] = Field(
        default=None, description="Marks the document as default."
    )
    metadata: Optional[MarkdownStr] = Field(
        default=None, description="Structured document metadata (Markdown)."
    )
    limit: int = Field(default=20, ge=1, le=100, description="Listing limit.")
    offset: int = Field(default=0, ge=0, description="Listing offset.")
    return_content: Optional[bool] = Field(
        default=None, description="Return full content."
    )


class UserConfigTool(Tool):
    name = "user_config"
    description = "Manages user configuration documents (Core Documents)."
    request_model = UserConfigRequest

    def __init__(self, context: AppContext):
        self._context = context
        self._service = UserConfigService(context.api_client)

    async def run(self, payload: UserConfigRequest, context: AppContext):
        action = payload.action
        if action is UserConfigAction.HELP:
            return await self._handle_help()
        if action is UserConfigAction.CREATE:
            if not payload.name or not payload.content:
                return text("❌ Provide name and content to create the document.")
            doc = await self._service.create(
                _strip_none(
                    {
                        "name": payload.name,
                        "content": payload.content,
                        "mode_id": payload.mode_id,
                        "is_default": payload.is_default,
                        "metadata": payload.metadata,
                    }
                )
            )
            return text(_format_doc(doc, header="✅ Document created"))

        if action is UserConfigAction.LIST:
            docs = await self._service.list(
                limit=payload.limit,
                offset=payload.offset,
                returnContent=payload.return_content,
            )
            if not docs:
                return text("📂 No documents found.")
            body = "\n\n".join(_format_doc(doc) for doc in docs)
            return text(f"📂 **Documents ({len(docs)}):**\n\n{body}")

        if action is UserConfigAction.GET:
            if not payload.id:
                return text("❌ Provide the document ID.")
            doc = await self._service.get(
                payload.id,
                returnContent=payload.return_content,
            )
            return text(_format_doc(doc, header="📂 Document details"))

        if action is UserConfigAction.UPDATE:
            if not payload.id:
                return text("❌ Provide the document ID to update.")
            data = _strip_none(
                {
                    "name": payload.name,
                    "content": payload.content,
                    "mode_id": payload.mode_id,
                    "is_default": payload.is_default,
                    "metadata": payload.metadata,
                }
            )
            doc = await self._service.update(payload.id, data)
            return text(_format_doc(doc, header="✅ Document updated"))

        if action is UserConfigAction.DELETE:
            if not payload.id:
                return text("❌ Provide the document ID.")
            await self._service.delete(payload.id)
            return text(f"🗑️ Document {payload.id} removed.")

        return text(
            "❌ Unsupported user_config action.\n\nChoose one of the values:\n"
            + "\n".join(f"- `{value}`" for value in UserConfigAction.choices())
        )

    async def _handle_help(self):
        return text(
            "📚 **Available actions for user_config**\n\n"
            + UserConfigAction.formatted_help()
        )


def _format_doc(doc: Dict[str, Any], header: Optional[str] = None) -> str:
    lines: List[str] = []
    if header:
        lines.append(header)
        lines.append("")
    lines.extend(
        [
            f"📂 **{doc.get('name', 'Unnamed')}**",
            f"ID: {doc.get('id', 'N/A')}",
            f"Default: {doc.get('is_default', False)}",
        ]
    )
    if doc.get("mode_id"):
        lines.append(f"Associated mode: {doc['mode_id']}")
    if doc.get("content") and len(doc["content"]) <= 400:
        lines.append("")
        lines.append(doc["content"])
    return "\n".join(lines)
