"""Caching module for Prompt Amplifier."""

from __future__ import annotations

from prompt_amplifier.cache.base import BaseCache, CacheConfig
from prompt_amplifier.cache.memory import MemoryCache
from prompt_amplifier.cache.disk import DiskCache

__all__ = [
    "BaseCache",
    "CacheConfig",
    "MemoryCache",
    "DiskCache",
]

