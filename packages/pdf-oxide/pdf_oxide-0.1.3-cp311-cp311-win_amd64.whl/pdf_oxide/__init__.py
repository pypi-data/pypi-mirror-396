"""
PDF Library - Fast PDF parsing and conversion

A high-performance PDF parsing library built with Rust,
providing text extraction, layout analysis, and conversion
to HTML and Markdown.

# Features

- **PDF Parsing**: Parse PDF 1.0-1.7 documents
- **Text Extraction**: Extract text with accurate Unicode mapping
- **Layout Analysis**: Multi-column detection, reading order determination
- **Format Conversion**: Convert to Markdown and HTML
- **High Performance**: Built with Rust for speed and memory safety

# Quick Start

```python
from pdf_oxide import PdfDocument

# Open a PDF
doc = PdfDocument("document.pdf")

# Get basic info
print(f"PDF version: {doc.version()}")
print(f"Pages: {doc.page_count()}")

# Extract text
text = doc.extract_text(0)
print(text)

# Convert to Markdown
markdown = doc.to_markdown(0, detect_headings=True)
with open("output.md", "w") as f:
    f.write(markdown)

# Convert to HTML
html = doc.to_html(0, preserve_layout=False)
with open("output.html", "w") as f:
    f.write(html)
```

# License

This project is licensed under the AGPL-3.0-or-later license.
If you use this library in a SaaS/network service, you must open-source your application.
"""

from .pdf_oxide import PdfDocument, VERSION

__all__ = ["PdfDocument", "VERSION"]
__version__ = "0.1.0"
