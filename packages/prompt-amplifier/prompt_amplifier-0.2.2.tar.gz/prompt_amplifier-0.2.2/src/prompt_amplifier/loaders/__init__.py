"""Document loaders for various file formats."""

from __future__ import annotations

from prompt_amplifier.loaders.base import BaseLoader, DirectoryLoader
from prompt_amplifier.loaders.csv import CSVLoader
from prompt_amplifier.loaders.json import JSONLoader

# Always available
from prompt_amplifier.loaders.txt import MarkdownLoader, TxtLoader

__all__ = [
    "BaseLoader",
    "DirectoryLoader",
    "TxtLoader",
    "MarkdownLoader",
    "CSVLoader",
    "JSONLoader",
]

# Optional loaders (require extra dependencies)
try:
    from prompt_amplifier.loaders.docx import DocxLoader

    __all__.append("DocxLoader")
except ImportError:
    pass

try:
    from prompt_amplifier.loaders.excel import ExcelLoader

    __all__.append("ExcelLoader")
except ImportError:
    pass

try:
    from prompt_amplifier.loaders.pdf import PDFLoader

    __all__.append("PDFLoader")
except ImportError:
    pass

# Web loaders (require requests, beautifulsoup4)
try:
    from prompt_amplifier.loaders.web import WebLoader

    __all__.append("WebLoader")
except ImportError:
    pass

try:
    from prompt_amplifier.loaders.web import SitemapLoader

    __all__.append("SitemapLoader")
except ImportError:
    pass

try:
    from prompt_amplifier.loaders.web import RSSLoader

    __all__.append("RSSLoader")
except ImportError:
    pass

# YouTube loader (requires youtube-transcript-api)
try:
    from prompt_amplifier.loaders.web import YouTubeLoader

    __all__.append("YouTubeLoader")
except ImportError:
    pass
