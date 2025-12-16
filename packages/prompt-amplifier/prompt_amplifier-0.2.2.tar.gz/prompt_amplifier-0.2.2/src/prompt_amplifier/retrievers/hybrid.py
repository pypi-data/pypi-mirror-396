"""Hybrid retriever combining keyword and vector search."""

from __future__ import annotations

import time
from typing import Any

from prompt_amplifier.embedders.base import BaseEmbedder, BaseSparseEmbedder
from prompt_amplifier.models.document import Chunk
from prompt_amplifier.models.result import SearchResult, SearchResults
from prompt_amplifier.retrievers.base import BaseRetriever
from prompt_amplifier.vectorstores.base import BaseVectorStore


class HybridRetriever(BaseRetriever):
    """
    Hybrid retriever combining dense and sparse search.

    Fuses results from vector search (semantic) and keyword search (BM25/TF-IDF)
    using Reciprocal Rank Fusion (RRF) or weighted scoring.

    Example:
        >>> hybrid = HybridRetriever(
        ...     dense_embedder=sentence_transformer,
        ...     sparse_embedder=bm25_embedder,
        ...     vectorstore=chroma_store,
        ...     dense_weight=0.7,
        ...     sparse_weight=0.3,
        ... )
        >>> results = hybrid.retrieve("deal health status")
    """

    def __init__(
        self,
        embedder: BaseEmbedder,  # Dense embedder
        vectorstore: BaseVectorStore,
        sparse_embedder: BaseSparseEmbedder | None = None,
        top_k: int = 10,
        dense_weight: float = 0.7,
        sparse_weight: float = 0.3,
        fusion_method: str = "rrf",  # "rrf" or "weighted"
        rrf_k: int = 60,  # RRF constant
        **kwargs: Any,
    ):
        """
        Initialize hybrid retriever.

        Args:
            embedder: Dense embedder (e.g., SentenceTransformers)
            vectorstore: Vector store for dense search
            sparse_embedder: Sparse embedder (e.g., BM25, TF-IDF)
            top_k: Number of results
            dense_weight: Weight for dense results (0-1)
            sparse_weight: Weight for sparse results (0-1)
            fusion_method: How to combine results ('rrf' or 'weighted')
            rrf_k: Constant for RRF formula
        """
        super().__init__(embedder, vectorstore, top_k, **kwargs)
        self.sparse_embedder = sparse_embedder
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
        self.fusion_method = fusion_method
        self.rrf_k = rrf_k

        # Normalize weights
        total = dense_weight + sparse_weight
        self.dense_weight = dense_weight / total
        self.sparse_weight = sparse_weight / total

        # Storage for sparse search (BM25 needs corpus)
        self._chunks_for_sparse: list[Chunk] = []

    def add_chunks_for_sparse(self, chunks: list[Chunk]) -> None:
        """
        Add chunks for sparse (keyword) search.

        Call this after adding chunks to the vector store.

        Args:
            chunks: Chunks to index for sparse search
        """
        self._chunks_for_sparse = chunks

        if self.sparse_embedder and hasattr(self.sparse_embedder, "fit"):
            texts = [c.content for c in chunks]
            self.sparse_embedder.fit(texts)

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filter: dict[str, Any] | None = None,
    ) -> SearchResults:
        """
        Retrieve using hybrid search.

        Args:
            query: Search query
            top_k: Number of results
            filter: Optional metadata filter (dense only)

        Returns:
            SearchResults with fused rankings
        """
        top_k = top_k or self.top_k
        start_time = time.time()

        # Dense (vector) search
        query_embedding = self.embedder.embed_single(query)
        dense_results = self.vectorstore.search(
            query_embedding=query_embedding,
            top_k=top_k * 2,  # Fetch more for fusion
            filter=filter,
        )

        # Sparse (keyword) search
        sparse_results = self._sparse_search(query, top_k * 2)

        # Fuse results
        if self.fusion_method == "rrf":
            fused = self._rrf_fusion(dense_results.results, sparse_results, top_k)
        else:
            fused = self._weighted_fusion(dense_results.results, sparse_results, top_k)

        search_time = (time.time() - start_time) * 1000

        return SearchResults(
            results=fused,
            query=query,
            total_candidates=dense_results.total_candidates,
            retriever_type="hybrid",
            search_time_ms=search_time,
        )

    def _sparse_search(self, query: str, top_k: int) -> list[SearchResult]:
        """Perform sparse (keyword) search."""
        if not self.sparse_embedder or not self._chunks_for_sparse:
            return []

        if not self.sparse_embedder.is_fitted:
            return []

        # Get BM25/TF-IDF scores
        from prompt_amplifier.embedders.tfidf import BM25Embedder

        if isinstance(self.sparse_embedder, BM25Embedder):
            # BM25 gives scores directly
            top_results = self.sparse_embedder.get_top_n(query, n=top_k)

            results = []
            for rank, (idx, score) in enumerate(top_results):
                if idx < len(self._chunks_for_sparse):
                    results.append(
                        SearchResult(
                            chunk=self._chunks_for_sparse[idx],
                            score=score,
                            rank=rank + 1,
                            retriever_type="sparse",
                        )
                    )
            return results
        else:
            # TF-IDF: embed query and compute similarities
            import numpy as np

            query_result = self.sparse_embedder.embed([query])
            query_vec = np.array(query_result.embeddings[0])

            # Embed all chunks (cached in sparse embedder)
            corpus_result = self.sparse_embedder.embed([c.content for c in self._chunks_for_sparse])
            corpus_matrix = np.array(corpus_result.embeddings)

            # Compute similarities
            similarities = np.dot(corpus_matrix, query_vec)
            top_indices = np.argsort(similarities)[::-1][:top_k]

            results = []
            for rank, idx in enumerate(top_indices):
                results.append(
                    SearchResult(
                        chunk=self._chunks_for_sparse[idx],
                        score=float(similarities[idx]),
                        rank=rank + 1,
                        retriever_type="sparse",
                    )
                )
            return results

    def _rrf_fusion(
        self,
        dense_results: list[SearchResult],
        sparse_results: list[SearchResult],
        top_k: int,
    ) -> list[SearchResult]:
        """
        Reciprocal Rank Fusion.

        RRF score = Σ 1/(k + rank) for each list where doc appears
        """
        # Build chunk_id -> RRF score mapping
        rrf_scores: dict[str, float] = {}
        chunk_map: dict[str, Chunk] = {}

        # Process dense results
        for result in dense_results:
            chunk_id = result.chunk.id
            chunk_map[chunk_id] = result.chunk
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0)
            rrf_scores[chunk_id] += self.dense_weight * (1.0 / (self.rrf_k + result.rank))

        # Process sparse results
        for result in sparse_results:
            chunk_id = result.chunk.id
            chunk_map[chunk_id] = result.chunk
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0)
            rrf_scores[chunk_id] += self.sparse_weight * (1.0 / (self.rrf_k + result.rank))

        # Sort by RRF score
        sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        # Build final results
        fused = []
        for rank, (chunk_id, score) in enumerate(sorted_items[:top_k]):
            fused.append(
                SearchResult(
                    chunk=chunk_map[chunk_id],
                    score=score,
                    rank=rank + 1,
                    retriever_type="hybrid",
                )
            )

        return fused

    def _weighted_fusion(
        self,
        dense_results: list[SearchResult],
        sparse_results: list[SearchResult],
        top_k: int,
    ) -> list[SearchResult]:
        """
        Weighted score fusion.

        Final score = dense_weight * dense_score + sparse_weight * sparse_score
        """
        # Normalize scores to [0, 1]
        dense_scores = self._normalize_scores(dense_results)
        sparse_scores = self._normalize_scores(sparse_results)

        # Combine scores
        combined: dict[str, float] = {}
        chunk_map: dict[str, Chunk] = {}

        for result, norm_score in zip(dense_results, dense_scores):
            chunk_id = result.chunk.id
            chunk_map[chunk_id] = result.chunk
            combined[chunk_id] = self.dense_weight * norm_score

        for result, norm_score in zip(sparse_results, sparse_scores):
            chunk_id = result.chunk.id
            chunk_map[chunk_id] = result.chunk
            combined[chunk_id] = combined.get(chunk_id, 0) + self.sparse_weight * norm_score

        # Sort by combined score
        sorted_items = sorted(combined.items(), key=lambda x: x[1], reverse=True)

        # Build final results
        fused = []
        for rank, (chunk_id, score) in enumerate(sorted_items[:top_k]):
            fused.append(
                SearchResult(
                    chunk=chunk_map[chunk_id],
                    score=score,
                    rank=rank + 1,
                    retriever_type="hybrid",
                )
            )

        return fused

    def _normalize_scores(self, results: list[SearchResult]) -> list[float]:
        """Normalize scores to [0, 1] using min-max scaling."""
        if not results:
            return []

        scores = [r.score for r in results]
        min_score = min(scores)
        max_score = max(scores)

        if max_score == min_score:
            return [1.0] * len(scores)

        return [(s - min_score) / (max_score - min_score) for s in scores]
