//! Structured text extraction with document semantics.
//!
//! This module provides structured extraction that preserves document hierarchy
//! including headers, paragraphs, lists, and formatting information.
//!
//! # Overview
//!
//! Unlike plain text extraction which returns a flat string, structured extraction
//! identifies document elements (headers, paragraphs, lists) and preserves their
//! formatting (bold, italic, font size).
//!
//! # Usage
//!
//! ```ignore
//! use pdf_oxide::PdfDocument;
//! use pdf_oxide::extractors::StructuredExtractor;
//!
//! let mut doc = PdfDocument::open("document.pdf")?;
//! let mut extractor = StructuredExtractor::new();
//! let structured = extractor.extract_page(&mut doc, 0)?;
//!
//! for element in structured.elements {
//!     match element {
//!         DocumentElement::Header { level, text, .. } => {
//!             println!("H{}: {}", level, text);
//!         }
//!         DocumentElement::Paragraph { text, .. } => {
//!             println!("P: {}", text);
//!         }
//!         DocumentElement::List { items, ordered, .. } => {
//!             println!("{} with {} items", if ordered { "OL" } else { "UL" }, items.len());
//!         }
//!     }
//! }
//! # Ok::<(), pdf_oxide::error::Error>(())
//! ```ignore

use crate::document::PdfDocument;
use crate::error::{Error, Result};
use crate::geometry::Rect;
use crate::layout::TextBlock;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// A structured document with semantic elements.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StructuredDocument {
    /// Document elements in reading order
    pub elements: Vec<DocumentElement>,

    /// Page dimensions
    pub page_size: (f32, f32), // (width, height)

    /// Metadata
    pub metadata: DocumentMetadata,
}

/// Document element types with semantic meaning.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum DocumentElement {
    /// Header/title element
    #[serde(rename = "header")]
    Header {
        /// Header level (1-6, where 1 is largest)
        level: u8,
        /// Text content
        text: String,
        /// Text styling
        style: TextStyle,
        /// Bounding box
        bbox: BoundingBox,
    },

    /// Paragraph element
    #[serde(rename = "paragraph")]
    Paragraph {
        /// Text content
        text: String,
        /// Text styling
        style: TextStyle,
        /// Bounding box
        bbox: BoundingBox,
        /// Text alignment (left, center, right, justified)
        alignment: TextAlignment,
    },

    /// List element (ordered or unordered)
    #[serde(rename = "list")]
    List {
        /// List items
        items: Vec<ListItem>,
        /// Whether list is ordered (numbered) or unordered (bullets)
        ordered: bool,
        /// Bounding box
        bbox: BoundingBox,
    },

    /// Table element (future enhancement)
    #[serde(rename = "table")]
    Table {
        /// Number of rows
        rows: usize,
        /// Number of columns
        cols: usize,
        /// Cell data (row-major order)
        cells: Vec<Vec<String>>,
        /// Bounding box
        bbox: BoundingBox,
    },
}

/// List item with optional nesting.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListItem {
    /// Item text
    pub text: String,
    /// Item styling
    pub style: TextStyle,
    /// Nested list (if any)
    pub nested: Option<Box<DocumentElement>>,
    /// Bounding box
    pub bbox: BoundingBox,
}

/// Text styling information.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TextStyle {
    /// Font family name
    pub font_family: String,
    /// Font size in points
    pub font_size: f32,
    /// Bold text
    pub bold: bool,
    /// Italic text
    pub italic: bool,
    /// Text color (RGB 0.0-1.0)
    pub color: (f32, f32, f32),
}

impl Default for TextStyle {
    fn default() -> Self {
        Self {
            font_family: "Unknown".to_string(),
            font_size: 12.0,
            bold: false,
            italic: false,
            color: (0.0, 0.0, 0.0), // black
        }
    }
}

/// Bounding box (x, y, width, height).
pub type BoundingBox = (f32, f32, f32, f32);

/// Text alignment.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum TextAlignment {
    /// Left-aligned
    Left,
    /// Center-aligned
    Center,
    /// Right-aligned
    Right,
    /// Justified
    Justified,
}

/// Document metadata.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DocumentMetadata {
    /// Total number of elements extracted
    pub element_count: usize,
    /// Number of headers
    pub header_count: usize,
    /// Number of paragraphs
    pub paragraph_count: usize,
    /// Number of lists
    pub list_count: usize,
    /// Number of tables
    pub table_count: usize,
}

/// Structured text extractor.
///
/// Converts positioned characters into semantic document elements.
pub struct StructuredExtractor {
    /// Configuration options
    config: ExtractorConfig,
}

/// Extraction configuration.
#[derive(Debug, Clone)]
pub struct ExtractorConfig {
    /// Minimum font size to consider as header (default: 14.0)
    pub min_header_size: f32,
    /// Maximum header levels to detect (default: 6)
    pub max_header_levels: u8,
    /// Vertical gap threshold for paragraph breaks (default: 1.5× avg line height)
    pub paragraph_gap_threshold: f32,
    /// Enable list detection
    pub detect_lists: bool,
    /// Enable table detection (future)
    pub detect_tables: bool,
}

impl Default for ExtractorConfig {
    fn default() -> Self {
        Self {
            min_header_size: 14.0,
            max_header_levels: 6,
            paragraph_gap_threshold: 1.5,
            detect_lists: true,
            detect_tables: false,
        }
    }
}

impl StructuredExtractor {
    /// Create a new structured extractor with default configuration.
    pub fn new() -> Self {
        Self {
            config: ExtractorConfig::default(),
        }
    }

    /// Create a new structured extractor with custom configuration.
    pub fn with_config(config: ExtractorConfig) -> Self {
        Self { config }
    }

    /// Extract structured content from a page.
    ///
    /// # Arguments
    ///
    /// * `document` - The PDF document
    /// * `page_num` - Zero-based page number
    ///
    /// # Returns
    ///
    /// A structured document with semantic elements.
    ///
    /// # Errors
    ///
    /// Returns an error if the page cannot be processed.
    pub fn extract_page(
        &mut self,
        document: &mut PdfDocument,
        page_num: u32,
    ) -> Result<StructuredDocument> {
        // Step 1: Extract text spans (already grouped by PDF text operators)
        let spans = document.extract_spans(page_num as usize)?;

        if spans.is_empty() {
            return Ok(StructuredDocument {
                elements: Vec::new(),
                page_size: (0.0, 0.0),
                metadata: DocumentMetadata {
                    element_count: 0,
                    header_count: 0,
                    paragraph_count: 0,
                    list_count: 0,
                    table_count: 0,
                },
            });
        }

        // Step 2: Convert spans to text blocks (spans are already properly grouped)
        let blocks = self.spans_to_blocks(&spans);

        // Step 3: Analyze font sizes for header detection
        let font_clusters = self.cluster_font_sizes(&blocks);

        // Step 4: Classify blocks as headers or body text
        let classified_blocks = self.classify_blocks(&blocks, &font_clusters);

        // Step 5: Detect lists
        let elements = if self.config.detect_lists {
            self.detect_document_elements(&classified_blocks)?
        } else {
            self.blocks_to_elements(&classified_blocks)
        };

        // Step 6: Calculate page size and metadata
        let page_size = self.calculate_page_size_from_spans(&spans);
        let metadata = self.calculate_metadata(&elements);

        Ok(StructuredDocument {
            elements,
            page_size,
            metadata,
        })
    }

    /// Convert text spans to text blocks.
    ///
    /// Spans are already properly grouped by the PDF content stream operators,
    /// so we just convert the data structure.
    fn spans_to_blocks(&self, spans: &[crate::layout::TextSpan]) -> Vec<TextBlock> {
        spans
            .iter()
            .map(|span| TextBlock {
                chars: Vec::new(), // Not needed for structure detection
                bbox: span.bbox,
                text: span.text.clone(),
                avg_font_size: span.font_size,
                dominant_font: span.font_name.clone(),
                is_bold: span.font_weight == crate::layout::FontWeight::Bold,
                mcid: span.mcid,
            })
            .collect()
    }

    /// Calculate page size from text spans.
    fn calculate_page_size_from_spans(&self, spans: &[crate::layout::TextSpan]) -> (f32, f32) {
        if spans.is_empty() {
            return (0.0, 0.0);
        }

        let mut max_x = 0.0f32;
        let mut max_y = 0.0f32;

        for span in spans {
            max_x = max_x.max(span.bbox.x + span.bbox.width);
            max_y = max_y.max(span.bbox.y + span.bbox.height);
        }

        (max_x, max_y)
    }

    /// Group characters into text blocks (lines/words).
    /// Cluster font sizes to identify header levels.
    fn cluster_font_sizes(&self, blocks: &[TextBlock]) -> HashMap<usize, f32> {
        if blocks.is_empty() {
            return HashMap::new();
        }

        // Step 1: Collect unique font sizes
        let mut font_sizes: Vec<f32> = blocks.iter().map(|b| b.avg_font_size).collect();
        font_sizes.sort_by(|a, b| b.partial_cmp(a).unwrap()); // Descending order
        font_sizes.dedup_by(|a, b| (*a - *b).abs() < 0.5); // Remove near-duplicates

        if font_sizes.is_empty() {
            return HashMap::new();
        }

        log::debug!("Unique font sizes: {:?}", font_sizes);

        // Step 2: Simple k-means clustering with k = min(6, num_sizes)
        let k = std::cmp::min(6, font_sizes.len());

        // Simple approach: Just divide sizes into k groups by sorting
        // Group 0 = largest sizes (H1), Group 1 = second largest (H2), etc.
        let mut clusters: HashMap<usize, f32> = HashMap::new();

        let group_size = (font_sizes.len() as f32 / k as f32).ceil() as usize;

        for (i, &size) in font_sizes.iter().enumerate() {
            let cluster_id = std::cmp::min(i / group_size, k - 1);

            // Only consider as header if >= min_header_size
            if size >= self.config.min_header_size {
                // Use the largest size in this cluster as representative
                let current_rep = clusters.get(&cluster_id).copied().unwrap_or(0.0);
                clusters.insert(cluster_id, current_rep.max(size));
            }
        }

        log::debug!("Font size clusters: {:?}", clusters);
        clusters
    }

    /// Classify blocks as headers or body text.
    fn classify_blocks(
        &self,
        blocks: &[TextBlock],
        clusters: &HashMap<usize, f32>,
    ) -> Vec<ClassifiedBlock> {
        blocks
            .iter()
            .map(|block| {
                let font_size = block.avg_font_size;

                // Find which cluster this block's font size belongs to
                let cluster_id = clusters
                    .iter()
                    .find(|(_, &rep_size)| (font_size - rep_size).abs() < 1.0)
                    .map(|(&id, _)| id);

                let classification = if let Some(cluster_id) = cluster_id {
                    // Check if it's a header
                    if cluster_id < self.config.max_header_levels as usize
                        && font_size >= self.config.min_header_size
                    {
                        BlockType::Header((cluster_id + 1) as u8) // 1-based header levels
                    } else {
                        BlockType::Paragraph
                    }
                } else {
                    // Not in any cluster, default to paragraph
                    BlockType::Paragraph
                };

                ClassifiedBlock {
                    block: block.clone(),
                    classification,
                }
            })
            .collect()
    }

    /// Detect document elements (headers, paragraphs, lists).
    fn detect_document_elements(&self, blocks: &[ClassifiedBlock]) -> Result<Vec<DocumentElement>> {
        let mut elements = Vec::new();
        let mut i = 0;

        while i < blocks.len() {
            let block = &blocks[i];

            // Check if this block starts with a list marker
            let trimmed_text = block.block.text.trim();
            let list_marker_info = self.detect_list_marker(trimmed_text);

            if let Some((is_ordered, marker_len)) = list_marker_info {
                // Start collecting list items
                let mut items = Vec::new();
                let mut list_bbox = block.block.bbox;
                let list_ordered = is_ordered;

                // Add first item
                let item_text = trimmed_text[marker_len..].trim().to_string();
                items.push(ListItem {
                    text: item_text,
                    style: Self::block_to_text_style(&block.block),
                    nested: None,
                    bbox: Self::bbox_from_rect(block.block.bbox),
                });

                // Collect consecutive list items
                i += 1;
                while i < blocks.len() {
                    let next_block = &blocks[i];
                    let next_trimmed = next_block.block.text.trim();

                    if let Some((next_ordered, next_marker_len)) =
                        self.detect_list_marker(next_trimmed)
                    {
                        // Check if it's the same type of list
                        if next_ordered == list_ordered {
                            let next_item_text = next_trimmed[next_marker_len..].trim().to_string();
                            items.push(ListItem {
                                text: next_item_text,
                                style: Self::block_to_text_style(&next_block.block),
                                nested: None,
                                bbox: Self::bbox_from_rect(next_block.block.bbox),
                            });
                            list_bbox = list_bbox.union(&next_block.block.bbox);
                            i += 1;
                        } else {
                            break;
                        }
                    } else {
                        break;
                    }
                }

                // Create list element
                elements.push(DocumentElement::List {
                    items,
                    ordered: list_ordered,
                    bbox: Self::bbox_from_rect(list_bbox),
                });
            } else {
                // Not a list item, convert based on classification
                match block.classification {
                    BlockType::Header(level) => {
                        elements.push(DocumentElement::Header {
                            level,
                            text: block.block.text.clone(),
                            style: Self::block_to_text_style(&block.block),
                            bbox: Self::bbox_from_rect(block.block.bbox),
                        });
                        i += 1;
                    },
                    BlockType::Paragraph => {
                        // Calculate page width from block position (estimate)
                        let page_width = block.block.bbox.x + block.block.bbox.width + 100.0;
                        let alignment = self.detect_alignment(&block.block, page_width);

                        elements.push(DocumentElement::Paragraph {
                            text: block.block.text.clone(),
                            style: Self::block_to_text_style(&block.block),
                            bbox: Self::bbox_from_rect(block.block.bbox),
                            alignment,
                        });
                        i += 1;
                    },
                    _ => {
                        i += 1;
                    },
                }
            }
        }

        Ok(elements)
    }

    /// Detect list marker at the beginning of text.
    /// Returns (is_ordered, marker_length) if found.
    fn detect_list_marker(&self, text: &str) -> Option<(bool, usize)> {
        let text_bytes = text.as_bytes();
        if text_bytes.is_empty() {
            return None;
        }

        // Bullet markers (unordered)
        let bullet_markers = ['•', '-', '*', '◦', '▪', '►'];
        if let Some(first_char) = text.chars().next() {
            if bullet_markers.contains(&first_char) {
                // Found bullet marker
                let marker_len = first_char.len_utf8();
                return Some((false, marker_len));
            }
        }

        // Numbered markers (ordered)
        // Pattern: digit(s) + '.' or ')'  or  letter + '.' or ')'
        // Examples: "1.", "2)", "a.", "b)", "i.", "ii.", "(1)", "(a)"

        // Check for parenthesized numbers/letters: "(1)", "(a)"
        if text_bytes[0] == b'(' {
            let mut end_idx = 1;
            while end_idx < text_bytes.len() && text_bytes[end_idx].is_ascii_alphanumeric() {
                end_idx += 1;
            }
            if end_idx < text_bytes.len() && text_bytes[end_idx] == b')' {
                return Some((true, end_idx + 1));
            }
        }

        // Check for number/letter followed by '.' or ')'
        let mut idx = 0;
        while idx < text_bytes.len()
            && (text_bytes[idx].is_ascii_digit() || text_bytes[idx].is_ascii_lowercase())
        {
            idx += 1;
        }

        if idx > 0 && idx < text_bytes.len() && (text_bytes[idx] == b'.' || text_bytes[idx] == b')')
        {
            // Check it's a valid marker (not too long, like a sentence ending)
            if idx <= 4 {
                return Some((true, idx + 1));
            }
        }

        None
    }

    /// Convert classified blocks to document elements (without list detection).
    fn blocks_to_elements(&self, blocks: &[ClassifiedBlock]) -> Vec<DocumentElement> {
        blocks
            .iter()
            .map(|block| match block.classification {
                BlockType::Header(level) => DocumentElement::Header {
                    level,
                    text: block.block.text.clone(),
                    style: Self::block_to_text_style(&block.block),
                    bbox: Self::bbox_from_rect(block.block.bbox),
                },
                BlockType::Paragraph => {
                    let page_width = block.block.bbox.x + block.block.bbox.width + 100.0;
                    let alignment = self.detect_alignment(&block.block, page_width);

                    DocumentElement::Paragraph {
                        text: block.block.text.clone(),
                        style: Self::block_to_text_style(&block.block),
                        bbox: Self::bbox_from_rect(block.block.bbox),
                        alignment,
                    }
                },
                _ => DocumentElement::Paragraph {
                    text: block.block.text.clone(),
                    style: Self::block_to_text_style(&block.block),
                    bbox: Self::bbox_from_rect(block.block.bbox),
                    alignment: TextAlignment::Left,
                },
            })
            .collect()
    }

    /// Detect text alignment based on position.
    fn detect_alignment(&self, block: &TextBlock, page_width: f32) -> TextAlignment {
        let left_margin = block.bbox.x;
        let right_margin = page_width - (block.bbox.x + block.bbox.width);

        // Center aligned if margins are approximately equal
        if (left_margin - right_margin).abs() < 10.0 {
            TextAlignment::Center
        } else if left_margin < 50.0 {
            TextAlignment::Left
        } else if right_margin < 50.0 {
            TextAlignment::Right
        } else {
            TextAlignment::Left // Default
        }
    }

    /// Convert TextBlock to TextStyle with bold/italic detection.
    fn block_to_text_style(block: &TextBlock) -> TextStyle {
        // Detect bold from font name
        let bold = block.is_bold || block.dominant_font.contains("Bold");

        // Detect italic from font name
        let italic =
            block.dominant_font.contains("Italic") || block.dominant_font.contains("Oblique");

        // Use first character's color if available, otherwise black
        let color = block
            .chars
            .first()
            .map(|c| (c.color.r, c.color.g, c.color.b))
            .unwrap_or((0.0, 0.0, 0.0));

        TextStyle {
            font_family: block.dominant_font.clone(),
            font_size: block.avg_font_size,
            bold,
            italic,
            color,
        }
    }

    /// Convert Rect to BoundingBox tuple.
    fn bbox_from_rect(rect: Rect) -> BoundingBox {
        (rect.x, rect.y, rect.width, rect.height)
    }

    /// Calculate page dimensions from characters.
    /// Calculate document metadata.
    fn calculate_metadata(&self, elements: &[DocumentElement]) -> DocumentMetadata {
        let mut header_count = 0;
        let mut paragraph_count = 0;
        let mut list_count = 0;
        let mut table_count = 0;

        for elem in elements {
            match elem {
                DocumentElement::Header { .. } => header_count += 1,
                DocumentElement::Paragraph { .. } => paragraph_count += 1,
                DocumentElement::List { .. } => list_count += 1,
                DocumentElement::Table { .. } => table_count += 1,
            }
        }

        DocumentMetadata {
            element_count: elements.len(),
            header_count,
            paragraph_count,
            list_count,
            table_count,
        }
    }
}

impl Default for StructuredExtractor {
    fn default() -> Self {
        Self::new()
    }
}

/// Classified text block.
#[derive(Debug, Clone)]
struct ClassifiedBlock {
    /// Original block
    block: TextBlock,
    /// Classification
    classification: BlockType,
}

/// Block classification.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[allow(dead_code)]
enum BlockType {
    /// Header at specified level
    Header(u8),
    /// Body paragraph
    Paragraph,
    /// List item
    ListItem,
    /// Table cell (future)
    TableCell,
}

impl StructuredDocument {
    /// Convert to plain text (for backward compatibility).
    pub fn to_plain_text(&self) -> String {
        let mut text = String::new();

        for element in &self.elements {
            match element {
                DocumentElement::Header { text: t, .. } => {
                    if !text.is_empty() {
                        text.push('\n');
                    }
                    text.push_str(t);
                    text.push('\n');
                },
                DocumentElement::Paragraph { text: t, .. } => {
                    if !text.is_empty() {
                        text.push('\n');
                    }
                    text.push_str(t);
                },
                DocumentElement::List { items, .. } => {
                    for item in items {
                        text.push('\n');
                        text.push_str(&item.text);
                    }
                },
                DocumentElement::Table { cells, .. } => {
                    for row in cells {
                        text.push('\n');
                        text.push_str(&row.join("\t"));
                    }
                },
            }
        }

        text
    }

    /// Export to JSON.
    pub fn to_json(&self) -> Result<String> {
        serde_json::to_string_pretty(self).map_err(|e| Error::ParseError {
            offset: 0,
            reason: format!("Failed to serialize to JSON: {}", e),
        })
    }
}
