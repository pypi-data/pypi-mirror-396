use pdf_oxide::PdfDocument;

fn main() {
    let mut doc = PdfDocument::open("../pdf_oxide_tests/pdfs/diverse/EU_GDPR_Regulation.pdf")
        .expect("Failed to open GDPR PDF");

    let spans = doc.extract_spans(0).expect("Failed to extract spans");

    let text: String = spans.iter().map(|s| s.text.as_str()).collect();

    let ascii_count = text.chars().filter(|c| c.is_ascii()).count();
    let total_count = text.chars().count();
    let ascii_ratio = ascii_count as f64 / total_count as f64;

    println!("Total chars: {}", total_count);
    println!("ASCII chars: {}", ascii_count);
    println!("ASCII ratio: {:.1}%", ascii_ratio * 100.0);

    // Show first 500 chars
    println!("\nFirst 500 chars:");
    println!("{}", &text[..500.min(text.len())]);

    // Check for non-ASCII
    let non_ascii: Vec<char> = text.chars().filter(|c| !c.is_ascii()).take(20).collect();
    if non_ascii.is_empty() {
        println!("\n❌ No non-ASCII characters found");
        println!("This PDF appears to be entirely ASCII English text.");
        println!("The test expectation may need adjustment.");
    } else {
        println!("\n✅ Found {} non-ASCII chars: {:?}", non_ascii.len(), non_ascii);
    }
}
