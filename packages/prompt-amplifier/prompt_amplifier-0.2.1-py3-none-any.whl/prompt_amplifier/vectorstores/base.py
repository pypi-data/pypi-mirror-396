"""Base vector store interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from prompt_amplifier.models.document import Chunk
from prompt_amplifier.models.result import SearchResults


class BaseVectorStore(ABC):
    """
    Abstract base class for all vector stores.

    Implement this class to add support for new vector databases.

    Example:
        >>> class MyVectorStore(BaseVectorStore):
        ...     def add(self, chunks: list[Chunk]) -> list[str]:
        ...         # Store chunks and return IDs
        ...         return [chunk.id for chunk in chunks]
        ...
        ...     def search(self, query_embedding: list[float], top_k: int) -> SearchResults:
        ...         # Search and return results
        ...         return SearchResults(results=[], query="")
    """

    def __init__(
        self,
        collection_name: str = "prompt_amplifier",
        **kwargs: Any,
    ):
        """
        Initialize the vector store.

        Args:
            collection_name: Name of the collection/index
            **kwargs: Store-specific configuration
        """
        self.collection_name = collection_name
        self.config = kwargs

    @abstractmethod
    def add(self, chunks: Sequence[Chunk]) -> list[str]:
        """
        Add chunks to the vector store.

        Chunks must have embeddings attached.

        Args:
            chunks: List of chunks with embeddings

        Returns:
            List of IDs for the added chunks

        Raises:
            VectorStoreError: If adding fails
        """
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> SearchResults:
        """
        Search for similar chunks.

        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter: Optional metadata filters

        Returns:
            SearchResults with ranked results

        Raises:
            VectorStoreError: If search fails
        """
        pass

    @abstractmethod
    def delete(self, ids: Sequence[str]) -> None:
        """
        Delete chunks by ID.

        Args:
            ids: List of chunk IDs to delete

        Raises:
            VectorStoreError: If deletion fails
        """
        pass

    @abstractmethod
    def get(self, ids: Sequence[str]) -> list[Chunk]:
        """
        Retrieve chunks by ID.

        Args:
            ids: List of chunk IDs

        Returns:
            List of Chunk objects

        Raises:
            DocumentNotFoundError: If chunk not found
        """
        pass

    @property
    @abstractmethod
    def count(self) -> int:
        """
        Get the number of chunks in the store.

        Returns:
            Number of stored chunks
        """
        pass

    def clear(self) -> None:
        """
        Remove all chunks from the store.

        Default implementation deletes all by getting and deleting IDs.
        Override for more efficient implementations.
        """
        # This is a fallback; subclasses should override with efficient implementation
        raise NotImplementedError("Subclass should implement clear()")

    def persist(self) -> None:
        """
        Persist the store to disk.

        No-op for stores that auto-persist or don't support persistence.
        """
        pass

    def load(self) -> None:
        """
        Load the store from disk.

        No-op for stores that auto-load or don't support persistence.
        """
        pass

    @property
    def store_name(self) -> str:
        """Name of this store implementation."""
        return self.__class__.__name__

    @property
    def is_persistent(self) -> bool:
        """
        Whether this store persists data.

        Returns:
            True if data survives restarts
        """
        return False

    @property
    def supports_filter(self) -> bool:
        """
        Whether this store supports metadata filtering.

        Returns:
            True if filter parameter is supported in search
        """
        return False

    def __repr__(self) -> str:
        return f"{self.store_name}(collection={self.collection_name}, count={self.count})"

    def __len__(self) -> int:
        return self.count
