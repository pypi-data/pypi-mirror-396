# Python Guide

Comprehensive guide for using pdf_oxide from Python.

## Table of Contents

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [API Overview](#api-overview)
- [Advanced Features](#advanced-features)
- [Integration Patterns](#integration-patterns)
- [Performance](#performance)
- [Type Hints](#type-hints)
- [Troubleshooting](#troubleshooting)

## Installation

### Using pip

```bash
pip install pdf_oxide
```

### From source

```bash
git clone https://github.com/yfedoseev/pdf_oxide
cd pdf_oxide
pip install maturin
maturin develop --release
```

### Requirements

- **Python**: 3.8 or later
- **Operating Systems**: Linux, macOS, Windows
- **Architecture**: x86_64, aarch64 (ARM64)

## Basic Usage

### Opening Documents

```python
from pdf_oxide import PdfDocument

# Open from file path
doc = PdfDocument.open("document.pdf")

# Open from bytes
with open("document.pdf", "rb") as f:
    data = f.read()
    doc = PdfDocument.from_bytes(data)
```

### Extracting Text

```python
# Single page
text = doc.extract_text(0)  # First page (0-indexed)

# All pages
all_text = doc.extract_text_all()

# Multiple pages
texts = [doc.extract_text(i) for i in range(doc.page_count())]

# With progress tracking
from tqdm import tqdm

texts = []
for i in tqdm(range(doc.page_count())):
    text = doc.extract_text(i)
    texts.append(text)
```

### Exporting Formats

```python
from pdf_oxide import PdfDocument, MarkdownExporter, HtmlExporter

doc = PdfDocument.open("document.pdf")

# Export to Markdown
md_exporter = MarkdownExporter()
markdown = md_exporter.export_all(doc)
with open("output.md", "w") as f:
    f.write(markdown)

# Export to HTML
html_exporter = HtmlExporter()
html = html_exporter.export_all(doc)
with open("output.html", "w") as f:
    f.write(html)

# Export single page
page_md = md_exporter.export_page(doc, 0)
```

## API Overview

### PdfDocument

```python
class PdfDocument:
    """PDF document handle."""

    @staticmethod
    def open(path: str) -> PdfDocument:
        """Open PDF from file path."""
        ...

    @staticmethod
    def from_bytes(data: bytes) -> PdfDocument:
        """Open PDF from bytes."""
        ...

    def page_count(self) -> int:
        """Get number of pages."""
        ...

    def extract_text(self, page_num: int) -> str:
        """Extract text from specific page (0-indexed)."""
        ...

    def extract_text_all(self) -> str:
        """Extract text from all pages."""
        ...

    def extract_form_fields(self) -> list[FormField]:
        """Extract form fields from document."""
        ...

    def extract_images(self, page_num: int) -> list[Image]:
        """Extract images from specific page."""
        ...

    def extract_bookmarks(self) -> list[Bookmark]:
        """Extract document outline/bookmarks."""
        ...

    def extract_annotations(self, page_num: int) -> list[Annotation]:
        """Extract annotations from specific page."""
        ...
```

### Exporters

```python
class MarkdownExporter:
    """Export PDF to Markdown format."""

    def __init__(self):
        """Create new Markdown exporter."""
        ...

    def export_page(self, doc: PdfDocument, page_num: int) -> str:
        """Export single page to Markdown."""
        ...

    def export_all(self, doc: PdfDocument) -> str:
        """Export all pages to Markdown."""
        ...

class HtmlExporter:
    """Export PDF to HTML format."""

    def __init__(self):
        """Create new HTML exporter."""
        ...

    def export_page(self, doc: PdfDocument, page_num: int) -> str:
        """Export single page to HTML."""
        ...

    def export_all(self, doc: PdfDocument) -> str:
        """Export all pages to HTML."""
        ...
```

### Data Classes

```python
class FormField:
    """PDF form field."""
    name: str
    value: str | None
    field_type: str

class Image:
    """Extracted image."""
    width: int
    height: int
    data: bytes

    def save(self, path: str) -> None:
        """Save image to file."""
        ...

class Bookmark:
    """Document bookmark/outline entry."""
    title: str
    page: int
    level: int

class Annotation:
    """PDF annotation."""
    annotation_type: str
    content: str
    rect: tuple[float, float, float, float]
```

## Advanced Features

### Form Field Extraction

```python
from pdf_oxide import PdfDocument

doc = PdfDocument.open("form.pdf")
fields = doc.extract_form_fields()

# Process form fields
form_data = {}
for field in fields:
    form_data[field.name] = field.value
    print(f"{field.name} ({field.field_type}): {field.value}")

# Export to JSON
import json
with open("form_data.json", "w") as f:
    json.dump(form_data, f, indent=2)
```

### Bookmark Extraction

```python
from pdf_oxide import PdfDocument

doc = PdfDocument.open("book.pdf")
bookmarks = doc.extract_bookmarks()

# Print table of contents
for bookmark in bookmarks:
    indent = "  " * bookmark.level
    print(f"{indent}{bookmark.title} (page {bookmark.page + 1})")

# Generate TOC markdown
toc = []
for bookmark in bookmarks:
    indent = "  " * bookmark.level
    toc.append(f"{indent}- [{bookmark.title}](#page-{bookmark.page + 1})")

print("\n".join(toc))
```

### Annotation Extraction

```python
from pdf_oxide import PdfDocument

doc = PdfDocument.open("annotated.pdf")

for page_num in range(doc.page_count()):
    annotations = doc.extract_annotations(page_num)

    if annotations:
        print(f"\nPage {page_num + 1}:")
        for ann in annotations:
            print(f"  [{ann.annotation_type}] {ann.content}")
```

### Image Extraction

```python
from pdf_oxide import PdfDocument
import os

doc = PdfDocument.open("document.pdf")
output_dir = "images"
os.makedirs(output_dir, exist_ok=True)

for page_num in range(doc.page_count()):
    images = doc.extract_images(page_num)

    for i, image in enumerate(images):
        filename = f"page{page_num + 1}_image{i + 1}.png"
        filepath = os.path.join(output_dir, filename)
        image.save(filepath)
        print(f"Saved: {filepath} ({image.width}×{image.height})")
```

## Integration Patterns

### Flask Web Service

```python
from flask import Flask, request, jsonify
from pdf_oxide import PdfDocument
import tempfile
import os

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        doc = PdfDocument.open(tmp_path)
        text = doc.extract_text_all()
        return jsonify({
            'pages': doc.page_count(),
            'text': text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        os.unlink(tmp_path)

if __name__ == '__main__':
    app.run(debug=True)
```

### Django Integration

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pdf_oxide import PdfDocument
import tempfile
import os

@csrf_exempt
def extract_pdf(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    if 'pdf' not in request.FILES:
        return JsonResponse({'error': 'No PDF provided'}, status=400)

    pdf_file = request.FILES['pdf']

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        for chunk in pdf_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        doc = PdfDocument.open(tmp_path)
        text = doc.extract_text_all()

        return JsonResponse({
            'success': True,
            'pages': doc.page_count(),
            'text': text
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    finally:
        os.unlink(tmp_path)
```

### Jupyter Notebook

```python
from pdf_oxide import PdfDocument
from IPython.display import Markdown, HTML

# Extract and display as Markdown
doc = PdfDocument.open("document.pdf")
markdown = MarkdownExporter().export_page(doc, 0)
display(Markdown(markdown))

# Or as HTML
html = HtmlExporter().export_page(doc, 0)
display(HTML(html))
```

### Pandas Integration

```python
from pdf_oxide import PdfDocument
import pandas as pd

# Extract form fields to DataFrame
doc = PdfDocument.open("form.pdf")
fields = doc.extract_form_fields()

df = pd.DataFrame([
    {
        'name': field.name,
        'type': field.field_type,
        'value': field.value
    }
    for field in fields
])

print(df)
```

## Performance

### Benchmarking

```python
import time
from pdf_oxide import PdfDocument

doc = PdfDocument.open("document.pdf")

start = time.time()
text = doc.extract_text_all()
elapsed = time.time() - start

print(f"Processed {doc.page_count()} pages in {elapsed:.2f}s")
print(f"Average: {elapsed / doc.page_count() * 1000:.1f}ms per page")
```

### Batch Processing

```python
from pathlib import Path
from pdf_oxide import PdfDocument
from concurrent.futures import ProcessPoolExecutor, as_completed
import time

def process_pdf(pdf_path):
    """Process single PDF and return results."""
    try:
        doc = PdfDocument.open(str(pdf_path))
        text = doc.extract_text_all()
        return {
            'path': str(pdf_path),
            'pages': doc.page_count(),
            'chars': len(text),
            'success': True
        }
    except Exception as e:
        return {
            'path': str(pdf_path),
            'error': str(e),
            'success': False
        }

# Process PDFs in parallel
pdf_dir = Path("pdfs")
pdf_files = list(pdf_dir.glob("*.pdf"))

start = time.time()

with ProcessPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(process_pdf, pdf): pdf for pdf in pdf_files}

    results = []
    for future in as_completed(futures):
        result = future.result()
        results.append(result)
        print(f"Processed: {result['path']}")

elapsed = time.time() - start

# Summary
successful = sum(1 for r in results if r['success'])
total_pages = sum(r.get('pages', 0) for r in results if r['success'])

print(f"\nProcessed {successful}/{len(results)} PDFs in {elapsed:.2f}s")
print(f"Total pages: {total_pages}")
print(f"Average: {elapsed / len(results) * 1000:.1f}ms per PDF")
```

### Memory-Efficient Processing

```python
from pdf_oxide import PdfDocument
import gc

def process_large_batch(pdf_paths, output_dir):
    """Process PDFs one at a time to minimize memory usage."""
    for pdf_path in pdf_paths:
        doc = PdfDocument.open(str(pdf_path))

        # Process page by page
        for page_num in range(doc.page_count()):
            text = doc.extract_text(page_num)

            # Write to output immediately
            output_file = output_dir / f"{pdf_path.stem}_page{page_num}.txt"
            output_file.write_text(text)

        # Explicitly release document
        del doc
        gc.collect()
```

## Type Hints

For better IDE support and type checking:

```python
from typing import List, Optional
from pdf_oxide import (
    PdfDocument,
    FormField,
    Image,
    Bookmark,
    Annotation,
    MarkdownExporter,
    HtmlExporter
)

def extract_and_process(pdf_path: str) -> dict:
    """Extract data from PDF with full type hints."""
    doc: PdfDocument = PdfDocument.open(pdf_path)

    # Extract various data
    text: str = doc.extract_text_all()
    fields: List[FormField] = doc.extract_form_fields()
    bookmarks: List[Bookmark] = doc.extract_bookmarks()

    return {
        'text': text,
        'fields': [{'name': f.name, 'value': f.value} for f in fields],
        'bookmarks': [{'title': b.title, 'page': b.page} for b in bookmarks]
    }
```

## Troubleshooting

### Common Issues

**1. Module not found:**
```python
# If you get "ModuleNotFoundError: No module named 'pdf_oxide'"
# Make sure it's installed:
pip install pdf_oxide

# Or if developing:
pip install maturin
maturin develop --release
```

**2. File not found:**
```python
# Always use absolute paths or verify relative paths
from pathlib import Path

pdf_path = Path("document.pdf").resolve()
if not pdf_path.exists():
    raise FileNotFoundError(f"PDF not found: {pdf_path}")

doc = PdfDocument.open(str(pdf_path))
```

**3. Memory issues with large files:**
```python
# Process page by page instead of all at once
doc = PdfDocument.open("large.pdf")

for page_num in range(doc.page_count()):
    text = doc.extract_text(page_num)
    # Process immediately, don't accumulate
    process_page(text)
```

**4. Unicode errors:**
```python
# Always use UTF-8 encoding when writing
text = doc.extract_text_all()
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(text)
```

### Error Handling

```python
from pdf_oxide import PdfDocument, PdfError

def safe_extract(pdf_path: str) -> Optional[str]:
    """Safely extract text with error handling."""
    try:
        doc = PdfDocument.open(pdf_path)
        return doc.extract_text_all()
    except PdfError as e:
        print(f"PDF error: {e}")
        return None
    except FileNotFoundError:
        print(f"File not found: {pdf_path}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

## Next Steps

- **[Advanced Features](ADVANCED_FEATURES.md)**: Learn about layout analysis and configuration
- **[Troubleshooting](TROUBLESHOOTING.md)**: Detailed troubleshooting guide
- **[API Documentation](https://docs.rs/pdf_oxide)**: Complete API reference
- **[Examples](../../examples/)**: More Python examples

## Getting Help

- **Issues**: https://github.com/yfedoseev/pdf_oxide/issues
- **Discussions**: https://github.com/yfedoseev/pdf_oxide/discussions
- **Documentation**: https://docs.rs/pdf_oxide
