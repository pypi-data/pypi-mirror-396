use pdf_oxide::PdfDocument;

fn main() {
    let _doc = PdfDocument::open(
        "../pdf_oxide_tests/pdfs/government/CFR_2024_Title33_Vol1_Navigation_and_Navigable_Waters.pdf",
    )
    .expect("Failed to open PDF");

    println!("=== Investigating ToUnicode CMap for R19 Font ===\n");

    // We need to access internal document structure
    // This is a diagnostic tool, so we'll print what we can see

    println!("Page 1 analysis:");
    println!("Font R19 appears to be causing issues");
    println!("Character code that becomes � needs investigation");
    println!();

    println!("Expected patterns:");
    println!("  '0–16' (en-dash U+2013)");
    println!("  '20402–0001' (en-dash U+2013)");
    println!("  '96–511' (en-dash U+2013)");
    println!();

    println!("Actual output:");
    println!("  '0�16' (replacement U+FFFD)");
    println!("  '20402�0001' (replacement U+FFFD)");
    println!("  '96�511' (replacement U+FFFD)");
    println!();

    println!("Hex analysis from previous diagnostic:");
    println!("  Text contains: EF BF BD (UTF-8 for U+FFFD)");
    println!("  This means ToUnicode CMap is already producing U+FFFD");
    println!();

    println!("Root cause options:");
    println!("  1. ToUnicode CMap explicitly maps character code to U+FFFD");
    println!("  2. ToUnicode CMap is malformed/corrupt for this character code");
    println!("  3. Character code doesn't exist in ToUnicode CMap (missing entry)");
    println!("  4. Our CMap parser is failing to decode this specific entry");
    println!();

    println!("PDF spec compliance:");
    println!("  Per ISO 32000-1:2008 section 9.10.2:");
    println!("  Priority 1: ToUnicode CMap (if present)");
    println!("  Priority 2: Predefined encodings (MacRomanEncoding, WinAnsiEncoding)");
    println!("  Priority 3: Composite fonts with predefined CMaps");
    println!("  Priority 4: Fallback (no way to determine Unicode)");
    println!();

    println!("Recommended fix:");
    println!("  1. Check if ToUnicode CMap has entry for en-dash character code");
    println!("  2. If missing/incorrect, fall back to MacRomanEncoding (en-dash is 0xD0)");
    println!("  3. If still fails, fall back to heuristic (byte 0xD0 -> U+2013)");
    println!();

    println!("Next steps:");
    println!("  1. Examine raw ToUnicode CMap from font R19");
    println!("  2. Identify what character code is used for en-dash");
    println!("  3. Check if it's in the CMap");
    println!("  4. Implement proper fallback handling");
}
