# SPDX-License-Identifier: MIT
"""HTTP client wrapper aligned with the Fênix Cloud Swagger."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from fenix_mcp.infrastructure.http_client import HttpClient


class FenixApiError(RuntimeError):
    """Represents an error returned by the Fênix API."""


def _to_query_value(value: Any) -> Any:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple, set)):
        return ",".join(str(item) for item in value)
    return value


def _strip_none(data: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        key: _to_query_value(value) for key, value in data.items() if value is not None
    }


@dataclass(slots=True)
class FenixApiClient:
    """Facade used by tools to communicate with the REST API."""

    base_url: str
    personal_access_token: Optional[str]
    core_documents_token: Optional[str] = None
    timeout: float = 30.0
    _http: HttpClient = field(init=False, repr=False)

    def __post_init__(self) -> None:
        headers: Dict[str, str] = {
            "User-Agent": "fenix-mcp-py/0.1.0",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.personal_access_token:
            headers["Authorization"] = f"Bearer {self.personal_access_token}"

        object.__setattr__(
            self,
            "_http",
            HttpClient(
                base_url=self.base_url,
                timeout=self.timeout,
                default_headers=headers,
            ),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def update_token(self, token: Optional[str]) -> None:
        """Update bearer token used for subsequent requests."""

        self.personal_access_token = token
        headers = dict(self._http.default_headers or {})
        if token:
            headers["Authorization"] = f"Bearer {token}"
        else:
            headers.pop("Authorization", None)
        self._http.default_headers = headers

    def update_core_documents_token(self, token: Optional[str]) -> None:
        """Update the MCP token used to access public core document endpoints."""

        self.core_documents_token = token

    def _build_params(
        self,
        *,
        required: Optional[Mapping[str, Any]] = None,
        optional: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}

        if required:
            for key, value in required.items():
                if value is None:
                    raise ValueError(f"Missing required query parameter: {key}")
                params[key] = _to_query_value(value)

        if optional:
            for key, value in optional.items():
                if value is None:
                    continue
                params[key] = _to_query_value(value)

        return params

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        response = self._http.request(
            method, endpoint, params=params, json=json, headers=headers
        )
        if response.status_code == 204:
            return None

        try:
            payload = response.json()
        except ValueError as exc:  # pragma: no cover - defensive
            raise FenixApiError(f"Invalid JSON response from {endpoint}") from exc

        if not response.ok:
            message = payload.get("message") or payload.get("error") or response.text
            raise FenixApiError(
                f"HTTP {response.status_code} calling {endpoint}: {message}"
            )

        return payload.get("data", payload)

    # ------------------------------------------------------------------
    # Health / profile
    # ------------------------------------------------------------------

    def get_health(self) -> Any:
        return self._request("GET", "/health")

    def get_profile(self) -> Any:
        return self._request("GET", "/api/auth/profile")

    # ------------------------------------------------------------------
    # Core documents
    # ------------------------------------------------------------------

    def list_core_documents(self, *, return_content: bool = False) -> Any:
        params = self._build_params(optional={"returnContent": return_content})
        headers = (
            {"x-mcp-token": self.core_documents_token}
            if self.core_documents_token
            else None
        )
        return self._request(
            "GET", "/api/core-documents/mcp/all", params=params, headers=headers
        )

    def get_core_document_by_name(
        self, name: str, *, return_content: bool = False
    ) -> Any:
        params = self._build_params(optional={"returnContent": return_content})
        headers = (
            {"x-mcp-token": self.core_documents_token}
            if self.core_documents_token
            else None
        )
        return self._request(
            "GET", f"/api/core-documents/mcp/{name}", params=params, headers=headers
        )

    def list_core_documents_auth(self, *, return_content: bool = False) -> Any:
        params = self._build_params(optional={"returnContent": return_content})
        return self._request("GET", "/api/core-documents", params=params)

    def get_core_document(self, name: str, *, return_content: bool = False) -> Any:
        params = self._build_params(optional={"returnContent": return_content})
        return self._request("GET", f"/api/core-documents/{name}", params=params)

    # ------------------------------------------------------------------
    # User core documents
    # ------------------------------------------------------------------

    def list_user_core_documents(self, *, return_content: bool = False) -> Any:
        params = self._build_params(optional={"returnContent": return_content})
        return self._request("GET", "/api/user-core-documents", params=params)

    def get_user_core_document(
        self, document_id: str, *, return_content: bool = False
    ) -> Any:
        params = self._build_params(optional={"returnContent": return_content})
        return self._request(
            "GET", f"/api/user-core-documents/{document_id}", params=params
        )

    def create_user_core_document(self, payload: Mapping[str, Any]) -> Any:
        return self._request("POST", "/api/user-core-documents", json=payload)

    def update_user_core_document(
        self, document_id: str, payload: Mapping[str, Any]
    ) -> Any:
        return self._request(
            "PATCH", f"/api/user-core-documents/{document_id}", json=payload
        )

    def delete_user_core_document(self, document_id: str) -> Any:
        return self._request("DELETE", f"/api/user-core-documents/{document_id}")

    # ------------------------------------------------------------------
    # Productivity (todo items)
    # ------------------------------------------------------------------

    def create_todo_item(self, payload: Mapping[str, Any]) -> Any:
        return self._request("POST", "/api/todo-items", json=payload)

    def list_todo_items(self, **filters: Any) -> Any:
        params = _strip_none(filters)
        return self._request("GET", "/api/todo-items", params=params)

    def get_todo_item(self, item_id: str, *, return_content: bool = False) -> Any:
        params = self._build_params(optional={"returnContent": return_content})
        return self._request("GET", f"/api/todo-items/{item_id}", params=params)

    def update_todo_item(self, item_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", f"/api/todo-items/{item_id}", json=payload)

    def delete_todo_item(self, item_id: str) -> Any:
        return self._request("DELETE", f"/api/todo-items/{item_id}")

    def update_todo_item_status(self, item_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", f"/api/todo-items/{item_id}/status", json=payload)

    def update_todo_item_priority(
        self, item_id: str, payload: Mapping[str, Any]
    ) -> Any:
        return self._request(
            "PATCH", f"/api/todo-items/{item_id}/priority", json=payload
        )

    def get_todo_stats(self) -> Any:
        return self._request("GET", "/api/todo-items/stats")

    def get_todo_categories(self) -> Any:
        return self._request("GET", "/api/todo-items/categories")

    def get_todo_tags(self) -> Any:
        return self._request("GET", "/api/todo-items/tags")

    def search_todo_items(self, *, query: str) -> Any:
        params = self._build_params(required={"q": query})
        return self._request("GET", "/api/todo-items/search", params=params)

    def list_todo_overdue(self) -> Any:
        return self._request("GET", "/api/todo-items/overdue")

    def list_todo_upcoming(self, *, days: Optional[int] = None) -> Any:
        params = self._build_params(optional={"days": days})
        return self._request("GET", "/api/todo-items/upcoming", params=params)

    # ------------------------------------------------------------------
    # Memories
    # ------------------------------------------------------------------

    def create_memory(self, payload: Mapping[str, Any]) -> Any:
        return self._request("POST", "/api/memories", json=payload)

    def list_memories(
        self,
        *,
        include_content: bool = True,
        include_metadata: bool = True,
        **filters: Any,
    ) -> Any:
        params = self._build_params(
            required={"content": include_content, "metadata": include_metadata},
            optional=filters,
        )
        return self._request("GET", "/api/memories", params=params)

    def get_memory(
        self,
        memory_id: str,
        *,
        include_content: bool = True,
        include_metadata: bool = True,
    ) -> Any:
        params = self._build_params(
            required={"content": include_content, "metadata": include_metadata}
        )
        return self._request("GET", f"/api/memories/{memory_id}", params=params)

    def update_memory(self, memory_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", f"/api/memories/{memory_id}", json=payload)

    def delete_memory(self, memory_id: str) -> Any:
        return self._request("DELETE", f"/api/memories/{memory_id}")

    def list_memories_by_tags(self, *, tags: str) -> Any:
        params = self._build_params(required={"tags": tags})
        return self._request("GET", "/api/memories/tags", params=params)

    def record_memory_access(self, memory_id: str) -> Any:
        return self._request("POST", f"/api/memories/{memory_id}/access")

    def find_similar_memories(self, payload: Mapping[str, Any]) -> Any:
        return self._request(
            "POST", "/api/memory-intelligence/similarity", json=payload
        )

    def consolidate_memories(self, payload: Mapping[str, Any]) -> Any:
        return self._request(
            "POST", "/api/memory-intelligence/consolidate", json=payload
        )

    def smart_create_memory(self, payload: Mapping[str, Any]) -> Any:
        return self._request(
            "POST", "/api/memory-intelligence/smart-create", json=payload
        )

    # ------------------------------------------------------------------
    # Configuration: modes and rules
    # ------------------------------------------------------------------

    def list_modes(
        self,
        *,
        include_rules: Optional[bool] = None,
        return_description: Optional[bool] = None,
        return_metadata: Optional[bool] = None,
    ) -> Any:
        params = self._build_params(
            optional={
                "includeRules": include_rules,
                "returnDescription": return_description,
                "returnMetadata": return_metadata,
            }
        )
        return self._request("GET", "/api/modes", params=params)

    def get_mode(
        self,
        mode_id: str,
        *,
        return_description: Optional[bool] = None,
        return_metadata: Optional[bool] = None,
    ) -> Any:
        params = self._build_params(
            optional={
                "returnDescription": return_description,
                "returnMetadata": return_metadata,
            }
        )
        return self._request("GET", f"/api/modes/{mode_id}", params=params)

    def create_mode(self, payload: Mapping[str, Any]) -> Any:
        return self._request("POST", "/api/modes", json=payload)

    def update_mode(self, mode_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", f"/api/modes/{mode_id}", json=payload)

    def delete_mode(self, mode_id: str) -> Any:
        return self._request("DELETE", f"/api/modes/{mode_id}")

    def list_rules(
        self,
        *,
        return_description: Optional[bool] = None,
        return_metadata: Optional[bool] = None,
        return_modes: Optional[bool] = None,
    ) -> Any:
        params = self._build_params(
            optional={
                "returnDescription": return_description,
                "returnMetadata": return_metadata,
                "returnModes": return_modes,
            }
        )
        return self._request("GET", "/api/rules", params=params)

    def get_rule(
        self,
        rule_id: str,
        *,
        return_description: Optional[bool] = None,
        return_metadata: Optional[bool] = None,
        return_modes: Optional[bool] = None,
    ) -> Any:
        params = self._build_params(
            optional={
                "returnDescription": return_description,
                "returnMetadata": return_metadata,
                "returnModes": return_modes,
            }
        )
        return self._request("GET", f"/api/rules/{rule_id}", params=params)

    def create_rule(self, payload: Mapping[str, Any]) -> Any:
        return self._request("POST", "/api/rules", json=payload)

    def update_rule(self, rule_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", f"/api/rules/{rule_id}", json=payload)

    def delete_rule(self, rule_id: str) -> Any:
        return self._request("DELETE", f"/api/rules/{rule_id}")

    def add_mode_rule(self, mode_id: str, rule_id: str) -> Any:
        payload = {"modeId": mode_id, "ruleId": rule_id}
        return self._request("POST", "/api/mode-rules", json=payload)

    def remove_mode_rule(self, mode_id: str, rule_id: str) -> Any:
        return self._request("DELETE", f"/api/mode-rules/mode/{mode_id}/rule/{rule_id}")

    def list_rules_by_mode(self, mode_id: str) -> Any:
        return self._request("GET", f"/api/mode-rules/mode/{mode_id}/rules")

    def list_modes_by_rule(self, rule_id: str) -> Any:
        return self._request("GET", f"/api/mode-rules/rule/{rule_id}/modes")

    # ------------------------------------------------------------------
    # Knowledge: documentation
    # ------------------------------------------------------------------

    def list_documentation_items(self, **filters: Any) -> Any:
        return self._request("GET", "/api/documentation", params=_strip_none(filters))

    def get_documentation_item(self, item_id: str, **filters: Any) -> Any:
        return self._request(
            "GET", f"/api/documentation/{item_id}", params=_strip_none(filters)
        )

    def create_documentation_item(self, payload: Mapping[str, Any]) -> Any:
        return self._request("POST", "/api/documentation", json=payload)

    def update_documentation_item(
        self, item_id: str, payload: Mapping[str, Any]
    ) -> Any:
        return self._request("PATCH", f"/api/documentation/{item_id}", json=payload)

    def delete_documentation_item(self, item_id: str) -> Any:
        return self._request("DELETE", f"/api/documentation/{item_id}")

    def get_documentation_children(self, item_id: str) -> Any:
        return self._request("GET", f"/api/documentation/{item_id}/children")

    def get_documentation_tree(self, item_id: str) -> Any:
        return self._request("GET", f"/api/documentation/{item_id}/tree")

    def get_documentation_full_tree(self) -> Any:
        return self._request("GET", "/api/documentation/tree")

    def search_documentation_items(self, *, query: str, limit: int) -> Any:
        params = self._build_params(required={"q": query, "limit": limit})
        return self._request("GET", "/api/documentation/search", params=params)

    def list_documentation_roots(self) -> Any:
        return self._request("GET", "/api/documentation/roots")

    def list_documentation_recent(self, *, limit: int) -> Any:
        params = self._build_params(required={"limit": limit})
        return self._request("GET", "/api/documentation/recent", params=params)

    def get_documentation_analytics(self) -> Any:
        return self._request("GET", "/api/documentation/analytics")

    def move_documentation_item(self, item_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request(
            "PATCH", f"/api/documentation/{item_id}/move", json=payload
        )

    def publish_documentation_item(self, item_id: str) -> Any:
        return self._request("PATCH", f"/api/documentation/{item_id}/publish")

    def create_documentation_version(
        self, item_id: str, payload: Mapping[str, Any]
    ) -> Any:
        return self._request(
            "POST", f"/api/documentation/{item_id}/version", json=payload
        )

    def duplicate_documentation_item(
        self, item_id: str, payload: Mapping[str, Any]
    ) -> Any:
        return self._request(
            "POST", f"/api/documentation/{item_id}/duplicate", json=payload
        )

    # ------------------------------------------------------------------
    # Knowledge: work items
    # ------------------------------------------------------------------

    def create_work_item(self, payload: Mapping[str, Any]) -> Any:
        return self._request("POST", "/api/work-items", json=payload)

    def list_work_items(self, **filters: Any) -> Any:
        return self._request("GET", "/api/work-items", params=_strip_none(filters))

    def get_work_item(self, item_id: str) -> Any:
        return self._request("GET", f"/api/work-items/{item_id}")

    def get_work_item_by_key(self, key: str) -> Any:
        return self._request("GET", f"/api/work-items/by-key/{key}")

    def assign_work_item_to_me(self, item_id: str) -> Any:
        return self._request("POST", f"/api/work-items/{item_id}/assign-to-me")

    def get_work_items_mine(self, *, limit: int = 50, offset: int = 0) -> Any:
        params = self._build_params(optional={"limit": limit, "offset": offset})
        return self._request("GET", "/api/work-items/mine", params=params)

    def update_work_item(self, item_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", f"/api/work-items/{item_id}", json=payload)

    def delete_work_item(self, item_id: str) -> Any:
        return self._request("DELETE", f"/api/work-items/{item_id}")

    def list_work_items_backlog(self) -> Any:
        return self._request("GET", "/api/work-items/backlog")

    def search_work_items(
        self,
        *,
        query: str,
        limit: int,
        item_type: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assignee_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Any:
        params = self._build_params(
            required={"q": query, "limit": limit},
            optional={
                "item_type": item_type,
                "status": status,
                "priority": priority,
                "assignee_id": assignee_id,
                "tags": ",".join(tags) if tags else None,
            },
        )
        return self._request("GET", "/api/work-items/search", params=params)

    def get_work_items_analytics(self) -> Any:
        return self._request("GET", "/api/work-items/analytics")

    def get_work_items_velocity(self, *, sprints_count: int) -> Any:
        params = self._build_params(required={"sprints_count": sprints_count})
        return self._request("GET", "/api/work-items/velocity", params=params)

    def list_work_items_by_sprint(self, *, sprint_id: str) -> Any:
        return self._request("GET", f"/api/work-items/by-sprint/{sprint_id}")

    def get_work_items_burndown(self, *, sprint_id: str) -> Any:
        return self._request("GET", f"/api/work-items/burndown/{sprint_id}")

    def list_work_items_by_epic(self, *, epic_id: str) -> Any:
        return self._request("GET", f"/api/work-items/by-epic/{epic_id}")

    def get_work_items_epic_progress(self, *, epic_id: str) -> Any:
        return self._request("GET", f"/api/work-items/epic-progress/{epic_id}")

    def list_work_items_by_board(self, *, board_id: str) -> Any:
        return self._request("GET", f"/api/work-items/by-board/{board_id}")

    def get_work_item_children(self, item_id: str) -> Any:
        return self._request("GET", f"/api/work-items/{item_id}/children")

    def move_work_item(self, item_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", f"/api/work-items/{item_id}/move", json=payload)

    def update_work_item_status(self, item_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", f"/api/work-items/{item_id}/status", json=payload)

    def move_work_item_to_board(self, item_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", f"/api/work-items/{item_id}/board", json=payload)

    def link_work_item(self, item_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", f"/api/work-items/{item_id}/link", json=payload)

    def assign_work_items_to_sprint(self, payload: Mapping[str, Any]) -> Any:
        return self._request("POST", "/api/work-items/assign-to-sprint", json=payload)

    def bulk_update_work_items(self, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", "/api/work-items/bulk-update", json=payload)

    def bulk_create_work_items(self, payload: Mapping[str, Any]) -> Any:
        return self._request("POST", "/api/work-items/bulk-create", json=payload)

    # ------------------------------------------------------------------
    # Knowledge: boards
    # ------------------------------------------------------------------

    def create_work_board(self, payload: Mapping[str, Any]) -> Any:
        return self._request("POST", "/api/work-boards", json=payload)

    def list_work_boards(self, **filters: Any) -> Any:
        return self._request("GET", "/api/work-boards", params=_strip_none(filters))

    def list_work_boards_by_team(self) -> Any:
        return self._request("GET", "/api/work-boards/by-team")

    def list_favorite_work_boards(self) -> Any:
        return self._request("GET", "/api/work-boards/favorites")

    def search_work_boards(self, *, query: str, limit: int) -> Any:
        params = self._build_params(required={"q": query, "limit": limit})
        return self._request("GET", "/api/work-boards/search", params=params)

    def list_recent_work_boards(self, *, limit: int) -> Any:
        params = self._build_params(required={"limit": limit})
        return self._request("GET", "/api/work-boards/recent", params=params)

    def get_work_board(self, board_id: str) -> Any:
        return self._request("GET", f"/api/work-boards/{board_id}")

    def update_work_board(self, board_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", f"/api/work-boards/{board_id}", json=payload)

    def delete_work_board(self, board_id: str) -> Any:
        return self._request("DELETE", f"/api/work-boards/{board_id}")

    def get_work_board_analytics(self, board_id: str) -> Any:
        return self._request("GET", f"/api/work-boards/{board_id}/analytics")

    def list_work_board_columns(self, board_id: str) -> Any:
        return self._request("GET", f"/api/work-boards/{board_id}/columns")

    def toggle_work_board_favorite(
        self, board_id: str, payload: Mapping[str, Any]
    ) -> Any:
        return self._request(
            "PATCH", f"/api/work-boards/{board_id}/favorite", json=payload
        )

    def clone_work_board(self, board_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request("POST", f"/api/work-boards/{board_id}/clone", json=payload)

    def reorder_work_boards(self, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", "/api/work-boards/reorder", json=payload)

    def create_work_board_column(self, payload: Mapping[str, Any]) -> Any:
        return self._request("POST", "/api/work-boards/columns", json=payload)

    def reorder_work_board_columns(self, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", "/api/work-boards/columns/reorder", json=payload)

    def get_work_board_column(self, column_id: str) -> Any:
        return self._request("GET", f"/api/work-boards/columns/{column_id}")

    def update_work_board_column(
        self, column_id: str, payload: Mapping[str, Any]
    ) -> Any:
        return self._request(
            "PATCH", f"/api/work-boards/columns/{column_id}", json=payload
        )

    def delete_work_board_column(self, column_id: str) -> Any:
        return self._request("DELETE", f"/api/work-boards/columns/{column_id}")

    # ------------------------------------------------------------------
    # Knowledge: sprints
    # ------------------------------------------------------------------

    def create_sprint(self, payload: Mapping[str, Any]) -> Any:
        return self._request("POST", "/api/sprints", json=payload)

    def list_sprints(self, **filters: Any) -> Any:
        return self._request("GET", "/api/sprints", params=_strip_none(filters))

    def get_sprint(self, sprint_id: str) -> Any:
        return self._request("GET", f"/api/sprints/{sprint_id}")

    def update_sprint(self, sprint_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", f"/api/sprints/{sprint_id}", json=payload)

    def delete_sprint(self, sprint_id: str) -> Any:
        return self._request("DELETE", f"/api/sprints/{sprint_id}")

    def list_sprints_by_team(self) -> Any:
        return self._request("GET", "/api/sprints/by-team")

    def list_recent_sprints(self, *, limit: int) -> Any:
        params = self._build_params(required={"limit": limit})
        return self._request("GET", "/api/sprints/recent", params=params)

    def search_sprints(self, *, query: str, limit: int) -> Any:
        params = self._build_params(required={"q": query, "limit": limit})
        return self._request("GET", "/api/sprints/search", params=params)

    def get_active_sprint(self) -> Any:
        return self._request("GET", "/api/sprints/active")

    def get_sprints_velocity(self) -> Any:
        return self._request("GET", "/api/sprints/velocity")

    def get_sprints_burndown(self) -> Any:
        return self._request("GET", "/api/sprints/burndown")

    def get_sprint_work_items(self, sprint_id: str) -> Any:
        return self._request("GET", f"/api/sprints/{sprint_id}/work-items")

    def add_work_items_to_sprint(
        self, sprint_id: str, payload: Mapping[str, Any]
    ) -> Any:
        return self._request(
            "POST", f"/api/sprints/{sprint_id}/work-items", json=payload
        )

    def remove_work_items_from_sprint(self, payload: Mapping[str, Any]) -> Any:
        return self._request("DELETE", "/api/sprints/work-items", json=payload)

    def get_sprint_analytics(self, sprint_id: str) -> Any:
        return self._request("GET", f"/api/sprints/{sprint_id}/analytics")

    def get_sprint_capacity(self, sprint_id: str) -> Any:
        return self._request("GET", f"/api/sprints/{sprint_id}/capacity")

    def start_sprint(self, sprint_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request("PATCH", f"/api/sprints/{sprint_id}/start", json=payload)

    def complete_sprint(self, sprint_id: str, payload: Mapping[str, Any]) -> Any:
        return self._request(
            "PATCH", f"/api/sprints/{sprint_id}/complete", json=payload
        )

    def cancel_sprint(self, sprint_id: str) -> Any:
        return self._request("PATCH", f"/api/sprints/{sprint_id}/cancel")
