//! Debug tool to diagnose page detection issues
//!
//! Usage: cargo run --example debug_page_detection <pdf_path>

use pdf_oxide::document::PdfDocument;
use pdf_oxide::object::Object;
use std::env;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::init();

    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        eprintln!("Usage: {} <pdf_path>", args[0]);
        std::process::exit(1);
    }

    let path = &args[1];
    println!("=== Debugging PDF: {} ===\n", path);

    // Open the document
    let mut doc = match PdfDocument::open(path) {
        Ok(d) => {
            println!("✓ PDF opened successfully");
            println!("  Version: {}.{}", d.version().0, d.version().1);
            d
        },
        Err(e) => {
            eprintln!("✗ Failed to open PDF: {}", e);
            return Err(e.into());
        },
    };

    println!();

    // Try to load catalog
    println!("=== Loading Catalog ===");
    let catalog = match doc.catalog() {
        Ok(c) => {
            println!("✓ Catalog loaded successfully");
            c
        },
        Err(e) => {
            eprintln!("✗ Failed to load catalog: {}", e);
            return Err(e.into());
        },
    };

    // Print catalog contents
    if let Some(cat_dict) = catalog.as_dict() {
        println!("  Catalog keys: {:?}", cat_dict.keys().collect::<Vec<_>>());

        // Check for Pages entry
        if let Some(pages_entry) = cat_dict.get("Pages") {
            println!("  Pages entry found: {:?}", pages_entry);

            // If it's a reference, try to load it
            if let Some(pages_ref) = pages_entry.as_reference() {
                println!("  Pages reference: {}", pages_ref);

                match doc.load_object(pages_ref) {
                    Ok(pages_obj) => {
                        println!("  ✓ Pages object loaded successfully");

                        if let Some(pages_dict) = pages_obj.as_dict() {
                            println!(
                                "  Pages object keys: {:?}",
                                pages_dict.keys().collect::<Vec<_>>()
                            );

                            // Check Type
                            if let Some(type_val) = pages_dict.get("Type") {
                                println!("  /Type: {:?}", type_val);
                            } else {
                                println!("  ✗ WARNING: No /Type field in Pages object");
                            }

                            // Check Count
                            if let Some(count_val) = pages_dict.get("Count") {
                                println!("  /Count: {:?}", count_val);
                                if let Some(count_int) = count_val.as_integer() {
                                    println!("  Page count from /Count: {}", count_int);
                                }
                            } else {
                                println!("  ✗ WARNING: No /Count field in Pages object");
                            }

                            // Check Kids
                            if let Some(kids_val) = pages_dict.get("Kids") {
                                println!("  /Kids: {:?}", kids_val);
                                if let Some(kids_array) = kids_val.as_array() {
                                    println!("  Kids array length: {}", kids_array.len());
                                    for (i, kid) in kids_array.iter().enumerate() {
                                        println!("    Kid[{}]: {:?}", i, kid);
                                    }
                                }
                            } else {
                                println!("  ✗ WARNING: No /Kids field in Pages object");
                            }
                        } else {
                            println!(
                                "  ✗ ERROR: Pages object is not a dictionary, it's: {:?}",
                                get_object_type(&pages_obj)
                            );
                        }
                    },
                    Err(e) => {
                        eprintln!("  ✗ Failed to load Pages object: {}", e);
                    },
                }
            } else {
                println!("  ✗ ERROR: Pages entry is not a reference: {:?}", pages_entry);
            }
        } else {
            println!("  ✗ ERROR: No Pages entry in catalog");
        }
    } else {
        println!("  ✗ ERROR: Catalog is not a dictionary");
    }

    println!();

    // Try to get page count using standard method
    println!("=== Testing page_count() method ===");
    match doc.page_count() {
        Ok(count) => {
            println!("✓ page_count() returned: {}", count);
        },
        Err(e) => {
            eprintln!("✗ page_count() failed: {}", e);
        },
    }

    Ok(())
}

fn get_object_type(obj: &Object) -> &'static str {
    match obj {
        Object::Null => "Null",
        Object::Boolean(_) => "Boolean",
        Object::Integer(_) => "Integer",
        Object::Real(_) => "Real",
        Object::String(_) => "String",
        Object::Name(_) => "Name",
        Object::Array(_) => "Array",
        Object::Dictionary(_) => "Dictionary",
        Object::Stream { .. } => "Stream",
        Object::Reference(_) => "Reference",
    }
}
