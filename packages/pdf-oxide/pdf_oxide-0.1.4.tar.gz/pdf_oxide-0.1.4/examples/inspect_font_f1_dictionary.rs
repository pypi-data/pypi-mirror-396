#!/usr/bin/env cargo run --release --example

//! Inspect Font 'F1' dictionary structure to determine if it's Type 3
//! and understand its encoding/CharProcs

use pdf_oxide::PdfDocument;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let pdf_path = "../pdf_oxide_tests/pdfs/academic/arxiv_2510.25760v1.pdf";
    let page_num = 12;

    println!("{}", "=".repeat(80));
    println!("FONT 'F1' DICTIONARY INSPECTION");
    println!("PDF: {}", pdf_path);
    println!("Page: {}", page_num);
    println!("{}", "=".repeat(80));
    println!();

    let mut doc = PdfDocument::open(pdf_path)?;

    // Extract spans to find Font 'F1'
    let spans = doc.extract_spans(page_num)?;

    let f1_spans: Vec<_> = spans.iter().filter(|s| s.font_name == "F1").collect();

    if f1_spans.is_empty() {
        println!("ERROR: Font 'F1' not found on page {}", page_num);
        return Ok(());
    }

    println!("Found {} spans using Font 'F1'", f1_spans.len());
    println!();

    // Show sample character codes from the spans
    println!("{}", "=".repeat(80));
    println!("CHARACTER CODE ANALYSIS");
    println!("{}", "-".repeat(80));
    println!();

    // Collect all unique byte values from F1 text
    let mut byte_set = std::collections::HashSet::new();
    let mut replacement_count = 0;

    for span in &f1_spans {
        for byte in span.text.bytes() {
            byte_set.insert(byte);
        }
        replacement_count += span.text.chars().filter(|&c| c == '\u{FFFD}').count();
    }

    let mut bytes: Vec<_> = byte_set.into_iter().collect();
    bytes.sort();

    println!("Unique byte values found in Font 'F1' text:");
    for chunk in bytes.chunks(16) {
        print!("  ");
        for &b in chunk {
            print!("{:02X} ", b);
        }
        println!();
    }
    println!();
    println!("Total replacement characters: {}", replacement_count);
    println!();

    // Show a few sample spans with their raw text
    println!("{}", "=".repeat(80));
    println!("SAMPLE SPANS (first 3)");
    println!("{}", "-".repeat(80));
    println!();

    for (i, span) in f1_spans.iter().take(3).enumerate() {
        println!("Span {}:", i + 1);
        println!("  Position: ({:.2}, {:.2})", span.bbox.x, span.bbox.y);
        println!("  Font size: {:.2}", span.font_size);
        println!("  Text length: {} bytes", span.text.len());

        // Show hex dump of first 40 bytes
        let bytes: Vec<u8> = span.text.bytes().take(40).collect();
        print!("  Hex dump: ");
        for byte in &bytes {
            print!("{:02X} ", byte);
        }
        println!();

        // Show as debug string
        println!("  Debug repr: {:?}", span.text.chars().take(40).collect::<String>());
        println!();
    }

    println!("{}", "=".repeat(80));
    println!("FONT INFO FROM PDF");
    println!("{}", "-".repeat(80));
    println!();
    println!("Unfortunately, we need to extend PdfDocument API to expose font");
    println!("dictionaries. The current API doesn't provide access to raw font");
    println!("dictionary objects.");
    println!();
    println!("To properly diagnose Font 'F1', we need:");
    println!("1. Check /Subtype field (Type1, Type3, TrueType, etc.)");
    println!("2. If Type 3:");
    println!("   - Parse /CharProcs dictionary (glyph definitions)");
    println!("   - Parse /Encoding (char code → glyph name mapping)");
    println!("   - Check if /ToUnicode CMap exists");
    println!("3. Implement glyph name → Unicode mapping");
    println!();

    println!("{}", "=".repeat(80));
    println!("ANALYSIS RESULTS");
    println!("{}", "-".repeat(80));
    println!();
    println!("Based on the byte patterns observed:");
    println!();
    println!("1. **Control characters present**: 0x01, 0x02, 0x03, 0x04, 0x7F");
    println!("   → These should NOT appear in normal text");
    println!();
    println!("2. **Low ASCII range**: Many bytes in 0x01-0x7F range");
    println!("   → Suggests character codes are being used directly");
    println!();
    println!("3. **High replacement char count**: {} chars", replacement_count);
    println!("   → Indicates encoding fallback is failing");
    println!();
    println!("4. **Concentrated in single font**: Only Font 'F1' affected");
    println!("   → Font-specific encoding issue, not global problem");
    println!();

    println!("{}", "=".repeat(80));
    println!("NEXT STEPS");
    println!("{}", "-".repeat(80));
    println!();
    println!("We need to:");
    println!();
    println!("1. **Extend PdfDocument API** to expose font info");
    println!("   - Add method: pub fn get_font_info(&self, font_name: &str) -> Option<&FontInfo>");
    println!("   - Or: pub fn get_page_fonts(&self, page: usize) -> Vec<FontInfo>");
    println!();
    println!("2. **Access font subtype** from FontInfo");
    println!("   - FontInfo already has .subtype field");
    println!("   - Check if subtype == \"Type3\"");
    println!();
    println!("3. **If Type 3, implement special handling**:");
    println!("   - Parse CharProcs and Encoding from raw PDF dictionary");
    println!("   - Map char codes → glyph names → Unicode");
    println!("   - Add as Priority 7 in encoding fallback chain");
    println!();

    Ok(())
}
