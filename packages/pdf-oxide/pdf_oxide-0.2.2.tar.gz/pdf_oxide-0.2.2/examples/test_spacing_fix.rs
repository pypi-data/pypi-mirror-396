//! Test spacing fix on problematic PDFs
//!
//! This example tests the Tc/Tw spacing fix on PDFs that previously
//! showed character spacing issues.

use pdf_oxide::document::PdfDocument;
use std::env;
use std::process;

fn main() {
    // Get PDF path from command line or use default
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        eprintln!("Usage: {} <pdf_file>", args[0]);
        eprintln!("\nTests text extraction on problematic PDFs to verify spacing fix.");
        process::exit(1);
    }

    let pdf_path = &args[1];

    println!("Testing spacing fix on: {}", pdf_path);
    println!("{}", "=".repeat(80));

    // Open PDF
    let mut doc = match PdfDocument::open(pdf_path) {
        Ok(doc) => doc,
        Err(e) => {
            eprintln!("Error opening PDF: {}", e);
            process::exit(1);
        },
    };

    let page_count = match doc.page_count() {
        Ok(count) => count,
        Err(e) => {
            eprintln!("Error getting page count: {}", e);
            process::exit(1);
        },
    };

    println!("PDF opened successfully");
    println!("Number of pages: {}", page_count);
    println!();

    // Extract text from first 3 pages using spans mode
    let pages_to_test = page_count.min(3);

    for page_num in 0..pages_to_test {
        println!("Page {}:", page_num + 1);
        println!("{}", "-".repeat(80));

        match doc.extract_spans(page_num) {
            Ok(spans) => {
                if spans.is_empty() {
                    println!("  (no text spans extracted)");
                } else {
                    println!("  Extracted {} spans", spans.len());
                    println!();

                    // Show first 20 spans to check for spacing issues
                    let show_count = spans.len().min(20);
                    for (i, span) in spans.iter().take(show_count).enumerate() {
                        println!("  Span {}: '{}'", i + 1, span.text);

                        // Highlight potential issues
                        if span.text.contains(" ") && span.text.len() < 10 {
                            // Short text with spaces might indicate spacing issue
                            let char_count =
                                span.text.chars().filter(|c| !c.is_whitespace()).count();
                            let space_count =
                                span.text.chars().filter(|c| c.is_whitespace()).count();
                            if space_count > char_count / 2 {
                                println!(
                                    "    ⚠️  WARNING: High space ratio ({}:{}) - possible spacing issue",
                                    space_count, char_count
                                );
                            }
                        }
                    }

                    if spans.len() > show_count {
                        println!("  ... and {} more spans", spans.len() - show_count);
                    }
                }
            },
            Err(e) => {
                eprintln!("  Error extracting text: {}", e);
            },
        }
        println!();
    }

    // Also extract full text to see the merged result
    println!("Full Text Extraction (first page):");
    println!("{}", "=".repeat(80));
    match doc.extract_text(0) {
        Ok(text) => {
            let preview_len = text.len().min(500);
            println!("{}", &text[..preview_len]);
            if text.len() > preview_len {
                println!("\n... (truncated, total {} chars)", text.len());
            }

            // Check for common spacing issues
            let patterns = [
                ("F i s c a l", "Should be: Fiscal"),
                ("Y e a r", "Should be: Year"),
                ("C o m m e r c e", "Should be: Commerce"),
            ];

            println!("\n{}", "-".repeat(80));
            println!("Checking for known spacing issues:");
            for (pattern, expected) in &patterns {
                if text.contains(pattern) {
                    println!("  ❌ FOUND ISSUE: '{}' ({})", pattern, expected);
                } else {
                    println!("  ✅ OK: Pattern '{}' not found", pattern);
                }
            }
        },
        Err(e) => {
            eprintln!("Error extracting full text: {}", e);
        },
    }
}
