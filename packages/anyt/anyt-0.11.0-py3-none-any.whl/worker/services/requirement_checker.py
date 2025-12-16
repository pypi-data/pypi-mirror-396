"""Base requirement checker interface and utilities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Generic, TypeVar

from worker.models.workflow_requirements import RequirementCheckResult

T = TypeVar("T")


@dataclass
class CachedResult:
    """Cached requirement check result with TTL."""

    result: RequirementCheckResult
    timestamp: datetime
    ttl: timedelta = timedelta(minutes=5)

    def is_valid(self) -> bool:
        """Check if cached result is still valid."""
        return datetime.now() - self.timestamp < self.ttl


class RequirementChecker(ABC, Generic[T]):
    """Base class for requirement checkers.

    Each checker validates a specific type of requirement and returns
    a RequirementCheckResult with success status and fix instructions.
    """

    def __init__(self) -> None:
        """Initialize the checker with an empty cache."""
        self._cache: dict[str, CachedResult] = {}

    @abstractmethod
    async def check(self, requirement: T) -> RequirementCheckResult:
        """Check if a requirement is satisfied.

        Args:
            requirement: The requirement to check

        Returns:
            RequirementCheckResult with success status and optional fix instructions
        """
        pass

    async def check_with_cache(
        self, requirement: T, cache_key: str, force: bool = False
    ) -> RequirementCheckResult:
        """Check requirement with caching support.

        Args:
            requirement: The requirement to check
            cache_key: Unique key for caching this check
            force: If True, bypass cache and force a fresh check

        Returns:
            RequirementCheckResult (cached or fresh)
        """
        # Check cache first (unless force is True)
        if not force and cache_key in self._cache:
            cached = self._cache[cache_key]
            if cached.is_valid():
                return cached.result

        # Perform actual check
        result = await self.check(requirement)

        # Cache the result
        self._cache[cache_key] = CachedResult(result=result, timestamp=datetime.now())

        return result

    def clear_cache(self) -> None:
        """Clear all cached results."""
        self._cache.clear()

    def _get_cache_key(self, requirement: Any) -> str:
        """Generate a cache key for a requirement.

        Default implementation uses requirement's model_dump_json.
        Subclasses can override for custom cache key logic.

        Args:
            requirement: The requirement to generate a key for

        Returns:
            A unique cache key string
        """
        # For Pydantic models, use model_dump_json
        if hasattr(requirement, "model_dump_json"):
            result: str = requirement.model_dump_json()
            return result
        # Fallback to string representation
        return str(requirement)
