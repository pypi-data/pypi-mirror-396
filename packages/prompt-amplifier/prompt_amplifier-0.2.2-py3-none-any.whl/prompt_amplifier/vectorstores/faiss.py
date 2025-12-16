"""FAISS vector store."""

from __future__ import annotations

import json
import pickle
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np

from prompt_amplifier.core.exceptions import DocumentNotFoundError, VectorStoreError
from prompt_amplifier.models.document import Chunk
from prompt_amplifier.models.result import SearchResult, SearchResults
from prompt_amplifier.vectorstores.base import BaseVectorStore


class FAISSStore(BaseVectorStore):
    """
    FAISS vector store (Meta).

    Highly optimized for similarity search. Supports various index types.

    Requires: faiss-cpu or faiss-gpu

    Index types:
        - "Flat": Exact search (best quality, slower for large datasets)
        - "IVF": Inverted file index (faster, approximate)
        - "HNSW": Hierarchical navigable small world (fast, good quality)

    Example:
        >>> store = FAISSStore(
        ...     dimension=384,
        ...     index_type="Flat",
        ...     persist_directory="./faiss_index"
        ... )
        >>> store.add(chunks)
        >>> results = store.search(query_embedding, top_k=5)
    """

    def __init__(
        self,
        collection_name: str = "prompt_amplifier",
        dimension: int | None = None,
        index_type: str = "Flat",
        metric: str = "cosine",
        persist_directory: str | None = None,
        nlist: int = 100,  # For IVF indexes
        **kwargs: Any,
    ):
        """
        Initialize FAISS store.

        Args:
            collection_name: Name for persistence
            dimension: Embedding dimension (auto-detected from first add)
            index_type: FAISS index type ('Flat', 'IVF', 'HNSW')
            metric: Distance metric ('cosine', 'l2', 'ip')
            persist_directory: Directory for persistence
            nlist: Number of clusters for IVF index
        """
        super().__init__(collection_name=collection_name, **kwargs)
        self.dimension = dimension
        self.index_type = index_type
        self.metric = metric
        self.persist_directory = persist_directory
        self.nlist = nlist

        self._index = None
        self._chunks: dict[str, Chunk] = {}
        self._id_to_idx: dict[str, int] = {}
        self._idx_to_id: dict[int, str] = {}
        self._next_idx = 0

        self._check_dependency()

        # Load existing index if persist_directory exists
        if persist_directory:
            self._try_load()

    def _check_dependency(self) -> None:
        """Check if faiss is installed."""
        try:
            import faiss  # noqa: F401
        except ImportError:
            raise ImportError(
                "faiss is required for FAISSStore. " "Install it with: pip install faiss-cpu"
            )

    def _create_index(self, dimension: int) -> Any:
        """Create FAISS index based on configuration."""
        import faiss

        # Determine metric
        if self.metric == "cosine":
            # For cosine, we normalize vectors and use inner product
            metric_type = faiss.METRIC_INNER_PRODUCT
        elif self.metric == "l2":
            metric_type = faiss.METRIC_L2
        elif self.metric == "ip":
            metric_type = faiss.METRIC_INNER_PRODUCT
        else:
            raise VectorStoreError(f"Unknown metric: {self.metric}")

        # Create index based on type
        if self.index_type == "Flat":
            if metric_type == faiss.METRIC_L2:
                index = faiss.IndexFlatL2(dimension)
            else:
                index = faiss.IndexFlatIP(dimension)

        elif self.index_type == "IVF":
            quantizer = faiss.IndexFlatL2(dimension)
            index = faiss.IndexIVFFlat(quantizer, dimension, self.nlist, metric_type)

        elif self.index_type == "HNSW":
            index = faiss.IndexHNSWFlat(dimension, 32, metric_type)

        else:
            raise VectorStoreError(f"Unknown index type: {self.index_type}")

        return index

    def add(self, chunks: Sequence[Chunk]) -> list[str]:
        """
        Add chunks to FAISS.

        Args:
            chunks: Chunks with embeddings

        Returns:
            List of chunk IDs
        """
        import faiss

        if not chunks:
            return []

        # Get embeddings
        embeddings = []
        ids = []

        for chunk in chunks:
            if chunk.embedding is None:
                raise VectorStoreError(f"Chunk {chunk.id} has no embedding.")

            embeddings.append(chunk.embedding)
            ids.append(chunk.id)
            self._chunks[chunk.id] = chunk

        # Convert to numpy
        vectors = np.array(embeddings, dtype=np.float32)

        # Auto-detect dimension from first add
        if self.dimension is None:
            self.dimension = vectors.shape[1]

        # Create index if needed
        if self._index is None:
            self._index = self._create_index(self.dimension)

        # Normalize for cosine similarity
        if self.metric == "cosine":
            faiss.normalize_L2(vectors)

        # Train IVF index if needed
        if self.index_type == "IVF" and not self._index.is_trained:
            if len(vectors) >= self.nlist:
                self._index.train(vectors)
            else:
                # Fall back to Flat if not enough vectors
                self._index = self._create_index(self.dimension)

        # Add to index
        self._index.add(vectors)

        # Update ID mappings
        for chunk_id in ids:
            self._id_to_idx[chunk_id] = self._next_idx
            self._idx_to_id[self._next_idx] = chunk_id
            self._next_idx += 1

        return ids

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> SearchResults:
        """
        Search FAISS index.

        Args:
            query_embedding: Query vector
            top_k: Number of results
            filter: Not supported by FAISS (ignored)

        Returns:
            SearchResults with ranked results
        """
        import faiss

        if self._index is None or self._index.ntotal == 0:
            return SearchResults(results=[], query="", retriever_type="faiss")

        start_time = time.time()

        # Convert query to numpy
        query = np.array([query_embedding], dtype=np.float32)

        # Normalize for cosine
        if self.metric == "cosine":
            faiss.normalize_L2(query)

        # Search
        top_k = min(top_k, self._index.ntotal)
        distances, indices = self._index.search(query, top_k)

        search_time = (time.time() - start_time) * 1000

        # Build results
        results = []
        for rank, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # FAISS returns -1 for no result
                continue

            chunk_id = self._idx_to_id.get(int(idx))
            if chunk_id is None:
                continue

            chunk = self._chunks.get(chunk_id)
            if chunk is None:
                continue

            # Convert distance to score
            if self.metric == "cosine" or self.metric == "ip":
                score = float(dist)  # Already similarity
            else:
                score = -float(dist)  # Negate L2 distance

            results.append(
                SearchResult(
                    chunk=chunk,
                    score=score,
                    rank=rank + 1,
                    retriever_type="faiss",
                )
            )

        return SearchResults(
            results=results,
            query="",
            total_candidates=self._index.ntotal,
            retriever_type="faiss",
            search_time_ms=search_time,
        )

    def delete(self, ids: Sequence[str]) -> None:
        """
        Delete chunks by ID.

        Note: FAISS doesn't support deletion well.
        This marks items as deleted but doesn't remove from index.
        """
        for chunk_id in ids:
            if chunk_id in self._chunks:
                del self._chunks[chunk_id]
                idx = self._id_to_idx.get(chunk_id)
                if idx is not None:
                    del self._id_to_idx[chunk_id]
                    del self._idx_to_id[idx]

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
        """Remove all chunks and reset index."""
        self._index = None
        self._chunks.clear()
        self._id_to_idx.clear()
        self._idx_to_id.clear()
        self._next_idx = 0

    def persist(self) -> None:
        """Save index and metadata to disk."""
        import faiss

        if not self.persist_directory or self._index is None:
            return

        path = Path(self.persist_directory)
        path.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        faiss.write_index(self._index, str(path / f"{self.collection_name}.faiss"))

        # Save metadata
        metadata = {
            "dimension": self.dimension,
            "metric": self.metric,
            "index_type": self.index_type,
            "next_idx": self._next_idx,
            "id_to_idx": self._id_to_idx,
            "idx_to_id": {int(k): v for k, v in self._idx_to_id.items()},
        }

        with open(path / f"{self.collection_name}_meta.json", "w") as f:
            json.dump(metadata, f)

        # Save chunks
        with open(path / f"{self.collection_name}_chunks.pkl", "wb") as f:
            pickle.dump(self._chunks, f)

    def _try_load(self) -> None:
        """Try to load existing index from disk."""
        import faiss

        if not self.persist_directory:
            return

        path = Path(self.persist_directory)
        index_path = path / f"{self.collection_name}.faiss"
        meta_path = path / f"{self.collection_name}_meta.json"
        chunks_path = path / f"{self.collection_name}_chunks.pkl"

        if not index_path.exists():
            return

        try:
            # Load index
            self._index = faiss.read_index(str(index_path))

            # Load metadata
            if meta_path.exists():
                with open(meta_path) as f:
                    metadata = json.load(f)

                self.dimension = metadata["dimension"]
                self.metric = metadata["metric"]
                self.index_type = metadata["index_type"]
                self._next_idx = metadata["next_idx"]
                self._id_to_idx = metadata["id_to_idx"]
                self._idx_to_id = {int(k): v for k, v in metadata["idx_to_id"].items()}

            # Load chunks
            if chunks_path.exists():
                with open(chunks_path, "rb") as f:
                    self._chunks = pickle.load(f)

        except Exception as e:
            # If loading fails, start fresh
            self._index = None
            print(f"Warning: Failed to load FAISS index: {e}")

    @property
    def count(self) -> int:
        """Number of vectors in index."""
        if self._index is None:
            return 0
        return self._index.ntotal

    @property
    def is_persistent(self) -> bool:
        return self.persist_directory is not None

    @property
    def supports_filter(self) -> bool:
        return False  # FAISS doesn't support metadata filtering
