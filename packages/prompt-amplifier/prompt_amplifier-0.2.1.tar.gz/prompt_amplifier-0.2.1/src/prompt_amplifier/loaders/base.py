"""Base loader interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from prompt_amplifier.models.document import Document


class BaseLoader(ABC):
    """
    Abstract base class for all document loaders.

    Implement this class to add support for new document formats.

    Example:
        >>> class MyCustomLoader(BaseLoader):
        ...     def load(self, source: str) -> list[Document]:
        ...         # Load documents from source
        ...         return [Document(content="...", source=source)]
        ...
        ...     @property
        ...     def supported_extensions(self) -> list[str]:
        ...         return [".custom"]
    """

    def __init__(self, **kwargs: Any):
        """
        Initialize the loader.

        Args:
            **kwargs: Loader-specific configuration options
        """
        self.config = kwargs

    @abstractmethod
    def load(self, source: str | Path) -> list[Document]:
        """
        Load documents from a source.

        Args:
            source: File path, directory path, or URL

        Returns:
            List of Document objects

        Raises:
            LoaderError: If loading fails
        """
        pass

    def lazy_load(self, source: str | Path) -> Iterator[Document]:
        """
        Lazily load documents one at a time.

        Useful for large files to avoid loading everything into memory.
        Default implementation calls load() and yields results.

        Args:
            source: File path, directory path, or URL

        Yields:
            Document objects one at a time
        """
        yield from self.load(source)

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """
        List of file extensions this loader supports.

        Returns:
            List of extensions including the dot (e.g., [".txt", ".md"])
        """
        pass

    @property
    def loader_name(self) -> str:
        """Name of this loader."""
        return self.__class__.__name__

    def can_load(self, source: str | Path) -> bool:
        """
        Check if this loader can handle the given source.

        Args:
            source: File path to check

        Returns:
            True if this loader can handle the source
        """
        path = Path(source)
        return path.suffix.lower() in [ext.lower() for ext in self.supported_extensions]

    def _create_document(
        self,
        content: str,
        source: str | Path,
        source_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Document:
        """
        Helper to create a Document with common fields filled in.

        Args:
            content: Document content
            source: Source path or URL
            source_type: Type of source (defaults to extension)
            metadata: Additional metadata

        Returns:
            Document object
        """
        path = Path(source)
        return Document(
            content=content,
            source=str(source),
            source_type=source_type or path.suffix.lstrip(".") or "unknown",
            metadata={
                "filename": path.name,
                "loader": self.loader_name,
                **(metadata or {}),
            },
        )

    def __repr__(self) -> str:
        return f"{self.loader_name}(extensions={self.supported_extensions})"


class DirectoryLoader(BaseLoader):
    """
    Load documents from a directory using appropriate loaders.

    Example:
        >>> loader = DirectoryLoader(glob="**/*.pdf")
        >>> docs = loader.load("./documents/")
    """

    def __init__(
        self,
        loaders: list[BaseLoader] | None = None,
        glob: str = "**/*",
        recursive: bool = True,
        **kwargs: Any,
    ):
        """
        Initialize directory loader.

        Args:
            loaders: List of loaders to use. If None, uses all available loaders.
            glob: Glob pattern for file matching
            recursive: Whether to search recursively
        """
        super().__init__(**kwargs)
        self.loaders = loaders or []
        self.glob_pattern = glob
        self.recursive = recursive
        self._loader_map: dict[str, BaseLoader] = {}
        self._build_loader_map()

    def _build_loader_map(self) -> None:
        """Build extension -> loader mapping."""
        for loader in self.loaders:
            for ext in loader.supported_extensions:
                self._loader_map[ext.lower()] = loader

    def register_loader(self, loader: BaseLoader) -> None:
        """
        Register a new loader.

        Args:
            loader: Loader instance to register
        """
        self.loaders.append(loader)
        for ext in loader.supported_extensions:
            self._loader_map[ext.lower()] = loader

    def load(self, source: str | Path) -> list[Document]:
        """
        Load all documents from a directory.

        Args:
            source: Directory path

        Returns:
            List of all loaded documents
        """
        path = Path(source)
        if not path.is_dir():
            raise ValueError(f"Source must be a directory: {source}")

        documents = []
        pattern = self.glob_pattern if self.recursive else f"*{self.glob_pattern}"

        for file_path in path.glob(pattern):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                loader = self._loader_map.get(ext)
                if loader:
                    try:
                        docs = loader.load(file_path)
                        documents.extend(docs)
                    except Exception as e:
                        # Log warning but continue with other files
                        print(f"Warning: Failed to load {file_path}: {e}")

        return documents

    def lazy_load(self, source: str | Path) -> Iterator[Document]:
        """Lazily load documents from directory."""
        path = Path(source)
        if not path.is_dir():
            raise ValueError(f"Source must be a directory: {source}")

        pattern = self.glob_pattern if self.recursive else f"*{self.glob_pattern}"

        for file_path in path.glob(pattern):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                loader = self._loader_map.get(ext)
                if loader:
                    try:
                        yield from loader.lazy_load(file_path)
                    except Exception as e:
                        print(f"Warning: Failed to load {file_path}: {e}")

    @property
    def supported_extensions(self) -> list[str]:
        """Return all supported extensions from registered loaders."""
        return list(self._loader_map.keys())
