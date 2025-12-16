//! Debug a specific failing PDF

use pdf_oxide::document::PdfDocument;

fn main() {
    env_logger::init();

    let pdf_path = std::env::args().nth(1).unwrap_or_else(|| {
        "../pdf_oxide_tests/pdfs/mixed/SEVNFYZBX7VQEWEG5SQQTFZK24PCUDFU.pdf".to_string()
    });

    println!("Attempting to open: {}", pdf_path);

    match PdfDocument::open(pdf_path) {
        Ok(mut pdf) => {
            println!("✓ Successfully opened PDF!");
            println!("  Version: {}.{}", pdf.version().0, pdf.version().1);

            println!("\nAttempting to get page count...");
            match pdf.page_count() {
                Ok(count) => {
                    println!("✓ Page count: {}", count);
                },
                Err(e) => {
                    eprintln!("✗ Failed to get page count:");
                    eprintln!("  Error: {}", e);
                    eprintln!("  Debug: {:?}", e);
                    std::process::exit(1);
                },
            }
        },
        Err(e) => {
            eprintln!("✗ Failed to open PDF:");
            eprintln!("  Error: {}", e);
            eprintln!("  Debug: {:?}", e);
            std::process::exit(1);
        },
    }
}
