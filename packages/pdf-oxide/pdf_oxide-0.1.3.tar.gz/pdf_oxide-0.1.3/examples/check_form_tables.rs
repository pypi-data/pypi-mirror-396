use pdf_oxide::{PdfDocument, converters::ConversionOptions};

fn main() {
    let mut doc = PdfDocument::open("../pdf_oxide_tests/pdfs/forms/irs_f1040.pdf")
        .expect("Failed to open form PDF");

    let markdown = doc
        .to_markdown(0, &ConversionOptions::default())
        .expect("Failed to convert to markdown");

    println!("Markdown length: {} chars", markdown.len());

    let table_rows = markdown
        .lines()
        .filter(|line| line.contains('|') && line.matches('|').count() >= 2)
        .count();

    println!("Table rows: {}", table_rows);

    if table_rows > 0 {
        println!("\n✅ Form has tables");
        println!("\nFirst 1000 chars:");
        println!("{}", &markdown[..1000.min(markdown.len())]);
    } else {
        println!("\n❌ No tables found in form");
        println!("\nFirst 1000 chars:");
        println!("{}", &markdown[..1000.min(markdown.len())]);
    }
}
