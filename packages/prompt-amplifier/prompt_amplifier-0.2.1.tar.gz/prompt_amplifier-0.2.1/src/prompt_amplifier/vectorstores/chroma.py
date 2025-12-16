"""ChromaDB vector store."""

from __future__ import annotations

import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from prompt_amplifier.core.exceptions import VectorStoreError
from prompt_amplifier.models.document import Chunk
from prompt_amplifier.models.result import SearchResult, SearchResults
from prompt_amplifier.vectorstores.base import BaseVectorStore


class ChromaStore(BaseVectorStore):
    """
    ChromaDB vector store.

    Easy to use, supports persistence, good for development and production.

    Requires: chromadb

    Example:
        >>> store = ChromaStore(
        ...     collection_name="my_docs",
        ...     persist_directory="./chroma_db"
        ... )
        >>> store.add(chunks)
        >>> results = store.search(query_embedding, top_k=5)
    """

    def __init__(
        self,
        collection_name: str = "prompt_amplifier",
        persist_directory: str | None = None,
        embedding_function: Any = None,
        distance_fn: str = "cosine",
        **kwargs: Any,
    ):
        """
        Initialize ChromaDB store.

        Args:
            collection_name: Name of the collection
            persist_directory: Directory for persistence (None = in-memory)
            embedding_function: Custom embedding function (optional)
            distance_fn: Distance function ('cosine', 'l2', 'ip')
        """
        super().__init__(collection_name=collection_name, **kwargs)
        self.persist_directory = persist_directory
        self.distance_fn = distance_fn

        self._client = None
        self._collection = None
        self._check_dependency()

    def _check_dependency(self) -> None:
        """Check if chromadb is installed."""
        try:
            import chromadb  # noqa: F401
        except ImportError:
            raise ImportError(
                "chromadb is required for ChromaStore. " "Install it with: pip install chromadb"
            )

    def _get_client(self) -> Any:
        """Get or create ChromaDB client."""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings

            if self.persist_directory:
                # Persistent client
                Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
                self._client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(anonymized_telemetry=False),
                )
            else:
                # In-memory client
                self._client = chromadb.Client(
                    settings=Settings(anonymized_telemetry=False),
                )

        return self._client

    def _get_collection(self) -> Any:
        """Get or create collection."""
        if self._collection is None:
            client = self._get_client()

            # Map distance function
            metadata = {}
            if self.distance_fn:
                metadata["hnsw:space"] = self.distance_fn

            self._collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata=metadata,
            )

        return self._collection

    def add(self, chunks: Sequence[Chunk]) -> list[str]:
        """
        Add chunks to ChromaDB.

        Args:
            chunks: Chunks with embeddings

        Returns:
            List of chunk IDs
        """
        if not chunks:
            return []

        collection = self._get_collection()

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for chunk in chunks:
            if chunk.embedding is None:
                raise VectorStoreError(f"Chunk {chunk.id} has no embedding.")

            ids.append(chunk.id)
            embeddings.append(chunk.embedding)
            documents.append(chunk.content)

            # Prepare metadata (ChromaDB requires simple types)
            metadata = {
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "source": chunk.source,
            }
            # Add other metadata (filter complex types)
            for k, v in chunk.metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    metadata[k] = v

            metadatas.append(metadata)

        try:
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to add to ChromaDB: {e}")

        return ids

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> SearchResults:
        """
        Search ChromaDB.

        Args:
            query_embedding: Query vector
            top_k: Number of results
            filter: Metadata filter (ChromaDB where clause)

        Returns:
            SearchResults with ranked results
        """
        collection = self._get_collection()
        start_time = time.time()

        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            raise VectorStoreError(f"ChromaDB search failed: {e}")

        search_time = (time.time() - start_time) * 1000

        # Build SearchResults
        search_results = []

        if results["ids"] and results["ids"][0]:
            ids = results["ids"][0]
            documents = results["documents"][0] if results["documents"] else [None] * len(ids)
            metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(ids)
            distances = results["distances"][0] if results["distances"] else [0.0] * len(ids)

            for rank, (id_, doc, meta, dist) in enumerate(
                zip(ids, documents, metadatas, distances)
            ):
                # Convert distance to similarity score
                # ChromaDB returns distances, smaller is better
                score = 1.0 - dist if self.distance_fn == "cosine" else -dist

                chunk = Chunk(
                    id=id_,
                    content=doc or "",
                    document_id=meta.get("document_id", ""),
                    chunk_index=meta.get("chunk_index", 0),
                    source=meta.get("source", ""),
                    metadata=meta,
                )

                search_results.append(
                    SearchResult(
                        chunk=chunk,
                        score=score,
                        rank=rank + 1,
                        retriever_type="chroma",
                    )
                )

        return SearchResults(
            results=search_results,
            query="",
            total_candidates=self.count,
            retriever_type="chroma",
            search_time_ms=search_time,
        )

    def delete(self, ids: Sequence[str]) -> None:
        """Delete chunks by ID."""
        collection = self._get_collection()
        try:
            collection.delete(ids=list(ids))
        except Exception as e:
            raise VectorStoreError(f"Failed to delete from ChromaDB: {e}")

    def get(self, ids: Sequence[str]) -> list[Chunk]:
        """Retrieve chunks by ID."""
        collection = self._get_collection()

        try:
            results = collection.get(
                ids=list(ids),
                include=["documents", "metadatas", "embeddings"],
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to get from ChromaDB: {e}")

        chunks = []
        if results["ids"]:
            for i, id_ in enumerate(results["ids"]):
                meta = results["metadatas"][i] if results["metadatas"] else {}
                doc = results["documents"][i] if results["documents"] else ""
                emb = results["embeddings"][i] if results["embeddings"] else None

                chunks.append(
                    Chunk(
                        id=id_,
                        content=doc or "",
                        document_id=meta.get("document_id", ""),
                        chunk_index=meta.get("chunk_index", 0),
                        source=meta.get("source", ""),
                        embedding=emb,
                        metadata=meta,
                    )
                )

        return chunks

    def clear(self) -> None:
        """Remove all chunks from collection."""
        client = self._get_client()
        try:
            client.delete_collection(self.collection_name)
            self._collection = None
        except Exception:
            pass  # Collection might not exist

    @property
    def count(self) -> int:
        """Number of chunks in collection."""
        collection = self._get_collection()
        return collection.count()

    @property
    def is_persistent(self) -> bool:
        return self.persist_directory is not None

    @property
    def supports_filter(self) -> bool:
        return True
