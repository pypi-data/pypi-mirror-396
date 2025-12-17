# SPDX-License-Identifier: MIT
"""Initialization tool implementation."""

from __future__ import annotations

import json
from enum import Enum
from typing import List, Optional

from pydantic import Field

from fenix_mcp.application.presenters import text
from fenix_mcp.application.tool_base import Tool, ToolRequest
from fenix_mcp.domain.initialization import InitializationService
from fenix_mcp.infrastructure.context import AppContext


class InitializeAction(str, Enum):
    INIT = "init"
    SETUP = "setup"


class InitializeRequest(ToolRequest):
    action: InitializeAction = Field(description="Initialization operation to execute.")
    include_user_docs: bool = Field(
        default=True,
        description=(
            "Include personal documents during initialization (only for init action)."
        ),
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=200,
        description=("Maximum number of core/personal documents to load."),
    )
    answers: Optional[List[str]] = Field(
        default=None,
        description=("List of 9 text answers to process the personalized setup."),
    )


class InitializeTool(Tool):
    name = "initialize"
    description = (
        "Initializes the Fenix Cloud environment or processes the personalized setup."
    )
    request_model = InitializeRequest

    def __init__(self, context: AppContext):
        self._context = context
        self._service = InitializationService(context.api_client, context.logger)

    async def run(self, payload: InitializeRequest, context: AppContext):
        if payload.action is InitializeAction.INIT:
            return await self._handle_init(payload)
        if payload.action is InitializeAction.SETUP:
            return await self._handle_setup(payload)
        return text("❌ Unknown initialization action.")

    async def _handle_init(self, payload: InitializeRequest):
        try:
            data = await self._service.gather_data(
                include_user_docs=payload.include_user_docs,
                limit=payload.limit,
            )
        except Exception as exc:  # pragma: no cover - defensive
            self._context.logger.error("Initialize failed: %s", exc)
            return text(
                "❌ Failed to load initialization data. "
                "Verify that the token has API access."
            )

        if (
            not data.core_documents
            and (not data.user_documents or not payload.include_user_docs)
            and not data.profile
        ):
            return text(
                "⚠️ Could not load documents or profile. Confirm the token and, if this is your first access, use `initialize action=setup` to answer the initial questionnaire."
            )

        payload_dict = {
            "profile": data.profile,
            "core_documents": data.core_documents,
            "user_documents": data.user_documents if payload.include_user_docs else [],
        }
        if data.recent_memories:
            payload_dict["recent_memories"] = data.recent_memories

        # Extract key IDs for easy reference
        profile = data.profile or {}
        user_info = profile.get("user") or {}
        tenant_info = profile.get("tenant") or {}
        team_info = profile.get("team") or {}

        context_lines = ["📋 **User Context**"]
        if user_info.get("id"):
            context_lines.append(f"- **user_id**: `{user_info['id']}`")
        if user_info.get("name"):
            context_lines.append(f"- **user_name**: {user_info['name']}")
        if tenant_info.get("id"):
            context_lines.append(f"- **tenant_id**: `{tenant_info['id']}`")
        if tenant_info.get("name"):
            context_lines.append(f"- **tenant_name**: {tenant_info['name']}")
        if team_info.get("id"):
            context_lines.append(f"- **team_id**: `{team_info['id']}`")
        if team_info.get("name"):
            context_lines.append(f"- **team_name**: {team_info['name']}")

        message_lines = context_lines + [
            "",
            "📦 **Complete initialization data**",
            "```json",
            json.dumps(payload_dict, ensure_ascii=False, indent=2),
            "```",
        ]

        if payload.include_user_docs and not data.user_documents and data.profile:
            message_lines.extend(
                [
                    "",
                    self._service.build_new_user_prompt(data),
                ]
            )

        return text("\n".join(message_lines))

    async def _handle_setup(self, payload: InitializeRequest):
        answers = payload.answers or []
        validation_error = self._service.validate_setup_answers(answers)
        if validation_error:
            return text(f"❌ {validation_error}")

        summary_lines = [
            "📝 **Personalized setup received!**",
            "",
            "Your answers have been registered. I will suggest documents, rules and routines based on this information.",
            "",
            "Answer summary:",
        ]
        for idx, answer in enumerate(answers, start=1):
            summary_lines.append(f"{idx}. {answer.strip()}")

        summary_lines.extend(
            [
                "",
                "You can now request specific content, for example:",
                "- `productivity action=todo_create ...`",
                "- `knowledge action=mode_list`",
            ]
        )

        return text("\n".join(summary_lines))
