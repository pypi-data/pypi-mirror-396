"""Vector store implementations for document persistence and search."""

from __future__ import annotations

from prompt_amplifier.vectorstores.base import BaseVectorStore
from prompt_amplifier.vectorstores.memory import MemoryStore

__all__ = [
    "BaseVectorStore",
    "MemoryStore",
]

# Optional vector stores
try:
    from prompt_amplifier.vectorstores.chroma import ChromaStore

    __all__.append("ChromaStore")
except ImportError:
    pass

try:
    from prompt_amplifier.vectorstores.faiss import FAISSStore

    __all__.append("FAISSStore")
except ImportError:
    pass
