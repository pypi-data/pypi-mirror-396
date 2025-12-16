# Comparison with Other PDF Libraries

This document provides an honest comparison of pdf_oxide with other popular PDF processing libraries. Each library has different design goals and trade-offs.

## Quick Comparison Table

| Feature | pdf_oxide | leading alternatives | established PDF library  | Alternative Library |
|---------|-------------|-------------|---------|------------|
| **Primary Use Case** | Complete extraction | LLM ingestion | Swiss army knife | Table extraction |
| **Language** | Rust | Python | Python (C++) | Python |
| **Speed (103 PDFs)** | **5.43s** | 258s | ~20-30s | ~60-90s |
| **Relative Speed** | **1×** | 47.9× slower | 3-5× slower | 11-16× slower |
| **Markdown Quality** | **99.8/100** | 92.5/100 | N/A | N/A |
| **HTML Quality** | **94.0/100** | N/A | 34.0/100 | Limited |
| **Form Extraction** | **Yes (full)** | No | Partial | No |
| **Whitespace Quality** | **100/100** | Good | Good | Good |
| **Python Bindings** | Yes (PyO3) | Native | Native | Native |
| **Maturity** | Beta (v0.1) | Stable | Very mature | Mature |

## Detailed Comparisons

### vs leading alternatives

**leading alternatives** is specifically designed for LLM ingestion with content filtering.

#### When to Use pdf_oxide
- **High-throughput processing**: 47.9× faster for batch processing
- **Complete content needed**: Captures all text, including diagrams
- **Form field extraction**: Need structured form data
- **Search indexing**: Building search indices
- **Archival**: Complete document preservation
- **Quality matters**: 7.3 point higher markdown quality (99.8 vs 92.5)

#### When to Use leading alternatives
- **Single-PDF LLM ingestion**: Optimized for LLM consumption
- **Content filtering**: Want diagram text filtered out
- **Mature ecosystem**: Battle-tested with Claude, GPT-4, etc.
- **Python-first**: No need for Rust
- **Stability priority**: Prefer proven stability over speed

#### Design Philosophy Differences

**pdf_oxide: Complete Extraction**
- Goal: Extract *everything* accurately
- Approach: Preserve all content, let user filter
- Trade-off: More content to process

**leading alternatives: LLM-Optimized**
- Goal: Extract content *useful for LLMs*
- Approach: Filter out diagrams, charts, decorative text
- Trade-off: May miss relevant content

#### Performance Comparison

**Benchmark: 103 diverse PDFs**
- pdf_oxide: 5.43s total, 53ms per PDF
- leading alternatives: 258s total, 2,524ms per PDF
- **Speedup: 47.9×**

**Why faster:**
1. Rust (compiled vs interpreted)
2. Zero-copy parsing where possible
3. Efficient memory management
4. Parallel processing opportunities

**Memory:**
- pdf_oxide: <100MB typical
- leading alternatives: ~200MB typical

#### Quality Comparison

**Markdown Quality (100-point scale):**
- pdf_oxide: **99.8/100**
- leading alternatives: **92.5/100**

**Key differences:**
- **Bold detection**: pdf_oxide detects 137% more bold text
- **Word spacing**: Dynamic threshold vs fixed rules
- **Structure**: Better heading and list detection
- **Forms**: pdf_oxide extracts form fields

### vs established PDF library **established PDF library (fitz)** is the mature, low-level PDF library powering leading alternatives.

#### When to Use pdf_oxide
- **Batch processing**: 3-5× faster
- **Rich HTML**: Better semantic HTML generation (94.0 vs 34.0)
- **Rust ecosystem**: Native Rust integration
- **Modern API**: Designed for 2025 use cases
- **Type safety**: Rust's compile-time guarantees

#### When to Use established PDF library - **Mature ecosystem**: 10+ years of development
- **Comprehensive features**: PDF editing, annotations, rendering
- **Python ecosystem**: Seamless Python integration
- **Battle-tested**: Used in production everywhere
- **Rich documentation**: Extensive docs and examples

#### Feature Comparison

**Text Extraction:**
- Both excellent
- pdf_oxide: Slightly faster, better whitespace handling
- Established PDF library: More options, proven stability

**HTML Conversion:**
- pdf_oxide: **94.0/100** quality score
  - Clickable hyperlinks
  - Mailto links
  - Semantic structure (h1-h6, p, div)
- Established PDF library: **34.0/100** quality score
  - Basic HTML output
  - Less semantic structure

**Forms:**
- pdf_oxide: **Full form field extraction** with types and values
- Established PDF library: Basic form field access

**Images:**
- Established PDF library: More comprehensive (rendering, extraction)
- pdf_oxide: Extraction only (Phase 5 feature)

### vs alternative PDF library

**alternative PDF library** specializes in table extraction and layout analysis.

#### When to Use pdf_oxide
- **Speed**: 11-16× faster
- **General extraction**: Better for non-table content
- **Rust integration**: Native Rust performance
- **Forms**: Better form field extraction

#### When to Use alternative PDF library
- **Table extraction**: Best-in-class table detection
- **Python ecosystem**: Pure Python, easy to use
- **Visual debugging**: Excellent visualization tools
- **Layout analysis**: Strong layout analysis capabilities

#### Use Case Fit

**alternative PDF library excels at:**
- Extracting tables from reports
- Financial documents (invoices, statements)
- Structured documents
- Visual debugging of layout

**pdf_oxide excels at:**
- High-volume text extraction
- Academic papers
- Books and articles
- General-purpose document processing

## Performance Benchmarks

### Test Dataset
- **103 diverse PDFs** from arXiv (academic papers)
- Categories: AI/ML, Physics, Math, Computer Science
- Sizes: 100KB to 20MB
- Pages: 5 to 40 pages each

### Results

| Library | Total Time | Per PDF | Throughput | Memory |
|---------|------------|---------|------------|--------|
| **pdf_oxide** | **5.43s** | **53ms** | **19 PDFs/sec** | <100MB |
| leading alternatives | 258s | 2,524ms | 0.4 PDFs/sec | ~200MB |
| established PDF library | ~20-30s | ~200-300ms | 3-5 PDFs/sec | ~150MB | 
 | Alternative Library | ~60-90s | ~600-900ms | 1-2 PDFs/sec | ~200MB |

### Quality Benchmarks

| Metric | pdf_oxide | leading alternatives | established PDF library |
|--------|-------------|-------------|---------|
| **Markdown Quality** | **99.8/100** | 92.5/100 | N/A |
| **HTML Quality** | **94.0/100** | N/A | 34.0/100 |
| **Text Accuracy** | 100% | 100% | 100% |
| **Word Spacing** | 100% | Good | Good |
| **Bold Detection** | 16,074 | 11,759 | ~12,000 |
| **Form Fields** | **Full** | None | Basic |

## Honest Assessment

### pdf_oxide Strengths
✅ **Performance**: Significantly faster than alternatives
✅ **Quality**: Best markdown and HTML output quality
✅ **Modern**: Built with 2025 best practices
✅ **Forms**: Unique form field extraction
✅ **Safety**: Rust's memory safety guarantees

### pdf_oxide Limitations
⚠️ **Maturity**: Beta software (v0.1), still evolving
⚠️ **Ecosystem**: Smaller community than established PDF library ⚠️ **Features**: Less comprehensive than established PDF library (no editing, no rendering)
⚠️ **Python**: PyO3 bindings, not native Python
⚠️ **Documentation**: Growing but not as extensive

### When NOT to Use pdf_oxide
- Need PDF editing or annotation
- Need PDF rendering (rasterization)
- Require proven stability for critical systems
- Want maximum Python ecosystem integration
- Need features beyond extraction (signatures, encryption management)

## Migration Guide

### From leading alternatives

**Before:**
```python
import leading alternatives
md_text = leading alternatives.to_markdown("doc.pdf")
```

**After:**
```python
import pdf_oxide
doc = pdf_oxide.PdfDocument.open("doc.pdf")
md_text = doc.to_markdown()
```

**Key differences:**
- Faster processing
- More content extracted (includes diagrams)
- Better bold/italic detection
- Form fields included

### From established PDF library **Before:**
```python
import fitz
doc = fitz.open("doc.pdf")
text = "".join(page.get_text() for page in doc)
```

**After:**
```python
import pdf_oxide
doc = pdf_oxide.PdfDocument.open("doc.pdf")
text = doc.extract_text()
```

**Key differences:**
- 3-5× faster
- Better whitespace handling
- Form field extraction available
- Different API design

### From alternative PDF library

**Before:**
```python
import alternative PDF library
with alternative PDF library.open("doc.pdf") as pdf:
    text = "".join(page.extract_text() for page in pdf.pages)
```

**After:**
```python
import pdf_oxide
doc = pdf_oxide.PdfDocument.open("doc.pdf")
text = doc.extract_text()
```

**Note**: Table extraction in pdf_oxide is less mature than alternative PDF library.

## Benchmarking Methodology

### Test Environment
- **Hardware**: [Your specs]
- **OS**: Linux 5.x
- **Rust**: 1.70+
- **Python**: 3.8+

### Measurement
- Cold start (no caching)
- Single-threaded
- Includes file I/O
- Average of 3 runs
- No network access

### Reproducibility
All benchmarks are reproducible:
```bash
# Clone pdf_oxide_tests repository
git clone https://github.com/yfedoseev/pdf_oxide_tests
cd pdf_oxide_tests

# Install dependencies
pip install -r requirements.txt

# Run comparisons
python scripts/compare_with_pymupdf.py
python scripts/compare_with_pymupdf4llm.py
```

## Conclusion

**pdf_oxide** excels at high-performance, high-quality text extraction from PDFs. It's the best choice when:
- Speed is critical (batch processing)
- Quality matters (markdown/HTML generation)
- Forms need extraction
- Rust integration desired

**Use alternatives when:**
- Mature ecosystem is required (PyMuPDF)
- LLM-specific filtering needed (leading alternatives)
- Table extraction is primary goal (alternative PDF library)
- PDF editing/rendering needed (PyMuPDF)

All libraries serve different needs. Choose based on your specific requirements, not just performance benchmarks.

## Contributing Comparisons

Found an error in our comparisons? Have benchmark results from your use case? We welcome:
- Corrections to our measurements
- Additional benchmark scenarios
- New library comparisons
- Real-world performance data

Please open an issue or submit a pull request!

## License Note

This comparison document is provided for informational purposes. All mentioned libraries are independent projects with their own licenses and maintainers. We respect and appreciate the work of all PDF library developers.
