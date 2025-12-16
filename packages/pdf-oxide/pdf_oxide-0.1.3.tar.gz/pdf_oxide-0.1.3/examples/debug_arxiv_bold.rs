use pdf_oxide::PdfDocument;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut pdf = PdfDocument::open("../pdf_oxide_tests/pdfs/academic/arxiv_2510.21165v1.pdf")?;
    let spans = pdf.extract_spans(0)?;

    println!("Total spans: {}", spans.len());
    println!("\nFirst 60 spans with bold status:\n");

    for (i, span) in spans.iter().take(60).enumerate() {
        let is_bold = span.font_weight.is_bold();
        println!("{:3}. weight={:?} bold={:5} text={:?}", i, span.font_weight, is_bold, span.text);
    }

    // Find spans containing "Chinese", "stock", "market"
    println!("\n\nSpans containing 'Chinese', 'stock', or 'market':");
    for (i, span) in spans.iter().enumerate() {
        let text_lower = span.text.to_lowercase();
        if text_lower.contains("chinese")
            || text_lower.contains("stock")
            || text_lower.contains("market")
        {
            let is_bold = span.font_weight.is_bold();
            println!(
                "{:3}. weight={:?} bold={:5} text={:?}",
                i, span.font_weight, is_bold, span.text
            );
        }
    }

    Ok(())
}
