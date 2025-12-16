//! Debug clustering behavior for the problematic arXiv PDF.
//!
//! This program enables detailed logging to trace word clustering
//! for the line where column mixing occurs (Y≈1535).
//!
//! Usage: RUST_LOG=warn cargo run --example debug_clustering
use pdf_oxide::{PdfDocument, error::Result};

fn main() -> Result<()> {
    // Initialize logger
    env_logger::init();

    let pdf_path = "../pdf_oxide_tests/pdfs/academic/arxiv_2510.21165v1.pdf";

    println!("=== Debug Clustering ===");
    println!("PDF: {}", pdf_path);
    println!("Looking for column mixing at Y≈1535");
    println!();
    println!("Watch for debug logs marked with 🔍");
    println!();

    let mut doc = PdfDocument::open(pdf_path)?;

    // Extract and convert - this will trigger the debug logging
    let _chars = doc.extract_spans(0)?;

    // Now convert to markdown which will cluster characters
    use pdf_oxide::converters::{ConversionOptions, MarkdownConverter};
    let converter = MarkdownConverter::new();
    let options = ConversionOptions {
        detect_headings: false,
        ..Default::default()
    };

    // Get spans for conversion
    let spans = doc.extract_spans(0)?;
    let result = converter.convert_page_from_spans(&spans, &options)?;

    println!("\n=== Result (first 600 chars) ===");
    println!("{}", &result[..result.len().min(600)]);

    // Check for mixing
    if result.contains("Tmheet") || result.contains("hfion") {
        println!("\n❌ Column mixing detected");
    } else {
        println!("\n✅ No column mixing found");
    }

    Ok(())
}
