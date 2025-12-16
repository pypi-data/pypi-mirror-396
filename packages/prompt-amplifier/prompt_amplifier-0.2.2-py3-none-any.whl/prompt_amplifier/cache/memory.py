"""In-memory cache implementation."""

from __future__ import annotations

import time
from collections import OrderedDict
from threading import Lock
from typing import Any

from prompt_amplifier.cache.base import BaseCache, CacheConfig, CacheEntry


class MemoryCache(BaseCache):
    """Thread-safe in-memory LRU cache.
    
    Uses an OrderedDict for LRU eviction and supports TTL.
    
    Example:
        ```python
        from prompt_amplifier.cache import MemoryCache, CacheConfig
        
        cache = MemoryCache(CacheConfig(ttl_seconds=3600, max_size=100))
        
        # Store a value
        cache.set("my_key", {"data": "value"})
        
        # Retrieve it
        result = cache.get("my_key")
        print(result)  # {"data": "value"}
        
        # Check stats
        print(cache.get_stats())
        ```
    """
    
    def __init__(self, config: CacheConfig | None = None):
        """Initialize the memory cache.
        
        Args:
            config: Cache configuration.
        """
        super().__init__(config)
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = Lock()
    
    def get(self, key: str) -> Any | None:
        """Retrieve a value from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            The cached value, or None if not found or expired.
        """
        if not self.config.enabled:
            return None
        
        with self._lock:
            if key not in self._cache:
                self._stats["misses"] += 1
                return None
            
            entry = self._cache[key]
            
            # Check TTL
            if self.config.ttl_seconds > 0:
                age = time.time() - entry.created_at
                if age > self.config.ttl_seconds:
                    del self._cache[key]
                    self._stats["misses"] += 1
                    self._stats["evictions"] += 1
                    return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.access_count += 1
            self._stats["hits"] += 1
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value in the cache.
        
        Args:
            key: The cache key.
            value: The value to cache.
            ttl: Optional TTL override (not used in memory cache, uses config).
        """
        if not self.config.enabled:
            return
        
        with self._lock:
            # Evict if at max size
            if self.config.max_size > 0:
                while len(self._cache) >= self.config.max_size:
                    # Remove oldest (first) item
                    self._cache.popitem(last=False)
                    self._stats["evictions"] += 1
            
            # Create or update entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                access_count=0,
            )
            
            self._cache[key] = entry
            self._cache.move_to_end(key)
            self._stats["sets"] += 1
    
    def delete(self, key: str) -> bool:
        """Delete a key from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            True if deleted, False if not found.
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> int:
        """Clear all entries from the cache.
        
        Returns:
            Number of entries cleared.
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count
    
    def size(self) -> int:
        """Get the number of entries in the cache.
        
        Returns:
            Number of cached entries.
        """
        return len(self._cache)
    
    def keys(self) -> list[str]:
        """Get all cache keys.
        
        Returns:
            List of cache keys.
        """
        with self._lock:
            return list(self._cache.keys())

