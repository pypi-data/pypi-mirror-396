import logging
import os
import re
from typing import Any, Dict, List

from ..interfaces import ContentReader
from .path_resolver import normalize_src_for_matching

logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup

    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


def parse_nav_document_robust(
    reader: ContentReader, nav_href: str
) -> List[Dict[str, str]]:
    """
    Parse EPUB3 navigation document using the robust logic from epub-tts.py

    Args:
        reader: Content reader interface for accessing EPUB content
        nav_href: Path to the navigation document within the EPUB
    """
    if not HAS_BS4:
        logger.warning("BeautifulSoup4 not found, cannot parse nav.xhtml. Skipping.")
        return []

    try:
        nav_content = reader.read_chapter(nav_href)
        nav_basedir = os.path.dirname(nav_href)
        nav_soup = BeautifulSoup(nav_content, "xml")

        # Look for the TOC navigation
        nav_toc = nav_soup.find("nav", attrs={"epub:type": "toc"})
        if not nav_toc:
            return []

        raw_chapters = []
        list_items = nav_toc.find_all("li")

        # Summary counters for less verbose logging
        chapter_count = 0
        group_header_count = 0
        total_items = len(list_items)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Found {total_items} <li> items in nav.xhtml - parsing...")

        for i, item in enumerate(list_items):
            span_tag = item.find("span")
            a_tag = item.find("a")

            # [FIX] Priority check change: Check for Link (<a>) FIRST.
            # This fixes issues where an <a> tag contains a <span> (e.g. for tcy styling),
            # ensuring it's treated as a chapter link with full text, not a group header.
            if a_tag and a_tag.get("href"):
                href = a_tag.get("href")
                # Resolve href relative to the nav document
                full_path = os.path.normpath(os.path.join(nav_basedir, href)).split(
                    "#"
                )[0]
                # .text will automatically concatenate text from children (including nested spans)
                title = " ".join(a_tag.text.strip().split())
                raw_chapters.append(
                    {
                        "type": "chapter",
                        "title": title,
                        "src": full_path,
                        "normalized_src": normalize_src_for_matching(full_path),
                    }
                )
                chapter_count += 1
            # Only check for span (group header) if it's NOT a link
            elif span_tag:
                title = " ".join(span_tag.text.strip().split())
                raw_chapters.append({"type": "group_header", "title": title})
                group_header_count += 1

        # Summary logging instead of per-item logging
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"TOC parsing complete: {chapter_count} chapters, "
                f"{group_header_count} group headers from {total_items} total items"
            )

        return raw_chapters
    except Exception as e:
        if reader.trace:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Failed to parse nav document {nav_href}: {e}")
        return []


def parse_ncx_document_robust(
    reader: ContentReader, ncx_href: str, basedir: str
) -> List[Dict[str, Any]]:
    """
    Parse EPUB2 NCX document with proper hierarchical structure.
    Return nested node structure with children attributes directly.

    Args:
        reader: Content reader interface for accessing EPUB content
        ncx_href: Path to the NCX document within the EPUB
        basedir: Base directory for resolving relative paths
    """
    try:
        ncx_content = reader.read_chapter(ncx_href)

        if HAS_BS4:
            ncx_soup = BeautifulSoup(ncx_content, "xml")
            # Only find root-level navPoint elements (direct children of navMap)
            nav_map = ncx_soup.find("navMap")
            if not nav_map:
                return []

            root_nav_points = nav_map.find_all("navPoint", recursive=False)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    f"Found {len(root_nav_points)} root <navPoint> items in toc.ncx"
                )

            # Define a regex pattern to match volume titles like "第X卷" or "Volume X"
            volume_pattern = re.compile(r"^(第.*卷|volume\s*\d+)", re.IGNORECASE)

            # Summary counters for less verbose logging
            total_chapters = 0
            total_groups = 0

            # Recursive function to process each navPoint and its children, returning nested structure
            def parse_nav_point_recursive(nav_point, depth=0):
                """Recursively parse navPoint, returning nested node structure"""
                nonlocal total_chapters, total_groups

                content_tag = nav_point.find("content", recursive=False)
                nav_label = nav_point.find("navLabel", recursive=False)

                if not content_tag or not nav_label:
                    return None

                full_path = os.path.normpath(
                    os.path.join(basedir, content_tag.get("src", ""))
                ).split("#")[0]
                title = " ".join(nav_label.text.strip().split())

                # Check if there are child nodes
                child_nav_points = nav_point.find_all("navPoint", recursive=False)

                if child_nav_points:
                    # This is a group node (has children)
                    total_groups += 1
                    children = []
                    for child in child_nav_points:
                        child_node = parse_nav_point_recursive(child, depth + 1)
                        if child_node:
                            children.append(child_node)

                    return {
                        "type": "group",
                        "title": title,
                        "src": full_path,
                        "expanded": False,
                        "children": children,
                    }
                else:
                    # This is a leaf node (chapter)
                    total_chapters += 1
                    return {
                        "type": "chapter",
                        "title": title,
                        "src": full_path,
                    }

            # Start recursive parsing from root level, return nested results
            nodes = []
            for nav_point in root_nav_points:
                node = parse_nav_point_recursive(nav_point, depth=0)
                if node:
                    # Check if this is a volume title, if so create a group
                    if volume_pattern.match(node["title"]):
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(
                                f"Creating group from volume pattern: '{node['title']}'"
                            )
                        # Convert volume title to group, set children to empty
                        # (since original NCX is flat)
                        group_node = {
                            "type": "group",
                            "title": node["title"],
                            "src": node["src"],
                            "expanded": False,
                            "children": [],
                        }
                        nodes.append(group_node)
                    else:
                        nodes.append(node)

            # Post-processing: assign non-volume chapters to the nearest volume group
            processed_nodes = []
            current_group = None

            for node in nodes:
                if node["type"] == "group":
                    # This is a volume group
                    current_group = node
                    processed_nodes.append(node)
                else:
                    # This is a chapter
                    if current_group:
                        # Add chapter to current group
                        current_group["children"].append(node)
                    else:
                        # If no current group, add to top level
                        processed_nodes.append(node)

            # Summary logging for NCX parsing
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    f"NCX parsing complete: {total_chapters} chapters, "
                    f"{total_groups} groups from {len(root_nav_points)} root navPoints"
                )

            return processed_nodes
        else:
            logger.warning("BeautifulSoup4 not available. NCX parsing will be limited.")
            return []

    except Exception as e:
        if reader.trace:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Failed to parse NCX document {ncx_href}: {e}")
        return []
