use pdf_oxide::{PdfDocument, converters::ConversionOptions};

fn main() {
    let pdf_path = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "../pdf_oxide_tests/pdfs/government/CFR_2024_Title33_Vol1_Navigation_and_Navigable_Waters.pdf".to_string());

    let mut doc = PdfDocument::open(&pdf_path).expect("Failed to open PDF");

    println!("=== Analyzing: {} ===\n", pdf_path.split('/').next_back().unwrap());

    // Extract spans to see raw encoding
    let spans = doc.extract_spans(0).expect("Failed to extract spans");

    println!("Total spans on page 0: {}\n", spans.len());

    let mut repl_spans = Vec::new();

    for (i, span) in spans.iter().enumerate() {
        let text = &span.text;

        // Look for replacement characters
        if text.contains('\u{FFFD}') {
            repl_spans.push((i, span));
        }
    }

    println!("Spans with replacement characters: {}\n", repl_spans.len());

    if !repl_spans.is_empty() {
        println!("=== Replacement Character Details ===\n");

        for (i, span) in repl_spans.iter().take(10) {
            println!("Span {}:", i);
            println!("  Text: {:?}", span.text);
            println!("  Font: {}", span.font_name);
            println!("  Font Size: {:.1}", span.font_size);

            // Show hex representation of problematic text
            let repl_pos: Vec<usize> = span
                .text
                .char_indices()
                .filter(|(_, c)| *c == '\u{FFFD}')
                .map(|(pos, _)| pos)
                .collect();

            println!("  Replacement char positions: {:?}", repl_pos);

            // Show surrounding characters
            for &pos in &repl_pos {
                let chars: Vec<char> = span.text.chars().collect();
                let idx = span.text[..pos].chars().count();

                print!("    Context: ");
                if idx > 0 {
                    print!("'{}'", chars[idx - 1]);
                }
                print!(" [�] ");
                if idx + 1 < chars.len() {
                    print!("'{}'", chars[idx + 1]);
                }
                println!();
            }

            println!();
        }
    }

    // Also check markdown output
    let markdown = doc
        .to_markdown(0, &ConversionOptions::default())
        .expect("Failed to convert");

    let repl_count = markdown.chars().filter(|&c| c == '\u{FFFD}').count();
    println!("\n=== Markdown Summary ===");
    println!("Total replacement characters: {}", repl_count);

    if repl_count > 0 {
        println!("\nFirst 5 lines with replacement chars:");
        let lines_with_repl: Vec<&str> = markdown
            .lines()
            .filter(|line| line.contains('\u{FFFD}'))
            .take(5)
            .collect();

        for line in lines_with_repl {
            // Highlight replacement chars
            let highlighted = line.replace('\u{FFFD}', "[�]");
            println!("  {}", highlighted);
        }
    }

    // Analyze patterns
    println!("\n=== Common Patterns ===");
    let patterns = [
        ("0-16", "0\u{FFFD}16"),
        ("01-1", "01\u{FFFD}1"),
        ("dash in section numbers", "\u{FFFD}"),
    ];

    for (expected, actual) in &patterns {
        if markdown.contains(actual) {
            let count = markdown.matches(actual).count();
            println!("  Pattern '{}' appears {} times", expected, count);
        }
    }
}
