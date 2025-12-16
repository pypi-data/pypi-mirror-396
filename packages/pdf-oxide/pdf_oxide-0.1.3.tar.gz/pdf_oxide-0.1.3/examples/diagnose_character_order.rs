//! Diagnostic tool to examine character extraction order from PDF.
//!
//! This program extracts characters from a PDF page and analyzes:
//! 1. The order they appear in the content stream (extraction order)
//! 2. Their spatial positions (X, Y coordinates)
//! 3. Comparison with correct left-to-right, top-to-bottom order
//!
//! Usage: cargo run --example diagnose_character_order <pdf_path> [page_num] [max_chars]

use pdf_oxide::{PdfDocument, error::Result};

fn main() -> Result<()> {
    env_logger::init();

    let args: Vec<String> = std::env::args().collect();

    if args.len() < 2 {
        eprintln!("Usage: {} <pdf_path> [page_num] [max_chars]", args[0]);
        eprintln!("\nExample:");
        eprintln!(
            "  cargo run --example diagnose_character_order ../pdf_oxide_tests/pdfs/academic/arxiv_2510.21165v1.pdf"
        );
        std::process::exit(1);
    }

    let pdf_path = &args[1];
    let page_num = args.get(2).and_then(|s| s.parse::<u32>().ok()).unwrap_or(0);
    let max_chars = args
        .get(3)
        .and_then(|s| s.parse::<usize>().ok())
        .unwrap_or(200);

    println!("=== Diagnosing Character Order ===");
    println!("PDF: {}", pdf_path);
    println!("Page: {}", page_num);
    println!();

    // Open PDF and extract characters
    let mut doc = PdfDocument::open(pdf_path)?;
    let chars = doc.extract_spans(page_num as usize)?;

    println!("Total characters extracted: {}", chars.len());
    println!();

    // Show first N characters in EXTRACTION ORDER
    println!("{}", "=".repeat(80));
    println!("EXTRACTION ORDER (as they appear in PDF content stream):");
    println!("{}", "=".repeat(80));

    for (i, ch) in chars.iter().take(max_chars).enumerate() {
        let display_char = if ch.text.chars().all(|c| c.is_ascii_graphic() || c == ' ') {
            format!("'{}'", ch.text)
        } else {
            format!("[{:?}]", ch.text)
        };
        println!(
            "{:3}: {} at X={:6.1} Y={:6.1} size={:.1}",
            i, display_char, ch.bbox.x, ch.bbox.y, ch.font_size
        );
    }
    println!();

    // Sort by spatial position (Y descending, then X ascending)
    // In PDF coordinates, larger Y = higher on page
    let mut sorted_chars: Vec<_> = chars.iter().take(max_chars).collect();
    sorted_chars.sort_by(|a, b| {
        // Primary: Y coordinate (descending - larger Y is higher on page)
        match b.bbox.y.partial_cmp(&a.bbox.y) {
            Some(std::cmp::Ordering::Equal) | None => {
                // Secondary: X coordinate (ascending - left to right)
                a.bbox
                    .x
                    .partial_cmp(&b.bbox.x)
                    .unwrap_or(std::cmp::Ordering::Equal)
            },
            other => other.unwrap(),
        }
    });

    println!("{}", "=".repeat(80));
    println!("SPATIAL ORDER (top-to-bottom, left-to-right):");
    println!("{}", "=".repeat(80));

    for (i, ch) in sorted_chars.iter().enumerate() {
        let display_char = if ch.text.chars().all(|c| c.is_ascii_graphic() || c == ' ') {
            format!("'{}'", ch.text)
        } else {
            format!("[{:?}]", ch.text)
        };
        println!(
            "{:3}: {} at X={:6.1} Y={:6.1} size={:.1}",
            i, display_char, ch.bbox.x, ch.bbox.y, ch.font_size
        );
    }
    println!();

    // Reconstruct text in both orders
    let extraction_order_text: String = chars
        .iter()
        .take(max_chars)
        .map(|ch| ch.text.as_str())
        .collect();
    let spatial_order_text: String = sorted_chars.iter().map(|ch| ch.text.as_str()).collect();

    println!("{}", "=".repeat(80));
    println!("TEXT COMPARISON:");
    println!("{}", "=".repeat(80));
    println!("\nExtraction order text (first {} chars):", max_chars);
    println!("{}", &extraction_order_text[..extraction_order_text.len().min(200)]);
    println!();
    println!("Spatial order text (first {} chars):", max_chars);
    println!("{}", &spatial_order_text[..spatial_order_text.len().min(200)]);
    println!();

    // Check if they differ
    if extraction_order_text != spatial_order_text {
        println!("❌ ORDER MISMATCH DETECTED!");
        println!("Characters in content stream are NOT in spatial left-to-right order.");
        println!("This is the ROOT CAUSE of column mixing.");

        // Find first difference
        for (i, (c1, c2)) in extraction_order_text
            .chars()
            .zip(spatial_order_text.chars())
            .enumerate()
        {
            if c1 != c2 {
                println!("\nFirst difference at position {}:", i);
                println!("  Extraction order: '{}'", c1);
                println!("  Spatial order:    '{}'", c2);
                break;
            }
        }
    } else {
        println!("✅ Orders match - content stream is already in spatial order");
    }
    println!();

    // Analyze Y-coordinate distribution to detect columns
    println!("{}", "=".repeat(80));
    println!("Y-COORDINATE ANALYSIS:");
    println!("{}", "=".repeat(80));

    // Group characters by Y coordinate (within 5 units tolerance)
    use std::collections::HashMap;
    let mut y_groups: HashMap<i32, Vec<&pdf_oxide::layout::TextSpan>> = HashMap::new();

    for ch in chars.iter().take(max_chars) {
        let y_rounded = (ch.bbox.y / 5.0).round() as i32 * 5;
        y_groups.entry(y_rounded).or_default().push(ch);
    }

    println!("\nFound {} distinct Y positions (±5 units)", y_groups.len());
    println!("\nLines with wide X range (potential multi-column):");

    let mut y_sorted: Vec<_> = y_groups.iter().collect();
    y_sorted.sort_by(|a, b| b.0.cmp(a.0)); // Sort by Y descending

    for (y, group) in y_sorted.iter().take(10) {
        let x_values: Vec<f32> = group.iter().map(|ch| ch.bbox.x).collect();
        let x_min = x_values.iter().fold(f32::INFINITY, |a, &b| a.min(b));
        let x_max = x_values.iter().fold(f32::NEG_INFINITY, |a, &b| a.max(b));
        let x_range = x_max - x_min;

        // If X range is very large, likely multi-column
        if x_range > 200.0 {
            let mut sorted_group = group.to_vec();
            sorted_group.sort_by(|a, b| a.bbox.x.partial_cmp(&b.bbox.x).unwrap());
            let text: String = sorted_group.iter().map(|ch| ch.text.as_str()).collect();

            println!(
                "  Y={:6.1}: X range {:6.1} - {:6.1} (width: {:6.1})",
                y, x_min, x_max, x_range
            );
            println!("            Text: {}", if text.len() > 80 { &text[..80] } else { &text });
        }
    }

    Ok(())
}
