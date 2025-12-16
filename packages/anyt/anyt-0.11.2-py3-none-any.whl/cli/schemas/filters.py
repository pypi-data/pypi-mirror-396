"""Common filter schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class BaseFilters(BaseModel):
    """Base filter class with common parameters."""

    limit: int = Field(default=50, description="Items per page", ge=1, le=100)
    offset: int = Field(default=0, description="Pagination offset", ge=0)
    sort_by: str = Field(default="id", description="Sort field")
    order: str = Field(default="desc", description="Sort order (asc/desc)")


class DateRangeFilter(BaseModel):
    """Date range filter."""

    start_date: Optional[str] = Field(
        default=None, description="Start date (ISO format)"
    )
    end_date: Optional[str] = Field(default=None, description="End date (ISO format)")
