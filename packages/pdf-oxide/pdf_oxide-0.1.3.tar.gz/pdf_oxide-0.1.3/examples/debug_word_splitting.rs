use pdf_oxide::PdfDocument;

fn main() {
    let mut doc = PdfDocument::open("../pdf_oxide_tests/pdfs/academic/arxiv_2510.21165v1.pdf")
        .expect("Failed to open arXiv PDF");

    let spans = doc.extract_spans(0).expect("Failed to extract spans");

    println!("Total spans: {}", spans.len());
    println!("\nFirst 30 spans:");
    for (i, span) in spans.iter().take(30).enumerate() {
        println!("{:3}. '{}' (font: {}, size: {})", i, span.text, span.font_name, span.font_size);
    }

    // Look for "various" or "var ious"
    println!("\n\nSearching for 'various' patterns:");
    let text: String = spans.iter().map(|s| s.text.as_str()).collect();

    if text.contains("var ious") {
        println!("❌ Found 'var ious' (split)");
    }
    if text.contains("various") {
        println!("✅ Found 'various' (correct)");
    }

    // Show context around "var"
    if let Some(idx) = text.find("var") {
        let start = idx.saturating_sub(20);
        let end = (idx + 30).min(text.len());
        println!("\nContext: '{}'", &text[start..end]);
    }
}
