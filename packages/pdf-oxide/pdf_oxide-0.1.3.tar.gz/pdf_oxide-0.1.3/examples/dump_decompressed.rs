//! Dump decompressed stream content

use pdf_oxide::PdfDocument;

fn main() {
    env_logger::init();

    let path = "../pdf_oxide_tests/pdfs/mixed/TYLWGSX5OYKE27DHTQXUJTBMKMHMKY3B.pdf";

    println!("==> Opening PDF");
    let mut doc = PdfDocument::open(path).unwrap();

    println!("\n==> Extracting text with detailed logging...");
    match doc.extract_text(0) {
        Ok(text) => {
            println!("\n✓ Extracted {} chars", text.len());
            if text.is_empty() {
                println!("⚠ WARNING: No text extracted!");
            } else {
                println!("\nFull text:\n{}", text);
            }
        },
        Err(e) => {
            eprintln!("\n✗ Failed to extract text: {}", e);
        },
    }
}
