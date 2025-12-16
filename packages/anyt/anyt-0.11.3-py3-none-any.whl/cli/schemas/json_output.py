"""JSON output schemas for CLI commands.

This module defines the standardized JSON schema contract for all CLI commands.
All commands with --json flag should follow these schemas to ensure:
1. Consistent structure for AI agents (Claude Code)
2. Predictable parsing and error handling
3. Type-safe integration with external tools

Schema Contract:
--------------
All JSON responses follow one of these patterns:

1. Single Item Response:
   {
     "success": true,
     "data": {
       "id": "t_123",
       "identifier": "DEV-42",
       ...
     }
   }

2. List Response:
   {
     "success": true,
     "items": [...],
     "count": 10,
     "total": 100,  # optional, for paginated results
     "page": 1,     # optional, for paginated results
   }

3. Success Response (no data):
   {
     "success": true,
     "message": "Operation completed"
   }

4. Error Response:
   {
     "success": false,
     "error": {
       "code": "NOT_FOUND",
       "message": "Task not found",
       ...additional error data...
     }
   }
"""

from typing import Any, Generic, Literal, Optional, TypedDict, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Error detail structure."""

    code: str = Field(..., description="Error code (e.g., NOT_FOUND, VALIDATION_ERROR)")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )


class SuccessResponse(BaseModel, Generic[T]):
    """Success response with data."""

    success: Literal[True] = True
    data: T = Field(..., description="Response data")


class ListResponse(BaseModel, Generic[T]):
    """List response with items."""

    success: Literal[True] = True
    items: list[T] = Field(..., description="List of items")
    count: int = Field(..., description="Number of items in this response")
    total: Optional[int] = Field(
        default=None, description="Total number of items (for pagination)"
    )
    page: Optional[int] = Field(default=None, description="Current page number")
    page_size: Optional[int] = Field(default=None, description="Items per page")


class MessageResponse(BaseModel):
    """Success response with message only."""

    success: Literal[True] = True
    message: str = Field(..., description="Success message")


class ErrorResponse(BaseModel):
    """Error response."""

    success: Literal[False] = False
    error: ErrorDetail = Field(..., description="Error details")


# ============================================================================
# Domain-specific response schemas
# ============================================================================


class TaskJSONSchema(TypedDict, total=False):
    """JSON schema for task responses.

    This defines the stable contract for task JSON output.
    All fields are optional to support partial responses.
    """

    # Core fields (always present)
    id: str  # Internal UUID
    uid: str  # Human-readable UID (e.g., t_1Z)
    identifier: str  # Workspace-scoped identifier (e.g., DEV-42)
    title: str
    status: str  # backlog, todo, active, blocked, done, canceled, archived
    priority: int  # -2 to 2

    # Optional fields
    description: str
    implementation_plan: str  # Implementation plan in markdown format
    owner_id: str
    owner_type: str  # user, agent
    project_id: int
    workspace_id: int
    phase: str

    # Metadata
    created_at: str  # ISO 8601 timestamp
    updated_at: str  # ISO 8601 timestamp
    completed_at: str  # ISO 8601 timestamp (if completed)

    # Relationships
    dependencies: list[str]  # List of dependent task identifiers
    blocking: list[str]  # List of blocked task identifiers


class WorkspaceJSONSchema(TypedDict, total=False):
    """JSON schema for workspace responses."""

    id: int
    uid: str
    identifier: str  # URL-friendly identifier
    name: str
    description: str
    created_at: str
    updated_at: str


class ProjectJSONSchema(TypedDict, total=False):
    """JSON schema for project responses."""

    id: int
    name: str
    identifier: str
    description: str
    workspace_id: int
    created_at: str
    updated_at: str


class ViewJSONSchema(TypedDict, total=False):
    """JSON schema for view responses."""

    id: int
    name: str
    description: str
    filters: dict[str, Any]
    workspace_id: int
    is_default: bool


# ============================================================================
# Command-specific response types
# ============================================================================


class TaskCreateResponse(SuccessResponse[TaskJSONSchema]):
    """Response from 'anyt task add --json'."""

    pass


class TaskShowResponse(SuccessResponse[TaskJSONSchema]):
    """Response from 'anyt task show --json'."""

    pass


class TaskListResponse(ListResponse[TaskJSONSchema]):
    """Response from 'anyt task list --json'."""

    pass


class TaskUpdateResponse(SuccessResponse[TaskJSONSchema]):
    """Response from 'anyt task edit --json'."""

    pass


class TaskDeleteResponse(MessageResponse):
    """Response from 'anyt task rm --json'."""

    pass


class WorkspaceListResponse(ListResponse[WorkspaceJSONSchema]):
    """Response from 'anyt workspace list --json'."""

    pass


class ProjectListResponse(ListResponse[ProjectJSONSchema]):
    """Response from 'anyt project list --json'."""

    pass


class ViewListResponse(ListResponse[ViewJSONSchema]):
    """Response from 'anyt view list --json'."""

    pass


# ============================================================================
# Helper functions for creating consistent responses
# ============================================================================


def success_data_response(data: Any) -> dict[str, Any]:
    """Create a success response with data.

    Args:
        data: Pydantic model or dict to include in response

    Returns:
        Standardized success response

    Example:
        >>> task = Task(...)
        >>> success_data_response(task)
        {"success": True, "data": {...}}
    """
    if hasattr(data, "model_dump"):
        data = data.model_dump(mode="json")
    return {"success": True, "data": data}


def success_list_response(
    items: list[Any],
    total: Optional[int] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> dict[str, Any]:
    """Create a success response with list of items.

    Args:
        items: List of Pydantic models or dicts
        total: Total number of items (for pagination)
        page: Current page number
        page_size: Items per page

    Returns:
        Standardized list response

    Example:
        >>> tasks = [Task(...), Task(...)]
        >>> success_list_response(tasks, total=100, page=1, page_size=20)
        {"success": True, "items": [...], "count": 2, "total": 100, ...}
    """
    serialized_items = [
        item.model_dump(mode="json") if hasattr(item, "model_dump") else item
        for item in items
    ]

    response: dict[str, Any] = {
        "success": True,
        "items": serialized_items,
        "count": len(serialized_items),
    }

    if total is not None:
        response["total"] = total
    if page is not None:
        response["page"] = page
    if page_size is not None:
        response["page_size"] = page_size

    return response


def success_message_response(message: str) -> dict[str, Any]:
    """Create a success response with message only.

    Args:
        message: Success message

    Returns:
        Standardized message response

    Example:
        >>> success_message_response("Task deleted successfully")
        {"success": True, "message": "Task deleted successfully"}
    """
    return {"success": True, "message": message}


def error_response(
    code: str, message: str, details: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """Create an error response.

    Args:
        code: Error code (e.g., NOT_FOUND, VALIDATION_ERROR)
        message: Human-readable error message
        details: Optional additional error details

    Returns:
        Standardized error response

    Example:
        >>> error_response("NOT_FOUND", "Task DEV-42 not found")
        {"success": False, "error": {"code": "NOT_FOUND", "message": "..."}}
    """
    error: dict[str, Any] = {"code": code, "message": message}
    if details:
        error.update(details)

    return {"success": False, "error": error}
