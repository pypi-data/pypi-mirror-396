"""Result models for search and expansion operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from prompt_amplifier.models.document import Chunk


@dataclass
class SearchResult:
    """
    Represents a single search result from the retriever.

    Attributes:
        chunk: The retrieved chunk
        score: Similarity/relevance score (higher is better)
        rank: Position in the result list (1-indexed)
        retriever_type: Type of retriever that produced this result
    """

    chunk: Chunk
    score: float
    rank: int = 0
    retriever_type: str = "vector"

    @property
    def content(self) -> str:
        """Shortcut to get chunk content."""
        return self.chunk.content

    @property
    def source(self) -> str:
        """Shortcut to get chunk source."""
        return self.chunk.source

    def __repr__(self) -> str:
        return (
            f"SearchResult(rank={self.rank}, score={self.score:.4f}, "
            f"source={self.source}, len={len(self.content)})"
        )


@dataclass
class SearchResults:
    """
    Collection of search results with metadata.
    """

    results: list[SearchResult]
    query: str
    total_candidates: int = 0
    retriever_type: str = "vector"
    search_time_ms: float = 0.0

    @property
    def chunks(self) -> list[Chunk]:
        """Get all chunks from results."""
        return [r.chunk for r in self.results]

    @property
    def contents(self) -> list[str]:
        """Get all content strings from results."""
        return [r.content for r in self.results]

    @property
    def top_score(self) -> Optional[float]:
        """Get the highest score."""
        return self.results[0].score if self.results else None

    def __len__(self) -> int:
        return len(self.results)

    def __iter__(self):
        return iter(self.results)

    def __getitem__(self, idx: int) -> SearchResult:
        return self.results[idx]


@dataclass
class ExpandResult:
    """
    Result of a prompt expansion operation.

    Attributes:
        prompt: The expanded, detailed prompt
        original_prompt: The original short prompt
        context_chunks: Chunks used for context
        schema_fields: Schema fields used (if any)
        metadata: Additional metadata about the expansion
        created_at: When the expansion was performed
    """

    prompt: str
    original_prompt: str
    context_chunks: list[Chunk] = field(default_factory=list)
    schema_fields: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Performance metrics
    retrieval_time_ms: float = 0.0
    generation_time_ms: float = 0.0
    total_time_ms: float = 0.0

    # Token usage (if available from LLM)
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None

    @property
    def context_sources(self) -> list[str]:
        """Get unique sources used for context."""
        return list(set(c.source for c in self.context_chunks))

    @property
    def context_count(self) -> int:
        """Number of context chunks used."""
        return len(self.context_chunks)

    @property
    def expansion_ratio(self) -> float:
        """Ratio of expanded prompt length to original."""
        if not self.original_prompt:
            return 0.0
        return len(self.prompt) / len(self.original_prompt)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "prompt": self.prompt,
            "original_prompt": self.original_prompt,
            "context_sources": self.context_sources,
            "context_count": self.context_count,
            "schema_fields": self.schema_fields,
            "expansion_ratio": self.expansion_ratio,
            "retrieval_time_ms": self.retrieval_time_ms,
            "generation_time_ms": self.generation_time_ms,
            "total_time_ms": self.total_time_ms,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return (
            f"ExpandResult(original='{self.original_prompt[:30]}...', "
            f"expanded_len={len(self.prompt)}, "
            f"context_chunks={self.context_count}, "
            f"expansion_ratio={self.expansion_ratio:.1f}x)"
        )
