//! Debug tool to analyze XObjects in a PDF

use pdf_oxide::document::PdfDocument;
use std::env;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::init();

    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <pdf_file>", args[0]);
        std::process::exit(1);
    }

    let pdf_path = &args[1];
    println!("Analyzing XObjects in: {}", pdf_path);

    let mut doc = PdfDocument::open(pdf_path)?;
    let page_count = doc.page_count()?;

    println!("PDF has {} pages", page_count);

    for page_idx in 0..page_count {
        println!("\n=== Page {} ===", page_idx + 1);

        // Extract chars to trigger processing
        match doc.extract_spans(page_idx) {
            Ok(chars) => {
                println!("Extracted {} characters", chars.len());
            },
            Err(e) => {
                println!("Error extracting text: {}", e);
            },
        }
    }

    Ok(())
}
