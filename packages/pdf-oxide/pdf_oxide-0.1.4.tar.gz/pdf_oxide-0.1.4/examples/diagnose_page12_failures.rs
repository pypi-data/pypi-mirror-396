#!/usr/bin/env cargo run --release --example

//! Diagnostic tool to analyze replacement character failures on page 12
//! of arxiv_2510.25760v1.pdf

use pdf_oxide::PdfDocument;
use pdf_oxide::converters::ConversionOptions;
use std::collections::HashMap;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let pdf_path = "../pdf_oxide_tests/pdfs/academic/arxiv_2510.25760v1.pdf";
    let page_num = 12;

    println!("{}", "=".repeat(80));
    println!("DIAGNOSING PAGE {} REPLACEMENT CHARACTER FAILURES", page_num);
    println!("PDF: {}", pdf_path);
    println!("{}", "=".repeat(80));
    println!();

    let mut doc = PdfDocument::open(pdf_path)?;

    // Convert the page
    let options = ConversionOptions::default();
    let markdown = doc.to_markdown(page_num, &options)?;

    // Find all replacement characters
    let mut replacement_positions = Vec::new();
    for (pos, ch) in markdown.char_indices() {
        if ch == '\u{FFFD}' {
            replacement_positions.push(pos);
        }
    }

    println!("Total replacement characters: {}", replacement_positions.len());
    println!();

    // Show context for each replacement char
    println!("REPLACEMENT CHARACTER CONTEXTS:");
    println!("{}", "-".repeat(80));

    for (i, pos) in replacement_positions.iter().take(20).enumerate() {
        // Use char_indices to find safe boundaries
        let chars: Vec<(usize, char)> = markdown.char_indices().collect();

        // Find the char index that corresponds to this byte position
        if let Some(char_idx) = chars.iter().position(|(byte_pos, _)| *byte_pos == *pos) {
            let start_char_idx = char_idx.saturating_sub(40);
            let end_char_idx = (char_idx + 40).min(chars.len());

            let start_byte = chars.get(start_char_idx).map(|(b, _)| *b).unwrap_or(0);
            let end_byte = chars
                .get(end_char_idx)
                .map(|(b, _)| *b)
                .unwrap_or(markdown.len());

            let context = &markdown[start_byte..end_byte];
            println!("{}. Position {}: ...{}...", i + 1, pos, context);
            println!();
        }
    }

    if replacement_positions.len() > 20 {
        println!("... and {} more", replacement_positions.len() - 20);
        println!();
    }

    // Analyze character distribution
    let total_chars = markdown.chars().count();
    let ascii_chars = markdown.chars().filter(|c| c.is_ascii()).count();
    let unicode_non_ascii = markdown
        .chars()
        .filter(|c| !c.is_ascii() && *c != '\u{FFFD}')
        .count();
    let replacement_chars = replacement_positions.len();

    println!("{}", "=".repeat(80));
    println!("CHARACTER DISTRIBUTION:");
    println!("  Total: {} chars", total_chars);
    println!(
        "  ASCII: {} ({:.1}%)",
        ascii_chars,
        (ascii_chars as f64 / total_chars as f64) * 100.0
    );
    println!(
        "  Unicode (non-ASCII): {} ({:.1}%)",
        unicode_non_ascii,
        (unicode_non_ascii as f64 / total_chars as f64) * 100.0
    );
    println!(
        "  Replacement (�): {} ({:.1}%)",
        replacement_chars,
        (replacement_chars as f64 / total_chars as f64) * 100.0
    );
    println!();

    // Extract spans to analyze character codes
    println!("{}", "=".repeat(80));
    println!("ANALYZING CHARACTER CODES ON PAGE {}:", page_num);
    println!("{}", "-".repeat(80));

    let spans = doc.extract_spans(page_num)?;
    let mut char_code_failures = HashMap::new();

    for span in &spans {
        for ch in span.text.chars() {
            if ch == '\u{FFFD}' {
                // This is a replacement char - we need to find the original code
                // Unfortunately at this point it's already been replaced
                *char_code_failures.entry("FFFD".to_string()).or_insert(0) += 1;
            }
        }
    }

    println!("Found {} spans on page {}", spans.len(), page_num);

    // Count spans with replacement chars
    let spans_with_issues: Vec<_> = spans
        .iter()
        .filter(|s| s.text.contains('\u{FFFD}'))
        .collect();

    println!("Spans containing � characters: {}", spans_with_issues.len());
    println!();

    if !spans_with_issues.is_empty() {
        println!("PROBLEMATIC SPANS (first 10):");
        for (i, span) in spans_with_issues.iter().take(10).enumerate() {
            println!("  {}. Font: '{}', Text: {:?}", i + 1, span.font_name, span.text);
        }
        println!();
    }

    // Get unique font names used on this page
    let mut font_names: Vec<_> = spans.iter().map(|s| s.font_name.as_str()).collect();
    font_names.sort();
    font_names.dedup();

    println!("{}", "=".repeat(80));
    println!("FONTS USED ON PAGE {}:", page_num);
    for font in &font_names {
        let span_count = spans.iter().filter(|s| s.font_name == *font).count();
        println!("  - '{}' ({} spans)", font, span_count);
    }
    println!();

    // Check which fonts are producing replacement chars
    let mut fonts_with_issues = HashMap::new();
    for span in spans_with_issues {
        *fonts_with_issues
            .entry(span.font_name.as_str())
            .or_insert(0) += 1;
    }

    if !fonts_with_issues.is_empty() {
        println!("{}", "=".repeat(80));
        println!("FONTS PRODUCING � CHARACTERS:");
        let mut sorted_fonts: Vec<_> = fonts_with_issues.iter().collect();
        sorted_fonts.sort_by_key(|(_, count)| std::cmp::Reverse(**count));

        for (font, count) in sorted_fonts {
            println!("  - '{}': {} spans with �", font, count);
        }
        println!();
    }

    println!("{}", "=".repeat(80));
    println!("RECOMMENDATION:");
    println!();
    println!("Next steps:");
    println!("1. Investigate the specific fonts producing � chars");
    println!("2. Check if these fonts have ToUnicode CMaps");
    println!("3. Analyze character codes in these fonts");
    println!("4. Add missing character mappings to Phase 7A fallback");
    println!();

    Ok(())
}
