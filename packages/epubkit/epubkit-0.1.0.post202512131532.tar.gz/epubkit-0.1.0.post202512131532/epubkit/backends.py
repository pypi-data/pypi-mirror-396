"""
Backend implementations for different content sources.
"""

import os
import zipfile
from typing import List, Optional

from .interfaces import ContentReader


class ZipContentReader(ContentReader):
    """
    Content reader for ZIP-based EPUB files.
    """

    def __init__(self, epub_path: str, trace: bool = False):
        self._epub_path = epub_path
        self._trace = trace
        self._zf: Optional[zipfile.ZipFile] = None
        self._opf_path: Optional[str] = None
        self._zip_namelist: List[str] = []

        self._open_epub()

    def _open_epub(self) -> None:
        """Open EPUB file and initialize metadata."""
        # Validate file exists
        if not os.path.exists(self.epub_path):
            raise FileNotFoundError(f"EPUB file not found: {self.epub_path}")

        # Open ZIP file
        self._zf = zipfile.ZipFile(self.epub_path, "r")
        self._zip_namelist = self._zf.namelist()

        # Find OPF path
        self._opf_path = self._find_opf_path()

    def _find_opf_path(self) -> Optional[str]:
        """Find the OPF file path from container.xml."""
        try:
            container_xml = "META-INF/container.xml"
            if container_xml not in self._zip_namelist:
                # Try case-insensitive search
                for name in self._zip_namelist:
                    if name.lower().endswith("meta-inf/container.xml"):
                        container_xml = name
                        break
                else:
                    raise FileNotFoundError("container.xml not found")

            # Parse container.xml
            import xml.etree.ElementTree as ET
            container_bytes = self._zf.read(container_xml)
            root = ET.fromstring(container_bytes)

            # Find rootfile element
            ns = {"cn": "urn:oasis:names:tc:opendocument:xmlns:container"}
            rf = root.find(".//cn:rootfile", ns)
            if rf is None:
                rf = root.find(".//rootfile")
            if rf is None:
                raise RuntimeError("No rootfile found in container.xml")

            full_path = rf.attrib.get("full-path")
            if not full_path:
                raise RuntimeError("rootfile missing full-path attribute")

            return full_path.replace("\\", "/")

        except Exception as e:
            raise RuntimeError(f"Failed to parse container.xml: {e}")

    def read_chapter(self, href: str) -> str:
        """Read chapter content by href."""
        try:
            return self._zf.read(href).decode("utf-8", errors="replace")
        except KeyError:
            raise FileNotFoundError(f"Chapter not found: {href}")

    @property
    def zf(self):
        """The zip file object."""
        return self._zf

    @property
    def opf_path(self) -> Optional[str]:
        """Path to the OPF file within the EPUB."""
        return self._opf_path

    @property
    def epub_path(self) -> str:
        """Path to the EPUB file on disk."""
        return self._epub_path

    @property
    def zip_namelist(self) -> List[str]:
        """List of all files in the EPUB archive."""
        return self._zip_namelist.copy()

    @property
    def trace(self) -> bool:
        """Whether to enable trace logging."""
        return self._trace

    @trace.setter
    def trace(self, value: bool):
        """Set trace logging."""
        self._trace = value

    def close(self) -> None:
        """Close the EPUB file."""
        if self._zf:
            self._zf.close()
            self._zf = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
