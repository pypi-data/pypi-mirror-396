//! Debug corrupt FlateDecode PDF
//!
//! Analyzes TYLWGSX5OYKE27DHTQXUJTBMKMHMKY3B.pdf to understand why extraction fails

use pdf_oxide::PdfDocument;

fn main() {
    env_logger::init();

    let path = "../pdf_oxide_tests/pdfs/mixed/TYLWGSX5OYKE27DHTQXUJTBMKMHMKY3B.pdf";

    println!("==> Opening PDF: {}", path);
    let mut doc = match PdfDocument::open(path) {
        Ok(d) => {
            println!("✓ PDF opened successfully");
            d
        },
        Err(e) => {
            eprintln!("✗ Failed to open PDF: {}", e);
            std::process::exit(1);
        },
    };

    println!("\n==> Getting page count...");
    let page_count = match doc.page_count() {
        Ok(count) => {
            println!("✓ Page count: {}", count);
            count
        },
        Err(e) => {
            eprintln!("✗ Failed to get page count: {}", e);
            std::process::exit(1);
        },
    };

    for page_num in 0..page_count {
        println!("\n==> Extracting text from page {}...", page_num);
        match doc.extract_text(page_num) {
            Ok(text) => {
                println!("✓ Extracted {} chars", text.len());
                if text.is_empty() {
                    println!("⚠ WARNING: No text extracted!");
                } else {
                    println!("First 200 chars: {:?}", &text.chars().take(200).collect::<String>());
                }
            },
            Err(e) => {
                eprintln!("✗ Failed to extract text: {}", e);
            },
        }
    }
}
