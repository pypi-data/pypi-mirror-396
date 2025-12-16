"""Web and URL loaders for fetching content from the internet."""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urljoin, urlparse

from prompt_amplifier.loaders.base import BaseLoader
from prompt_amplifier.models.document import Document


class WebLoader(BaseLoader):
    """
    Load content from web URLs.

    Fetches web pages and extracts text content, removing HTML tags,
    scripts, and styles.

    Example:
        >>> loader = WebLoader()
        >>> docs = loader.load("https://example.com/page")
        >>> print(docs[0].content[:100])

        >>> # Load multiple URLs
        >>> docs = loader.load_urls([
        ...     "https://example.com/page1",
        ...     "https://example.com/page2"
        ... ])
    """

    def __init__(
        self,
        timeout: int = 30,
        headers: Optional[dict] = None,
        verify_ssl: bool = True,
        extract_links: bool = False,
    ):
        """
        Initialize the WebLoader.

        Args:
            timeout: Request timeout in seconds.
            headers: Custom HTTP headers to send with requests.
            verify_ssl: Whether to verify SSL certificates.
            extract_links: Whether to extract and include links in metadata.
        """
        self.timeout = timeout
        self.headers = headers or {"User-Agent": "Mozilla/5.0 (compatible; PromptAmplifier/1.0)"}
        self.verify_ssl = verify_ssl
        self.extract_links = extract_links

    def _check_dependencies(self) -> None:
        """Check if required dependencies are installed."""
        try:
            import requests  # noqa: F401
            from bs4 import BeautifulSoup  # noqa: F401
        except ImportError as e:
            missing = str(e).split("'")[1] if "'" in str(e) else "requests/beautifulsoup4"
            raise ImportError(
                f"{missing} is required for WebLoader. "
                f"Install it with: pip install requests beautifulsoup4"
            ) from e

    def load(self, source: str) -> list[Document]:
        """
        Load content from a single URL.

        Args:
            source: URL to fetch content from.

        Returns:
            List containing a single Document with the page content.

        Raises:
            ValueError: If the URL is invalid.
            ImportError: If required dependencies are not installed.
        """
        self._check_dependencies()
        import requests
        from bs4 import BeautifulSoup

        # Validate URL
        parsed = urlparse(source)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL: {source}")

        try:
            response = requests.get(
                source,
                headers=self.headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch URL {source}: {e}") from e

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        # Extract title
        title = soup.title.string if soup.title else ""

        # Extract main content
        # Try to find main content area
        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", {"class": re.compile(r"content|main|article", re.I)})
            or soup.body
        )

        if main_content:
            text = main_content.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)

        # Clean up whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)

        metadata = {
            "source": source,
            "title": title.strip() if title else "",
            "url": source,
            "domain": parsed.netloc,
        }

        # Extract links if requested
        if self.extract_links:
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http"):
                    links.append(href)
                elif href.startswith("/"):
                    links.append(urljoin(source, href))
            metadata["links"] = links[:50]  # Limit to 50 links

        return [Document(content=text.strip(), metadata=metadata)]

    def load_urls(self, urls: list[str]) -> list[Document]:
        """
        Load content from multiple URLs.

        Args:
            urls: List of URLs to fetch.

        Returns:
            List of Documents, one per URL.
        """
        documents = []
        for url in urls:
            try:
                docs = self.load(url)
                documents.extend(docs)
            except Exception as e:
                # Log error but continue with other URLs
                print(f"Warning: Failed to load {url}: {e}")
        return documents

    @property
    def supported_extensions(self) -> list[str]:
        """Web loader doesn't use file extensions."""
        return []


class YouTubeLoader(BaseLoader):
    """
    Load transcripts from YouTube videos.

    Extracts the transcript/captions from YouTube videos.

    Example:
        >>> loader = YouTubeLoader()
        >>> docs = loader.load("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        >>> print(docs[0].content[:100])
    """

    def __init__(self, language: str = "en"):
        """
        Initialize the YouTubeLoader.

        Args:
            language: Preferred language for transcripts.
        """
        self.language = language

    def _check_dependencies(self) -> None:
        """Check if required dependencies are installed."""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi  # noqa: F401
        except ImportError:
            raise ImportError(
                "youtube-transcript-api is required for YouTubeLoader. "
                "Install it with: pip install youtube-transcript-api"
            )

    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        patterns = [
            r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
            r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        raise ValueError(f"Could not extract video ID from URL: {url}")

    def load(self, source: str) -> list[Document]:
        """
        Load transcript from a YouTube video.

        Args:
            source: YouTube video URL or video ID.

        Returns:
            List containing a single Document with the transcript.
        """
        self._check_dependencies()
        from youtube_transcript_api import YouTubeTranscriptApi

        # Extract video ID
        if "youtube.com" in source or "youtu.be" in source:
            video_id = self._extract_video_id(source)
        else:
            video_id = source

        try:
            # Try to get transcript in preferred language
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            try:
                transcript = transcript_list.find_transcript([self.language])
            except Exception:
                # Fall back to any available transcript
                transcript = transcript_list.find_transcript(
                    transcript_list._manually_created_transcripts.keys()
                    or transcript_list._generated_transcripts.keys()
                )

            transcript_data = transcript.fetch()

            # Combine transcript segments
            text_parts = []
            for segment in transcript_data:
                text_parts.append(segment["text"])

            content = " ".join(text_parts)

            metadata = {
                "source": source,
                "video_id": video_id,
                "language": transcript.language,
                "is_generated": transcript.is_generated,
            }

            return [Document(content=content, metadata=metadata)]

        except Exception as e:
            raise ValueError(f"Failed to get transcript for {source}: {e}") from e

    @property
    def supported_extensions(self) -> list[str]:
        """YouTube loader doesn't use file extensions."""
        return []


class SitemapLoader(BaseLoader):
    """
    Load content from websites using their sitemap.

    Parses sitemap.xml and fetches content from listed URLs.

    Example:
        >>> loader = SitemapLoader(max_pages=10)
        >>> docs = loader.load("https://example.com/sitemap.xml")
    """

    def __init__(
        self,
        max_pages: int = 50,
        filter_pattern: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize the SitemapLoader.

        Args:
            max_pages: Maximum number of pages to fetch.
            filter_pattern: Regex pattern to filter URLs (only fetch matching).
            timeout: Request timeout in seconds.
        """
        self.max_pages = max_pages
        self.filter_pattern = filter_pattern
        self.timeout = timeout
        self._web_loader = WebLoader(timeout=timeout)

    def _check_dependencies(self) -> None:
        """Check if required dependencies are installed."""
        try:
            import requests  # noqa: F401
            from bs4 import BeautifulSoup  # noqa: F401
        except ImportError:
            raise ImportError(
                "requests and beautifulsoup4 are required for SitemapLoader. "
                "Install with: pip install requests beautifulsoup4"
            )

    def _parse_sitemap(self, sitemap_url: str) -> list[str]:
        """Parse sitemap XML and extract URLs."""
        import requests
        from bs4 import BeautifulSoup

        response = requests.get(sitemap_url, timeout=self.timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "xml")
        urls = []

        # Handle sitemap index (contains other sitemaps)
        sitemap_tags = soup.find_all("sitemap")
        if sitemap_tags:
            for sitemap in sitemap_tags[: self.max_pages]:
                loc = sitemap.find("loc")
                if loc:
                    urls.extend(self._parse_sitemap(loc.text))
                    if len(urls) >= self.max_pages:
                        break
        else:
            # Regular sitemap with URLs
            for url_tag in soup.find_all("url"):
                loc = url_tag.find("loc")
                if loc:
                    url = loc.text
                    # Apply filter if specified
                    if self.filter_pattern:
                        if re.search(self.filter_pattern, url):
                            urls.append(url)
                    else:
                        urls.append(url)

                    if len(urls) >= self.max_pages:
                        break

        return urls[: self.max_pages]

    def load(self, source: str) -> list[Document]:
        """
        Load content from all URLs in a sitemap.

        Args:
            source: URL to sitemap.xml file.

        Returns:
            List of Documents, one per page.
        """
        self._check_dependencies()

        urls = self._parse_sitemap(source)
        print(f"Found {len(urls)} URLs in sitemap, fetching content...")

        return self._web_loader.load_urls(urls)

    @property
    def supported_extensions(self) -> list[str]:
        """Sitemap loader uses .xml extension."""
        return [".xml"]


class RSSLoader(BaseLoader):
    """
    Load content from RSS/Atom feeds.

    Example:
        >>> loader = RSSLoader()
        >>> docs = loader.load("https://example.com/feed.xml")
    """

    def __init__(self, max_entries: int = 20, fetch_content: bool = True):
        """
        Initialize the RSSLoader.

        Args:
            max_entries: Maximum number of feed entries to process.
            fetch_content: Whether to fetch full content from links.
        """
        self.max_entries = max_entries
        self.fetch_content = fetch_content
        self._web_loader = WebLoader()

    def _check_dependencies(self) -> None:
        """Check if required dependencies are installed."""
        try:
            import feedparser  # noqa: F401
        except ImportError:
            raise ImportError(
                "feedparser is required for RSSLoader. " "Install it with: pip install feedparser"
            )

    def load(self, source: str) -> list[Document]:
        """
        Load content from an RSS/Atom feed.

        Args:
            source: URL to the RSS/Atom feed.

        Returns:
            List of Documents, one per feed entry.
        """
        self._check_dependencies()
        import feedparser

        feed = feedparser.parse(source)

        documents = []
        for entry in feed.entries[: self.max_entries]:
            # Get content from entry
            content = ""
            if hasattr(entry, "content") and entry.content:
                content = entry.content[0].get("value", "")
            elif hasattr(entry, "summary"):
                content = entry.summary
            elif hasattr(entry, "description"):
                content = entry.description

            # Strip HTML tags
            content = re.sub(r"<[^>]+>", "", content)

            # If fetch_content is True and we have a link, fetch full content
            if self.fetch_content and hasattr(entry, "link") and entry.link:
                try:
                    full_docs = self._web_loader.load(entry.link)
                    if full_docs:
                        content = full_docs[0].content
                except Exception:
                    pass  # Use summary content if fetch fails

            metadata = {
                "source": source,
                "title": getattr(entry, "title", ""),
                "link": getattr(entry, "link", ""),
                "published": getattr(entry, "published", ""),
                "author": getattr(entry, "author", ""),
            }

            if content.strip():
                documents.append(Document(content=content.strip(), metadata=metadata))

        return documents

    @property
    def supported_extensions(self) -> list[str]:
        """RSS loader handles feed URLs."""
        return [".xml", ".rss", ".atom"]
