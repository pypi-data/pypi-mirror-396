"""Data models for PromptForge."""

from __future__ import annotations

from prompt_amplifier.models.document import Chunk, Document
from prompt_amplifier.models.embedding import EmbeddingResult
from prompt_amplifier.models.result import ExpandResult, SearchResult

__all__ = [
    "Document",
    "Chunk",
    "ExpandResult",
    "SearchResult",
    "EmbeddingResult",
]
