"""CSV file loader."""

from __future__ import annotations

import csv
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from prompt_amplifier.core.exceptions import LoaderError
from prompt_amplifier.loaders.base import BaseLoader
from prompt_amplifier.models.document import Document


class CSVLoader(BaseLoader):
    """
    Load CSV files as documents.

    Each row becomes a document, or the entire file as one document.

    Example:
        >>> loader = CSVLoader(row_as_document=True)
        >>> docs = loader.load("data.csv")
    """

    def __init__(
        self,
        encoding: str = "utf-8",
        delimiter: str = ",",
        row_as_document: bool = False,
        content_columns: list[str] | None = None,
        metadata_columns: list[str] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize CSV loader.

        Args:
            encoding: File encoding
            delimiter: CSV delimiter
            row_as_document: If True, each row becomes a document
            content_columns: Columns to use for content (all if None)
            metadata_columns: Columns to extract as metadata
        """
        super().__init__(**kwargs)
        self.encoding = encoding
        self.delimiter = delimiter
        self.row_as_document = row_as_document
        self.content_columns = content_columns
        self.metadata_columns = metadata_columns or []

    def load(self, source: str | Path) -> list[Document]:
        """Load a CSV file."""
        path = Path(source)

        if not path.exists():
            raise LoaderError(f"File not found: {source}")

        try:
            with open(path, encoding=self.encoding, newline="") as f:
                reader = csv.DictReader(f, delimiter=self.delimiter)
                rows = list(reader)
                headers = reader.fieldnames or []
        except Exception as e:
            raise LoaderError(f"Failed to read CSV {source}: {e}")

        if not rows:
            return []

        if self.row_as_document:
            return self._load_rows_as_documents(rows, headers, source)
        else:
            return self._load_as_single_document(rows, headers, source)

    def _load_rows_as_documents(
        self,
        rows: list[dict],
        headers: list[str],
        source: str | Path,
    ) -> list[Document]:
        """Create one document per row."""
        documents = []

        content_cols = self.content_columns or headers

        for i, row in enumerate(rows):
            # Build content from specified columns
            content_parts = []
            for col in content_cols:
                if col in row and row[col]:
                    content_parts.append(f"{col}: {row[col]}")

            content = "\n".join(content_parts)

            # Extract metadata
            metadata = {"row_index": i}
            for col in self.metadata_columns:
                if col in row:
                    metadata[col] = row[col]

            documents.append(
                self._create_document(
                    content=content,
                    source=source,
                    source_type="csv",
                    metadata=metadata,
                )
            )

        return documents

    def _load_as_single_document(
        self,
        rows: list[dict],
        headers: list[str],
        source: str | Path,
    ) -> list[Document]:
        """Load entire CSV as single document."""
        content_cols = self.content_columns or headers

        lines = []
        # Add header
        lines.append(" | ".join(content_cols))
        lines.append("-" * 40)

        # Add rows
        for row in rows:
            values = [str(row.get(col, "")) for col in content_cols]
            lines.append(" | ".join(values))

        content = "\n".join(lines)

        return [
            self._create_document(
                content=content,
                source=source,
                source_type="csv",
                metadata={
                    "row_count": len(rows),
                    "columns": headers,
                },
            )
        ]

    def lazy_load(self, source: str | Path) -> Iterator[Document]:
        """Lazily load CSV row by row."""
        path = Path(source)

        if not self.row_as_document:
            yield from self.load(source)
            return

        try:
            with open(path, encoding=self.encoding, newline="") as f:
                reader = csv.DictReader(f, delimiter=self.delimiter)
                headers = reader.fieldnames or []
                content_cols = self.content_columns or headers

                for i, row in enumerate(reader):
                    content_parts = []
                    for col in content_cols:
                        if col in row and row[col]:
                            content_parts.append(f"{col}: {row[col]}")

                    content = "\n".join(content_parts)

                    metadata = {"row_index": i}
                    for col in self.metadata_columns:
                        if col in row:
                            metadata[col] = row[col]

                    yield self._create_document(
                        content=content,
                        source=source,
                        source_type="csv",
                        metadata=metadata,
                    )
        except Exception as e:
            raise LoaderError(f"Failed to read CSV {source}: {e}")

    @property
    def supported_extensions(self) -> list[str]:
        return [".csv"]
