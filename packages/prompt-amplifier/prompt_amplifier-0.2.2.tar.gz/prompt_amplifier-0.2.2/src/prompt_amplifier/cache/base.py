"""Base cache interface and configuration."""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CacheConfig:
    """Configuration for caching behavior.
    
    Attributes:
        enabled: Whether caching is enabled.
        cache_embeddings: Cache embedding results.
        cache_generations: Cache LLM generation results.
        cache_searches: Cache search results.
        ttl_seconds: Time-to-live for cache entries (0 = no expiry).
        max_size: Maximum number of entries (0 = unlimited).
        cache_dir: Directory for disk cache (if using DiskCache).
    """
    
    enabled: bool = True
    cache_embeddings: bool = True
    cache_generations: bool = True
    cache_searches: bool = True
    ttl_seconds: int = 3600  # 1 hour default
    max_size: int = 1000
    cache_dir: str = ".prompt_amplifier_cache"


@dataclass
class CacheEntry:
    """A single cache entry with metadata."""
    
    key: str
    value: Any
    created_at: float = 0.0
    access_count: int = 0
    metadata: dict = field(default_factory=dict)


def generate_cache_key(*args: Any, prefix: str = "") -> str:
    """Generate a deterministic cache key from arguments.
    
    Args:
        *args: Values to include in the key.
        prefix: Optional prefix for the key.
        
    Returns:
        A SHA256 hash string.
    """
    # Convert args to a stable string representation
    key_parts = []
    for arg in args:
        if isinstance(arg, (list, dict)):
            key_parts.append(json.dumps(arg, sort_keys=True, default=str))
        else:
            key_parts.append(str(arg))
    
    key_string = "|".join(key_parts)
    hash_value = hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    if prefix:
        return f"{prefix}:{hash_value}"
    return hash_value


class BaseCache(ABC):
    """Abstract base class for cache implementations.
    
    All cache backends must implement these methods.
    """
    
    def __init__(self, config: CacheConfig | None = None):
        """Initialize the cache.
        
        Args:
            config: Cache configuration. Uses defaults if not provided.
        """
        self.config = config or CacheConfig()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0,
        }
    
    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Retrieve a value from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            The cached value, or None if not found or expired.
        """
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value in the cache.
        
        Args:
            key: The cache key.
            value: The value to cache.
            ttl: Optional TTL override in seconds.
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a key from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            True if the key was deleted, False if not found.
        """
        pass
    
    @abstractmethod
    def clear(self) -> int:
        """Clear all entries from the cache.
        
        Returns:
            Number of entries cleared.
        """
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Get the number of entries in the cache.
        
        Returns:
            Number of cached entries.
        """
        pass
    
    def get_stats(self) -> dict:
        """Get cache statistics.
        
        Returns:
            Dictionary with hits, misses, sets, evictions.
        """
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0.0
        
        return {
            **self._stats,
            "total_requests": total,
            "hit_rate": hit_rate,
            "size": self.size(),
        }
    
    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        return self.get(key) is not None
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(size={self.size()}, config={self.config})"

