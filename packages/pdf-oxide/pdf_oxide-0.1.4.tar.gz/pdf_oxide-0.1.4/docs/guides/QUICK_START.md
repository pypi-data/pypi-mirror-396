# Quick Start Guide

Get started with pdf_oxide in 5 minutes.

## Table of Contents

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Common Use Cases](#common-use-cases)
- [Next Steps](#next-steps)

## Installation

### Rust

Add to your `Cargo.toml`:

```toml
[dependencies]
pdf_oxide = "0.1"
```

Or use cargo:

```bash
cargo add pdf_oxide
```

### Python

```bash
pip install pdf_oxide
```

## Basic Usage

### Rust

```rust
use pdf_oxide::PdfDocument;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Open a PDF file
    let mut doc = PdfDocument::open("document.pdf")?;

    // Extract text from first page
    let text = doc.extract_text(0)?;
    println!("{}", text);

    // Extract text from all pages
    for page_num in 0..doc.page_count() {
        let text = doc.extract_text(page_num)?;
        println!("Page {}: {}", page_num + 1, text);
    }

    Ok(())
}
```

### Python

```python
from pdf_oxide import PdfDocument

# Open a PDF file
doc = PdfDocument.open("document.pdf")

# Extract text from first page
text = doc.extract_text(0)
print(text)

# Extract text from all pages
for page_num in range(doc.page_count()):
    text = doc.extract_text(page_num)
    print(f"Page {page_num + 1}: {text}")
```

## Common Use Cases

### 1. Export to Markdown

**Rust:**
```rust
use pdf_oxide::{PdfDocument, MarkdownExporter};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut doc = PdfDocument::open("document.pdf")?;
    let exporter = MarkdownExporter::new();

    // Export single page
    let markdown = exporter.export_page(&mut doc, 0)?;
    std::fs::write("output.md", markdown)?;

    // Export all pages
    let markdown = exporter.export_all(&mut doc)?;
    std::fs::write("full_document.md", markdown)?;

    Ok(())
}
```

**Python:**
```python
from pdf_oxide import PdfDocument, MarkdownExporter

doc = PdfDocument.open("document.pdf")
exporter = MarkdownExporter()

# Export single page
markdown = exporter.export_page(doc, 0)
with open("output.md", "w") as f:
    f.write(markdown)

# Export all pages
markdown = exporter.export_all(doc)
with open("full_document.md", "w") as f:
    f.write(markdown)
```

### 2. Export to HTML

**Rust:**
```rust
use pdf_oxide::{PdfDocument, HtmlExporter};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut doc = PdfDocument::open("document.pdf")?;
    let exporter = HtmlExporter::new();

    let html = exporter.export_all(&mut doc)?;
    std::fs::write("output.html", html)?;

    Ok(())
}
```

**Python:**
```python
from pdf_oxide import PdfDocument, HtmlExporter

doc = PdfDocument.open("document.pdf")
exporter = HtmlExporter()

html = exporter.export_all(doc)
with open("output.html", "w") as f:
    f.write(html)
```

### 3. Extract Form Fields

**Rust:**
```rust
use pdf_oxide::PdfDocument;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut doc = PdfDocument::open("form.pdf")?;

    // Get all form fields
    let fields = doc.extract_form_fields()?;

    for field in fields {
        println!("Field: {} = {:?}", field.name, field.value);
    }

    Ok(())
}
```

**Python:**
```python
from pdf_oxide import PdfDocument

doc = PdfDocument.open("form.pdf")

# Get all form fields
fields = doc.extract_form_fields()

for field in fields:
    print(f"Field: {field.name} = {field.value}")
```

### 4. Extract Images

**Rust:**
```rust
use pdf_oxide::PdfDocument;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut doc = PdfDocument::open("document.pdf")?;

    // Extract images from first page
    let images = doc.extract_images(0)?;

    for (i, image) in images.iter().enumerate() {
        let filename = format!("image_{}.png", i);
        image.save(&filename)?;
        println!("Saved: {}", filename);
    }

    Ok(())
}
```

**Python:**
```python
from pdf_oxide import PdfDocument

doc = PdfDocument.open("document.pdf")

# Extract images from first page
images = doc.extract_images(0)

for i, image in enumerate(images):
    filename = f"image_{i}.png"
    image.save(filename)
    print(f"Saved: {filename}")
```

### 5. Batch Processing

**Rust:**
```rust
use pdf_oxide::PdfDocument;
use std::fs;
use std::path::Path;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let pdf_dir = Path::new("pdfs");
    let output_dir = Path::new("output");
    fs::create_dir_all(output_dir)?;

    for entry in fs::read_dir(pdf_dir)? {
        let entry = entry?;
        let path = entry.path();

        if path.extension().and_then(|s| s.to_str()) == Some("pdf") {
            println!("Processing: {:?}", path);

            let mut doc = PdfDocument::open(&path)?;
            let text = doc.extract_text_all()?;

            let output_path = output_dir.join(
                path.file_stem().unwrap()
            ).with_extension("txt");

            fs::write(output_path, text)?;
        }
    }

    Ok(())
}
```

**Python:**
```python
from pdf_oxide import PdfDocument
import os
from pathlib import Path

pdf_dir = Path("pdfs")
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

for pdf_file in pdf_dir.glob("*.pdf"):
    print(f"Processing: {pdf_file}")

    doc = PdfDocument.open(str(pdf_file))
    text = doc.extract_text_all()

    output_file = output_dir / f"{pdf_file.stem}.txt"
    output_file.write_text(text)
```

## Performance Tips

### 1. Use Streaming for Large Documents

Instead of loading entire document:
```rust
// Good for large documents
for page_num in 0..doc.page_count() {
    let text = doc.extract_text(page_num)?;
    process_page(text);
}
```

Rather than:
```rust
// Can be memory-intensive
let all_text = doc.extract_text_all()?;
```

### 2. Batch Processing with Parallelism

**Rust (with rayon):**
```rust
use rayon::prelude::*;
use pdf_oxide::PdfDocument;

fn process_pdfs(paths: Vec<PathBuf>) -> Vec<String> {
    paths.par_iter()
        .filter_map(|path| {
            PdfDocument::open(path)
                .and_then(|mut doc| doc.extract_text_all())
                .ok()
        })
        .collect()
}
```

**Python (with multiprocessing):**
```python
from multiprocessing import Pool
from pdf_oxide import PdfDocument

def extract_text(path):
    doc = PdfDocument.open(path)
    return doc.extract_text_all()

with Pool(8) as pool:
    results = pool.map(extract_text, pdf_paths)
```

## Error Handling

### Rust

```rust
use pdf_oxide::{PdfDocument, Error};

fn safe_extract(path: &str) -> Result<String, Error> {
    let mut doc = PdfDocument::open(path)?;
    let text = doc.extract_text_all()?;
    Ok(text)
}

fn main() {
    match safe_extract("document.pdf") {
        Ok(text) => println!("Text: {}", text),
        Err(e) => eprintln!("Error: {}", e),
    }
}
```

### Python

```python
from pdf_oxide import PdfDocument, PdfError

def safe_extract(path):
    try:
        doc = PdfDocument.open(path)
        return doc.extract_text_all()
    except PdfError as e:
        print(f"Error: {e}")
        return None

text = safe_extract("document.pdf")
if text:
    print(f"Text: {text}")
```

## Next Steps

- **[Python Guide](PYTHON_GUIDE.md)**: Python-specific features and best practices
- **[Advanced Features](ADVANCED_FEATURES.md)**: Layout analysis, custom configurations
- **[Troubleshooting](TROUBLESHOOTING.md)**: Common issues and solutions
- **[API Documentation](https://docs.rs/pdf_oxide)**: Complete API reference
- **[Examples](../../examples/)**: More code examples

## Getting Help

- **Documentation**: https://docs.rs/pdf_oxide
- **Issues**: https://github.com/yfedoseev/pdf_oxide/issues
- **Discussions**: https://github.com/yfedoseev/pdf_oxide/discussions

## Performance Expectations

On a modern system (Intel i7/AMD Ryzen, 16GB RAM):

- **Simple PDFs**: 10-50ms per page
- **Complex PDFs**: 50-200ms per page
- **Image extraction**: 100-500ms per page (depends on image count/size)
- **Form extraction**: 20-100ms per document

Our benchmark suite (103 PDFs) processes in **5.43 seconds total** (53ms average per PDF).

For comparison, leading alternatives takes **259.94 seconds** for the same suite (47.9× slower).

See [BENCHMARKS.md](../BENCHMARKS.md) for detailed performance metrics.
