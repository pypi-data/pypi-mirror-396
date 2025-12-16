# Advanced Features

Deep dive into advanced capabilities of pdf_oxide.

## Table of Contents

- [Layout Analysis](#layout-analysis)
- [Configuration Options](#configuration-options)
- [Custom Processing](#custom-processing)
- [Performance Optimization](#performance-optimization)
- [Bookmarks and Annotations](#bookmarks-and-annotations)
- [Form Field Processing](#form-field-processing)
- [Character-Level Extraction](#character-level-extraction)

## Layout Analysis

The library uses sophisticated layout analysis algorithms to understand document structure.

### DBSCAN Clustering

DBSCAN (Density-Based Spatial Clustering) is used for grouping characters into words and lines.

**How it works:**
- Groups characters based on spatial proximity
- Epsilon (ε): 1.5× median character height
- MinPts: 2 for chars→words, 3 for words→lines
- Uses R*-tree spatial index for O(log n) performance

**Benefits:**
- Handles variable spacing
- Works with multi-column layouts
- Robust to outliers

### XY-Cut Algorithm

XY-Cut recursively divides pages to detect columns and regions.

**How it works:**
- Projects content onto X and Y axes
- Finds gaps in projection profiles
- Recursively splits at gaps
- Maximum depth: 10 levels

**Configuration:**
```rust
use pdf_oxide::{PdfDocument, LayoutConfig};

let config = LayoutConfig {
    xy_cut_threshold: 0.05,  // 5% of page dimension
    max_recursion_depth: 10,
    enable_multi_column: true,
};

let mut doc = PdfDocument::with_config("document.pdf", config)?;
```

### Font Clustering

Groups text by font characteristics for better formatting detection.

**Features:**
- Size tolerance: ±1pt
- Family exact matching
- Outlier rejection: <2% usage

## Configuration Options

### Parser Limits

Protect against malicious or malformed PDFs:

```rust
use pdf_oxide::{PdfDocument, ParserLimits};

let limits = ParserLimits {
    max_file_size: 500 * 1024 * 1024,  // 500 MB
    max_objects: 1_000_000,             // 1M objects
    max_recursion: 100,                 // 100 levels deep
    max_string_length: 10 * 1024 * 1024, // 10 MB
    max_array_length: 100_000,          // 100k items
};

let mut doc = PdfDocument::with_limits("document.pdf", limits)?;
```

**Python:**
```python
from pdf_oxide import PdfDocument, ParserLimits

limits = ParserLimits(
    max_file_size=500 * 1024 * 1024,
    max_objects=1_000_000,
    max_recursion=100,
    max_string_length=10 * 1024 * 1024,
    max_array_length=100_000
)

doc = PdfDocument.with_limits("document.pdf", limits)
```

### Text Extraction Options

Fine-tune text extraction behavior:

```rust
use pdf_oxide::{PdfDocument, TextConfig};

let config = TextConfig {
    word_spacing_threshold: 0.25,  // 0.25× char width
    line_spacing_threshold: 1.2,   // 1.2× char height
    preserve_whitespace: true,
    detect_bold: true,
    detect_italic: true,
};

let mut doc = PdfDocument::open("document.pdf")?;
doc.set_text_config(config);

let text = doc.extract_text(0)?;
```

**Python:**
```python
from pdf_oxide import PdfDocument, TextConfig

config = TextConfig(
    word_spacing_threshold=0.25,
    line_spacing_threshold=1.2,
    preserve_whitespace=True,
    detect_bold=True,
    detect_italic=True
)

doc = PdfDocument.open("document.pdf")
doc.set_text_config(config)

text = doc.extract_text(0)
```

## Custom Processing

### Character-Level Extraction

Access individual characters with bounding boxes:

```rust
use pdf_oxide::{PdfDocument, Character};

let mut doc = PdfDocument::open("document.pdf")?;
let chars: Vec<Character> = doc.extract_characters(0)?;

for ch in chars {
    println!(
        "Char: '{}' at ({:.2}, {:.2}) size {:.2}pt font '{}'",
        ch.text,
        ch.x,
        ch.y,
        ch.font_size,
        ch.font_name
    );
}
```

**Python:**
```python
from pdf_oxide import PdfDocument

doc = PdfDocument.open("document.pdf")
chars = doc.extract_characters(0)

for ch in chars:
    print(f"Char: '{ch.text}' at ({ch.x:.2f}, {ch.y:.2f}) "
          f"size {ch.font_size:.2f}pt font '{ch.font_name}'")
```

### Custom Exporters

Create custom export formats:

```rust
use pdf_oxide::{PdfDocument, Character};

struct CustomExporter;

impl CustomExporter {
    fn export(&self, doc: &mut PdfDocument, page_num: u32) -> Result<String> {
        let chars = doc.extract_characters(page_num)?;

        // Custom processing
        let mut output = String::new();

        for ch in chars {
            // Apply custom logic
            if ch.font_size > 16.0 {
                output.push_str(&format!("<h1>{}</h1>", ch.text));
            } else {
                output.push(ch.text);
            }
        }

        Ok(output)
    }
}
```

### Text Block Extraction

Get structured text blocks with metadata:

```rust
use pdf_oxide::{PdfDocument, TextBlock};

let mut doc = PdfDocument::open("document.pdf")?;
let blocks: Vec<TextBlock> = doc.extract_text_blocks(0)?;

for block in blocks {
    println!("Block: {}", block.text);
    println!("  Position: ({}, {})", block.x, block.y);
    println!("  Size: {}×{}", block.width, block.height);
    println!("  Font: {} {}pt", block.font_name, block.font_size);
    println!("  Bold: {}, Italic: {}", block.is_bold, block.is_italic);
}
```

## Performance Optimization

### Zero-Copy Parsing

The library uses zero-copy techniques for efficiency:

```rust
use pdf_oxide::PdfDocument;
use std::fs;

// Efficient: memory-mapped file
let mut doc = PdfDocument::open("document.pdf")?;

// Less efficient: loads entire file
let data = fs::read("document.pdf")?;
let mut doc = PdfDocument::from_bytes(&data)?;
```

### Streaming Processing

Process large documents without loading everything:

```rust
use pdf_oxide::PdfDocument;

let mut doc = PdfDocument::open("large.pdf")?;

// Stream pages one at a time
for page_num in 0..doc.page_count() {
    let text = doc.extract_text(page_num)?;

    // Process immediately
    process_page(text);

    // Page data can be garbage collected
}
```

### Parallel Processing

Process multiple PDFs in parallel:

**Rust:**
```rust
use rayon::prelude::*;
use pdf_oxide::PdfDocument;

let results: Vec<String> = pdf_paths
    .par_iter()
    .filter_map(|path| {
        PdfDocument::open(path)
            .and_then(|mut doc| doc.extract_text_all())
            .ok()
    })
    .collect();
```

**Python:**
```python
from multiprocessing import Pool
from pdf_oxide import PdfDocument

def extract(path):
    doc = PdfDocument.open(path)
    return doc.extract_text_all()

with Pool(8) as pool:
    results = pool.map(extract, pdf_paths)
```

### Caching

Implement caching for repeated operations:

**Python:**
```python
from functools import lru_cache
from pdf_oxide import PdfDocument

@lru_cache(maxsize=100)
def extract_cached(pdf_path: str, page_num: int) -> str:
    """Cache extracted text by path and page."""
    doc = PdfDocument.open(pdf_path)
    return doc.extract_text(page_num)
```

## Bookmarks and Annotations

### Working with Bookmarks

Extract and manipulate document outline:

```rust
use pdf_oxide::{PdfDocument, Bookmark};

let mut doc = PdfDocument::open("book.pdf")?;
let bookmarks = doc.extract_bookmarks()?;

// Print hierarchical structure
fn print_bookmarks(bookmarks: &[Bookmark], indent: usize) {
    for bookmark in bookmarks {
        println!(
            "{}{} → page {}",
            "  ".repeat(indent),
            bookmark.title,
            bookmark.page + 1
        );

        if !bookmark.children.is_empty() {
            print_bookmarks(&bookmark.children, indent + 1);
        }
    }
}

print_bookmarks(&bookmarks, 0);
```

**Python:**
```python
from pdf_oxide import PdfDocument

doc = PdfDocument.open("book.pdf")
bookmarks = doc.extract_bookmarks()

def print_bookmarks(bookmarks, indent=0):
    for bookmark in bookmarks:
        print("  " * indent + f"{bookmark.title} → page {bookmark.page + 1}")
        if bookmark.children:
            print_bookmarks(bookmark.children, indent + 1)

print_bookmarks(bookmarks)
```

### Annotation Processing

Extract and analyze annotations:

```rust
use pdf_oxide::{PdfDocument, Annotation, AnnotationType};

let mut doc = PdfDocument::open("annotated.pdf")?;

for page_num in 0..doc.page_count() {
    let annotations = doc.extract_annotations(page_num)?;

    for ann in annotations {
        match ann.annotation_type {
            AnnotationType::Text => {
                println!("Comment: {}", ann.content);
            }
            AnnotationType::Highlight => {
                println!("Highlighted: {} at {:?}", ann.content, ann.rect);
            }
            AnnotationType::Link => {
                println!("Link to: {}", ann.content);
            }
            _ => {}
        }
    }
}
```

## Form Field Processing

### Extracting Form Data

```rust
use pdf_oxide::{PdfDocument, FormField, FormFieldType};

let mut doc = PdfDocument::open("form.pdf")?;
let fields = doc.extract_form_fields()?;

for field in fields {
    match field.field_type {
        FormFieldType::Text => {
            println!("Text field '{}': {}", field.name, field.value.unwrap_or_default());
        }
        FormFieldType::Checkbox => {
            let checked = field.value.as_ref().map(|v| v == "Yes").unwrap_or(false);
            println!("Checkbox '{}': {}", field.name, checked);
        }
        FormFieldType::Radio => {
            println!("Radio '{}': {}", field.name, field.value.unwrap_or_default());
        }
        FormFieldType::ComboBox => {
            println!("Dropdown '{}': {}", field.name, field.value.unwrap_or_default());
        }
        _ => {}
    }
}
```

### Form Field Hierarchy

Some PDFs have nested form fields:

```rust
use pdf_oxide::PdfDocument;

let mut doc = PdfDocument::open("complex_form.pdf")?;
let fields = doc.extract_form_fields()?;

fn print_field_tree(fields: &[FormField], indent: usize) {
    for field in fields {
        println!(
            "{}{} ({}): {:?}",
            "  ".repeat(indent),
            field.name,
            field.field_type,
            field.value
        );

        if !field.children.is_empty() {
            print_field_tree(&field.children, indent + 1);
        }
    }
}

print_field_tree(&fields, 0);
```

## Character-Level Extraction

For advanced text analysis:

```rust
use pdf_oxide::{PdfDocument, Character};

let mut doc = PdfDocument::open("document.pdf")?;
let chars = doc.extract_characters(0)?;

// Find all bold text
let bold_chars: Vec<&Character> = chars.iter()
    .filter(|ch| ch.is_bold)
    .collect();

// Calculate text statistics
let avg_font_size = chars.iter()
    .map(|ch| ch.font_size)
    .sum::<f32>() / chars.len() as f32;

println!("Average font size: {:.2}pt", avg_font_size);

// Find text at specific location
let chars_at_top = chars.iter()
    .filter(|ch| ch.y < 100.0)
    .map(|ch| ch.text)
    .collect::<String>();

println!("Top of page: {}", chars_at_top);
```

## Stream Filters

The library supports various PDF stream filters:

### Supported Filters

- **FlateDecode**: Zlib/Deflate compression (most common)
- **LZWDecode**: LZW compression
- **ASCII85Decode**: ASCII85 encoding
- **ASCIIHexDecode**: Hexadecimal encoding
- **RunLengthDecode**: Run-length encoding
- **DCTDecode**: JPEG compression
- **CCITTFaxDecode**: CCITT Group 3/4 fax compression

### Custom Stream Processing

Access raw stream data:

```rust
use pdf_oxide::{PdfDocument, Stream};

let mut doc = PdfDocument::open("document.pdf")?;

// Access raw stream
let stream = doc.get_stream(stream_id)?;

match stream.filter {
    Some(Filter::FlateDecode) => {
        let decompressed = stream.decode()?;
        // Process decompressed data
    }
    None => {
        // Process raw data
        let data = stream.data;
    }
    _ => {}
}
```

## Diagnostics

### Document Information

```rust
use pdf_oxide::PdfDocument;

let mut doc = PdfDocument::open("document.pdf")?;

println!("PDF Version: {}", doc.version());
println!("Pages: {}", doc.page_count());
println!("Encrypted: {}", doc.is_encrypted());

if let Some(info) = doc.info() {
    println!("Title: {}", info.title.unwrap_or_default());
    println!("Author: {}", info.author.unwrap_or_default());
    println!("Creator: {}", info.creator.unwrap_or_default());
    println!("Producer: {}", info.producer.unwrap_or_default());
    println!("Created: {:?}", info.creation_date);
}
```

### Performance Profiling

```rust
use pdf_oxide::PdfDocument;
use std::time::Instant;

let mut doc = PdfDocument::open("document.pdf")?;

// Profile text extraction
let start = Instant::now();
let text = doc.extract_text(0)?;
let elapsed = start.elapsed();

println!("Text extraction: {:?}", elapsed);
println!("Characters extracted: {}", text.len());
println!("Throughput: {:.2} chars/ms", text.len() as f64 / elapsed.as_millis() as f64);
```

## Next Steps

- **[Troubleshooting](TROUBLESHOOTING.md)**: Solutions to common problems
- **[API Documentation](https://docs.rs/pdf_oxide)**: Complete API reference
- **[Examples](../../examples/)**: More code examples
- **[Benchmarks](../BENCHMARKS.md)**: Performance comparisons

## Getting Help

- **Issues**: https://github.com/yfedoseev/pdf_oxide/issues
- **Discussions**: https://github.com/yfedoseev/pdf_oxide/discussions
- **Documentation**: https://docs.rs/pdf_oxide
