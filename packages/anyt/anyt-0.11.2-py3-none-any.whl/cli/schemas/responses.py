"""API response schemas."""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard API success response wrapper."""

    success: bool = Field(default=True, description="Success flag")
    data: T = Field(description="Response data")
    message: Optional[str] = Field(default=None, description="Optional message")


class ErrorResponse(BaseModel):
    """Standard API error response."""

    success: bool = Field(default=False, description="Success flag")
    message: str = Field(description="Error message")
    details: Optional[dict[str, Any]] = Field(default=None, description="Error details")
