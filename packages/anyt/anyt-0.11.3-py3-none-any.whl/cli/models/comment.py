"""Comment domain models for task comments."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    """Model for creating a new comment."""

    content: str = Field(..., min_length=1, description="Comment content")
    mentioned_users: list[str] = Field(
        default_factory=list, description="List of mentioned user identifiers"
    )
    task_id: int = Field(..., description="Task ID (numeric)")
    author_id: str = Field(..., description="Author ID (user ID or API key)")
    author_type: str | None = Field(
        default=None, description="Author type (user or agent)"
    )
    parent_id: int | None = Field(
        default=None, description="Parent comment ID for replies"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "Completed implementation, ready for review",
                "mentioned_users": ["user123"],
                "task_id": 123,
                "author_id": "api_key_or_user_id",
                "author_type": "agent",
            }
        }
    )


class Comment(BaseModel):
    """Comment domain model."""

    id: int = Field(..., description="Unique comment identifier")
    content: str = Field(..., description="Comment content")
    created_at: datetime = Field(..., description="Comment creation timestamp")
    user_id: int | None = Field(
        None, description="User who created the comment (optional)"
    )
    task_id: str = Field(..., description="Task identifier (e.g., DEV-42)")
    mentioned_users: list[str] = Field(
        default_factory=list, description="List of mentioned user identifiers"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 123,
                "content": "This is a comment",
                "created_at": "2025-10-23T20:30:00Z",
                "user_id": 456,
                "task_id": "DEV-42",
                "mentioned_users": ["user123"],
            }
        }
    )
