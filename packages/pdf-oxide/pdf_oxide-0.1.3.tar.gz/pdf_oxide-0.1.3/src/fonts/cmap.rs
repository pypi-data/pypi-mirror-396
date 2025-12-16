//! ToUnicode CMap parser.
//!
//! CMap (Character Map) streams define the mapping from character codes
//! to Unicode characters. This is essential for text extraction when fonts
//! use custom encodings.
//!
//! Phase 4, Task 4.4

use crate::error::Result;
use regex::Regex;
use std::collections::HashMap;

/// A character map from character codes to Unicode strings.
///
/// Keys are character codes (typically 1-4 bytes), values are Unicode strings.
/// We use u32 to support multi-byte character codes found in CID fonts.
pub type CMap = HashMap<u32, String>;

/// Decode a UTF-16 surrogate pair encoded as a 32-bit value.
///
/// PDF ToUnicode CMaps sometimes encode Unicode code points > U+FFFF
/// as UTF-16 surrogate pairs represented as 8 hex digits.
///
/// Example: D835DF0C (0xD835DF0C) represents:
/// - High surrogate: 0xD835
/// - Low surrogate: 0xDF0C
/// - Decoded: U+1D70C (MATHEMATICAL ITALIC SMALL RHO '𝜌')
///
/// # Arguments
///
/// * `value` - A 32-bit value where the high 16 bits are the high surrogate
///            and the low 16 bits are the low surrogate
///
/// # Returns
///
/// The decoded Unicode character as a String, or None if the surrogate pair is invalid
fn decode_utf16_surrogate_pair(value: u32) -> Option<String> {
    let high = (value >> 16) as u16;
    let low = (value & 0xFFFF) as u16;

    // Check if these are valid surrogate pairs
    // High surrogate: 0xD800 - 0xDBFF
    // Low surrogate: 0xDC00 - 0xDFFF
    if (0xD800..=0xDBFF).contains(&high) && (0xDC00..=0xDFFF).contains(&low) {
        // Decode UTF-16 surrogate pair to Unicode code point
        let codepoint = 0x10000 + (((high & 0x3FF) as u32) << 10) + ((low & 0x3FF) as u32);
        char::from_u32(codepoint).map(|ch| ch.to_string())
    } else {
        // Not a valid surrogate pair, try as a direct code point
        char::from_u32(value).map(|ch| ch.to_string())
    }
}

/// Parse a ToUnicode CMap stream.
///
/// ToUnicode CMaps contain mappings in two formats:
/// - `bfchar`: Single character mappings
/// - `bfrange`: Range mappings
///
/// # Format Examples
///
/// ```text
/// beginbfchar
/// <0041> <0041>  % Maps 0x41 to Unicode U+0041 ('A')
/// <0042> <0042>  % Maps 0x42 to Unicode U+0042 ('B')
/// endbfchar
///
/// beginbfrange
/// <0020> <007E> <0020>  % Maps 0x20-0x7E to U+0020-U+007E (ASCII printable)
/// endbfrange
/// ```
///
/// # Arguments
///
/// * `data` - Raw CMap stream data (should be decoded/decompressed first)
///
/// # Returns
///
/// A HashMap mapping character codes to Unicode strings.
///
/// # Examples
///
/// ```
/// use pdf_oxide::fonts::parse_tounicode_cmap;
///
/// let cmap_data = b"beginbfchar\n<0041> <0041>\nendbfchar";
/// let cmap = parse_tounicode_cmap(cmap_data).unwrap();
/// assert_eq!(cmap.get(&0x41), Some(&"A".to_string()));
/// ```
pub fn parse_tounicode_cmap(data: &[u8]) -> Result<CMap> {
    let mut cmap = HashMap::new();
    let content = String::from_utf8_lossy(data);

    // Parse bfchar sections
    // PDF Spec: ISO 32000-1:2008, Section 9.10.3 - ToUnicode CMaps
    // Format: <srcCode> <dstString>
    for section in extract_sections(&content, "beginbfchar", "endbfchar") {
        for line in section.lines() {
            if let Some((src, dst)) = parse_bfchar_line(line) {
                log::trace!("ToUnicode bfchar: 0x{:02X} -> {:?}", src, dst);
                cmap.insert(src, dst);
            }
        }
    }

    // Parse bfrange sections
    // PDF Spec: ISO 32000-1:2008, Section 9.10.3 - ToUnicode CMaps
    // Format: <srcCodeLo> <srcCodeHi> [<dstString0> <dstString1> ... <dstStringN>]
    //     or: <srcCodeLo> <srcCodeHi> <dstString>
    for section in extract_sections(&content, "beginbfrange", "endbfrange") {
        for line in section.lines() {
            if let Some(mappings) = parse_bfrange_line(line) {
                log::trace!("ToUnicode bfrange: {} mappings parsed", mappings.len());
                for (src, dst) in mappings {
                    cmap.insert(src, dst);
                }
            }
        }
    }

    Ok(cmap)
}

/// Extract sections between begin and end markers.
fn extract_sections<'a>(content: &'a str, begin: &str, end: &str) -> Vec<&'a str> {
    let mut sections = Vec::new();
    let mut remaining = content;

    while let Some(begin_pos) = remaining.find(begin) {
        let after_begin = &remaining[begin_pos + begin.len()..];
        if let Some(end_pos) = after_begin.find(end) {
            sections.push(&after_begin[..end_pos]);
            remaining = &after_begin[end_pos + end.len()..];
        } else {
            break;
        }
    }

    sections
}

/// Parse a bfchar line: `<src> <dst>`
///
/// Example: `<0041> <0041>` maps character code 0x41 to Unicode U+0041.
/// Example: `<0003> <00410042>` maps character code 0x03 to Unicode "AB" (multi-char mapping).
/// Example: `<D840DC3E> <20C49>` maps 4-byte character code to Unicode (for CID fonts).
fn parse_bfchar_line(line: &str) -> Option<(u32, String)> {
    lazy_static::lazy_static! {
        static ref RE: Regex = Regex::new(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>").unwrap();
    }

    RE.captures(line).and_then(|caps| {
        // Parse source character code (1-4 bytes)
        let src = u32::from_str_radix(&caps[1], 16).ok()?;

        // Parse destination - could be one Unicode code point or multiple
        let dst_hex = &caps[2];

        // Handle different destination formats:
        // - 4 chars or less: single Unicode code point
        // - 8 chars: could be UTF-16 surrogate pair OR two code points
        // - More than 8 chars: multiple code points (ligatures)
        let dst = if dst_hex.len() <= 4 {
            let dst_code = u32::from_str_radix(dst_hex, 16).ok()?;
            char::from_u32(dst_code)?.to_string()
        } else if dst_hex.len() == 8 {
            // 8 hex digits - try UTF-16 surrogate pair first
            let dst_code = u32::from_str_radix(dst_hex, 16).ok()?;
            if let Some(decoded) = decode_utf16_surrogate_pair(dst_code) {
                decoded
            } else {
                // Fall back to two separate 4-digit code points (ligature)
                let mut result = String::new();
                if let Ok(code1) = u32::from_str_radix(&dst_hex[0..4], 16) {
                    if let Some(ch) = char::from_u32(code1) {
                        result.push(ch);
                    }
                }
                if let Ok(code2) = u32::from_str_radix(&dst_hex[4..8], 16) {
                    if let Some(ch) = char::from_u32(code2) {
                        result.push(ch);
                    }
                }
                if result.is_empty() {
                    return None;
                }
                result
            }
        } else {
            // Multi-character mapping (ligatures) - split into 4-char chunks
            let mut result = String::new();
            for i in (0..dst_hex.len()).step_by(4) {
                let end = (i + 4).min(dst_hex.len());
                if let Ok(code) = u32::from_str_radix(&dst_hex[i..end], 16) {
                    if let Some(ch) = char::from_u32(code) {
                        result.push(ch);
                    }
                }
            }
            if result.is_empty() {
                return None;
            }
            result
        };

        Some((src, dst))
    })
}

/// Parse a bfrange line: `<start> <end> <dst>`
///
/// Example: `<0020> <007E> <0020>` maps codes 0x20-0x7E to Unicode U+0020-U+007E.
///
/// There are two formats:
/// 1. `<start> <end> <dst>` - Sequential mapping starting at dst
/// 2. `<start> <end> [<dst1> <dst2> ...]` - Array of individual destinations
///
/// This function supports both formats.
fn parse_bfrange_line(line: &str) -> Option<Vec<(u32, String)>> {
    lazy_static::lazy_static! {
        // Format 1: <start> <end> <dst>
        static ref RE_SEQ: Regex = Regex::new(
            r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>"
        ).unwrap();
        // Format 2: <start> <end> [<dst1> <dst2> ...]
        static ref RE_ARRAY: Regex = Regex::new(
            r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*\[((?:\s*<[0-9A-Fa-f]+>\s*)+)\]"
        ).unwrap();
    }

    // Try format 2 first (array format)
    // Example: <005F> <0061> [<00660066> <00660069> <00660066006C>]
    // Maps codes 0x5F, 0x60, 0x61 to "ff", "fi", "ffl" respectively
    if let Some(caps) = RE_ARRAY.captures(line) {
        let start = u32::from_str_radix(&caps[1], 16).ok()?;
        let end = u32::from_str_radix(&caps[2], 16).ok()?;
        let array_str = &caps[3];

        // Extract all destination hex strings from array
        // Each can be a single Unicode code point OR multiple code points (for ligatures)
        lazy_static::lazy_static! {
            static ref RE_HEX: Regex = Regex::new(r"<([0-9A-Fa-f]+)>").unwrap();
        }
        let dst_hexes: Vec<&str> = RE_HEX
            .captures_iter(array_str)
            .map(|cap| cap.get(1).unwrap().as_str())
            .collect();

        let mut result = Vec::new();
        let range_size = (end - start + 1) as usize;

        // SPEC VALIDATION: PDF Spec ISO 32000-1:2008, Section 9.10.3
        // The array must have exactly (end - start + 1) entries.
        // Current behavior (lenient): Use what's available, ignore extras/missing.
        // Proper strict mode: Should fail if array size doesn't match range_size.
        if dst_hexes.len() != range_size {
            log::warn!(
                "ToUnicode bfrange array size mismatch: expected {} entries for range 0x{:X}-0x{:X}, got {}",
                range_size,
                start,
                end,
                dst_hexes.len()
            );
        }

        for (i, &dst_hex) in dst_hexes.iter().take(range_size).enumerate() {
            let src = start + i as u32;

            // Parse destination - could be one Unicode code point, UTF-16 surrogate, or multiple (ligature)
            let dst = if dst_hex.len() <= 4 {
                // Single Unicode code point
                let dst_code = u32::from_str_radix(dst_hex, 16).ok()?;
                char::from_u32(dst_code)?.to_string()
            } else if dst_hex.len() == 8 {
                // 8 hex digits - try UTF-16 surrogate pair first
                let dst_code = u32::from_str_radix(dst_hex, 16).ok()?;
                if let Some(decoded) = decode_utf16_surrogate_pair(dst_code) {
                    decoded
                } else {
                    // Fall back to two separate code points (ligature)
                    let mut unicode_string = String::new();
                    if let Ok(code) = u32::from_str_radix(&dst_hex[0..4], 16) {
                        if let Some(ch) = char::from_u32(code) {
                            unicode_string.push(ch);
                        }
                    }
                    if let Ok(code) = u32::from_str_radix(&dst_hex[4..8], 16) {
                        if let Some(ch) = char::from_u32(code) {
                            unicode_string.push(ch);
                        }
                    }
                    if unicode_string.is_empty() {
                        continue;
                    }
                    unicode_string
                }
            } else {
                // Multi-character mapping (e.g., "ffi", "ffl" for ligatures)
                // Split into 4-char chunks, each representing one Unicode code point
                let mut unicode_string = String::new();
                for chunk_start in (0..dst_hex.len()).step_by(4) {
                    let chunk_end = (chunk_start + 4).min(dst_hex.len());
                    if let Ok(code) = u32::from_str_radix(&dst_hex[chunk_start..chunk_end], 16) {
                        if let Some(ch) = char::from_u32(code) {
                            unicode_string.push(ch);
                        }
                    }
                }
                if unicode_string.is_empty() {
                    continue; // Skip this mapping if parsing failed
                }
                unicode_string
            };

            result.push((src, dst));
        }
        return Some(result);
    }

    // Try format 1 (sequential format)
    if let Some(caps) = RE_SEQ.captures(line) {
        let start = u32::from_str_radix(&caps[1], 16).ok()?;
        let end = u32::from_str_radix(&caps[2], 16).ok()?;
        let dst_start = u32::from_str_radix(&caps[3], 16).ok()?;

        let mut result = Vec::new();
        let range_size = end.saturating_sub(start).min(10000); // Safety limit
        for i in 0..=range_size {
            let src = start.wrapping_add(i);
            let dst_code = dst_start.wrapping_add(i);

            // Try to decode as UTF-16 surrogate pair first (for values > 0xFFFF)
            let unicode_string = if dst_code > 0xFFFF {
                decode_utf16_surrogate_pair(dst_code)
            } else {
                // Normal Unicode code point
                char::from_u32(dst_code).map(|ch| ch.to_string())
            };

            if let Some(s) = unicode_string {
                result.push((src, s));
            }
        }
        return Some(result);
    }

    None
}

/// Parse a CID to Unicode mapping (simplified version for CID fonts).
///
/// This is a wrapper around `parse_tounicode_cmap` for consistency.
pub fn parse_cid_to_unicode(data: &[u8]) -> Result<CMap> {
    parse_tounicode_cmap(data)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_bfchar_single() {
        let data = b"beginbfchar\n<0041> <0041>\nendbfchar";
        let cmap = parse_tounicode_cmap(data).unwrap();
        assert_eq!(cmap.get(&0x41), Some(&"A".to_string()));
    }

    #[test]
    fn test_parse_bfchar_multiple() {
        let data = b"beginbfchar\n<0041> <0041>\n<0042> <0042>\n<0043> <0043>\nendbfchar";
        let cmap = parse_tounicode_cmap(data).unwrap();
        assert_eq!(cmap.get(&0x41), Some(&"A".to_string()));
        assert_eq!(cmap.get(&0x42), Some(&"B".to_string()));
        assert_eq!(cmap.get(&0x43), Some(&"C".to_string()));
    }

    #[test]
    fn test_parse_bfchar_non_ascii() {
        let data = b"beginbfchar\n<00E9> <00E9>\nendbfchar"; // é
        let cmap = parse_tounicode_cmap(data).unwrap();
        assert_eq!(cmap.get(&0xE9), Some(&"é".to_string()));
    }

    #[test]
    fn test_parse_bfrange_simple() {
        let data = b"beginbfrange\n<0041> <0043> <0041>\nendbfrange";
        let cmap = parse_tounicode_cmap(data).unwrap();
        assert_eq!(cmap.get(&0x41), Some(&"A".to_string()));
        assert_eq!(cmap.get(&0x42), Some(&"B".to_string()));
        assert_eq!(cmap.get(&0x43), Some(&"C".to_string()));
    }

    #[test]
    fn test_parse_bfrange_ascii_printable() {
        let data = b"beginbfrange\n<0020> <007E> <0020>\nendbfrange";
        let cmap = parse_tounicode_cmap(data).unwrap();

        // Check space
        assert_eq!(cmap.get(&0x20), Some(&" ".to_string()));
        // Check '0'
        assert_eq!(cmap.get(&0x30), Some(&"0".to_string()));
        // Check 'A'
        assert_eq!(cmap.get(&0x41), Some(&"A".to_string()));
        // Check 'z'
        assert_eq!(cmap.get(&0x7A), Some(&"z".to_string()));
        // Check '~'
        assert_eq!(cmap.get(&0x7E), Some(&"~".to_string()));
    }

    #[test]
    fn test_parse_mixed_bfchar_bfrange() {
        let data = b"beginbfchar\n<0041> <0058>\nendbfchar\nbeginbfrange\n<0042> <0044> <0042>\nendbfrange";
        let cmap = parse_tounicode_cmap(data).unwrap();

        assert_eq!(cmap.get(&0x41), Some(&"X".to_string())); // Custom mapping
        assert_eq!(cmap.get(&0x42), Some(&"B".to_string())); // Range mapping
        assert_eq!(cmap.get(&0x43), Some(&"C".to_string()));
        assert_eq!(cmap.get(&0x44), Some(&"D".to_string()));
    }

    #[test]
    fn test_parse_empty_cmap() {
        let data = b"";
        let cmap = parse_tounicode_cmap(data).unwrap();
        assert!(cmap.is_empty());
    }

    #[test]
    fn test_parse_cmap_with_whitespace() {
        let data = b"beginbfchar\n  <0041>    <0041>  \n  <0042>  <0042>\nendbfchar";
        let cmap = parse_tounicode_cmap(data).unwrap();
        assert_eq!(cmap.get(&0x41), Some(&"A".to_string()));
        assert_eq!(cmap.get(&0x42), Some(&"B".to_string()));
    }

    #[test]
    fn test_parse_bfchar_line() {
        assert_eq!(parse_bfchar_line("<0041> <0041>"), Some((0x41, "A".to_string())));
        assert_eq!(parse_bfchar_line("<00E9> <00E9>"), Some((0xE9, "é".to_string())));
        assert_eq!(parse_bfchar_line("invalid line"), None);
    }

    #[test]
    fn test_parse_bfrange_line() {
        let result = parse_bfrange_line("<0041> <0043> <0041>").unwrap();
        assert_eq!(result.len(), 3);
        assert_eq!(result[0], (0x41, "A".to_string()));
        assert_eq!(result[1], (0x42, "B".to_string()));
        assert_eq!(result[2], (0x43, "C".to_string()));
    }

    #[test]
    fn test_parse_bfrange_line_single_char() {
        let result = parse_bfrange_line("<0041> <0041> <0041>").unwrap();
        assert_eq!(result.len(), 1);
        assert_eq!(result[0], (0x41, "A".to_string()));
    }

    #[test]
    fn test_parse_bfrange_line_invalid() {
        assert!(parse_bfrange_line("invalid").is_none());
    }

    #[test]
    fn test_extract_sections() {
        let content =
            "before\nbeginbfchar\ndata1\nendbfchar\nmiddle\nbeginbfchar\ndata2\nendbfchar\nafter";
        let sections = extract_sections(content, "beginbfchar", "endbfchar");
        assert_eq!(sections.len(), 2);
        assert!(sections[0].contains("data1"));
        assert!(sections[1].contains("data2"));
    }

    #[test]
    fn test_extract_sections_none() {
        let content = "no sections here";
        let sections = extract_sections(content, "beginbfchar", "endbfchar");
        assert_eq!(sections.len(), 0);
    }

    #[test]
    fn test_parse_cid_to_unicode() {
        let data = b"beginbfchar\n<0041> <0041>\nendbfchar";
        let cmap = parse_cid_to_unicode(data).unwrap();
        assert_eq!(cmap.get(&0x41), Some(&"A".to_string()));
    }

    #[test]
    fn test_parse_hex_case_insensitive() {
        let data = b"beginbfchar\n<00aB> <00Ab>\nendbfchar";
        let cmap = parse_tounicode_cmap(data).unwrap();
        assert_eq!(cmap.get(&0xAB), Some(&"«".to_string()));
    }

    #[test]
    fn test_parse_multiple_sections() {
        let data = b"beginbfchar\n<0041> <0041>\nendbfchar\nbeginbfchar\n<0042> <0042>\nendbfchar";
        let cmap = parse_tounicode_cmap(data).unwrap();
        assert_eq!(cmap.len(), 2);
        assert_eq!(cmap.get(&0x41), Some(&"A".to_string()));
        assert_eq!(cmap.get(&0x42), Some(&"B".to_string()));
    }

    #[test]
    fn test_parse_bfchar_ligature() {
        // Test single glyph to multiple characters (ligature expansion)
        let data = b"beginbfchar\n<000C> <00660069>\nendbfchar"; // fi ligature
        let cmap = parse_tounicode_cmap(data).unwrap();
        assert_eq!(cmap.get(&0x0C), Some(&"fi".to_string()));
    }

    #[test]
    fn test_parse_bfchar_multiple_ligatures() {
        // Test multiple ligature mappings
        let data =
            b"beginbfchar\n<000B> <00660066>\n<000C> <00660069>\n<000D> <0066006C>\nendbfchar";
        let cmap = parse_tounicode_cmap(data).unwrap();
        assert_eq!(cmap.get(&0x0B), Some(&"ff".to_string())); // ff
        assert_eq!(cmap.get(&0x0C), Some(&"fi".to_string())); // fi
        assert_eq!(cmap.get(&0x0D), Some(&"fl".to_string())); // fl
    }

    #[test]
    fn test_parse_bfrange_array_ligatures() {
        // Test bfrange with array format containing ligature mappings
        // Example from PDF spec: <005F> <0061> [<00660066> <00660069> <00660066006C>]
        let data =
            b"beginbfrange\n<005F> <0061> [<00660066> <00660069> <00660066006C>]\nendbfrange";
        let cmap = parse_tounicode_cmap(data).unwrap();
        assert_eq!(cmap.get(&0x5F), Some(&"ff".to_string())); // code 0x5F -> "ff"
        assert_eq!(cmap.get(&0x60), Some(&"fi".to_string())); // code 0x60 -> "fi"
        assert_eq!(cmap.get(&0x61), Some(&"ffl".to_string())); // code 0x61 -> "ffl"
    }

    #[test]
    fn test_parse_bfrange_array_mixed() {
        // Test bfrange with array containing both single and multi-character mappings
        let data = b"beginbfrange\n<0010> <0012> [<0041> <00660069> <0043>]\nendbfrange";
        let cmap = parse_tounicode_cmap(data).unwrap();
        assert_eq!(cmap.get(&0x10), Some(&"A".to_string())); // code 0x10 -> "A"
        assert_eq!(cmap.get(&0x11), Some(&"fi".to_string())); // code 0x11 -> "fi"
        assert_eq!(cmap.get(&0x12), Some(&"C".to_string())); // code 0x12 -> "C"
    }
}
