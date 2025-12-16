"""Recursive text chunker."""

from __future__ import annotations

import re
from typing import Any

from prompt_amplifier.chunkers.base import BaseChunker
from prompt_amplifier.models.document import Chunk, Document


class RecursiveChunker(BaseChunker):
    """
    Recursively split text using a hierarchy of separators.

    Tries to split on larger semantic boundaries first (paragraphs),
    then falls back to smaller ones (sentences, words) if needed.

    Example:
        >>> chunker = RecursiveChunker(chunk_size=500, chunk_overlap=50)
        >>> chunks = chunker.chunk(document)
    """

    DEFAULT_SEPARATORS = [
        "\n\n\n",  # Multiple newlines (section breaks)
        "\n\n",  # Paragraph breaks
        "\n",  # Line breaks
        ". ",  # Sentence endings
        "? ",
        "! ",
        "; ",  # Clause breaks
        ", ",  # Comma breaks
        " ",  # Word breaks
        "",  # Character level (last resort)
    ]

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: list[str] | None = None,
        keep_separator: bool = True,
        **kwargs: Any,
    ):
        """
        Initialize recursive chunker.

        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
            separators: List of separators (uses defaults if None)
            keep_separator: Whether to keep separators in chunks
        """
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap, **kwargs)
        self.separators = separators or self.DEFAULT_SEPARATORS
        self.keep_separator = keep_separator

    def chunk(self, document: Document) -> list[Chunk]:
        """Split document into chunks."""
        text = document.content

        if not text or not text.strip():
            return []

        # Recursively split
        splits = self._split_text(text, self.separators)

        # Merge splits into chunks of appropriate size
        chunks = self._merge_splits(splits, document)

        return chunks

    def _split_text(self, text: str, separators: list[str]) -> list[str]:
        """Recursively split text using separators."""
        if not separators:
            return [text]

        separator = separators[0]
        remaining_separators = separators[1:]

        # Split on current separator
        if separator == "":
            # Character-level split
            splits = list(text)
        else:
            splits = self._split_on_separator(text, separator)

        # Check if any split is too large
        final_splits = []
        for split in splits:
            if len(split) <= self.chunk_size:
                final_splits.append(split)
            elif remaining_separators:
                # Recursively split with next separator
                final_splits.extend(self._split_text(split, remaining_separators))
            else:
                # Can't split further, keep as is
                final_splits.append(split)

        return final_splits

    def _split_on_separator(self, text: str, separator: str) -> list[str]:
        """Split text on separator, optionally keeping it."""
        if self.keep_separator:
            # Keep separator at end of each split
            parts = text.split(separator)
            result = []
            for i, part in enumerate(parts):
                if i < len(parts) - 1:
                    result.append(part + separator)
                elif part:  # Don't add empty last part
                    result.append(part)
            return result
        else:
            return [p for p in text.split(separator) if p]

    def _merge_splits(self, splits: list[str], document: Document) -> list[Chunk]:
        """Merge small splits into appropriately sized chunks."""
        chunks = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_length = len(split)

            # If single split is larger than chunk_size, it becomes its own chunk
            if split_length > self.chunk_size:
                # Save current accumulated chunk first
                if current_chunk:
                    chunk_text = "".join(current_chunk)
                    chunks.append(
                        self._create_chunk(
                            content=chunk_text,
                            document=document,
                            chunk_index=len(chunks),
                        )
                    )
                    current_chunk = []
                    current_length = 0

                # Add oversized split as its own chunk
                chunks.append(
                    self._create_chunk(
                        content=split,
                        document=document,
                        chunk_index=len(chunks),
                    )
                )
                continue

            # Check if adding this split would exceed chunk_size
            if current_length + split_length > self.chunk_size:
                # Save current chunk
                if current_chunk:
                    chunk_text = "".join(current_chunk)
                    chunks.append(
                        self._create_chunk(
                            content=chunk_text,
                            document=document,
                            chunk_index=len(chunks),
                        )
                    )

                # Start new chunk with overlap
                if self.chunk_overlap > 0 and current_chunk:
                    overlap_text = self._get_overlap(current_chunk)
                    current_chunk = [overlap_text] if overlap_text else []
                    current_length = len(overlap_text) if overlap_text else 0
                else:
                    current_chunk = []
                    current_length = 0

            # Add split to current chunk
            current_chunk.append(split)
            current_length += split_length

        # Don't forget the last chunk
        if current_chunk:
            chunk_text = "".join(current_chunk)
            chunks.append(
                self._create_chunk(
                    content=chunk_text,
                    document=document,
                    chunk_index=len(chunks),
                )
            )

        return chunks

    def _get_overlap(self, splits: list[str]) -> str:
        """Get overlap text from end of splits."""
        combined = "".join(splits)
        if len(combined) <= self.chunk_overlap:
            return combined
        return combined[-self.chunk_overlap :]


class FixedSizeChunker(BaseChunker):
    """
    Split text into fixed-size chunks.

    Simple chunker that splits by character count.

    Example:
        >>> chunker = FixedSizeChunker(chunk_size=500, chunk_overlap=50)
        >>> chunks = chunker.chunk(document)
    """

    def chunk(self, document: Document) -> list[Chunk]:
        """Split document into fixed-size chunks."""
        text = document.content

        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            chunks.append(
                self._create_chunk(
                    content=chunk_text,
                    document=document,
                    chunk_index=len(chunks),
                )
            )

            start = end - self.chunk_overlap

        return chunks


class SentenceChunker(BaseChunker):
    """
    Split text into chunks by sentence boundaries.

    Uses regex to detect sentence endings.

    Example:
        >>> chunker = SentenceChunker(sentences_per_chunk=5)
        >>> chunks = chunker.chunk(document)
    """

    SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+")

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        sentences_per_chunk: int | None = None,
        **kwargs: Any,
    ):
        """
        Initialize sentence chunker.

        Args:
            chunk_size: Max chunk size in characters
            chunk_overlap: Overlap between chunks
            sentences_per_chunk: Fixed number of sentences per chunk (overrides size)
        """
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap, **kwargs)
        self.sentences_per_chunk = sentences_per_chunk

    def chunk(self, document: Document) -> list[Chunk]:
        """Split document by sentences."""
        text = document.content

        if not text:
            return []

        # Split into sentences
        sentences = self.SENTENCE_PATTERN.split(text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return [
                self._create_chunk(
                    content=text,
                    document=document,
                    chunk_index=0,
                )
            ]

        if self.sentences_per_chunk:
            return self._chunk_by_sentence_count(sentences, document)
        else:
            return self._chunk_by_size(sentences, document)

    def _chunk_by_sentence_count(
        self,
        sentences: list[str],
        document: Document,
    ) -> list[Chunk]:
        """Create chunks with fixed sentence count."""
        chunks = []

        for i in range(0, len(sentences), self.sentences_per_chunk):
            chunk_sentences = sentences[i : i + self.sentences_per_chunk]
            chunk_text = " ".join(chunk_sentences)

            chunks.append(
                self._create_chunk(
                    content=chunk_text,
                    document=document,
                    chunk_index=len(chunks),
                    metadata={"sentence_count": len(chunk_sentences)},
                )
            )

        return chunks

    def _chunk_by_size(
        self,
        sentences: list[str],
        document: Document,
    ) -> list[Chunk]:
        """Create chunks up to max size."""
        chunks = []
        current_sentences = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence) + 1  # +1 for space

            if current_length + sentence_length > self.chunk_size and current_sentences:
                # Save current chunk
                chunk_text = " ".join(current_sentences)
                chunks.append(
                    self._create_chunk(
                        content=chunk_text,
                        document=document,
                        chunk_index=len(chunks),
                    )
                )

                # Start new chunk (no overlap for sentence chunker)
                current_sentences = []
                current_length = 0

            current_sentences.append(sentence)
            current_length += sentence_length

        # Last chunk
        if current_sentences:
            chunk_text = " ".join(current_sentences)
            chunks.append(
                self._create_chunk(
                    content=chunk_text,
                    document=document,
                    chunk_index=len(chunks),
                )
            )

        return chunks
