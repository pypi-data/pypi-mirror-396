"""
Abstract interfaces for epubkit components.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class ContentReader(ABC):
    """
    Abstract interface for reading EPUB content.

    This interface decouples TOC parsing components from
    specific EPUB parser implementations.
    """

    @abstractmethod
    def read_chapter(self, href: str) -> str:
        """
        Read chapter content by href.

        Args:
            href: The href of the chapter to read

        Returns:
            The chapter content as a string
        """
        pass

    @property
    @abstractmethod
    def zf(self) -> Any:
        """The zip file object containing the EPUB."""
        pass

    @property
    @abstractmethod
    def opf_path(self) -> Optional[str]:
        """Path to the OPF file within the EPUB."""
        pass

    @property
    @abstractmethod
    def epub_path(self) -> str:
        """Path to the EPUB file on disk."""
        pass

    @property
    @abstractmethod
    def zip_namelist(self) -> List[str]:
        """List of all files in the EPUB archive."""
        pass

    @property
    @abstractmethod
    def trace(self) -> bool:
        """Whether to enable trace logging."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the content reader and clean up resources."""
        pass
