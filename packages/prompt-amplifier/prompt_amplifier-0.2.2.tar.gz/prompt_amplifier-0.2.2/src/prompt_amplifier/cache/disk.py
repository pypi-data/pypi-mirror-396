"""Disk-based cache implementation."""

from __future__ import annotations

import json
import os
import pickle
import time
from pathlib import Path
from typing import Any

from prompt_amplifier.cache.base import BaseCache, CacheConfig


class DiskCache(BaseCache):
    """Persistent disk-based cache.
    
    Stores cache entries as files on disk for persistence across sessions.
    Uses pickle for serialization (supports complex Python objects).
    
    Example:
        ```python
        from prompt_amplifier.cache import DiskCache, CacheConfig
        
        cache = DiskCache(CacheConfig(
            cache_dir="./my_cache",
            ttl_seconds=86400  # 24 hours
        ))
        
        # Store a value
        cache.set("embeddings:doc1", [0.1, 0.2, 0.3])
        
        # Retrieve it (even after restart)
        result = cache.get("embeddings:doc1")
        ```
    """
    
    def __init__(self, config: CacheConfig | None = None):
        """Initialize the disk cache.
        
        Args:
            config: Cache configuration.
        """
        super().__init__(config)
        self._cache_dir = Path(self.config.cache_dir)
        self._ensure_cache_dir()
        self._index_file = self._cache_dir / "_index.json"
        self._index = self._load_index()
    
    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_index(self) -> dict:
        """Load the cache index from disk."""
        if self._index_file.exists():
            try:
                with open(self._index_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_index(self) -> None:
        """Save the cache index to disk."""
        with open(self._index_file, "w") as f:
            json.dump(self._index, f, indent=2)
    
    def _get_file_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        # Sanitize key for filename
        safe_key = key.replace(":", "_").replace("/", "_")
        return self._cache_dir / f"{safe_key}.pkl"
    
    def get(self, key: str) -> Any | None:
        """Retrieve a value from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            The cached value, or None if not found or expired.
        """
        if not self.config.enabled:
            return None
        
        if key not in self._index:
            self._stats["misses"] += 1
            return None
        
        entry_meta = self._index[key]
        
        # Check TTL
        if self.config.ttl_seconds > 0:
            age = time.time() - entry_meta.get("created_at", 0)
            if age > self.config.ttl_seconds:
                self.delete(key)
                self._stats["misses"] += 1
                return None
        
        # Load from disk
        file_path = self._get_file_path(key)
        if not file_path.exists():
            del self._index[key]
            self._save_index()
            self._stats["misses"] += 1
            return None
        
        try:
            with open(file_path, "rb") as f:
                value = pickle.load(f)
            
            self._stats["hits"] += 1
            
            # Update access count
            entry_meta["access_count"] = entry_meta.get("access_count", 0) + 1
            self._save_index()
            
            return value
        except (pickle.PickleError, IOError):
            self.delete(key)
            self._stats["misses"] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value in the cache.
        
        Args:
            key: The cache key.
            value: The value to cache.
            ttl: Optional TTL override (not currently used).
        """
        if not self.config.enabled:
            return
        
        # Evict if at max size
        if self.config.max_size > 0:
            while len(self._index) >= self.config.max_size:
                # Remove oldest entry
                oldest_key = min(
                    self._index.keys(),
                    key=lambda k: self._index[k].get("created_at", 0)
                )
                self.delete(oldest_key)
                self._stats["evictions"] += 1
        
        # Save to disk
        file_path = self._get_file_path(key)
        try:
            with open(file_path, "wb") as f:
                pickle.dump(value, f)
            
            # Update index
            self._index[key] = {
                "created_at": time.time(),
                "access_count": 0,
                "file": str(file_path),
            }
            self._save_index()
            self._stats["sets"] += 1
            
        except (pickle.PickleError, IOError) as e:
            # Silently fail on cache errors
            pass
    
    def delete(self, key: str) -> bool:
        """Delete a key from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            True if deleted, False if not found.
        """
        if key not in self._index:
            return False
        
        # Delete file
        file_path = self._get_file_path(key)
        if file_path.exists():
            try:
                os.remove(file_path)
            except OSError:
                pass
        
        # Update index
        del self._index[key]
        self._save_index()
        
        return True
    
    def clear(self) -> int:
        """Clear all entries from the cache.
        
        Returns:
            Number of entries cleared.
        """
        count = len(self._index)
        
        # Delete all cache files
        for key in list(self._index.keys()):
            self.delete(key)
        
        return count
    
    def size(self) -> int:
        """Get the number of entries in the cache.
        
        Returns:
            Number of cached entries.
        """
        return len(self._index)
    
    def keys(self) -> list[str]:
        """Get all cache keys.
        
        Returns:
            List of cache keys.
        """
        return list(self._index.keys())
    
    def get_disk_usage(self) -> int:
        """Get total disk usage of the cache in bytes.
        
        Returns:
            Total bytes used by cache files.
        """
        total = 0
        for file_path in self._cache_dir.glob("*.pkl"):
            total += file_path.stat().st_size
        return total

