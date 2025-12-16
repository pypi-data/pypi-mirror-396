use pdf_oxide::PdfDocument;

fn main() {
    let mut doc = PdfDocument::open(
        "../pdf_oxide_tests/pdfs/diverse/NASA_Apollo_11_Preliminary_Science_Report.pdf",
    )
    .expect("Failed to open NASA PDF");

    let spans = doc.extract_spans(0).expect("Failed to extract spans");

    let text: String = spans.iter().map(|s| s.text.as_str()).collect();

    // Check word statistics
    let words: Vec<&str> = text.split_whitespace().collect();
    let avg_length = words.iter().map(|w| w.len()).sum::<usize>() as f64 / words.len() as f64;

    println!("Total chars: {}", text.len());
    println!("Total words: {}", words.len());
    println!("Avg word length: {:.1}", avg_length);

    // Show some long words
    let mut long_words: Vec<&str> = words.iter().filter(|w| w.len() > 15).copied().collect();
    long_words.sort_by_key(|w| std::cmp::Reverse(w.len()));
    long_words.truncate(20);

    println!("\nTop 20 longest words:");
    for (i, word) in long_words.iter().enumerate() {
        println!("{}. {} ({} chars)", i + 1, word, word.len());
    }

    // Check first 500 chars
    println!("\nFirst 500 chars:");
    println!("{}", &text[..500.min(text.len())]);
}
