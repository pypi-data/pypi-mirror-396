"""Base retriever interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from prompt_amplifier.embedders.base import BaseEmbedder
from prompt_amplifier.models.result import SearchResults
from prompt_amplifier.vectorstores.base import BaseVectorStore


class BaseRetriever(ABC):
    """
    Abstract base class for all retrievers.

    Retrievers combine embedders and vector stores to find relevant chunks.

    Example:
        >>> class MyRetriever(BaseRetriever):
        ...     def retrieve(self, query: str, top_k: int) -> SearchResults:
        ...         # Embed query and search
        ...         embedding = self.embedder.embed_single(query)
        ...         return self.vectorstore.search(embedding, top_k)
    """

    def __init__(
        self,
        embedder: BaseEmbedder,
        vectorstore: BaseVectorStore,
        top_k: int = 10,
        **kwargs: Any,
    ):
        """
        Initialize the retriever.

        Args:
            embedder: Embedder for query encoding
            vectorstore: Vector store for search
            top_k: Default number of results
            **kwargs: Retriever-specific configuration
        """
        self.embedder = embedder
        self.vectorstore = vectorstore
        self.top_k = top_k
        self.config = kwargs

    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filter: dict[str, Any] | None = None,
    ) -> SearchResults:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: Search query string
            top_k: Number of results (uses default if None)
            filter: Optional metadata filters

        Returns:
            SearchResults with ranked results
        """
        pass

    def retrieve_with_scores(
        self,
        query: str,
        top_k: int | None = None,
        score_threshold: float = 0.0,
    ) -> SearchResults:
        """
        Retrieve chunks above a score threshold.

        Args:
            query: Search query
            top_k: Number of results
            score_threshold: Minimum score to include

        Returns:
            Filtered SearchResults
        """
        results = self.retrieve(query, top_k)

        # Filter by score threshold
        filtered = [r for r in results.results if r.score >= score_threshold]

        return SearchResults(
            results=filtered,
            query=query,
            total_candidates=results.total_candidates,
            retriever_type=results.retriever_type,
            search_time_ms=results.search_time_ms,
        )

    @property
    def retriever_name(self) -> str:
        """Name of this retriever."""
        return self.__class__.__name__

    def __repr__(self) -> str:
        return (
            f"{self.retriever_name}("
            f"embedder={self.embedder.embedder_name}, "
            f"store={self.vectorstore.store_name}, "
            f"top_k={self.top_k})"
        )
