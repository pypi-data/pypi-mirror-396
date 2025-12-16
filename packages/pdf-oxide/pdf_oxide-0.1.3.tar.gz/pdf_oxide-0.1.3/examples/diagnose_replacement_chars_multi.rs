use pdf_oxide::{PdfDocument, converters::ConversionOptions};

fn main() {
    let pdf_path = "../pdf_oxide_tests/pdfs/government/CFR_2024_Title33_Vol1_Navigation_and_Navigable_Waters.pdf";

    let mut doc = PdfDocument::open(pdf_path).expect("Failed to open PDF");

    println!("=== Analyzing CFR Title 33 (Multiple Pages) ===\n");

    // Check first 10 pages
    let page_count = doc.page_count().expect("Failed to get page count");
    for page_num in 0..10.min(page_count) {
        println!("Page {}:", page_num);

        match doc.extract_spans(page_num) {
            Ok(spans) => {
                let repl_count: usize = spans
                    .iter()
                    .map(|s| s.text.chars().filter(|&c| c == '\u{FFFD}').count())
                    .sum();

                if repl_count > 0 {
                    println!("  ⚠️  {} replacement characters found!", repl_count);

                    // Show examples
                    for span in spans.iter().filter(|s| s.text.contains('\u{FFFD}')).take(3) {
                        println!("    Example: {:?} (font: {})", span.text, span.font_name);
                    }
                } else {
                    println!("  ✅ No replacement characters");
                }
            },
            Err(e) => println!("  ❌ Error: {}", e),
        }
    }

    println!("\n=== Checking Markdown Output ===");

    for page_num in 0..5.min(page_count) {
        match doc.to_markdown(page_num, &ConversionOptions::default()) {
            Ok(markdown) => {
                let repl_count = markdown.chars().filter(|&c| c == '\u{FFFD}').count();

                if repl_count > 0 {
                    println!("Page {}: {} replacement chars in markdown", page_num, repl_count);

                    // Show problematic lines
                    let problem_lines: Vec<&str> = markdown
                        .lines()
                        .filter(|line| line.contains('\u{FFFD}'))
                        .take(2)
                        .collect();

                    for line in problem_lines {
                        let highlighted = line.replace('\u{FFFD}', "[�]");
                        println!("  {}", highlighted);
                    }
                }
            },
            Err(e) => println!("Page {}: Error - {}", page_num, e),
        }
    }
}
