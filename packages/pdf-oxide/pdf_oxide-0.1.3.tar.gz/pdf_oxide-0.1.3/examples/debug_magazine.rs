use pdf_oxide::PdfDocument;

fn main() {
    let mut doc =
        PdfDocument::open("../pdf_oxide_tests/pdfs/diverse/Magazine_Scientific_American_1845.pdf")
            .expect("Failed to open magazine PDF");

    let spans = doc.extract_spans(0).expect("Failed to extract spans");

    println!("Total spans: {}", spans.len());

    // Build full text
    let text: String = spans.iter().map(|s| s.text.as_str()).collect();

    // Check for problematic patterns
    if text.contains("Hlarly") {
        println!("❌ Found 'Hlarly' (should be 'Particularly')");
    }
    if text.contains("Particularly") {
        println!("✅ Found 'Particularly' (correct)");
    }

    if text.contains("lculated") {
        println!("❌ Found 'lculated' (should be 'calculated')");
    }
    if text.contains("calculated") {
        println!("✅ Found 'calculated' (correct)");
    }

    if text.contains("volum@s") {
        println!("❌ Found 'volum@s' (should be 'volume')");
    }

    // Show spans with "Particularly" or "Hlarly"
    println!("\nSpans containing 'arly' or 'Particularly':");
    for (i, span) in spans.iter().enumerate() {
        if span.text.to_lowercase().contains("arly")
            || span.text.to_lowercase().contains("particularly")
        {
            println!(
                "{:3}. '{}' (font: {}, size: {})",
                i, span.text, span.font_name, span.font_size
            );
        }
    }

    // Show context around "lculated" if found
    if let Some(idx) = text.find("lculated") {
        let start = idx.saturating_sub(30);
        let end = (idx + 40).min(text.len());
        println!("\nContext around 'lculated': '{}'", &text[start..end]);
    }
}
