//! Test xref stream parsing on a specific PDF

use pdf_oxide::document::PdfDocument;

fn main() {
    env_logger::init();

    let pdf_path = "../pdf_oxide_tests/pdfs/forms/irs_fw4.pdf";

    println!("Attempting to open: {}", pdf_path);

    match PdfDocument::open(pdf_path) {
        Ok(pdf) => {
            println!("✓ Successfully opened PDF!");
            println!("  Version: {}.{}", pdf.version().0, pdf.version().1);
        },
        Err(e) => {
            eprintln!("✗ Failed to open PDF:");
            eprintln!("  Error: {}", e);
            eprintln!("  Debug: {:?}", e);
            std::process::exit(1);
        },
    }
}
