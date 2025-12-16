# PDF Specification Reference

This directory contains the official PDF 1.7 specification (ISO 32000-1:2008) converted to markdown for easy reference during development.

## Files

- **`PDF32000_2008.pdf`** - Original PDF specification (22 MB, 756 pages)
- **`pdf.md`** - Markdown version for quick searching/reading (2.2 MB, 2.1M characters)

## How to Use

This markdown version allows you to quickly search and reference the PDF specification without leaving your editor:

1. **Search for specific topics**: Use your editor's search (`Ctrl+F` or `Cmd+F`)
   - Example: Search for "Tj operator", "Text positioning", "ToUnicode CMap"

2. **Jump to sections**: Use markdown headers to navigate
   - Section 9: Text (text operators, fonts, positioning)
   - Section 7: Syntax (PDF objects, streams, file structure)
   - Section 8: Graphics (coordinate systems, graphics state)

3. **Quick reference during debugging**: Keep this file open while investigating PDF issues

## Key Sections for Text Extraction

When working on text extraction bugs, these sections are most relevant:

### **Section 9.4: Text Objects** (Critical!)
- **9.4.3**: Text-Showing Operators (`Tj`, `TJ`, `'`, `"`)
- **9.4.4**: Text-Positioning Operators (`Td`, `TD`, `Tm`, `T*`)
- Explains how PDFs encode text and positioning

### **Section 9.3: Text State Parameters**
- Font, font size, character spacing, word spacing
- Text rise, horizontal scaling

### **Section 9.7: Composite Fonts**
- **9.7.5**: CMap (Character Map) - for multi-byte encodings
- **9.10.3**: ToUnicode CMaps - converts character codes to Unicode

### **Section 7.3.8: Stream Objects**
- Content streams containing text operators

### **Section 14.8: Structure Hierarchy**
- Tagged PDF structure tree (for reading order)

## Conversion Process

The markdown was generated using leading alternatives:

```bash
leading alternatives.to_markdown('PDF32000_2008.pdf', page_chunks=False)
```

This preserves the structure while making the spec easily searchable in any text editor.

## Source

**Official Adobe PDF Specification**:
- URL: https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf
- Standard: ISO 32000-1:2008 (PDF 1.7)
- License: Freely available from Adobe with ISO permission

## Usage Tips

**Quick searches for common issues**:
- `"Tj operator"` - Basic text showing
- `"TJ operator"` - Text showing with positioning
- `"word spacing"` - Space handling between words
- `"text positioning"` - How text coordinates work
- `"ToUnicode CMap"` - Character code to Unicode mapping
- `"reading order"` - Structure tree reading order

**Understanding our implementation**:
- Compare our TextSpan implementation with Section 9.4.3
- Check text positioning logic against Section 9.4.4
- Validate CMap parsing against Section 9.7.5

## Note

This is the official PDF 1.7 specification. For PDF 2.0 (ISO 32000-2:2020), you would need to obtain the newer specification separately.
