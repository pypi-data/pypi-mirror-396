"""Base chunker interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from prompt_amplifier.models.document import Chunk, Document


class BaseChunker(ABC):
    """
    Abstract base class for all text chunkers.

    Implement this class to add custom chunking strategies.

    Example:
        >>> class MyChunker(BaseChunker):
        ...     def chunk(self, document: Document) -> list[Chunk]:
        ...         # Split document into chunks
        ...         return [Chunk(content=..., document_id=document.id, chunk_index=0)]
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        **kwargs: Any,
    ):
        """
        Initialize the chunker.

        Args:
            chunk_size: Target size of each chunk (in characters)
            chunk_overlap: Overlap between consecutive chunks
            **kwargs: Chunker-specific configuration
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.config = kwargs

        if chunk_overlap >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})"
            )

    @abstractmethod
    def chunk(self, document: Document) -> list[Chunk]:
        """
        Split a document into chunks.

        Args:
            document: Document to split

        Returns:
            List of Chunk objects
        """
        pass

    def chunk_documents(self, documents: Sequence[Document]) -> list[Chunk]:
        """
        Split multiple documents into chunks.

        Args:
            documents: List of documents to split

        Returns:
            List of all chunks from all documents
        """
        chunks = []
        for doc in documents:
            chunks.extend(self.chunk(doc))
        return chunks

    def chunk_text(self, text: str, source: str = "text") -> list[Chunk]:
        """
        Convenience method to chunk raw text.

        Args:
            text: Text to chunk
            source: Source identifier

        Returns:
            List of Chunk objects
        """
        doc = Document(content=text, source=source, source_type="text")
        return self.chunk(doc)

    def _create_chunk(
        self,
        content: str,
        document: Document,
        chunk_index: int,
        metadata: dict[str, Any] | None = None,
    ) -> Chunk:
        """
        Helper to create a Chunk with common fields filled in.

        Args:
            content: Chunk content
            document: Parent document
            chunk_index: Index of this chunk
            metadata: Additional metadata

        Returns:
            Chunk object
        """
        return Chunk(
            content=content,
            document_id=document.id,
            chunk_index=chunk_index,
            source=document.source,
            metadata={
                "source_type": document.source_type,
                "chunker": self.chunker_name,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                **(metadata or {}),
            },
        )

    @property
    def chunker_name(self) -> str:
        """Name of this chunker."""
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"{self.chunker_name}(" f"size={self.chunk_size}, " f"overlap={self.chunk_overlap})"
