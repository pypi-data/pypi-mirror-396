"""PDF file loader."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from prompt_amplifier.core.exceptions import LoaderError
from prompt_amplifier.loaders.base import BaseLoader
from prompt_amplifier.models.document import Document


class PDFLoader(BaseLoader):
    """
    Load PDF files.

    Requires: pymupdf (fitz)

    Example:
        >>> loader = PDFLoader()
        >>> docs = loader.load("document.pdf")
    """

    def __init__(
        self,
        page_as_document: bool = False,
        extract_images: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize PDF loader.

        Args:
            page_as_document: If True, each page becomes a document
            extract_images: Whether to extract image descriptions (OCR)
        """
        super().__init__(**kwargs)
        self.page_as_document = page_as_document
        self.extract_images = extract_images
        self._check_dependency()

    def _check_dependency(self) -> None:
        """Check if pymupdf is installed."""
        try:
            import fitz  # noqa: F401
        except ImportError:
            raise ImportError(
                "PyMuPDF is required for PDFLoader. " "Install it with: pip install pymupdf"
            )

    def load(self, source: str | Path) -> list[Document]:
        """Load a PDF file."""
        import fitz

        path = Path(source)

        if not path.exists():
            raise LoaderError(f"File not found: {source}")

        try:
            doc = fitz.open(str(path))
        except Exception as e:
            raise LoaderError(f"Failed to open PDF {source}: {e}")

        try:
            if self.page_as_document:
                documents = self._load_pages_as_documents(doc, source)
            else:
                documents = self._load_as_single_document(doc, source)
        finally:
            doc.close()

        return documents

    def _load_as_single_document(
        self,
        doc: Any,
        source: str | Path,
    ) -> list[Document]:
        """Load entire PDF as single document."""
        pages_text = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            if text:
                pages_text.append(f"--- Page {page_num + 1} ---\n{text}")

        content = "\n\n".join(pages_text)

        metadata = self._extract_metadata(doc)
        metadata["page_count"] = len(doc)

        return [
            self._create_document(
                content=content,
                source=source,
                source_type="pdf",
                metadata=metadata,
            )
        ]

    def _load_pages_as_documents(
        self,
        doc: Any,
        source: str | Path,
    ) -> list[Document]:
        """Load each page as a separate document."""
        documents = []
        base_metadata = self._extract_metadata(doc)

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()

            if not text:
                continue

            metadata = {
                **base_metadata,
                "page_number": page_num + 1,
                "total_pages": len(doc),
            }

            documents.append(
                self._create_document(
                    content=text,
                    source=source,
                    source_type="pdf",
                    metadata=metadata,
                )
            )

        return documents

    def _extract_metadata(self, doc: Any) -> dict[str, Any]:
        """Extract PDF metadata."""
        metadata = doc.metadata or {}
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
        }

    def lazy_load(self, source: str | Path) -> Iterator[Document]:
        """Lazily load PDF page by page."""
        import fitz

        path = Path(source)

        if not path.exists():
            raise LoaderError(f"File not found: {source}")

        doc = fitz.open(str(path))
        base_metadata = self._extract_metadata(doc)

        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text").strip()

                if not text:
                    continue

                metadata = {
                    **base_metadata,
                    "page_number": page_num + 1,
                    "total_pages": len(doc),
                }

                yield self._create_document(
                    content=text,
                    source=source,
                    source_type="pdf",
                    metadata=metadata,
                )
        finally:
            doc.close()

    @property
    def supported_extensions(self) -> list[str]:
        return [".pdf"]
