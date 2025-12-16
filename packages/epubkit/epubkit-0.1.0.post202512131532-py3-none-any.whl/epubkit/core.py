"""
Core EPUB processing classes.
"""

from typing import Any, Dict, List, Optional

from .backends import ZipContentReader
from .epub.toc_builder import TOCBuilder
from .interfaces import ContentReader


class EPUB:
    """
    Main EPUB processing class providing a high-level API.

    This is the primary interface for users of epubkit.
    """

    def __init__(self, path: str, trace: bool = False):
        """
        Open an EPUB file.

        Args:
            path: Path to the EPUB file
            trace: Enable trace logging for debugging
        """
        self._path = path
        self._trace = trace
        self._reader: Optional[ContentReader] = None
        self._toc_builder: Optional[TOCBuilder] = None
        self._toc_cache: Optional[Dict] = None

        self._open()

    def _open(self) -> None:
        """Initialize the EPUB reader and components."""
        self._reader = ZipContentReader(self._path, self._trace)
        self._toc_builder = TOCBuilder(self._reader)

    @property
    def path(self) -> str:
        """Path to the EPUB file."""
        return self._path

    @property
    def title(self) -> Optional[str]:
        """Book title extracted from metadata."""
        toc = self.toc
        return toc.get("book_title")

    @property
    def toc(self) -> Dict:
        """
        Table of contents data.

        Returns a dictionary containing:
        - book_title: Book title
        - nodes: Hierarchical TOC structure
        - spine_order: Reading order from OPF spine
        - toc_source: Source of TOC data (nav.xhtml, toc.ncx, spine)
        - raw_chapters: Flat list of chapters
        """
        if self._toc_cache is None:
            self._toc_cache = self._toc_builder.build_toc()
        return self._toc_cache

    @property
    def spine(self) -> List[Dict]:
        """Chapters in reading order."""
        return self.toc.get("raw_chapters", [])

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Basic metadata extracted from the EPUB.

        Returns a dictionary with available metadata fields.
        """
        toc = self.toc
        return {
            "title": toc.get("book_title"),
            "toc_source": toc.get("toc_source"),
            "spine_count": len(toc.get("spine_order", [])),
            "chapter_count": len(toc.get("raw_chapters", [])),
        }

    def read_chapter(self, href: str) -> str:
        """
        Read a chapter by its href.

        Args:
            href: The href of the chapter to read

        Returns:
            Chapter content as a string
        """
        return self._reader.read_chapter(href)

    def get_chapter_by_index(self, index: int) -> Optional[Dict]:
        """
        Get chapter by index in spine order.

        Args:
            index: Zero-based index in reading order

        Returns:
            Chapter info dictionary or None if index is invalid
        """
        spine = self.spine
        if 0 <= index < len(spine):
            return spine[index]
        return None

    def find_chapter_by_href(self, href: str) -> Optional[Dict]:
        """
        Find chapter by href.

        Args:
            href: Chapter href to search for

        Returns:
            Chapter info dictionary or None if not found
        """
        for chapter in self.spine:
            if chapter.get("src") == href:
                return chapter
        return None

    def close(self) -> None:
        """Close the EPUB file and clean up resources."""
        if self._reader:
            self._reader.close()
            self._reader = None
        self._toc_cache = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self) -> str:
        title = self.title or "Unknown Title"
        return f"EPUB(title='{title}', path='{self.path}')"
