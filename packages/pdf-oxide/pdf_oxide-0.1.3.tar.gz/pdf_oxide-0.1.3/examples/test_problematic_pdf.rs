// Test problematic PDF directly from Rust
use pdf_oxide::PdfDocument;

fn main() {
    println!("Testing problematic PDF directly from Rust...\n");

    // Test the garbled text PDF
    let pdf_path = "../pdf_oxide_tests/pdfs/mixed/2Z5VOQ6G6CMR5GMVSAAXULXHXTMJPTM2.pdf";

    println!("Opening: {}", pdf_path);

    let mut doc = match PdfDocument::open(pdf_path) {
        Ok(d) => d,
        Err(e) => {
            eprintln!("Failed to open PDF: {}", e);
            return;
        },
    };

    let page_count = match doc.page_count() {
        Ok(c) => c,
        Err(e) => {
            eprintln!("Failed to get page count: {}", e);
            return;
        },
    };

    println!("Pages: {}\n", page_count);

    // Extract first page using CHARACTER extraction (OLD METHOD)
    println!("=== PAGE 1 TEXT (Character mode - OLD) ===");
    match doc.extract_text(0) {
        Ok(text) => {
            println!("Text length: {} characters", text.len());
            println!("\nFirst 300 chars:");
            println!("{}\n", &text.chars().take(300).collect::<String>());
        },
        Err(e) => {
            eprintln!("Failed to extract text: {}", e);
        },
    }

    // Extract first page using SPAN extraction (NEW METHOD with TJ buffering)
    println!("\n=== PAGE 1 TEXT (Span mode - NEW with TJ buffering) ===");
    match doc.extract_spans(0) {
        Ok(spans) => {
            println!("Number of spans: {}", spans.len());
            let text: String = spans.iter().map(|s| s.text.as_str()).collect();
            println!("Total text length: {} characters", text.len());
            println!("\nFirst 300 chars:");
            println!("{}\n", &text.chars().take(300).collect::<String>());
        },
        Err(e) => {
            eprintln!("Failed to extract spans: {}", e);
        },
    }

    // Test a working PDF for comparison
    println!("\n\n=== TESTING PROBLEMATIC PDF (should be fixed with TJ buffering) ===\n");
    let good_pdf = "../pdf_oxide_tests/pdfs/mixed/5PFVA6CO2FP66IJYJJ4YMWOLK5EHRCCD.pdf";

    println!("Opening: {}", good_pdf);
    let mut doc2 = match PdfDocument::open(good_pdf) {
        Ok(d) => d,
        Err(e) => {
            eprintln!("Failed to open PDF: {}", e);
            return;
        },
    };

    println!("=== PROBLEMATIC PDF PAGE 1 - Character mode (OLD) ===");
    match doc2.extract_text(0) {
        Ok(text) => {
            println!("Text length: {} characters", text.len());
            println!("\nFirst 300 chars:");
            println!("{}\n", &text.chars().take(300).collect::<String>());
        },
        Err(e) => {
            eprintln!("Failed to extract text: {}", e);
        },
    }

    println!("\n=== PROBLEMATIC PDF PAGE 1 - Span mode (NEW with TJ buffering) ===");
    match doc2.extract_spans(0) {
        Ok(spans) => {
            println!("Number of spans: {}", spans.len());
            let text: String = spans.iter().map(|s| s.text.as_str()).collect();
            println!("Total text length: {} characters", text.len());
            println!("\nFirst 300 chars:");
            println!("{}\n", &text.chars().take(300).collect::<String>());
        },
        Err(e) => {
            eprintln!("Failed to extract spans: {}", e);
        },
    }
}
