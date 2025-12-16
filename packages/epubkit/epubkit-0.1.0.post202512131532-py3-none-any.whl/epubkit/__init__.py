"""
epubkit - A comprehensive EPUB processing toolkit for Python.

This package provides a clean, extensible API for reading and processing
EPUB files with support for table of contents parsing and content access.
"""

from .core import EPUB
from .cfi import CFI, CFIGenerator, CFIResolver
from .__about__ import __version__

__all__ = [
    # Main API
    "open",
    "EPUB",

    # CFI support
    "CFI",
    "CFIGenerator",
    "CFIResolver",

    # Version
    "__version__",
]


def open(path: str, trace: bool = False) -> EPUB:
    """
    Open an EPUB file.

    This is the main entry point for epubkit. It provides a simple,
    Pythonic interface for working with EPUB files.

    Args:
        path: Path to the EPUB file
        trace: Enable detailed logging for debugging

    Returns:
        An EPUB object for accessing the book's content

    Example:
        >>> import epubkit
        >>> book = epubkit.open("my_book.epub")
        >>> print(book.title)
        >>> for chapter in book.spine:
        ...     print(chapter["title"])
        >>> content = book.read_chapter("chapter1.xhtml")
    """
    return EPUB(path, trace)
