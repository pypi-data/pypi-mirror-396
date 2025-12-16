"""
Cache manager for workflow step results.
Supports both in-memory and Redis caching.
"""

import hashlib
import json
import pickle
from pathlib import Path
from typing import Any, Dict, Optional

from rich.markup import escape

from cli.commands.console import console


class CacheManager:
    """Manages caching of workflow step results."""

    def __init__(self, cache_dir: Optional[Path] = None, use_redis: bool = False):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory for filesystem cache (default: .anyt/cache)
            use_redis: Whether to use Redis for caching
        """
        self.cache_dir = cache_dir or Path.cwd() / ".anyt" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.use_redis = use_redis
        self.redis_client: Optional[Any] = None

        if use_redis:
            try:
                import redis  # type: ignore[import-not-found,unused-ignore]

                self.redis_client = redis.Redis(
                    host="localhost", port=6379, db=0, decode_responses=False
                )
                self.redis_client.ping()
                console.print("[dim]✓ Connected to Redis cache[/dim]")
            except (ImportError, ConnectionError, OSError) as e:
                # ImportError: redis package not installed
                # ConnectionError: Redis server not available
                # OSError: Network errors
                console.print(
                    f"[yellow]Warning: Could not connect to Redis: {e}[/yellow]"
                )
                console.print("[dim]Falling back to filesystem cache[/dim]")
                self.redis_client = None

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached value by key."""
        if self.redis_client:
            return await self._get_redis(key)
        else:
            return await self._get_filesystem(key)

    async def set(
        self, key: str, value: Dict[str, Any], ttl: Optional[int] = None
    ) -> None:
        """Set cached value with optional TTL."""
        if self.redis_client:
            await self._set_redis(key, value, ttl)
        else:
            await self._set_filesystem(key, value)

    async def delete(self, key: str) -> None:
        """Delete cached value."""
        if self.redis_client:
            self.redis_client.delete(key)
        else:
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                cache_file.unlink()

    async def clear(self) -> None:
        """Clear all cached values."""
        if self.redis_client:
            self.redis_client.flushdb()
        else:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()

    async def _get_redis(self, key: str) -> Optional[Dict[str, Any]]:
        """Get from Redis cache."""
        try:
            if self.redis_client:
                data = self.redis_client.get(key)
                if data:
                    return pickle.loads(data)  # type: ignore[no-any-return]
        except (ConnectionError, OSError, pickle.UnpicklingError) as e:
            # ConnectionError: Redis connection lost
            # OSError: Network errors
            # UnpicklingError: Corrupted cache data
            console.print(f"[yellow]Cache read error: {escape(str(e))}[/yellow]")
        return None

    async def _set_redis(
        self, key: str, value: Dict[str, Any], ttl: Optional[int] = None
    ) -> None:
        """Set in Redis cache."""
        try:
            if self.redis_client:
                data = pickle.dumps(value)
                if ttl:
                    self.redis_client.setex(key, ttl, data)
                else:
                    self.redis_client.set(key, data)
        except (ConnectionError, OSError, pickle.PicklingError) as e:
            # ConnectionError: Redis connection lost
            # OSError: Network errors
            # PicklingError: Value cannot be serialized
            console.print(f"[yellow]Cache write error: {escape(str(e))}[/yellow]")

    async def _get_filesystem(self, key: str) -> Optional[Dict[str, Any]]:
        """Get from filesystem cache."""
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)  # type: ignore[no-any-return]
            except (OSError, json.JSONDecodeError) as e:
                # OSError: File system errors
                # JSONDecodeError: Corrupted cache file
                console.print(f"[yellow]Cache read error: {escape(str(e))}[/yellow]")
        return None

    async def _set_filesystem(self, key: str, value: Dict[str, Any]) -> None:
        """Set in filesystem cache."""
        cache_file = self._get_cache_file(key)
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(value, f, indent=2)
        except (OSError, TypeError) as e:
            # OSError: File system errors (permission denied, disk full)
            # TypeError: Value cannot be serialized to JSON
            console.print(f"[yellow]Cache write error: {escape(str(e))}[/yellow]")

    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for a key."""
        # Hash the key to create a safe filename
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
