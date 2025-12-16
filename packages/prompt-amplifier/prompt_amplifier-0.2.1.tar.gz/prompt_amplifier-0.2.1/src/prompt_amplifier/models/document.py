"""Document and Chunk data models."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class Document:
    """
    Represents a loaded document from any source.

    Attributes:
        id: Unique identifier for the document
        content: The text content of the document
        source: Original source path or URL
        source_type: Type of source (pdf, docx, csv, etc.)
        metadata: Additional metadata (author, created_date, etc.)
        created_at: When this document object was created
    """

    content: str
    source: str
    source_type: str = "unknown"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Generate content hash for deduplication."""
        if "content_hash" not in self.metadata:
            self.metadata["content_hash"] = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute MD5 hash of content for deduplication."""
        return hashlib.md5(self.content.encode("utf-8")).hexdigest()

    @property
    def content_hash(self) -> str:
        """Get the content hash."""
        return self.metadata.get("content_hash", self._compute_hash())

    def __len__(self) -> int:
        """Return the length of the content."""
        return len(self.content)

    def __repr__(self) -> str:
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"Document(id={self.id[:8]}, source={self.source}, len={len(self)}, preview='{preview}')"


@dataclass
class Chunk:
    """
    Represents a chunk of text split from a document.

    Attributes:
        id: Unique identifier for the chunk
        content: The text content of the chunk
        document_id: ID of the parent document
        chunk_index: Position of this chunk in the document (0-indexed)
        source: Original source path or URL (inherited from document)
        embedding: Vector embedding (populated after embedding)
        metadata: Additional metadata
    """

    content: str
    document_id: str
    chunk_index: int
    source: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    embedding: Optional[list[float]] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    # Token/character counts (useful for context window management)
    char_count: int = field(init=False)

    def __post_init__(self) -> None:
        """Compute derived fields."""
        self.char_count = len(self.content)

    @property
    def has_embedding(self) -> bool:
        """Check if this chunk has been embedded."""
        return self.embedding is not None and len(self.embedding) > 0

    @property
    def embedding_dim(self) -> Optional[int]:
        """Get the dimension of the embedding."""
        return len(self.embedding) if self.embedding else None

    def __len__(self) -> int:
        """Return the length of the content."""
        return self.char_count

    def __repr__(self) -> str:
        embedded = "✓" if self.has_embedding else "✗"
        return (
            f"Chunk(id={self.id[:8]}, doc={self.document_id[:8]}, "
            f"idx={self.chunk_index}, len={len(self)}, embedded={embedded})"
        )


@dataclass
class ChunkBatch:
    """
    A batch of chunks for efficient processing.

    Useful for batched embedding operations.
    """

    chunks: list[Chunk]

    @property
    def contents(self) -> list[str]:
        """Get all chunk contents."""
        return [c.content for c in self.chunks]

    @property
    def ids(self) -> list[str]:
        """Get all chunk IDs."""
        return [c.id for c in self.chunks]

    def set_embeddings(self, embeddings: list[list[float]]) -> None:
        """Set embeddings for all chunks in batch."""
        if len(embeddings) != len(self.chunks):
            raise ValueError(
                f"Embedding count ({len(embeddings)}) doesn't match chunk count ({len(self.chunks)})"
            )
        for chunk, embedding in zip(self.chunks, embeddings):
            chunk.embedding = embedding

    def __len__(self) -> int:
        return len(self.chunks)

    def __iter__(self):
        return iter(self.chunks)
