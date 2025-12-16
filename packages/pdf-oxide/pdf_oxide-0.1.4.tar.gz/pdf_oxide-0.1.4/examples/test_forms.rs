//! Test form field extraction from IRS F1040

use pdf_oxide::document::PdfDocument;
use pdf_oxide::extractors::forms::FormExtractor;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let pdf_path = "../pdf_oxide_tests/pdfs/forms/irs_f1040.pdf";

    println!("Opening PDF: {}", pdf_path);
    let mut doc = PdfDocument::open(pdf_path)?;

    println!("Extracting form fields...\n");
    let fields = FormExtractor::extract_fields(&mut doc)?;

    println!("Found {} form fields:", fields.len());
    println!("{}", "=".repeat(80));

    for (i, field) in fields.iter().enumerate() {
        println!("\nField #{}:", i + 1);
        println!("  Name: {}", field.name);
        println!("  Full Name: {}", field.full_name);
        println!("  Type: {:?}", field.field_type);
        println!("  Value: {:?}", field.value);
        if let Some(tooltip) = &field.tooltip {
            println!("  Tooltip: {}", tooltip);
        }
        if let Some(bounds) = &field.bounds {
            println!(
                "  Position: ({:.1}, {:.1}) to ({:.1}, {:.1})",
                bounds[0], bounds[1], bounds[2], bounds[3]
            );
        }

        // Only print first 20 fields to avoid spam
        if i >= 19 {
            println!("\n... and {} more fields", fields.len() - 20);
            break;
        }
    }

    Ok(())
}
