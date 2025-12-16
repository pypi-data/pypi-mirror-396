//! Heading detection using font clustering.
//!
//! This module classifies text blocks into heading levels (H1, H2, H3) or body text
//! based on font size, weight, and other typographic features.

use crate::layout::text_block::TextBlock;
use std::collections::HashMap;

/// Classification of text block hierarchy.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum HeadingLevel {
    /// Main heading (largest, often bold)
    H1,
    /// Section heading
    H2,
    /// Subsection heading
    H3,
    /// Regular body text
    Body,
    /// Small text (footnotes, captions, etc.)
    Small,
}

/// Detect heading levels for a collection of text blocks.
///
/// This analyzes font sizes and weights across all blocks to classify
/// each block as a heading level or body text.
///
/// # Arguments
///
/// * `blocks` - The text blocks to classify
///
/// # Returns
///
/// A vector of heading levels, one per block.
///
/// # Examples
///
/// ```ignore
/// use pdf_oxide::geometry::Rect;
/// use pdf_oxide::layout::{TextChar, TextBlock, FontWeight, Color};
/// use pdf_oxide::layout::heading_detector::{detect_headings, HeadingLevel};
///
/// let chars1 = vec![
///     TextChar {
///         char: 'T',
///         bbox: Rect::new(0.0, 0.0, 10.0, 24.0),
///         font_name: "Times".to_string(),
///         font_size: 24.0,
///         font_weight: FontWeight::Bold,
///         color: Color::black(),
///     },
/// ];
/// let title = TextBlock::from_chars(chars1);
///
/// let chars2 = vec![
///     TextChar {
///         char: 'B',
///         bbox: Rect::new(0.0, 30.0, 10.0, 12.0),
///         font_name: "Times".to_string(),
///         font_size: 12.0,
///         font_weight: FontWeight::Normal,
///         color: Color::black(),
///     },
/// ];
/// let body = TextBlock::from_chars(chars2);
///
/// let blocks = vec![title, body];
/// let levels = detect_headings(&blocks);
///
/// assert_eq!(levels[0], HeadingLevel::H1);
/// assert_eq!(levels[1], HeadingLevel::Body);
/// ```ignore
pub fn detect_headings(blocks: &[TextBlock]) -> Vec<HeadingLevel> {
    if blocks.is_empty() {
        return vec![];
    }

    // Cluster font sizes to identify distinct levels
    let size_clusters = cluster_font_sizes(blocks);

    // Classify each block based on its font features
    blocks
        .iter()
        .enumerate()
        .map(|(i, block)| classify_block(block, &size_clusters, i))
        .collect()
}

/// Cluster font sizes to identify distinct typographic levels.
///
/// Returns a map from block index to its size cluster.
fn cluster_font_sizes(blocks: &[TextBlock]) -> HashMap<usize, usize> {
    let sizes: Vec<f32> = blocks.iter().map(|b| b.avg_font_size).collect();

    // Find unique sizes and group similar ones
    let mut unique_sizes: Vec<f32> = sizes.clone();
    unique_sizes.sort_by(|a, b| b.partial_cmp(a).unwrap()); // Descending order
    unique_sizes.dedup_by(|a, b| (*a - *b).abs() < 1.0); // Merge sizes within 1pt

    // Assign each block to nearest size cluster
    let mut clusters = HashMap::new();
    for (i, &size) in sizes.iter().enumerate() {
        // Find nearest unique size
        let cluster_id = unique_sizes
            .iter()
            .position(|&s| (s - size).abs() < 1.5)
            .unwrap_or(0);

        clusters.insert(i, cluster_id);
    }

    clusters
}

/// Classify a single block based on font features.
///
/// Uses rule-based classification considering:
/// - Font size (absolute and relative to other blocks)
/// - Font weight (bold vs normal)
/// - Font size clusters
fn classify_block(
    block: &TextBlock,
    size_clusters: &HashMap<usize, usize>,
    block_idx: usize,
) -> HeadingLevel {
    let size = block.avg_font_size;
    let is_bold = block.is_bold;
    let _cluster = size_clusters.get(&block_idx).copied().unwrap_or(0);

    // Rule-based classification with thresholds
    // These thresholds are typical for academic papers and documents

    if size >= 22.0 && is_bold {
        // Very large bold text -> H1 (title)
        HeadingLevel::H1
    } else if size >= 18.0 && is_bold {
        // Large bold text -> H2 (section heading)
        HeadingLevel::H2
    } else if size >= 16.0 && is_bold {
        // Medium-large bold -> H2 (section heading)
        HeadingLevel::H2
    } else if size >= 14.0 && is_bold {
        // Medium bold -> H3 (subsection heading)
        HeadingLevel::H3
    } else if size >= 14.0 && !is_bold {
        // Medium normal -> could be H3 or body, default to body
        HeadingLevel::Body
    } else if size < 9.0 {
        // Very small text -> footnotes, captions, etc.
        HeadingLevel::Small
    } else {
        // Default: regular body text
        HeadingLevel::Body
    }
}

/// Get a numeric hierarchy level for sorting (lower = higher in hierarchy).
impl HeadingLevel {
    /// Get the hierarchy level as a number (0 = H1, 1 = H2, ..., 4 = Small).
    ///
    /// # Examples
    ///
    /// ```
    /// use pdf_oxide::layout::heading_detector::HeadingLevel;
    ///
    /// assert_eq!(HeadingLevel::H1.hierarchy_level(), 0);
    /// assert_eq!(HeadingLevel::H2.hierarchy_level(), 1);
    /// assert_eq!(HeadingLevel::Body.hierarchy_level(), 3);
    /// ```
    pub fn hierarchy_level(&self) -> u8 {
        match self {
            HeadingLevel::H1 => 0,
            HeadingLevel::H2 => 1,
            HeadingLevel::H3 => 2,
            HeadingLevel::Body => 3,
            HeadingLevel::Small => 4,
        }
    }

    /// Check if this is a heading (H1, H2, or H3).
    ///
    /// # Examples
    ///
    /// ```
    /// use pdf_oxide::layout::heading_detector::HeadingLevel;
    ///
    /// assert!(HeadingLevel::H1.is_heading());
    /// assert!(HeadingLevel::H2.is_heading());
    /// assert!(!HeadingLevel::Body.is_heading());
    /// ```
    pub fn is_heading(&self) -> bool {
        matches!(self, HeadingLevel::H1 | HeadingLevel::H2 | HeadingLevel::H3)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::geometry::Rect;
    use crate::layout::{Color, FontWeight, TextChar};

    fn mock_block_with_font(text: &str, size: f32, bold: bool) -> TextBlock {
        let weight = if bold {
            FontWeight::Bold
        } else {
            FontWeight::Normal
        };

        let chars: Vec<TextChar> = text
            .chars()
            .enumerate()
            .map(|(i, c)| TextChar {
                char: c,
                bbox: Rect::new(i as f32 * 10.0, 0.0, 10.0, size),
                font_name: "Times".to_string(),
                font_size: size,
                font_weight: weight,
                color: Color::black(),
                mcid: None,
            })
            .collect();

        TextBlock::from_chars(chars)
    }

    #[test]
    fn test_classify_h1() {
        let block = mock_block_with_font("Title", 24.0, true);
        let blocks = vec![block];
        let levels = detect_headings(&blocks);

        assert_eq!(levels[0], HeadingLevel::H1);
    }

    #[test]
    fn test_classify_h2() {
        let block = mock_block_with_font("Section", 18.0, true);
        let blocks = vec![block];
        let levels = detect_headings(&blocks);

        assert_eq!(levels[0], HeadingLevel::H2);
    }

    #[test]
    fn test_classify_h3() {
        let block = mock_block_with_font("Subsection", 14.0, true);
        let blocks = vec![block];
        let levels = detect_headings(&blocks);

        assert_eq!(levels[0], HeadingLevel::H3);
    }

    #[test]
    fn test_classify_body() {
        let block = mock_block_with_font("Regular text", 12.0, false);
        let blocks = vec![block];
        let levels = detect_headings(&blocks);

        assert_eq!(levels[0], HeadingLevel::Body);
    }

    #[test]
    fn test_classify_small() {
        let block = mock_block_with_font("Footnote", 8.0, false);
        let blocks = vec![block];
        let levels = detect_headings(&blocks);

        assert_eq!(levels[0], HeadingLevel::Small);
    }

    #[test]
    fn test_mixed_document() {
        let blocks = vec![
            mock_block_with_font("Main Title", 24.0, true),   // H1
            mock_block_with_font("Introduction", 18.0, true), // H2
            mock_block_with_font("Background", 14.0, true),   // H3
            mock_block_with_font("Lorem ipsum dolor", 12.0, false), // Body
            mock_block_with_font("Figure 1: Caption", 8.0, false), // Small
        ];

        let levels = detect_headings(&blocks);

        assert_eq!(levels[0], HeadingLevel::H1);
        assert_eq!(levels[1], HeadingLevel::H2);
        assert_eq!(levels[2], HeadingLevel::H3);
        assert_eq!(levels[3], HeadingLevel::Body);
        assert_eq!(levels[4], HeadingLevel::Small);
    }

    #[test]
    fn test_hierarchy_level() {
        assert_eq!(HeadingLevel::H1.hierarchy_level(), 0);
        assert_eq!(HeadingLevel::H2.hierarchy_level(), 1);
        assert_eq!(HeadingLevel::H3.hierarchy_level(), 2);
        assert_eq!(HeadingLevel::Body.hierarchy_level(), 3);
        assert_eq!(HeadingLevel::Small.hierarchy_level(), 4);
    }

    #[test]
    fn test_is_heading() {
        assert!(HeadingLevel::H1.is_heading());
        assert!(HeadingLevel::H2.is_heading());
        assert!(HeadingLevel::H3.is_heading());
        assert!(!HeadingLevel::Body.is_heading());
        assert!(!HeadingLevel::Small.is_heading());
    }

    #[test]
    fn test_detect_headings_empty() {
        let blocks: Vec<TextBlock> = vec![];
        let levels = detect_headings(&blocks);
        assert_eq!(levels.len(), 0);
    }
}
