# SPDX-License-Identifier: MIT
"""Base abstractions for MCP tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Annotated, Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from fenix_mcp.infrastructure.context import AppContext

T = TypeVar("T")


def sanitize_null(value: Optional[T]) -> Optional[T]:
    """Convert string 'null' to None. Handles AI agents passing 'null' as string."""
    if value == "null" or value == "None" or value == "":
        return None
    return value


def sanitize_null_list(value: Optional[List[T]]) -> Optional[List[T]]:
    """Sanitize list values, converting 'null' string to None."""
    if value == "null" or value == "None" or value == "":  # type: ignore
        return None
    if isinstance(value, list):
        return [v for v in value if v != "null" and v != "None" and v != ""]
    return value


# =============================================================================
# Type aliases for common field types - generates proper JSON schema
# =============================================================================

# UUID string - format: uuid, with regex pattern validation
UUIDStr = Annotated[
    str,
    Field(
        pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
        json_schema_extra={"format": "uuid"},
    ),
]

# ISO 8601 date string (YYYY-MM-DD)
DateStr = Annotated[
    str,
    Field(
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        json_schema_extra={"format": "date"},
        examples=["2025-01-15"],
    ),
]

# ISO 8601 datetime string (YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DD)
DateTimeStr = Annotated[
    str,
    Field(
        pattern=r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$",
        json_schema_extra={"format": "date-time"},
        examples=["2025-01-15T10:30:00Z", "2025-01-15"],
    ),
]

# Markdown content - indicates rich text
MarkdownStr = Annotated[
    str,
    Field(
        json_schema_extra={"format": "markdown", "contentMediaType": "text/markdown"},
    ),
]

# Mermaid diagram hint for markdown fields
MERMAID_HINT = """
💡 **Tip**: You can use Mermaid code blocks to create visual diagrams.

Flowchart example:
```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
```

Sequence diagram example:
```mermaid
sequenceDiagram
    participant U as User
    participant A as API
    U->>A: Request
    A-->>U: Response
```

Supported types: flowchart, sequenceDiagram, classDiagram, gantt, pie, mindmap, gitGraph.
"""

# Short title/name strings (1-300 chars)
TitleStr = Annotated[
    str,
    StringConstraints(min_length=1, max_length=300),
]

# Description strings (up to 1000 chars)
DescriptionStr = Annotated[
    str,
    StringConstraints(max_length=1000),
]

# Tag string (lowercase, alphanumeric with hyphens/underscores)
TagStr = Annotated[
    str,
    Field(
        pattern=r"^[a-zA-Z0-9_-]+$",
        examples=["bug", "feature", "high-priority"],
    ),
]

# Category strings
CategoryStr = Annotated[
    str,
    StringConstraints(max_length=100),
]

# Language code (ISO 639-1)
LanguageStr = Annotated[
    str,
    Field(
        pattern=r"^[a-z]{2}(-[A-Z]{2})?$",
        examples=["pt", "en", "pt-BR", "en-US"],
    ),
]

# Version string (semver-like)
VersionStr = Annotated[
    str,
    Field(
        pattern=r"^[0-9]+(\.[0-9]+)*(-[a-zA-Z0-9]+)?$",
        max_length=20,
        examples=["1.0", "2.1.3", "1.0.0-beta"],
    ),
]

# Emoji string (single emoji or short code)
EmojiStr = Annotated[
    str,
    StringConstraints(max_length=10),
]


class ToolRequest(BaseModel):
    """Base request payload."""

    model_config = ConfigDict(extra="forbid")


ToolResponse = Dict[str, Any]


class Tool(ABC):
    """Interface implemented by all tools."""

    name: str
    description: str
    request_model: Type[ToolRequest] = ToolRequest

    def schema(self) -> Dict[str, Any]:
        """Return JSON schema describing the tool arguments."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.request_model.model_json_schema(),
        }

    async def execute(
        self, raw_arguments: Dict[str, Any], context: AppContext
    ) -> ToolResponse:
        """Validate raw arguments and run the tool."""
        payload = self.request_model.model_validate(raw_arguments or {})
        return await self.run(payload, context)

    @abstractmethod
    async def run(self, payload: ToolRequest, context: AppContext) -> ToolResponse:
        """Execute business logic and return a MCP-formatted response."""
