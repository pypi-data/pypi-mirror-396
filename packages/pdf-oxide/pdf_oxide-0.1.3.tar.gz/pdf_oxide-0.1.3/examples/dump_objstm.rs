//! Dump object stream decompressed data to analyze corruption
//!
//! This helps us understand what's in the compressed stream that's causing parsing failures

use pdf_oxide::{Error, PdfDocument};
use std::fs;

fn main() -> Result<(), Error> {
    let test_files = vec![
        ("../pdf_oxide_tests/pdfs/newspapers/IA_0001-cdc-2015-american-tour.pdf", 11),
        ("../pdf_oxide_tests/pdfs/newspapers/IA_0001-cdc-2018-american-tour.pdf", 10),
        ("../pdf_oxide_tests/pdfs/newspapers/IA_0001-chambers-museum.pdf", 31),
    ];

    for (file_path, objstm_id) in test_files {
        println!("\n========================================");
        println!("File: {}", file_path);
        println!("Object Stream ID: {}", objstm_id);
        println!("========================================\n");

        if !std::path::Path::new(file_path).exists() {
            println!("⚠️  File not found, skipping\n");
            continue;
        }

        match PdfDocument::open(file_path) {
            Ok(mut doc) => {
                // Load the object stream
                let obj_ref = pdf_oxide::object::ObjectRef::new(objstm_id, 0);
                match doc.load_object(obj_ref) {
                    Ok(obj) => {
                        println!("✅ Loaded object {}", objstm_id);

                        // Check if it's a stream
                        match &obj {
                            pdf_oxide::object::Object::Stream { dict, .. } => {
                                println!("\n📋 Stream Dictionary:");
                                for (key, value) in dict.iter() {
                                    println!("  /{}: {:?}", key, value);
                                }

                                // Try to decode the stream
                                println!("\n🔓 Attempting to decode stream...");
                                match obj.decode_stream_data() {
                                    Ok(decoded) => {
                                        println!(
                                            "✅ Decompression succeeded: {} bytes",
                                            decoded.len()
                                        );

                                        // Dump first 500 bytes as hex + ASCII
                                        println!("\n📄 First 500 bytes (hex + ASCII):");
                                        let dump_len = decoded.len().min(500);
                                        for (i, chunk) in decoded[..dump_len].chunks(16).enumerate()
                                        {
                                            print!("{:08x}  ", i * 16);

                                            // Hex
                                            for (j, byte) in chunk.iter().enumerate() {
                                                print!("{:02x} ", byte);
                                                if j == 7 {
                                                    print!(" ");
                                                }
                                            }

                                            // Pad if last chunk is short
                                            for _ in chunk.len()..16 {
                                                print!("   ");
                                            }

                                            print!(" |");

                                            // ASCII
                                            for byte in chunk {
                                                let ch = if *byte >= 32 && *byte <= 126 {
                                                    *byte as char
                                                } else {
                                                    '.'
                                                };
                                                print!("{}", ch);
                                            }

                                            println!("|");
                                        }

                                        // Try to parse as UTF-8 string
                                        println!("\n📝 As UTF-8 (lossy, first 500 bytes):");
                                        let text = String::from_utf8_lossy(&decoded[..dump_len]);
                                        println!("{}", text);

                                        // Save to file for detailed inspection
                                        let filename = format!(
                                            "/tmp/objstm_{}_{}.bin",
                                            file_path.split('/').next_back().unwrap_or("unknown"),
                                            objstm_id
                                        );
                                        match fs::write(&filename, &decoded) {
                                            Ok(_) => println!(
                                                "\n💾 Saved full decompressed data to: {}",
                                                filename
                                            ),
                                            Err(e) => println!("\n⚠️  Failed to save: {}", e),
                                        }

                                        // Extract N and First parameters
                                        if let Some(n) = dict.get("N").and_then(|o| o.as_integer())
                                        {
                                            if let Some(first) =
                                                dict.get("First").and_then(|o| o.as_integer())
                                            {
                                                println!("\n🔍 Attempting to parse pairs section:");
                                                println!("   /N (number of objects): {}", n);
                                                println!(
                                                    "   /First (offset to objects): {}",
                                                    first
                                                );

                                                if (first as usize) <= decoded.len() {
                                                    let pairs_data = &decoded[..first as usize];
                                                    println!(
                                                        "\n   Pairs section ({} bytes):",
                                                        pairs_data.len()
                                                    );
                                                    print!("   Hex: ");
                                                    for byte in pairs_data.iter().take(100) {
                                                        print!("{:02x} ", byte);
                                                    }
                                                    println!();
                                                    println!(
                                                        "   ASCII: {}",
                                                        String::from_utf8_lossy(pairs_data)
                                                    );

                                                    // Try to manually parse integers
                                                    let pairs_str =
                                                        String::from_utf8_lossy(pairs_data);
                                                    let tokens: Vec<&str> =
                                                        pairs_str.split_whitespace().collect();
                                                    println!(
                                                        "\n   Tokens found: {} (expected {} for {} pairs)",
                                                        tokens.len(),
                                                        n * 2,
                                                        n
                                                    );

                                                    if !tokens.is_empty() {
                                                        println!(
                                                            "   First 10 tokens: {:?}",
                                                            &tokens[..tokens.len().min(10)]
                                                        );
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    Err(e) => {
                                        println!("❌ Decompression failed: {}", e);
                                    },
                                }
                            },
                            _ => {
                                println!("❌ Object {} is not a stream", objstm_id);
                            },
                        }
                    },
                    Err(e) => {
                        println!("❌ Failed to load object {}: {}", objstm_id, e);
                    },
                }
            },
            Err(e) => {
                println!("❌ Failed to open PDF: {}", e);
            },
        }
    }

    println!("\n========================================");
    println!("Diagnostic complete");
    println!("========================================");
    Ok(())
}
