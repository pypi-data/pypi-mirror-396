//! Dump raw stream bytes from corrupt PDF object

use pdf_oxide::PdfDocument;
use std::fs;

fn main() {
    let path = "../pdf_oxide_tests/pdfs/mixed/TYLWGSX5OYKE27DHTQXUJTBMKMHMKY3B.pdf";

    println!("==> Opening PDF");
    let mut doc = PdfDocument::open(path).unwrap();

    // Load the page
    doc.page_count().unwrap();

    // Object 76 is the content stream (from debug log)
    println!("\n==> Loading object 76 (content stream)");

    // Read the raw file to find object 76's stream
    let file_data = fs::read(path).unwrap();

    // Find "76 0 obj" in file
    let needle = b"76 0 obj";
    let mut pos = 0;
    for i in 0..file_data.len() - needle.len() {
        if &file_data[i..i + needle.len()] == needle {
            pos = i;
            break;
        }
    }

    println!("Found object 76 at byte {}", pos);

    // Find "stream" marker
    let stream_marker = b"\nstream\n";
    let mut stream_start = 0;
    for i in pos..std::cmp::min(pos + 500, file_data.len()) {
        if file_data[i..].starts_with(stream_marker) {
            stream_start = i + stream_marker.len();
            break;
        }
    }

    // Also check for \r\nstream\r\n
    let stream_marker_cr = b"\r\nstream\r\n";
    for i in pos..std::cmp::min(pos + 500, file_data.len()) {
        if file_data[i..].starts_with(stream_marker_cr) {
            stream_start = i + stream_marker_cr.len();
            break;
        }
    }

    println!("Stream starts at byte {}", stream_start);

    // Dump first 500 bytes of stream
    let stream_data = &file_data[stream_start..std::cmp::min(stream_start + 500, file_data.len())];

    println!("\n==> First 500 bytes of stream (hex):");
    for (i, chunk) in stream_data.chunks(16).enumerate() {
        print!("{:04x}: ", i * 16);
        for byte in chunk {
            print!("{:02x} ", byte);
        }
        println!();
    }

    println!("\n==> First 500 bytes of stream (raw):");
    println!("{:?}", &stream_data[..std::cmp::min(200, stream_data.len())]);

    // Try to decompress with different methods
    println!("\n==> Trying raw interpretation as text:");
    match std::str::from_utf8(stream_data) {
        Ok(text) => println!("UTF-8 text: {:?}", &text[..std::cmp::min(200, text.len())]),
        Err(e) => println!("Not valid UTF-8: {}", e),
    }

    // Check if it might be a different encoding by looking at byte patterns
    println!("\n==> Stream byte statistics:");
    let mut ascii_count = 0;
    let mut high_byte_count = 0;
    for &byte in stream_data {
        if (32..127).contains(&byte) {
            ascii_count += 1;
        } else if byte >= 128 {
            high_byte_count += 1;
        }
    }
    println!(
        "ASCII printable: {}/{} ({:.1}%)",
        ascii_count,
        stream_data.len(),
        100.0 * ascii_count as f64 / stream_data.len() as f64
    );
    println!(
        "High bytes (>=128): {}/{} ({:.1}%)",
        high_byte_count,
        stream_data.len(),
        100.0 * high_byte_count as f64 / stream_data.len() as f64
    );
}
