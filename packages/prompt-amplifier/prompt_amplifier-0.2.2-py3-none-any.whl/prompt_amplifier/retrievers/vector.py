"""Vector similarity retriever."""

from __future__ import annotations

import time
from typing import Any

from prompt_amplifier.embedders.base import BaseEmbedder
from prompt_amplifier.models.result import SearchResult, SearchResults
from prompt_amplifier.retrievers.base import BaseRetriever
from prompt_amplifier.vectorstores.base import BaseVectorStore


class VectorRetriever(BaseRetriever):
    """
    Standard vector similarity retriever.

    Embeds the query and searches the vector store for similar chunks.

    Example:
        >>> retriever = VectorRetriever(embedder, vectorstore, top_k=10)
        >>> results = retriever.retrieve("What is the deal status?")
    """

    def __init__(
        self,
        embedder: BaseEmbedder,
        vectorstore: BaseVectorStore,
        top_k: int = 10,
        score_threshold: float | None = None,
        **kwargs: Any,
    ):
        """
        Initialize vector retriever.

        Args:
            embedder: Embedder for query encoding
            vectorstore: Vector store for search
            top_k: Number of results to return
            score_threshold: Minimum score to include (optional)
        """
        super().__init__(embedder, vectorstore, top_k, **kwargs)
        self.score_threshold = score_threshold

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filter: dict[str, Any] | None = None,
    ) -> SearchResults:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: Search query
            top_k: Number of results (uses default if None)
            filter: Optional metadata filter

        Returns:
            SearchResults with ranked chunks
        """
        top_k = top_k or self.top_k
        start_time = time.time()

        # Embed query
        query_embedding = self.embedder.embed_single(query)

        # Search vector store
        results = self.vectorstore.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter=filter,
        )

        # Apply score threshold if set
        if self.score_threshold is not None:
            filtered_results = [r for r in results.results if r.score >= self.score_threshold]
            results = SearchResults(
                results=filtered_results,
                query=query,
                total_candidates=results.total_candidates,
                retriever_type="vector",
                search_time_ms=results.search_time_ms,
            )
        else:
            results.query = query
            results.retriever_type = "vector"

        # Update total time
        results.search_time_ms = (time.time() - start_time) * 1000

        return results


class MMRRetriever(BaseRetriever):
    """
    Maximal Marginal Relevance (MMR) retriever.

    Balances relevance with diversity to avoid redundant results.

    Formula: MMR = λ * sim(query, doc) - (1-λ) * max(sim(doc, selected_docs))

    Example:
        >>> retriever = MMRRetriever(embedder, vectorstore, lambda_mult=0.5)
        >>> results = retriever.retrieve("What is the deal status?")
    """

    def __init__(
        self,
        embedder: BaseEmbedder,
        vectorstore: BaseVectorStore,
        top_k: int = 10,
        lambda_mult: float = 0.5,
        fetch_k: int = 20,
        **kwargs: Any,
    ):
        """
        Initialize MMR retriever.

        Args:
            embedder: Embedder for encoding
            vectorstore: Vector store for search
            top_k: Final number of results
            lambda_mult: Balance between relevance (1) and diversity (0)
            fetch_k: Number of candidates to fetch before MMR reranking
        """
        super().__init__(embedder, vectorstore, top_k, **kwargs)
        self.lambda_mult = lambda_mult
        self.fetch_k = fetch_k

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filter: dict[str, Any] | None = None,
    ) -> SearchResults:
        """
        Retrieve with MMR for diversity.

        Args:
            query: Search query
            top_k: Number of final results
            filter: Optional metadata filter

        Returns:
            SearchResults with diverse, relevant chunks
        """
        import numpy as np

        top_k = top_k or self.top_k
        start_time = time.time()

        # Embed query
        query_embedding = self.embedder.embed_single(query)
        query_vec = np.array(query_embedding)

        # Fetch more candidates than needed
        initial_results = self.vectorstore.search(
            query_embedding=query_embedding,
            top_k=self.fetch_k,
            filter=filter,
        )

        if not initial_results.results:
            return SearchResults(
                results=[],
                query=query,
                total_candidates=0,
                retriever_type="mmr",
                search_time_ms=(time.time() - start_time) * 1000,
            )

        # Get embeddings for candidates
        candidates = initial_results.results
        candidate_embeddings = []

        for result in candidates:
            if result.chunk.embedding:
                candidate_embeddings.append(np.array(result.chunk.embedding))
            else:
                # Re-embed if needed
                emb = self.embedder.embed_single(result.chunk.content)
                candidate_embeddings.append(np.array(emb))

        candidate_embeddings = np.array(candidate_embeddings)

        # MMR selection
        selected_indices = []
        remaining_indices = list(range(len(candidates)))

        for _ in range(min(top_k, len(candidates))):
            if not remaining_indices:
                break

            # Calculate MMR scores
            mmr_scores = []

            for idx in remaining_indices:
                # Relevance to query
                relevance = self._cosine_similarity(query_vec, candidate_embeddings[idx])

                # Diversity (max similarity to already selected)
                if selected_indices:
                    selected_embeddings = candidate_embeddings[selected_indices]
                    similarities = [
                        self._cosine_similarity(candidate_embeddings[idx], se)
                        for se in selected_embeddings
                    ]
                    max_similarity = max(similarities)
                else:
                    max_similarity = 0

                # MMR score
                mmr = self.lambda_mult * relevance - (1 - self.lambda_mult) * max_similarity
                mmr_scores.append((idx, mmr))

            # Select best
            best_idx, _ = max(mmr_scores, key=lambda x: x[1])
            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)

        # Build results
        mmr_results = []
        for rank, idx in enumerate(selected_indices):
            result = candidates[idx]
            mmr_results.append(
                SearchResult(
                    chunk=result.chunk,
                    score=result.score,
                    rank=rank + 1,
                    retriever_type="mmr",
                )
            )

        search_time = (time.time() - start_time) * 1000

        return SearchResults(
            results=mmr_results,
            query=query,
            total_candidates=initial_results.total_candidates,
            retriever_type="mmr",
            search_time_ms=search_time,
        )

    def _cosine_similarity(self, a: Any, b: Any) -> float:
        """Compute cosine similarity between two vectors."""
        import numpy as np

        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))
