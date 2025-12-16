"""
TOC Builder - Specialized component for EPUB table of contents parsing
"""

import logging
import os
import re
from typing import Any, Dict, List

from ..interfaces import ContentReader
from .metadata_parser import extract_book_title
from .opf_parser import parse_opf
from .path_resolver import normalize_src_for_matching
from .toc_parser import (
    parse_nav_document_robust,
    parse_ncx_document_robust,
)

logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup

    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


class TOCBuilder:
    """
    Specialized component for building EPUB table of contents.

    Handles EPUB2/3 TOC parsing with proper fallbacks:
    - nav.xhtml (EPUB3)
    - toc.ncx (EPUB2)
    - spine fallback (emergency)
    """

    def __init__(self, reader: ContentReader):
        """
        Initialize TOC builder with content reader interface.

        Args:
            reader: Content reader interface for accessing EPUB content
        """
        self.reader = reader

    def build_toc(self) -> Dict:
        """
        Build comprehensive TOC with proper EPUB standard support.

        Returns:
            Dict containing 'book_title', 'nodes', 'spine_order', 'toc_source', 'raw_chapters'
        """
        try:
            return self._extract_structured_toc()
        except Exception as e:
            logger.warning(f"Structured TOC extraction failed: {e}")
            return self._spine_fallback_toc()

    def _extract_structured_toc(self) -> Dict:
        """
        Extract structured TOC following EPUB standards.
        Priority: nav.xhtml (EPUB3) → toc.ncx (EPUB2) → spine fallback
        """
        if not self.reader.zf or not self.reader.opf_path:
            raise RuntimeError("EPUB not properly opened")

        if self.reader.trace:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("--- Starting TOC Build Process ---")

        # Read OPF file
        opf_bytes = self._read_opf_file()
        opf = self._parse_opf_content(opf_bytes)

        # Extract metadata
        book_title = extract_book_title(opf, self.reader.epub_path)
        basedir = os.path.dirname(self.reader.opf_path)
        basedir = f"{basedir}/" if basedir else ""

        # Parse OPF structure and reuse results to avoid duplicate parsing
        # Unpack the results that parse_opf already logged about
        manifest, spine_order, ncx, navdoc = parse_opf(opf_bytes, basedir)

        if self.reader.trace:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    f"TOC Builder: Reusing parsed OPF data - spine has {len(spine_order)} items."
                )

        # Parse TOC from various sources
        toc_result = self._parse_toc_sources(navdoc, ncx, basedir, spine_order)
        nodes, raw_chapters, toc_source = toc_result

        if self.reader.trace:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    f"--- TOC Build Process Finished. Final source: {toc_source} ---"
                )

        return {
            "book_title": book_title,
            "nodes": nodes,
            "spine_order": spine_order,
            "toc_source": toc_source,
            "raw_chapters": raw_chapters,
        }

    def _read_opf_file(self) -> bytes:
        """Read and return OPF file content."""
        try:
            return self.reader.zf.read(self.reader.opf_path)
        except KeyError:
            # Try case-insensitive search
            for name in self.reader.zip_namelist:
                if name.lower() == self.reader.opf_path.lower():
                    return self.reader.zf.read(name)
            raise FileNotFoundError(f"OPF file not found: {self.reader.opf_path}")

    def _parse_opf_content(self, opf_bytes: bytes) -> Any:
        """Parse OPF content based on available XML parser."""
        if HAS_BS4:
            return BeautifulSoup(opf_bytes.decode("utf-8", errors="replace"), "xml")
        else:
            import xml.etree.ElementTree as ET

            return ET.fromstring(opf_bytes)

    def _parse_toc_sources(
        self, navdoc: str, ncx: str, basedir: str, spine_order: List[str]
    ) -> tuple[List[Dict], List[Dict], str]:
        """Parse TOC from various sources with proper fallbacks."""
        raw_chapters = []
        nodes = []
        toc_source = "None"

        # Try NAV document first (EPUB3)
        if navdoc:
            raw_chapters = self._parse_nav_toc(navdoc, ncx, basedir)
            if raw_chapters:
                # Check if we need to fallback to NCX for better grouping
                has_groups = any(
                    chap.get("type") == "group_header" for chap in raw_chapters
                )
                if not has_groups and ncx:
                    nodes = parse_ncx_document_robust(self.reader, ncx, basedir)
                    if nodes:
                        toc_source = "toc.ncx"
                        raw_chapters = self._flatten_toc_nodes_for_raw_list(nodes)
                        return nodes, raw_chapters, toc_source
                # Build nodes from raw chapters for NAV
                nodes = self._build_node_hierarchy(raw_chapters)
                toc_source = "nav.xhtml"
                return nodes, raw_chapters, toc_source

        # Try NCX document (EPUB2)
        if not raw_chapters and ncx:
            nodes = parse_ncx_document_robust(self.reader, ncx, basedir)
            if nodes:
                toc_source = "toc.ncx"
                raw_chapters = self._flatten_toc_nodes_for_raw_list(nodes)
                return nodes, raw_chapters, toc_source

        # Fallback to spine parsing
        if not raw_chapters and spine_order:
            toc_source = "spine"
            raw_chapters = self._build_spine_chapters(spine_order)
            nodes = raw_chapters.copy()  # For spine fallback, nodes are simple chapters

        return nodes, raw_chapters, toc_source

    def _parse_nav_toc(self, navdoc: str, ncx: str, basedir: str) -> List[Dict]:
        """Parse NAV document and fallback logic."""
        raw_chapters = parse_nav_document_robust(self.reader, navdoc)
        return raw_chapters

    def _build_spine_chapters(self, spine_order: List[str]) -> List[Dict]:
        """Build raw chapters from spine order as last resort."""
        raw_chapters = []
        for spine_href in spine_order:
            title = os.path.basename(spine_href)
            title = os.path.splitext(title)[0]
            title = title.replace("_", " ").replace("-", " ")
            title = " ".join(word.capitalize() for word in title.split())

            if self.reader.trace:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(
                        f"  item: Creating chapter from spine: '{title}' -> '{spine_href}'"
                    )

            raw_chapters.append(
                {
                    "type": "chapter",
                    "title": title,
                    "src": spine_href,
                    "normalized_src": normalize_src_for_matching(spine_href),
                }
            )
        return raw_chapters

    def _build_node_hierarchy(self, raw_chapters: List[Dict]) -> List[Dict]:
        """Build hierarchical node structure from raw chapters."""
        nodes = []
        current_group = None

        if self.reader.trace:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("--- Finalizing Node Structure (Grouping) ---")

        # Define patterns for grouping
        volume_pattern = re.compile(r"^(第.*卷|volume\s*\d+)", re.IGNORECASE)

        for chap in raw_chapters:
            title = chap["title"]

            # Check for volume grouping
            if volume_pattern.match(title):
                if self.reader.trace:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(
                            f"Creating new group from volume pattern: '{title}'"
                        )
                current_group = {
                    "type": "group",
                    "title": title,
                    "expanded": False,
                    "children": [],
                    "src": chap.get("src"),
                }
                nodes.append(current_group)

            # Check for group header pattern
            elif chap.get("type") == "group_header":
                if self.reader.trace:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(
                            f"Creating new group from 'group_header': '{title}'"
                        )
                current_group = {
                    "type": "group",
                    "title": title,
                    "expanded": False,
                    "children": [],
                }
                nodes.append(current_group)

            # Check for bracket grouping pattern
            elif (
                chap.get("type") == "chapter"
                and title.startswith("【")
                and title.endswith("】")
            ):
                if self.reader.trace:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(
                            f"Creating new group from fallback pattern '〈...〉': '{title}'"
                        )
                current_group = {
                    "type": "group",
                    "title": title,
                    "expanded": False,
                    "children": [],
                }
                nodes.append(current_group)

            # Regular chapter
            else:
                node = {"type": "chapter", "title": title, "src": chap.get("src")}
                if current_group:
                    if self.reader.trace:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(
                                f"  Adding chapter '{title}' to group '{current_group['title']}'"
                            )
                    current_group["children"].append(node)
                else:
                    if self.reader.trace:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(
                                f"Adding chapter '{title}' as a top-level node."
                            )
                    nodes.append(node)

        return nodes

    def _flatten_toc_nodes_for_raw_list(self, nodes: List[Dict]) -> List[Dict]:
        """Recursively flatten hierarchical nodes into a flat list for raw_chapters."""
        flat_list = []

        def recurse(node_list: List[Dict]):
            for node in node_list:
                if node.get("type") == "chapter":
                    flat_list.append(
                        {
                            "type": "chapter",
                            "title": node.get("title", "Untitled"),
                            "src": node.get("src", ""),
                            "normalized_src": normalize_src_for_matching(
                                node.get("src", "")
                            ),
                        }
                    )
                elif node.get("type") == "group":
                    if "children" in node and node["children"]:
                        recurse(node["children"])

        recurse(nodes)
        return flat_list

    def _spine_fallback_toc(self) -> Dict:
        """Emergency fallback: use basic spine parsing."""
        try:
            if not self.reader.zf or not self.reader.opf_path:
                raise RuntimeError("EPUB not properly opened")

            import xml.etree.ElementTree as ET

            opf_bytes = self.reader.zf.read(self.reader.opf_path)
            root = ET.fromstring(opf_bytes)

            # Extract manifest
            manifest = {}
            for item in root.findall(".//*[@id][@href]"):
                item_id = item.attrib.get("id")
                href = item.attrib.get("href")
                if item_id and href:
                    manifest[item_id] = href

            # Extract spine order
            spine_hrefs = []
            spine = root.find(".//spine") or root.find(".//{*}spine")
            if spine is not None:
                for itemref in spine.findall("itemref") or spine.findall("{*}itemref"):
                    idref = itemref.attrib.get("idref")
                    if idref and idref in manifest:
                        spine_hrefs.append(manifest[idref])

            # Build simple nodes
            nodes = []
            raw_chapters = []
            for idx, href in enumerate(spine_hrefs, 1):
                title = os.path.basename(href)
                title = os.path.splitext(title)[0]
                chapter_data = {
                    "type": "chapter",
                    "title": title,
                    "src": href,
                    "index": idx,
                    "normalized_src": normalize_src_for_matching(href),
                }
                nodes.append(chapter_data)
                raw_chapters.append(chapter_data)

            book_title = extract_book_title(root, self.reader.epub_path)

            return {
                "book_title": book_title,
                "nodes": nodes,
                "spine_order": spine_hrefs,
                "toc_source": "fallback",
                "raw_chapters": raw_chapters,
            }

        except Exception as e:
            logger.error(f"Even fallback TOC parsing failed: {e}")
            return {
                "book_title": os.path.basename(self.reader.epub_path),
                "nodes": [],
                "spine_order": [],
                "toc_source": "error",
                "raw_chapters": [],
            }
