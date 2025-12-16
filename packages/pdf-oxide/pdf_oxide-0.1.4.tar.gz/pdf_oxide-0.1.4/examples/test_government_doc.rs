use pdf_oxide::{PdfDocument, error::Result};

fn main() -> Result<()> {
    env_logger::init();

    let pdf_path = "../pdf_oxide_tests/pdfs/government/CFR_2024_Title07_Vol1_Agriculture.pdf";

    println!("Testing government document with column detection...");
    println!("PDF: {}", pdf_path);
    println!();

    let mut doc = PdfDocument::open(pdf_path)?;

    // Extract first page
    let spans = doc.extract_spans(0)?;

    // Get first 500 characters
    let text: String = spans
        .iter()
        .map(|s| s.text.as_str())
        .collect::<Vec<_>>()
        .join(" ");

    let preview = if text.len() > 500 {
        &text[..500]
    } else {
        &text
    };

    println!("First 500 chars of extracted text:");
    println!("{}", preview);
    println!();

    // Check for garbling patterns
    if text.contains("FY 2B0u0d7g") || text.contains("SDeecfuerniSstEaeynf") {
        println!("❌ GARBLING DETECTED - Column detection failed!");
    } else if text.contains("FY 2007") && text.contains("Budget") {
        println!("✅ Text looks good - Column detection working!");
    } else {
        println!("⚠️ Text quality unclear - manual inspection needed");
    }

    Ok(())
}
