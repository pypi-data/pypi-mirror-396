use pdf_oxide::PdfDocument;
use std::env;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Enable logging
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    let pdf_path = env::args()
        .nth(1)
        .expect("Usage: debug_zero_chars <pdf_path>");

    println!("=== Debugging: {} ===", pdf_path);
    println!();

    // Open document
    let mut doc = match PdfDocument::open(&pdf_path) {
        Ok(d) => {
            println!("✓ Document opened successfully");
            d
        },
        Err(e) => {
            println!("✗ Failed to open document: {:?}", e);
            return Err(e.into());
        },
    };

    let page_count = doc.page_count()?;
    println!("✓ Pages detected: {}", page_count);
    println!();

    // Try to extract text from each page
    let mut total_chars = 0;
    for page_num in 0..page_count {
        println!("--- Page {} ---", page_num);

        // Try text extraction
        match doc.extract_text(page_num) {
            Ok(text) => {
                let char_count = text.len();
                total_chars += char_count;
                println!("  ✓ Extracted {} characters", char_count);
                if char_count == 0 {
                    println!("  ⚠ WARNING: Zero characters extracted!");
                } else if char_count < 100 {
                    println!("  Preview: {:?}", &text[..char_count.min(100)]);
                }
            },
            Err(e) => {
                println!("  ✗ Text extraction failed: {:?}", e);
            },
        }
        println!();
    }

    println!("=== Summary ===");
    println!("Total characters extracted: {}", total_chars);
    if total_chars == 0 {
        println!("⚠ ZERO CHARACTERS EXTRACTED - This PDF needs investigation!");
        println!("\nTo debug further, enable debug logging:");
        println!("  RUST_LOG=debug cargo run --example debug_zero_chars {}", pdf_path);
    }

    Ok(())
}
