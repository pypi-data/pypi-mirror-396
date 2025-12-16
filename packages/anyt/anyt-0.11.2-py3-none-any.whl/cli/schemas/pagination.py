"""Pagination schemas."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""

    items: list[T] = Field(description="List of items")
    total: int = Field(description="Total count of items")
    limit: int = Field(description="Items per page")
    offset: int = Field(description="Pagination offset")


class PaginationParams(BaseModel):
    """Pagination query parameters."""

    limit: int = Field(default=50, description="Items per page", ge=1, le=100)
    offset: int = Field(default=0, description="Pagination offset", ge=0)
    sort_by: str = Field(default="id", description="Sort field")
    order: str = Field(default="desc", description="Sort order (asc/desc)")
