#!/usr/bin/env cargo run --release --example

//! Deep analysis of font 'F1' from page 12 to understand Type 3 font structure

use pdf_oxide::PdfDocument;
use std::collections::HashMap;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let pdf_path = "../pdf_oxide_tests/pdfs/academic/arxiv_2510.25760v1.pdf";
    let page_num = 12;

    println!("{}", "=".repeat(80));
    println!("FONT 'F1' DEEP ANALYSIS - Page {}", page_num);
    println!("PDF: {}", pdf_path);
    println!("{}", "=".repeat(80));
    println!();

    let mut doc = PdfDocument::open(pdf_path)?;

    // Get font information from the page
    println!("Step 1: Extracting font details from page resources...");
    println!();

    // We need to access the font dictionary directly
    // This requires accessing internal structures
    let spans = doc.extract_spans(page_num)?;

    println!("Found {} total spans on page {}", spans.len(), page_num);
    println!();

    // Find all F1 spans
    let f1_spans: Vec<_> = spans.iter().filter(|s| s.font_name == "F1").collect();

    println!("Found {} spans using font 'F1'", f1_spans.len());
    println!();

    // Analyze character codes in F1 spans
    println!("{}", "=".repeat(80));
    println!("CHARACTER CODE ANALYSIS");
    println!("{}", "-".repeat(80));
    println!();

    let mut char_codes: HashMap<u8, usize> = HashMap::new();

    for span in &f1_spans {
        // The text is already decoded, but we can look at the bytes
        for ch in span.text.chars() {
            if ch == '\u{FFFD}' {
                // This is a replacement char - track it
                // Note: At this point we've lost the original char code
                continue;
            }
            // Track visible characters
            if ch.is_ascii() && !ch.is_control() {
                *char_codes.entry(ch as u8).or_insert(0) += 1;
            }
        }
    }

    println!("Character codes found in F1 spans:");
    let mut sorted_codes: Vec<_> = char_codes.iter().collect();
    sorted_codes.sort_by_key(|(code, _)| **code);

    for (code, count) in sorted_codes.iter().take(20) {
        println!("  0x{:02X} ({}): {} occurrences", code, **code as char, count);
    }
    println!();

    // Show sample spans
    println!("{}", "=".repeat(80));
    println!("SAMPLE F1 SPANS (first 5)");
    println!("{}", "-".repeat(80));
    println!();

    for (i, span) in f1_spans.iter().take(5).enumerate() {
        println!("Span {}:", i + 1);
        println!("  Position: ({:.2}, {:.2})", span.bbox.x, span.bbox.y);
        println!("  Font size: {:.2}", span.font_size);
        println!("  Text length: {} chars", span.text.len());
        println!(
            "  Text (first 100 chars): {:?}",
            span.text.chars().take(100).collect::<String>()
        );

        let replacement_count = span.text.chars().filter(|&c| c == '\u{FFFD}').count();
        println!("  Replacement chars: {}", replacement_count);
        println!();
    }

    println!("{}", "=".repeat(80));
    println!("RECOMMENDATIONS");
    println!("{}", "-".repeat(80));
    println!();
    println!("To fix Font 'F1' issues, we need to:");
    println!("1. Access the font dictionary for font 'F1'");
    println!("2. Check /Subtype to confirm if it's Type 3");
    println!("3. If Type 3, parse /CharProcs for glyph definitions");
    println!("4. Extract /Encoding to map char codes to glyph names");
    println!("5. Map glyph names to Unicode using Adobe Glyph List");
    println!();
    println!("This requires extending PdfDocument API to expose font dictionaries.");
    println!();

    Ok(())
}
