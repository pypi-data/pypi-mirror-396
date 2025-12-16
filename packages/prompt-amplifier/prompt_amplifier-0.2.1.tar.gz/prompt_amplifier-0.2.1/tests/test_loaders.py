"""Tests for document loaders."""

from __future__ import annotations

import json

import pytest

from prompt_amplifier.core.exceptions import LoaderError
from prompt_amplifier.loaders import CSVLoader, JSONLoader, TxtLoader


class TestTxtLoader:
    """Tests for TxtLoader."""

    def test_load_txt_file(self, temp_txt_file):
        """Test loading a text file."""
        loader = TxtLoader()
        docs = loader.load(temp_txt_file)

        assert len(docs) == 1
        assert "This is test content" in docs[0].content
        assert docs[0].source_type == "txt"

    def test_supported_extensions(self):
        """Test supported extensions."""
        loader = TxtLoader()
        assert ".txt" in loader.supported_extensions
        assert ".text" in loader.supported_extensions

    def test_can_load(self, temp_txt_file):
        """Test can_load method."""
        loader = TxtLoader()
        assert loader.can_load(temp_txt_file)
        assert not loader.can_load("test.pdf")

    def test_load_nonexistent_file(self, temp_dir):
        """Test loading nonexistent file raises error."""
        loader = TxtLoader()

        with pytest.raises(LoaderError):
            loader.load(temp_dir / "nonexistent.txt")

    def test_load_with_encoding(self, temp_dir):
        """Test loading with specific encoding."""
        file_path = temp_dir / "utf8.txt"
        file_path.write_text("Hello 世界", encoding="utf-8")

        loader = TxtLoader(encoding="utf-8")
        docs = loader.load(file_path)

        assert "世界" in docs[0].content


class TestCSVLoader:
    """Tests for CSVLoader."""

    def test_load_csv_single_document(self, temp_csv_file):
        """Test loading CSV as single document."""
        loader = CSVLoader(row_as_document=False)
        docs = loader.load(temp_csv_file)

        assert len(docs) == 1
        assert "item1" in docs[0].content
        assert "item2" in docs[0].content

    def test_load_csv_row_as_document(self, temp_csv_file):
        """Test loading CSV with each row as document."""
        loader = CSVLoader(row_as_document=True)
        docs = loader.load(temp_csv_file)

        assert len(docs) == 2
        assert "item1" in docs[0].content
        assert "item2" in docs[1].content

    def test_load_csv_specific_columns(self, temp_csv_file):
        """Test loading specific columns."""
        loader = CSVLoader(
            row_as_document=True,
            content_columns=["name", "value"],
        )
        docs = loader.load(temp_csv_file)

        assert len(docs) == 2
        assert "description" not in docs[0].content.lower() or "First item" not in docs[0].content

    def test_csv_metadata_columns(self, temp_csv_file):
        """Test extracting metadata columns."""
        loader = CSVLoader(
            row_as_document=True,
            metadata_columns=["name"],
        )
        docs = loader.load(temp_csv_file)

        assert docs[0].metadata.get("name") == "item1"


class TestJSONLoader:
    """Tests for JSONLoader."""

    def test_load_json_array(self, temp_json_file):
        """Test loading JSON array."""
        loader = JSONLoader()
        docs = loader.load(temp_json_file)

        assert len(docs) == 2

    def test_load_json_single_object(self, temp_dir):
        """Test loading single JSON object."""
        file_path = temp_dir / "single.json"
        file_path.write_text(json.dumps({"title": "Test", "content": "Content"}))

        loader = JSONLoader()
        docs = loader.load(file_path)

        assert len(docs) == 1

    def test_load_json_with_content_key(self, temp_json_file):
        """Test loading with specific content key."""
        loader = JSONLoader(content_key="content")
        docs = loader.load(temp_json_file)

        assert docs[0].content == "Content one"
        assert docs[1].content == "Content two"

    def test_load_json_with_metadata(self, temp_json_file):
        """Test extracting metadata from JSON."""
        loader = JSONLoader(metadata_keys=["title"])
        docs = loader.load(temp_json_file)

        assert docs[0].metadata.get("title") == "Doc 1"


class TestBaseLoader:
    """Tests for BaseLoader abstract class."""

    def test_create_document_helper(self, temp_txt_file):
        """Test _create_document helper method."""
        loader = TxtLoader()
        doc = loader._create_document(
            content="Test content",
            source=temp_txt_file,
            metadata={"custom": "value"},
        )

        assert doc.content == "Test content"
        assert doc.metadata["custom"] == "value"
        assert doc.metadata["loader"] == "TxtLoader"
        assert doc.metadata["filename"] == temp_txt_file.name


class TestDirectoryLoader:
    """Tests for DirectoryLoader."""

    def test_load_directory(self, temp_dir):
        """Test loading from directory."""
        from prompt_amplifier.loaders.base import DirectoryLoader

        # Create test files
        (temp_dir / "file1.txt").write_text("Content one")
        (temp_dir / "file2.txt").write_text("Content two")
        (temp_dir / "ignored.xyz").write_text("Should be ignored")

        loader = DirectoryLoader(loaders=[TxtLoader()])
        docs = loader.load(temp_dir)

        assert len(docs) == 2

    def test_register_loader(self, temp_dir):
        """Test registering new loader."""
        from prompt_amplifier.loaders.base import DirectoryLoader

        (temp_dir / "test.txt").write_text("Test")

        loader = DirectoryLoader()
        loader.register_loader(TxtLoader())

        docs = loader.load(temp_dir)
        assert len(docs) == 1
