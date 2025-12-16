"""Embedding result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class EmbeddingResult:
    """
    Result of an embedding operation.

    Attributes:
        embeddings: List of embedding vectors
        model: Model used for embedding
        dimension: Dimension of the embedding vectors
        input_texts: Original input texts (optional)
        usage: Token usage information (if available)
    """

    embeddings: list[list[float]]
    model: str
    dimension: int
    input_texts: Optional[list[str]] = None
    usage: dict[str, int] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Performance
    embedding_time_ms: float = 0.0

    @property
    def count(self) -> int:
        """Number of embeddings."""
        return len(self.embeddings)

    @property
    def total_tokens(self) -> Optional[int]:
        """Total tokens used (if available)."""
        return self.usage.get("total_tokens")

    def __len__(self) -> int:
        return self.count

    def __iter__(self):
        return iter(self.embeddings)

    def __getitem__(self, idx: int) -> list[float]:
        return self.embeddings[idx]

    def __repr__(self) -> str:
        return (
            f"EmbeddingResult(count={self.count}, dim={self.dimension}, "
            f"model={self.model}, time={self.embedding_time_ms:.1f}ms)"
        )


@dataclass
class SparseEmbedding:
    """
    Sparse embedding representation (for BM25, TF-IDF).

    Attributes:
        indices: Non-zero indices
        values: Values at those indices
        dimension: Total dimension of the sparse vector
    """

    indices: list[int]
    values: list[float]
    dimension: int

    @property
    def nnz(self) -> int:
        """Number of non-zero elements."""
        return len(self.indices)

    @property
    def sparsity(self) -> float:
        """Sparsity ratio (0 = all zeros, 1 = all non-zero)."""
        return self.nnz / self.dimension if self.dimension > 0 else 0.0

    def to_dense(self) -> list[float]:
        """Convert to dense vector."""
        dense = [0.0] * self.dimension
        for idx, val in zip(self.indices, self.values):
            dense[idx] = val
        return dense

    @classmethod
    def from_dense(cls, dense: list[float], threshold: float = 1e-9) -> SparseEmbedding:
        """Create from dense vector, filtering near-zero values."""
        indices = []
        values = []
        for i, v in enumerate(dense):
            if abs(v) > threshold:
                indices.append(i)
                values.append(v)
        return cls(indices=indices, values=values, dimension=len(dense))

    def __repr__(self) -> str:
        return (
            f"SparseEmbedding(nnz={self.nnz}, dim={self.dimension}, sparsity={self.sparsity:.2%})"
        )
