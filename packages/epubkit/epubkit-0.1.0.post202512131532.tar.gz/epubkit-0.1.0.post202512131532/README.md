# epubkit

A comprehensive EPUB processing toolkit for Python.

## Features

- **EPUB Reading**: Parse EPUB files with support for EPUB2/3 standards
- **Table of Contents**: Extract and navigate book structure
- **Content Access**: Read chapters and access metadata
- **CFI Support**: Canonical Fragment Identifier parsing and generation
- **Extensible**: Plugin architecture for different content sources

## Installation

```bash
pip install epubkit
```

## Quick Start

```python
import epubkit

# Open an EPUB file
book = epubkit.open("my_book.epub")

# Access metadata
print(f"Title: {book.title}")

# Navigate chapters
for chapter in book.spine:
    print(f"- {chapter['title']}")

# Read content
content = book.read_chapter("chapter1.xhtml")

# CFI support
cfi = epubkit.CFIGenerator.generate_cfi(spine_index, node, offset)
```

## License

MIT License
