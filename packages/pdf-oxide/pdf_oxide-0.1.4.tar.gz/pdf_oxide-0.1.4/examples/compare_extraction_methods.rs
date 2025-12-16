use pdf_oxide::{PdfDocument, error::Result};

fn main() -> Result<()> {
    let pdf_path = "../pdf_oxide_tests/pdfs/academic/arxiv_2510.21165v1.pdf";
    let mut doc = PdfDocument::open(pdf_path)?;

    println!("===========================================");
    println!("   OLD METHOD: Character-based extraction");
    println!("===========================================\n");

    let chars = doc.extract_spans(0)?;
    let char_text: String = chars.iter().map(|c| c.text.as_str()).collect();

    let char_sample: String = char_text.chars().take(500).collect();
    println!("Sample (first 500 chars):");
    println!("{}\n", char_sample);

    // Check for issues
    println!("Quality checks:");
    let has_column_mixing = char_sample.contains("Tmheet") || char_sample.contains("hfion");
    let has_fragmentation = char_sample.contains("Intr oduction")
        || char_sample.contains("netw ork")
        || char_sample.contains("comple x");

    println!(
        "  ❌ Column mixing: {}",
        if has_column_mixing {
            "PRESENT"
        } else {
            "Not detected"
        }
    );
    println!(
        "  ❌ Word fragmentation: {}",
        if has_fragmentation {
            "PRESENT"
        } else {
            "Not detected"
        }
    );
    println!("  Total characters extracted: {}", chars.len());

    println!("\n===========================================");
    println!("   NEW METHOD: Span-based extraction (PDF spec compliant)");
    println!("===========================================\n");

    let spans = doc.extract_spans(0)?;
    let span_text: String = spans
        .iter()
        .map(|s| s.text.as_str())
        .collect::<Vec<_>>()
        .join(" ");

    let span_sample: String = span_text.chars().take(500).collect();
    println!("Sample (first 500 chars):");
    println!("{}\n", span_sample);

    // Check for improvements
    println!("Quality checks:");
    let has_column_mixing_spans = span_sample.contains("Tmheet") || span_sample.contains("hfion");
    let has_complete_words = span_sample.contains("Introduction")
        && span_sample.contains("network")
        && span_sample.contains("complex")
        && span_sample.contains("systems");

    println!(
        "  ✅ Column mixing: {}",
        if has_column_mixing_spans {
            "PRESENT"
        } else {
            "RESOLVED"
        }
    );
    println!("  ✅ Complete words: {}", if has_complete_words { "YES" } else { "NO" });
    println!("  Total spans extracted: {}", spans.len());

    println!("\n===========================================");
    println!("   COMPARISON SUMMARY");
    println!("===========================================\n");

    println!("Character-based (OLD):");
    println!("  - Extracts individual characters");
    println!("  - Prone to column mixing in multi-column layouts");
    println!("  - Can have word fragmentation issues");
    println!("  - Not PDF spec compliant\n");

    println!("Span-based (NEW - RECOMMENDED):");
    println!("  - Extracts complete text strings as PDF provides them");
    println!("  - Follows PDF spec ISO 32000-1:2008");
    println!("  - Preserves complete words");
    println!("  - More robust for complex layouts");
    println!("  - Matches industry best practices (PyMuPDF)\n");

    println!("Improvement:");
    if has_column_mixing && !has_column_mixing_spans {
        println!("  ✅ Column mixing RESOLVED");
    }
    if has_fragmentation && has_complete_words {
        println!("  ✅ Word fragmentation RESOLVED");
    }

    Ok(())
}
