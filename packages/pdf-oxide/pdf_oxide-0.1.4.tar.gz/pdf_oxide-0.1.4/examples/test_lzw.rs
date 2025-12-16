//! Test LZW decoding on real PDF data.

use pdf_oxide::decoders::{Ascii85Decoder, LzwDecoder, StreamDecoder};
use std::fs;

fn main() {
    env_logger::init();

    println!("Testing LZW decoding...\n");

    // Read the LZW input (ASCII85 already decoded)
    let lzw_data = fs::read("/tmp/lzw_input.bin").expect("Failed to read /tmp/lzw_input.bin");
    println!("LZW input size: {} bytes", lzw_data.len());
    println!("First 50 bytes: {:02X?}", &lzw_data[..50.min(lzw_data.len())]);

    // Try to decode with our LZW decoder
    let decoder = LzwDecoder;
    match decoder.decode(&lzw_data) {
        Ok(decoded) => {
            println!("\n✓ LZW decode SUCCESS!");
            println!("  Decoded size: {} bytes", decoded.len());
            println!(
                "  First 200 chars: {}",
                String::from_utf8_lossy(&decoded[..200.min(decoded.len())])
            );
        },
        Err(e) => {
            eprintln!("\n✗ LZW decode FAILED: {}", e);
            eprintln!("  Error details: {:?}", e);
        },
    }

    // Also test the full pipeline
    println!("\n\n=== Testing full pipeline (ASCII85 + LZW) ===");

    let pdf_path = "../pdf_oxide_tests/pdfs/mixed/45W73IZ4UHYYGASU2Y4JO6Q7SC56OPTI.pdf";
    let pdf_data = fs::read(pdf_path).expect("Failed to read PDF");

    // Find stream 3
    let obj_start = pdf_data.windows(7).position(|w| w == b"3 0 obj").unwrap();
    let stream_start = pdf_data[obj_start..]
        .windows(7)
        .position(|w| w == b"stream\n")
        .unwrap()
        + obj_start
        + 7;
    let stream_end = pdf_data[stream_start..]
        .windows(9)
        .position(|w| w == b"endstream")
        .unwrap()
        + stream_start;
    let stream_data = &pdf_data[stream_start..stream_end];

    println!("Stream size: {} bytes", stream_data.len());

    // Decode ASCII85 first
    let ascii85 = Ascii85Decoder;
    match ascii85.decode(stream_data) {
        Ok(after_ascii85) => {
            println!("✓ ASCII85 decoded: {} bytes", after_ascii85.len());

            // Now LZW
            match decoder.decode(&after_ascii85) {
                Ok(decoded) => {
                    println!("✓ LZW decoded: {} bytes", decoded.len());
                    println!("\nDecoded text preview:");
                    println!("{}", String::from_utf8_lossy(&decoded[..500.min(decoded.len())]));
                },
                Err(e) => {
                    eprintln!("✗ LZW decode failed: {}", e);
                },
            }
        },
        Err(e) => {
            eprintln!("✗ ASCII85 decode failed: {}", e);
        },
    }
}
