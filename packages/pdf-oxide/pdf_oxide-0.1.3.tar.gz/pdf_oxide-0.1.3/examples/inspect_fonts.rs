//! Inspect font information in a PDF to debug text extraction issues.

use pdf_oxide::document::PdfDocument;

fn main() {
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    let pdf_path = std::env::args().nth(1).unwrap_or_else(|| {
        "../pdf_oxide_tests/pdfs/mixed/45W73IZ4UHYYGASU2Y4JO6Q7SC56OPTI.pdf".to_string()
    });

    println!("Inspecting: {}\n", pdf_path);

    match PdfDocument::open(&pdf_path) {
        Ok(mut pdf) => {
            println!("✓ PDF version: {}.{}", pdf.version().0, pdf.version().1);

            match pdf.page_count() {
                Ok(count) => {
                    println!("✓ Pages: {}", count);

                    // Test text extraction on first page
                    if count > 0 {
                        println!("\n=== TEXT EXTRACTION TEST ===");
                        match pdf.extract_spans(0) {
                            Ok(chars) => {
                                println!("✓ Extracted {} characters from page 0", chars.len());
                                if !chars.is_empty() {
                                    let text: String =
                                        chars.iter().map(|c| c.text.as_str()).collect();
                                    println!("\nFirst 200 chars of extracted text:");
                                    println!("{}", &text[..text.len().min(200)]);
                                } else {
                                    println!("\n✗ NO CHARACTERS EXTRACTED!");
                                    println!("This is the issue we need to debug.\n");
                                }
                            },
                            Err(e) => {
                                eprintln!("✗ Text extraction failed: {}", e);
                            },
                        }
                    }
                },
                Err(e) => {
                    eprintln!("✗ Failed to get page count: {}", e);
                    std::process::exit(1);
                },
            }
        },
        Err(e) => {
            eprintln!("✗ Failed to open PDF: {}", e);
            std::process::exit(1);
        },
    }
}
