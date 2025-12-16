"""JSON file loader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from prompt_amplifier.core.exceptions import LoaderError
from prompt_amplifier.loaders.base import BaseLoader
from prompt_amplifier.models.document import Document


class JSONLoader(BaseLoader):
    """
    Load JSON files as documents.

    Example:
        >>> loader = JSONLoader(jq_filter=".data[]")
        >>> docs = loader.load("data.json")
    """

    def __init__(
        self,
        encoding: str = "utf-8",
        content_key: str | None = None,
        metadata_keys: list[str] | None = None,
        flatten: bool = False,
        **kwargs: Any,
    ):
        """
        Initialize JSON loader.

        Args:
            encoding: File encoding
            content_key: Key to extract as content (uses entire JSON if None)
            metadata_keys: Keys to extract as metadata
            flatten: Whether to flatten nested structures
        """
        super().__init__(**kwargs)
        self.encoding = encoding
        self.content_key = content_key
        self.metadata_keys = metadata_keys or []
        self.flatten = flatten

    def load(self, source: str | Path) -> list[Document]:
        """Load a JSON file."""
        path = Path(source)

        if not path.exists():
            raise LoaderError(f"File not found: {source}")

        try:
            with open(path, encoding=self.encoding) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise LoaderError(f"Invalid JSON in {source}: {e}")
        except Exception as e:
            raise LoaderError(f"Failed to read {source}: {e}")

        return self._process_data(data, source)

    def _process_data(self, data: Any, source: str | Path) -> list[Document]:
        """Process JSON data into documents."""
        # Handle list of objects
        if isinstance(data, list):
            documents = []
            for i, item in enumerate(data):
                doc = self._item_to_document(item, source, index=i)
                if doc:
                    documents.append(doc)
            return documents

        # Handle single object
        elif isinstance(data, dict):
            doc = self._item_to_document(data, source)
            return [doc] if doc else []

        # Handle primitive
        else:
            return [
                self._create_document(
                    content=str(data),
                    source=source,
                    source_type="json",
                )
            ]

    def _item_to_document(
        self,
        item: dict,
        source: str | Path,
        index: int | None = None,
    ) -> Document | None:
        """Convert a JSON object to a Document."""
        if not isinstance(item, dict):
            content = str(item)
        elif self.content_key and self.content_key in item:
            content = str(item[self.content_key])
        else:
            # Convert entire object to formatted string
            if self.flatten:
                content = self._flatten_dict(item)
            else:
                content = json.dumps(item, indent=2, ensure_ascii=False)

        if not content.strip():
            return None

        # Extract metadata
        metadata: dict[str, Any] = {}
        if index is not None:
            metadata["index"] = index

        for key in self.metadata_keys:
            if isinstance(item, dict) and key in item:
                metadata[key] = item[key]

        return self._create_document(
            content=content,
            source=source,
            source_type="json",
            metadata=metadata,
        )

    def _flatten_dict(self, d: dict, parent_key: str = "", sep: str = ".") -> str:
        """Flatten nested dict to string."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.append(self._flatten_dict(v, new_key, sep))
            elif isinstance(v, list):
                items.append(f"{new_key}: {json.dumps(v)}")
            else:
                items.append(f"{new_key}: {v}")
        return "\n".join(items)

    @property
    def supported_extensions(self) -> list[str]:
        return [".json", ".jsonl"]
