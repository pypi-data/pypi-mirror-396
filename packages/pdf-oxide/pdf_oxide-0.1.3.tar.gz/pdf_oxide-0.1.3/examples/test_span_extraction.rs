use pdf_oxide::{PdfDocument, error::Result};

fn main() -> Result<()> {
    env_logger::init();

    let pdf_path = "../pdf_oxide_tests/pdfs/academic/arxiv_2510.21165v1.pdf";

    println!("Opening PDF: {}", pdf_path);
    let mut doc = PdfDocument::open(pdf_path)?;

    println!("\n=== Testing TextSpan-based extraction (PDF spec compliant) ===");
    let spans = doc.extract_spans(0)?;

    println!("Extracted {} text spans", spans.len());

    // Show first 30 spans to see the text structure
    println!("\nFirst 30 spans:");
    for (i, span) in spans.iter().take(30).enumerate() {
        println!(
            "{:3}: [x:{:6.1}, y:{:6.1}, w:{:6.1}, h:{:5.1}] \"{}\"",
            i,
            span.bbox.x,
            span.bbox.y,
            span.bbox.width,
            span.bbox.height,
            span.text.chars().take(50).collect::<String>()
        );
    }

    // Check for column mixing patterns
    let all_text = spans
        .iter()
        .map(|s| s.text.as_str())
        .collect::<Vec<_>>()
        .join(" ");

    println!("\n=== Checking for column mixing ===");
    if all_text.contains("Tmheet") || all_text.contains("hfion") {
        println!("❌ Column mixing STILL PRESENT");

        // Find where it occurs
        for (i, span) in spans.iter().enumerate() {
            if span.text.contains("Tmheet") || span.text.contains("hfion") {
                println!("Found at span {}: \"{}\"", i, span.text);
            }
        }
    } else {
        println!("✅ No column mixing detected");
    }

    // Look for expected words that should appear separately
    let has_methods = all_text.contains("methods") || all_text.contains("method");
    let has_financial = all_text.contains("financial") || all_text.contains("Financial");
    let has_the = all_text.contains("The ") || all_text.contains("the ");

    println!("\n=== Content validation ===");
    println!("Contains 'methods': {}", has_methods);
    println!("Contains 'financial': {}", has_financial);
    println!("Contains 'The': {}", has_the);

    // Show a sample of continuous text
    println!("\n=== Sample text (first 500 chars) ===");
    let sample: String = all_text.chars().take(500).collect();
    println!("{}", sample);

    Ok(())
}
