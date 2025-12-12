"""Disk caching for analysis results."""

import json
from pathlib import Path
from typing import Any, Optional

import diskcache


class AnalysisCache:
    """Disk-based cache for analysis results."""

    def __init__(self, cache_dir: Optional[str] = None, ttl_days: int = 30):
        """
        Initialize cache.

        Args:
            cache_dir: Cache directory path (default: ~/.cache/ossval)
            ttl_days: Time-to-live in days
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".cache" / "ossval"

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache = diskcache.Cache(str(self.cache_dir), size_limit=2**30)  # 1GB limit
        self.ttl_seconds = ttl_days * 24 * 60 * 60

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            return self.cache.get(key, default=None)
        except Exception:
            return None

    def set(self, key: str, value: Any) -> None:
        """Set value in cache with TTL."""
        try:
            self.cache.set(key, value, expire=self.ttl_seconds)
        except Exception:
            pass

    def clear(self) -> None:
        """Clear all cache entries."""
        try:
            self.cache.clear()
        except Exception:
            pass

    def info(self) -> dict[str, Any]:
        """Get cache information."""
        try:
            return {
                "cache_dir": str(self.cache_dir),
                "size": self.cache.volume(),
                "count": len(self.cache),
            }
        except Exception:
            return {"cache_dir": str(self.cache_dir), "size": 0, "count": 0}

