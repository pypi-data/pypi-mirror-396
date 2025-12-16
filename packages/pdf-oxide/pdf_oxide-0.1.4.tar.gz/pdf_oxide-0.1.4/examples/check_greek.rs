use pdf_oxide::PdfDocument;

fn main() {
    let mut doc = PdfDocument::open("../pdf_oxide_tests/pdfs/academic/arxiv_2510.21165v1.pdf")
        .expect("Failed to open academic PDF");

    let spans = doc.extract_spans(0).expect("Failed to extract spans");

    let text: String = spans.iter().map(|s| s.text.as_str()).collect();

    println!("Total text length: {} chars", text.len());

    // Check for Greek letters
    let greek_letters = [
        'ρ', 'σ', 'μ', 'α', 'β', 'γ', 'δ', 'ε', 'θ', 'λ', 'π', 'τ', 'φ', 'χ', 'ψ', 'ω',
    ];

    let mut found = Vec::new();
    for &letter in &greek_letters {
        if text.contains(letter) {
            found.push(letter);
        }
    }

    println!("Greek letters found: {:?}", found);

    // Search for "Pearson" to see context
    if let Some(idx) = text.find("Pearson") {
        let start = idx.saturating_sub(20);
        let end = (idx + 100).min(text.len());
        println!("\nContext around 'Pearson':");
        println!("{}", &text[start..end]);
    }

    // Search for lowercase rho
    if text.contains('ρ') {
        println!("\n✅ Found ρ (rho)");
    } else {
        println!("\n❌ No ρ (rho) found");
        // Check what's there instead
        if let Some(idx) = text.find("Pearson") {
            let start = idx;
            let end = (idx + 50).min(text.len());
            println!("After 'Pearson': {:?}", &text[start..end]);
        }
    }
}
