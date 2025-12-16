"""In-memory vector store."""

from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any

import numpy as np

from prompt_amplifier.core.exceptions import DocumentNotFoundError, VectorStoreError
from prompt_amplifier.models.document import Chunk
from prompt_amplifier.models.result import SearchResult, SearchResults
from prompt_amplifier.vectorstores.base import BaseVectorStore


class MemoryStore(BaseVectorStore):
    """
    Simple in-memory vector store.

    Good for testing, prototyping, and small datasets.
    Does not persist data.

    Example:
        >>> store = MemoryStore()
        >>> store.add(chunks)
        >>> results = store.search(query_embedding, top_k=5)
    """

    def __init__(
        self,
        collection_name: str = "default",
        metric: str = "cosine",
        **kwargs: Any,
    ):
        """
        Initialize in-memory store.

        Args:
            collection_name: Name of the collection
            metric: Distance metric ('cosine', 'euclidean', 'dot')
        """
        super().__init__(collection_name=collection_name, **kwargs)
        self.metric = metric

        # Storage
        self._chunks: dict[str, Chunk] = {}
        self._embeddings: dict[str, list[float]] = {}
        self._embedding_matrix: np.ndarray | None = None
        self._id_to_index: dict[str, int] = {}
        self._index_to_id: dict[int, str] = {}
        self._dirty = False  # Track if matrix needs rebuild

    def add(self, chunks: Sequence[Chunk]) -> list[str]:
        """
        Add chunks to the store.

        Args:
            chunks: Chunks with embeddings

        Returns:
            List of chunk IDs
        """
        ids = []

        for chunk in chunks:
            if chunk.embedding is None:
                raise VectorStoreError(
                    f"Chunk {chunk.id} has no embedding. " "Embed chunks before adding to store."
                )

            # Store chunk and embedding
            self._chunks[chunk.id] = chunk
            self._embeddings[chunk.id] = chunk.embedding
            ids.append(chunk.id)

        self._dirty = True  # Matrix needs rebuild
        return ids

    def _build_matrix(self) -> None:
        """Build numpy matrix from embeddings for efficient search."""
        if not self._embeddings:
            self._embedding_matrix = None
            return

        # Build ordered list
        ids = list(self._embeddings.keys())
        self._id_to_index = {id_: i for i, id_ in enumerate(ids)}
        self._index_to_id = {i: id_ for i, id_ in enumerate(ids)}

        # Build matrix
        embeddings = [self._embeddings[id_] for id_ in ids]
        self._embedding_matrix = np.array(embeddings, dtype=np.float32)

        # Normalize for cosine similarity
        if self.metric == "cosine":
            norms = np.linalg.norm(self._embedding_matrix, axis=1, keepdims=True)
            norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
            self._embedding_matrix = self._embedding_matrix / norms

        self._dirty = False

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
            top_k: Number of results
            filter: Metadata filter (basic support)

        Returns:
            SearchResults with ranked results
        """
        if self._dirty or self._embedding_matrix is None:
            self._build_matrix()

        if self._embedding_matrix is None or len(self._embedding_matrix) == 0:
            return SearchResults(results=[], query="", retriever_type="memory")

        start_time = time.time()

        # Convert query to numpy
        query = np.array(query_embedding, dtype=np.float32)

        # Normalize for cosine
        if self.metric == "cosine":
            query_norm = np.linalg.norm(query)
            if query_norm > 0:
                query = query / query_norm

        # Compute similarities
        if self.metric == "cosine" or self.metric == "dot":
            scores = np.dot(self._embedding_matrix, query)
        elif self.metric == "euclidean":
            distances = np.linalg.norm(self._embedding_matrix - query, axis=1)
            scores = -distances  # Negate so higher is better
        else:
            raise VectorStoreError(f"Unknown metric: {self.metric}")

        # Apply filter if provided
        if filter:
            mask = self._apply_filter(filter)
            scores = np.where(mask, scores, -np.inf)

        # Get top-k indices
        top_k = min(top_k, len(scores))
        top_indices = np.argsort(scores)[::-1][:top_k]

        # Build results
        results = []
        for rank, idx in enumerate(top_indices):
            if scores[idx] == -np.inf:
                continue

            chunk_id = self._index_to_id[int(idx)]
            chunk = self._chunks[chunk_id]

            results.append(
                SearchResult(
                    chunk=chunk,
                    score=float(scores[idx]),
                    rank=rank + 1,
                    retriever_type="memory",
                )
            )

        search_time = (time.time() - start_time) * 1000

        return SearchResults(
            results=results,
            query="",
            total_candidates=len(self._chunks),
            retriever_type="memory",
            search_time_ms=search_time,
        )

    def _apply_filter(self, filter: dict[str, Any]) -> np.ndarray:
        """Apply metadata filter, return boolean mask."""
        mask = np.ones(len(self._chunks), dtype=bool)

        for idx, chunk_id in self._index_to_id.items():
            chunk = self._chunks[chunk_id]
            for key, value in filter.items():
                if chunk.metadata.get(key) != value:
                    mask[idx] = False
                    break

        return mask

    def delete(self, ids: Sequence[str]) -> None:
        """Delete chunks by ID."""
        for chunk_id in ids:
            self._chunks.pop(chunk_id, None)
            self._embeddings.pop(chunk_id, None)

        self._dirty = True

    def get(self, ids: Sequence[str]) -> list[Chunk]:
        """Retrieve chunks by ID."""
        results = []
        for chunk_id in ids:
            if chunk_id in self._chunks:
                results.append(self._chunks[chunk_id])
            else:
                raise DocumentNotFoundError(
                    f"Chunk not found: {chunk_id}", details={"id": chunk_id}
                )
        return results

    def clear(self) -> None:
        """Remove all chunks."""
        self._chunks.clear()
        self._embeddings.clear()
        self._embedding_matrix = None
        self._id_to_index.clear()
        self._index_to_id.clear()
        self._dirty = False

    @property
    def count(self) -> int:
        """Number of chunks in store."""
        return len(self._chunks)

    @property
    def is_persistent(self) -> bool:
        return False

    @property
    def supports_filter(self) -> bool:
        return True
