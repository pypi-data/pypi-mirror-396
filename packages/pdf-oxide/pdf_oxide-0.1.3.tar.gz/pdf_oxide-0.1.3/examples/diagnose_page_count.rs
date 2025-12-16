//! Diagnostic tool to investigate page count zero issue
//!
//! This tool helps understand why certain PDFs return page_count = 0

use pdf_oxide::{Error, PdfDocument};
use std::env;

fn main() -> Result<(), Error> {
    env::set_var("RUST_LOG", "pdf_oxide=debug");
    env_logger::init();

    let test_files = vec![
        "../pdf_oxide_tests/pdfs/newspapers/IA_0001-cdc-2015-american-tour.pdf",
        "../pdf_oxide_tests/pdfs/newspapers/IA_0001-cdc-2018-american-tour.pdf",
        "../pdf_oxide_tests/pdfs/newspapers/IA_0001-chambers-museum.pdf",
    ];

    println!("\n=== Diagnosing Page Count Zero Issue ===\n");

    for file_path in test_files {
        println!("📄 File: {}", file_path);
        println!("{}", "=".repeat(80));

        if !std::path::Path::new(file_path).exists() {
            println!("⚠️  File not found, skipping\n");
            continue;
        }

        match PdfDocument::open(file_path) {
            Ok(mut doc) => {
                // Try to get page count
                println!("\n1️⃣ Attempting page_count()...");
                match doc.page_count() {
                    Ok(count) => {
                        println!("   ✅ Page count: {}", count);
                        if count == 0 {
                            println!("   ❌ ISSUE: Page count is zero!");
                        }
                    },
                    Err(e) => {
                        println!("   ❌ Error: {}", e);
                    },
                }

                // Try to inspect catalog
                println!("\n2️⃣ Inspecting catalog...");
                match doc.catalog() {
                    Ok(catalog) => {
                        println!("   ✅ Catalog loaded");

                        if let Some(catalog_dict) = catalog.as_dict() {
                            println!(
                                "   Catalog keys: {:?}",
                                catalog_dict.keys().collect::<Vec<_>>()
                            );

                            // Check for /Pages
                            if let Some(pages_entry) = catalog_dict.get("Pages") {
                                println!("   ✅ /Pages entry found: {:?}", pages_entry);

                                if let Some(pages_ref) = pages_entry.as_reference() {
                                    println!("   ✅ /Pages is a reference: {}", pages_ref);

                                    // Load the /Pages object
                                    match doc.load_object(pages_ref) {
                                        Ok(pages_obj) => {
                                            println!("   ✅ /Pages object loaded");

                                            if let Some(pages_dict) = pages_obj.as_dict() {
                                                println!(
                                                    "   Pages dict keys: {:?}",
                                                    pages_dict.keys().collect::<Vec<_>>()
                                                );

                                                // Check for /Count
                                                if let Some(count_entry) = pages_dict.get("Count") {
                                                    println!(
                                                        "   ✅ /Count entry found: {:?}",
                                                        count_entry
                                                    );

                                                    if let Some(count_int) =
                                                        count_entry.as_integer()
                                                    {
                                                        println!(
                                                            "   ✅ /Count value: {}",
                                                            count_int
                                                        );
                                                    } else {
                                                        println!(
                                                            "   ❌ /Count is not an integer: {:?}",
                                                            count_entry
                                                        );
                                                    }
                                                } else {
                                                    println!(
                                                        "   ❌ /Count entry not found in /Pages"
                                                    );
                                                }

                                                // Check for /Kids
                                                if let Some(kids_entry) = pages_dict.get("Kids") {
                                                    println!(
                                                        "   ✅ /Kids entry found: {:?}",
                                                        kids_entry
                                                    );

                                                    if let Some(kids_array) = kids_entry.as_array()
                                                    {
                                                        println!(
                                                            "   ✅ /Kids is an array with {} items",
                                                            kids_array.len()
                                                        );
                                                    } else {
                                                        println!("   ❌ /Kids is not an array");
                                                    }
                                                } else {
                                                    println!("   ⚠️  /Kids entry not found");
                                                }

                                                // Check /Type
                                                if let Some(type_entry) = pages_dict.get("Type") {
                                                    if let Some(type_name) = type_entry.as_name() {
                                                        println!("   Type: /{}", type_name);
                                                    }
                                                }
                                            } else {
                                                println!("   ❌ /Pages object is not a dictionary");
                                            }
                                        },
                                        Err(e) => {
                                            println!("   ❌ Failed to load /Pages object: {}", e);
                                        },
                                    }
                                } else {
                                    println!("   ❌ /Pages is not a reference: {:?}", pages_entry);
                                }
                            } else {
                                println!("   ❌ /Pages entry not found in catalog");
                            }
                        } else {
                            println!("   ❌ Catalog is not a dictionary");
                        }
                    },
                    Err(e) => {
                        println!("   ❌ Failed to load catalog: {}", e);
                    },
                }

                // Try span extraction on first page
                println!("\n3️⃣ Testing span extraction on page 0...");
                match doc.extract_spans(0) {
                    Ok(spans) => {
                        println!("   ✅ Extracted {} spans", spans.len());
                        if !spans.is_empty() {
                            println!("   First 3 spans:");
                            for (i, span) in spans.iter().take(3).enumerate() {
                                println!(
                                    "      {}. \"{}\" at ({:.1}, {:.1})",
                                    i + 1,
                                    span.text.chars().take(30).collect::<String>(),
                                    span.bbox.x,
                                    span.bbox.y
                                );
                            }
                        } else {
                            println!("   ⚠️  No spans extracted - might be scanned image");
                        }
                    },
                    Err(e) => {
                        println!("   ❌ Span extraction failed: {}", e);
                    },
                }

                // Try markdown extraction
                println!("\n4️⃣ Testing markdown extraction...");
                match doc.to_markdown(0, &pdf_oxide::converters::ConversionOptions::default()) {
                    Ok(markdown) => {
                        println!("   ✅ Extracted {} chars", markdown.len());
                        if !markdown.is_empty() {
                            let preview = markdown.chars().take(200).collect::<String>();
                            println!("   Preview: {}", preview);
                        }
                    },
                    Err(e) => {
                        println!("   ❌ Markdown extraction failed: {}", e);
                    },
                }
            },
            Err(e) => {
                println!("❌ Failed to open PDF: {}", e);
            },
        }

        println!("\n");
    }

    println!("\n=== Diagnosis Complete ===");
    Ok(())
}
