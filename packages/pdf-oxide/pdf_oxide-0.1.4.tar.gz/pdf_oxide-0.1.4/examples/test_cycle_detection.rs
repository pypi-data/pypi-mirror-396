use pdf_oxide::document::PdfDocument;

fn main() {
    // Test the problematic PDF
    let path = "../pdf_oxide_tests/pdfs/mixed/HNBALTFDCV5YCQB772EJLOZGFV3JQLXS.pdf";

    println!("Testing cycle detection on: {}", path);

    let mut doc = match PdfDocument::open(path) {
        Ok(doc) => doc,
        Err(e) => {
            eprintln!("Failed to open PDF: {}", e);
            std::process::exit(1);
        },
    };

    println!("✓ PDF opened successfully");

    // Get page count
    let page_count = match doc.page_count() {
        Ok(count) => count,
        Err(e) => {
            eprintln!("Failed to get page count: {}", e);
            std::process::exit(1);
        },
    };

    println!("✓ Page count: {}", page_count);

    // Check for circular references
    println!("\nChecking for circular references...");
    let cycles = doc.check_for_circular_references();

    if cycles.is_empty() {
        println!("✓ No circular references detected");
    } else {
        println!("⚠ Found {} circular references:", cycles.len());
        for (from, to) in &cycles {
            println!("  {} → {}", from, to);
        }
    }

    // Extract text from all pages (gracefully handle errors)
    println!("\nExtracting text from all pages...");
    let mut total_chars = 0;
    let mut successful_pages = 0;
    let mut failed_pages = 0;

    for i in 0..page_count {
        match doc.extract_text(i) {
            Ok(text) => {
                println!("✓ Page {}: {} characters extracted", i + 1, text.len());
                total_chars += text.len();
                successful_pages += 1;
            },
            Err(e) => {
                println!("⚠ Page {}: Failed to extract text: {}", i + 1, e);
                failed_pages += 1;
            },
        }
    }

    println!("\n===========================");
    println!("Extraction Summary");
    println!("===========================");
    println!("Total pages:       {}", page_count);
    println!("Successful:        {}", successful_pages);
    println!("Failed:            {}", failed_pages);
    println!("Total characters:  {}", total_chars);

    if successful_pages > 0 {
        println!("\n✅ Stack overflow is FIXED! At least one page extracted successfully.");
    } else {
        println!("\n⚠ No pages extracted, but no stack overflow occurred.");
    }
}
