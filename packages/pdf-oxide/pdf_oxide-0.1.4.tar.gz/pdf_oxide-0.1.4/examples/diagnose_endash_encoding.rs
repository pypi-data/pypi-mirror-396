use pdf_oxide::{PdfDocument, converters::ConversionOptions};

fn main() {
    let mut doc = PdfDocument::open(
        "../pdf_oxide_tests/pdfs/government/CFR_2024_Title33_Vol1_Navigation_and_Navigable_Waters.pdf",
    )
    .expect("Failed to open PDF");

    println!("=== Investigating En-Dash Encoding Issue ===\n");

    // Extract spans to see raw encoding for early pages
    for page_num in 0..5 {
        println!("Page {}:", page_num);

        match doc.extract_spans(page_num) {
            Ok(spans) => {
                // Look for spans with replacement characters or patterns like "0 16"
                for (i, span) in spans.iter().enumerate() {
                    let text = &span.text;

                    // Check for replacement characters
                    if text.contains('\u{FFFD}') {
                        println!("  Span {}: Found replacement character", i);
                        println!("    Text: {:?}", text);
                        println!("    Font: {}", span.font_name);

                        // Show hex bytes of the text around replacement char
                        let bytes = text.as_bytes();
                        println!("    Hex: {:02X?}", &bytes[..bytes.len().min(50)]);
                        println!();
                    }

                    // Check for patterns that might have en-dash
                    if text.contains("0 16")
                        || text.contains("0–16")
                        || text.contains("20402")
                        || text.contains("96 511")
                    {
                        println!("  Span {}: Potential en-dash pattern", i);
                        println!("    Text: {:?}", text);
                        println!("    Font: {}", span.font_name);

                        // Count spaces vs dashes
                        let space_count = text.matches(' ').count();
                        let dash_count = text.matches('–').count();
                        let repl_count = text.matches('\u{FFFD}').count();

                        println!(
                            "    Spaces: {}, Dashes: {}, Replacements: {}",
                            space_count, dash_count, repl_count
                        );
                        println!();
                    }
                }
            },
            Err(e) => println!("  Error extracting spans: {}", e),
        }
    }

    println!("\n=== Markdown Conversion Check ===");

    // Convert first few pages to markdown
    for page_num in 0..5 {
        match doc.to_markdown(page_num, &ConversionOptions::default()) {
            Ok(markdown) => {
                let repl_count = markdown.chars().filter(|&c| c == '\u{FFFD}').count();

                if repl_count > 0 {
                    println!("Page {}: {} replacement characters", page_num, repl_count);

                    // Show lines with replacement chars
                    let problem_lines: Vec<&str> = markdown
                        .lines()
                        .filter(|line| line.contains('\u{FFFD}'))
                        .take(3)
                        .collect();

                    for line in problem_lines {
                        println!("  {}", line);
                    }
                    println!();
                }
            },
            Err(e) => println!("Page {}: Error - {}", page_num, e),
        }
    }
}
