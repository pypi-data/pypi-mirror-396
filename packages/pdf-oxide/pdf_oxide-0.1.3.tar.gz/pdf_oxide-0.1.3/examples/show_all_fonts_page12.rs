#!/usr/bin/env cargo run --release --example

//! Show all fonts used on page 12 with their subtypes

use pdf_oxide::PdfDocument;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::init();

    let pdf_path = "../pdf_oxide_tests/pdfs/academic/arxiv_2510.25760v1.pdf";
    let page_num = 12;

    println!("{}", "=".repeat(80));
    println!("ALL FONTS ON PAGE {}", page_num);
    println!("PDF: {}", pdf_path);
    println!("{}", "=".repeat(80));
    println!();

    let mut doc = PdfDocument::open(pdf_path)?;

    // Extract spans to find all fonts used
    let spans = doc.extract_spans(page_num)?;

    let mut font_names: std::collections::HashSet<String> = std::collections::HashSet::new();
    for span in &spans {
        font_names.insert(span.font_name.clone());
    }

    let mut font_names: Vec<_> = font_names.into_iter().collect();
    font_names.sort();

    println!("Fonts found on page {}:", page_num);
    for (i, font) in font_names.iter().enumerate() {
        let span_count = spans.iter().filter(|s| s.font_name == *font).count();

        // Count replacement chars for this font
        let replacement_count: usize = spans
            .iter()
            .filter(|s| s.font_name == *font)
            .map(|s| s.text.chars().filter(|&c| c == '\u{FFFD}').count())
            .sum();

        let has_issues = if replacement_count > 0 {
            " ⚠️ PROBLEMATIC"
        } else {
            ""
        };

        println!(
            "{}. '{}' - {} spans, {} replacement chars{}",
            i + 1,
            font,
            span_count,
            replacement_count,
            has_issues
        );
    }
    println!();

    println!("{}", "=".repeat(80));
    println!("NOTE: Font subtype information is logged during font loading.");
    println!("Run with RUST_LOG=pdf_oxide=warn to see Type 3 font warnings.");
    println!("{}", "=".repeat(80));

    Ok(())
}
