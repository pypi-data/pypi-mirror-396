# Troubleshooting Guide

Solutions to common problems when using pdf_oxide.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Runtime Errors](#runtime-errors)
- [Performance Issues](#performance-issues)
- [Quality Issues](#quality-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Integration Issues](#integration-issues)

## Installation Issues

### Rust: Compilation Errors

**Problem:** `cargo build` fails with compiler errors

**Solutions:**

1. **Update Rust:**
   ```bash
   rustup update
   ```
   Minimum required: Rust 1.70+

2. **Check dependencies:**
   ```bash
   cargo clean
   cargo build
   ```

3. **Platform-specific dependencies:**
   - **Linux:** Install development libraries
     ```bash
     # Debian/Ubuntu
     sudo apt-get install build-essential

     # Fedora/RHEL
     sudo dnf groupinstall "Development Tools"
     ```

   - **macOS:** Install Xcode Command Line Tools
     ```bash
     xcode-select --install
     ```

   - **Windows:** Install Visual Studio Build Tools
     - Download from https://visualstudio.microsoft.com/downloads/
     - Select "C++ build tools"

### Python: Module Not Found

**Problem:** `ModuleNotFoundError: No module named 'pdf_oxide'`

**Solutions:**

1. **Install package:**
   ```bash
   pip install pdf_oxide
   ```

2. **Check Python version:**
   ```bash
   python --version  # Should be 3.8+
   ```

3. **Verify installation:**
   ```bash
   pip list | grep pdf_oxide
   ```

4. **For development:**
   ```bash
   pip install maturin
   maturin develop --release
   ```

### Python: Binary Incompatibility

**Problem:** `ImportError: dynamic module does not define module export function`

**Solutions:**

1. **Reinstall with correct Python version:**
   ```bash
   pip uninstall pdf_oxide
   pip install pdf_oxide
   ```

2. **Build from source:**
   ```bash
   pip install maturin
   git clone https://github.com/yfedoseev/pdf_oxide
   cd pdf_oxide
   maturin develop --release
   ```

## Runtime Errors

### File Not Found

**Problem:** `Error: Failed to open PDF: No such file or directory`

**Solutions:**

**Rust:**
```rust
use std::path::Path;

let path = Path::new("document.pdf");
if !path.exists() {
    eprintln!("File not found: {:?}", path);
    return Err("File not found".into());
}

let mut doc = PdfDocument::open(path)?;
```

**Python:**
```python
from pathlib import Path

path = Path("document.pdf")
if not path.exists():
    print(f"File not found: {path}")
    raise FileNotFoundError(f"File not found: {path}")

doc = PdfDocument.open(str(path))
```

### Invalid PDF

**Problem:** `Error: Invalid PDF: Missing header`

**Causes:**
- File is corrupted
- File is not a PDF
- File is truncated
- File is encrypted

**Solutions:**

1. **Verify file is PDF:**
   ```bash
   file document.pdf
   # Should show: "PDF document, version X.Y"
   ```

2. **Check file size:**
   ```bash
   ls -lh document.pdf
   # Should be > 0 bytes
   ```

3. **Try opening in PDF viewer:**
   - If Adobe Reader/Preview can't open it, it's corrupted

4. **Check for encryption:**
   ```bash
   pdfinfo document.pdf | grep Encrypted
   ```

   If encrypted, the library doesn't support encrypted PDFs yet.

### Memory Errors

**Problem:** `Error: Out of memory` or process killed

**Causes:**
- PDF is extremely large
- Decompression bomb
- Memory leak

**Solutions:**

1. **Process page by page:**
   ```rust
   // Instead of
   let text = doc.extract_text_all()?;

   // Do this
   for page_num in 0..doc.page_count() {
       let text = doc.extract_text(page_num)?;
       process_page(text);
   }
   ```

2. **Set parser limits:**
   ```rust
   let limits = ParserLimits {
       max_file_size: 100 * 1024 * 1024,  // 100 MB
       ..Default::default()
   };

   let mut doc = PdfDocument::with_limits("large.pdf", limits)?;
   ```

3. **Increase system limits:**
   ```bash
   # Linux
   ulimit -v 8388608  # 8 GB virtual memory
   ```

### Parse Errors

**Problem:** `Error: Parse error at byte 1234: unexpected token`

**Causes:**
- Malformed PDF
- Non-standard PDF structure
- Library bug

**Solutions:**

1. **Try to repair PDF:**
   ```bash
   # Using Ghostscript
   gs -o repaired.pdf -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress input.pdf
   ```

2. **Report issue:**
   - Open issue at https://github.com/yfedoseev/pdf_oxide/issues
   - Include PDF file (if shareable) or anonymized version
   - Include error message and stack trace

3. **Workaround with other tools:**
   ```python
   # Try established PDF library as fallback
   import fitz
   doc = fitz.open("problematic.pdf")
   ```

## Performance Issues

### Slow Text Extraction

**Problem:** Text extraction takes too long

**Diagnosis:**

```rust
use std::time::Instant;

let start = Instant::now();
let text = doc.extract_text(0)?;
let elapsed = start.elapsed();

println!("Extraction took: {:?}", elapsed);
println!("Characters: {}", text.len());
println!("Throughput: {:.2} chars/ms", text.len() as f64 / elapsed.as_millis() as f64);
```

**Expected performance:**
- Simple PDFs: 10-50ms per page
- Complex PDFs: 50-200ms per page

**Solutions:**

1. **Use release build:**
   ```bash
   # Rust
   cargo build --release

   # Python
   pip install pdf_oxide  # Already optimized
   ```

2. **Profile to find bottleneck:**
   ```bash
   cargo install flamegraph
   cargo flamegraph --bin your_program
   ```

3. **Parallel processing:**
   ```rust
   use rayon::prelude::*;

   let texts: Vec<String> = (0..doc.page_count())
       .into_par_iter()
       .map(|page_num| doc.extract_text(page_num).unwrap())
       .collect();
   ```

### High Memory Usage

**Problem:** Process uses too much memory

**Diagnosis:**

```bash
# Linux
/usr/bin/time -v ./your_program

# Look for "Maximum resident set size"
```

**Solutions:**

1. **Stream processing:**
   ```rust
   // Don't accumulate all text
   for page_num in 0..doc.page_count() {
       let text = doc.extract_text(page_num)?;
       write_to_file(text)?;  // Write immediately
   }
   ```

2. **Release document when done:**
   ```rust
   {
       let mut doc = PdfDocument::open("large.pdf")?;
       let text = doc.extract_text(0)?;
       // doc dropped here, memory freed
   }
   ```

3. **Python: Explicit cleanup:**
   ```python
   import gc

   doc = PdfDocument.open("large.pdf")
   text = doc.extract_text(0)
   del doc
   gc.collect()
   ```

## Quality Issues

### Missing Text

**Problem:** Some text is not extracted

**Causes:**
- Text is in images (requires OCR)
- Text uses unsupported fonts
- Text uses custom encodings

**Solutions:**

1. **Check if text is selectable in PDF viewer:**
   - If you can't select text in Adobe Reader, it's likely images

2. **Try different extraction:**
   ```rust
   // Get character-level data
   let chars = doc.extract_characters(0)?;
   for ch in chars {
       println!("Char: '{}' at ({}, {})", ch.text, ch.x, ch.y);
   }
   ```

3. **Use OCR (not yet supported):**
   - Wait for OCR feature (planned for v3.0)
   - Or use Tesseract as preprocessing step

### Incorrect Word Spacing

**Problem:** Words are merged or have extra spaces

**Diagnosis:**
```rust
let text = doc.extract_text(0)?;
println!("Text: {}", text);
// Look for patterns like "helloworld" or "h e l l o"
```

**Solutions:**

1. **Adjust word spacing threshold:**
   ```rust
   let config = TextConfig {
       word_spacing_threshold: 0.3,  // Increase if words merge
       ..Default::default()
   };

   doc.set_text_config(config);
   ```

2. **Report issue:**
   - This shouldn't happen (we've tested extensively)
   - Please report with example PDF

### Bold Detection Issues

**Problem:** Bold text not detected or false positives

**Solutions:**

1. **Enable bold detection:**
   ```rust
   let config = TextConfig {
       detect_bold: true,
       ..Default::default()
   };
   ```

2. **Check character-level data:**
   ```rust
   let chars = doc.extract_characters(0)?;
   for ch in chars.iter().filter(|c| c.is_bold) {
       println!("Bold: '{}'", ch.text);
   }
   ```

### Table Extraction

**Problem:** Tables not properly extracted

**Note:** Table detection is currently disabled (being re-implemented).

**Workarounds:**

1. **Manual parsing:**
   ```python
   text = doc.extract_text(0)
   # Parse text manually to extract table data
   ```

2. **Use specialized tool:**
   ```python
   import alternative PDF library
   with alternative PDF library.open("table.pdf") as pdf:
       table = pdf.pages[0].extract_table()
   ```

## Platform-Specific Issues

### Linux: OpenSSL Errors

**Problem:** `error while loading shared libraries: libssl.so.1.1`

**Solution:**
```bash
# Debian/Ubuntu
sudo apt-get install libssl-dev

# Fedora/RHEL
sudo dnf install openssl-devel
```

### macOS: Permission Denied

**Problem:** `Permission denied` when opening PDF

**Solution:**
```bash
# Check file permissions
ls -l document.pdf

# Fix permissions
chmod 644 document.pdf
```

### Windows: DLL Not Found

**Problem:** `The code execution cannot proceed because X.dll was not found`

**Solutions:**

1. **Install Visual C++ Redistributable:**
   - Download from https://aka.ms/vs/17/release/vc_redist.x64.exe

2. **Add to PATH:**
   ```powershell
   $env:PATH += ";C:\path\to\dlls"
   ```

## Integration Issues

### Flask: File Upload Issues

**Problem:** Uploaded file can't be processed

**Solution:**
```python
from flask import request
import tempfile
import os

@app.route('/extract', methods=['POST'])
def extract():
    file = request.files['file']

    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        doc = PdfDocument.open(tmp_path)
        text = doc.extract_text_all()
        return {'text': text}
    finally:
        os.unlink(tmp_path)  # Clean up
```

### Django: Unicode Errors

**Problem:** `UnicodeEncodeError` when saving extracted text

**Solution:**
```python
# Always use UTF-8
text = doc.extract_text_all()
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write(text)
```

### Jupyter: Kernel Dies

**Problem:** Jupyter kernel crashes when processing large PDFs

**Solution:**
```python
# Process in chunks
doc = PdfDocument.open("large.pdf")

for i in range(0, doc.page_count(), 10):
    # Process 10 pages at a time
    for page_num in range(i, min(i + 10, doc.page_count())):
        text = doc.extract_text(page_num)
        process(text)
```

## Debugging

### Enable Debug Logging

**Rust:**
```rust
env_logger::init();
// Set RUST_LOG=debug when running

let mut doc = PdfDocument::open("document.pdf")?;
```

**Python:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

doc = PdfDocument.open("document.pdf")
```

### Minimal Reproducible Example

When reporting issues, provide:

```rust
// Minimal example that reproduces the issue
use pdf_oxide::PdfDocument;

fn main() {
    let mut doc = PdfDocument::open("problem.pdf").unwrap();
    let text = doc.extract_text(0).unwrap();
    println!("{}", text);
    // Expected: "correct text"
    // Actual: "incorrect text"
}
```

### Collect Diagnostics

```bash
# System info
uname -a

# Rust version
rustc --version
cargo --version

# Python version
python --version
pip show pdf_oxide

# PDF info
pdfinfo document.pdf

# File size
ls -lh document.pdf
```

## Getting Help

### Before Opening Issue

1. Check this troubleshooting guide
2. Search existing issues: https://github.com/yfedoseev/pdf_oxide/issues
3. Try latest version: `cargo update` or `pip install --upgrade pdf_oxide`

### Opening an Issue

Include:

1. **System information:**
   - OS and version
   - Rust/Python version
   - Library version

2. **Minimal reproducible example:**
   - Code that reproduces the issue
   - Sample PDF (if shareable)

3. **Expected vs actual behavior:**
   - What you expected to happen
   - What actually happened

4. **Error messages:**
   - Complete error output
   - Stack traces

5. **Diagnostics:**
   - Run with debug logging
   - Include relevant output

### Community Resources

- **GitHub Issues**: https://github.com/yfedoseev/pdf_oxide/issues
- **GitHub Discussions**: https://github.com/yfedoseev/pdf_oxide/discussions
- **Documentation**: https://docs.rs/pdf_oxide
- **Examples**: https://github.com/yfedoseev/pdf_oxide/tree/main/examples

## Known Limitations

### Not Yet Supported

- **Encrypted PDFs**: Encryption/decryption not implemented
- **OCR**: Scanned documents require external OCR
- **Tables**: Table detection being re-implemented
- **Rotated Text**: Basic support only
- **Vertical Text**: Minimal support
- **PDF Forms (editing)**: Read-only for now
- **Digital Signatures**: Not supported

### Planned Features

See [CHANGELOG.md](../../CHANGELOG.md) for roadmap.

## Next Steps

- **[Quick Start](QUICK_START.md)**: Get started quickly
- **[Advanced Features](ADVANCED_FEATURES.md)**: Learn advanced capabilities
- **[API Documentation](https://docs.rs/pdf_oxide)**: Complete API reference
- **[Examples](../../examples/)**: More code examples

## Still Having Issues?

If this guide doesn't solve your problem:

1. Open an issue: https://github.com/yfedoseev/pdf_oxide/issues/new
2. Start a discussion: https://github.com/yfedoseev/pdf_oxide/discussions/new
3. Check the documentation: https://docs.rs/pdf_oxide

We're here to help! 🚀
