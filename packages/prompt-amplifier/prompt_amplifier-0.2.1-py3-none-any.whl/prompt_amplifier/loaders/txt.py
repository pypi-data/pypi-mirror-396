"""Plain text file loader."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from prompt_amplifier.core.exceptions import LoaderError
from prompt_amplifier.loaders.base import BaseLoader
from prompt_amplifier.models.document import Document


class TxtLoader(BaseLoader):
    """
    Load plain text files (.txt, .text).

    Example:
        >>> loader = TxtLoader()
        >>> docs = loader.load("document.txt")
    """

    def __init__(self, encoding: str = "utf-8", **kwargs: Any):
        """
        Initialize text loader.

        Args:
            encoding: File encoding (default: utf-8)
        """
        super().__init__(**kwargs)
        self.encoding = encoding

    def load(self, source: str | Path) -> list[Document]:
        """Load a text file."""
        path = Path(source)

        if not path.exists():
            raise LoaderError(f"File not found: {source}")

        if not path.is_file():
            raise LoaderError(f"Not a file: {source}")

        try:
            content = path.read_text(encoding=self.encoding)
        except UnicodeDecodeError as e:
            raise LoaderError(
                f"Failed to decode {source} with encoding {self.encoding}",
                details={"encoding": self.encoding, "error": str(e)},
            )
        except Exception as e:
            raise LoaderError(f"Failed to read {source}: {e}")

        return [
            self._create_document(
                content=content,
                source=source,
                source_type="txt",
                metadata={
                    "encoding": self.encoding,
                    "file_size": path.stat().st_size,
                },
            )
        ]

    @property
    def supported_extensions(self) -> list[str]:
        return [".txt", ".text"]


class MarkdownLoader(BaseLoader):
    """
    Load Markdown files (.md, .markdown).

    Example:
        >>> loader = MarkdownLoader()
        >>> docs = loader.load("README.md")
    """

    def __init__(self, encoding: str = "utf-8", **kwargs: Any):
        super().__init__(**kwargs)
        self.encoding = encoding

    def load(self, source: str | Path) -> list[Document]:
        """Load a markdown file."""
        path = Path(source)

        if not path.exists():
            raise LoaderError(f"File not found: {source}")

        try:
            content = path.read_text(encoding=self.encoding)
        except Exception as e:
            raise LoaderError(f"Failed to read {source}: {e}")

        return [
            self._create_document(
                content=content,
                source=source,
                source_type="markdown",
                metadata={"encoding": self.encoding},
            )
        ]

    @property
    def supported_extensions(self) -> list[str]:
        return [".md", ".markdown"]
