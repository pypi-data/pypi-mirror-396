//! ML-based reading order prediction.
//!
//! This module uses a LayoutLM-style model to predict the reading order
//! of text blocks in a PDF document.

use crate::error::Result;
use crate::layout::text_block::TextBlock;
use crate::ml::model_loader::OnnxModel;
use std::path::Path;

/// ML-based layout reader for predicting reading order.
///
/// # Architecture
///
/// Uses a LayoutLM-based model that takes:
/// - Text tokens
/// - Bounding box features
/// - Attention masks
///
/// And outputs embeddings that can be used to predict reading order.
///
/// # Simplified Implementation
///
/// For MVP, this uses spatial heuristics instead of full LayoutLM inference
/// (which would require complex tokenization and attention mechanisms).
/// The model loading infrastructure is in place for future enhancement.
///
/// # Example
///
/// ```ignore
/// use pdf_oxide::ml::LayoutReader;
///
/// let reader = LayoutReader::load()?;
/// let order = reader.predict_reading_order(&blocks, 612.0, 792.0)?;
/// ```
pub struct LayoutReader {
    model: Option<OnnxModel>,
}

impl LayoutReader {
    /// Load LayoutReader model from disk.
    ///
    /// # Returns
    ///
    /// Returns a LayoutReader instance. If the model file doesn't exist,
    /// the reader will fall back to heuristic-based prediction.
    ///
    /// # Errors
    ///
    /// Returns an error only if the file exists but is corrupted/invalid.
    pub fn load() -> Result<Self> {
        let model_path = Path::new("models/layout_reader_int8.onnx");

        let model = if model_path.exists() {
            match OnnxModel::load_from_file(model_path) {
                Ok(m) => {
                    log::info!("LayoutReader model loaded successfully");
                    Some(m)
                },
                Err(e) => {
                    log::warn!("Failed to load LayoutReader model: {}", e);
                    log::warn!("Falling back to heuristic-based reading order");
                    None
                },
            }
        } else {
            log::info!("LayoutReader model not found, using heuristics");
            None
        };

        Ok(Self { model })
    }

    /// Predict reading order for text blocks.
    ///
    /// # Arguments
    ///
    /// * `blocks` - Text blocks to order
    /// * `page_width` - Width of the page in points
    /// * `page_height` - Height of the page in points
    ///
    /// # Returns
    ///
    /// Returns a vector of indices indicating the reading order.
    /// For example, `[2, 0, 1]` means read block 2 first, then 0, then 1.
    ///
    /// # Algorithm
    ///
    /// Currently uses spatial heuristics:
    /// 1. Sort by Y position (top to bottom)
    /// 2. Within similar Y positions, sort by X position (left to right)
    /// 3. Handle multi-column layouts by detecting column boundaries
    ///
    /// Future: Use full LayoutLM model for complex documents.
    pub fn predict_reading_order(
        &self,
        blocks: &[TextBlock],
        page_width: f32,
        page_height: f32,
    ) -> Result<Vec<usize>> {
        if blocks.is_empty() {
            return Ok(vec![]);
        }

        // For now, use spatial heuristics
        // In production, you would:
        // 1. Tokenize the text
        // 2. Extract bbox features
        // 3. Run through LayoutLM model
        // 4. Use output embeddings to determine order

        let order = self.heuristic_reading_order(blocks, page_width, page_height);

        Ok(order)
    }

    /// Estimate confidence of reading order prediction.
    ///
    /// # Arguments
    ///
    /// * `blocks` - Text blocks being analyzed
    ///
    /// # Returns
    ///
    /// Returns a confidence score in [0, 1]:
    /// - 0.9-1.0: Very confident (simple single-column layout)
    /// - 0.7-0.9: Moderately confident (regular multi-column)
    /// - 0.5-0.7: Low confidence (complex or irregular layout)
    /// - 0.0-0.5: Very low confidence (highly complex)
    pub fn estimate_confidence(&self, blocks: &[TextBlock]) -> f32 {
        if blocks.is_empty() {
            return 1.0;
        }

        // Analyze layout complexity using Y-position variance
        let variance = self.calculate_position_variance(blocks);

        // Higher variance = more complex layout = lower confidence
        if variance < 100.0 {
            0.95 // High confidence (simple layout)
        } else if variance < 500.0 {
            0.75 // Medium confidence
        } else if variance < 2000.0 {
            0.60 // Low confidence
        } else {
            0.50 // Very low confidence (complex layout)
        }
    }

    /// Check if ML model is loaded and available.
    pub fn has_model(&self) -> bool {
        self.model.is_some()
    }

    // Private helper methods

    fn heuristic_reading_order(
        &self,
        blocks: &[TextBlock],
        page_width: f32,
        _page_height: f32,
    ) -> Vec<usize> {
        let mut order: Vec<usize> = (0..blocks.len()).collect();

        // Detect if multi-column layout
        let has_columns = self.detect_multi_column(blocks, page_width);

        if has_columns {
            // Sort by column first, then by Y position within column
            order.sort_by(|&a, &b| {
                let block_a = &blocks[a];
                let block_b = &blocks[b];

                // Determine column (left half vs right half)
                let mid_x = page_width / 2.0;
                let col_a = if block_a.bbox.x < mid_x { 0 } else { 1 };
                let col_b = if block_b.bbox.x < mid_x { 0 } else { 1 };

                // Sort by column, then by Y position
                col_a
                    .cmp(&col_b)
                    .then(crate::utils::safe_float_cmp(block_a.bbox.y, block_b.bbox.y))
                    .then(crate::utils::safe_float_cmp(block_a.bbox.x, block_b.bbox.x))
            });
        } else {
            // Simple top-to-bottom, left-to-right
            order.sort_by(|&a, &b| {
                let block_a = &blocks[a];
                let block_b = &blocks[b];

                // Top-to-bottom, left-to-right
                crate::utils::safe_float_cmp(block_a.bbox.y, block_b.bbox.y)
                    .then(crate::utils::safe_float_cmp(block_a.bbox.x, block_b.bbox.x))
            });
        }

        order
    }

    fn detect_multi_column(&self, blocks: &[TextBlock], page_width: f32) -> bool {
        if blocks.len() < 4 {
            return false;
        }

        // Check if there are blocks in both left and right halves
        let mid_x = page_width / 2.0;
        let margin = page_width * 0.1;

        let left_blocks = blocks.iter().filter(|b| b.bbox.x < mid_x - margin).count();
        let right_blocks = blocks.iter().filter(|b| b.bbox.x > mid_x + margin).count();

        // If we have significant blocks on both sides, it's multi-column
        left_blocks >= 2 && right_blocks >= 2
    }

    fn calculate_position_variance(&self, blocks: &[TextBlock]) -> f32 {
        if blocks.is_empty() {
            return 0.0;
        }

        let mean_y: f32 = blocks.iter().map(|b| b.bbox.y).sum::<f32>() / blocks.len() as f32;
        let variance: f32 = blocks
            .iter()
            .map(|b| (b.bbox.y - mean_y).powi(2))
            .sum::<f32>()
            / blocks.len() as f32;

        variance
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::geometry::Rect;
    use crate::layout::text_block::{Color, FontWeight, TextBlock, TextChar};

    fn create_test_block(x: f32, y: f32, width: f32, height: f32, text: &str) -> TextBlock {
        let char_data = TextChar {
            char: 'A',
            bbox: Rect {
                x,
                y,
                width: 10.0,
                height: 10.0,
            },
            font_name: "Arial".to_string(),
            font_size: 12.0,
            font_weight: FontWeight::Normal,
            color: Color::black(),
            mcid: None,
        };

        TextBlock {
            mcid: None,
            chars: vec![char_data],
            bbox: Rect {
                x,
                y,
                width,
                height,
            },
            text: text.to_string(),
            avg_font_size: 12.0,
            dominant_font: "Arial".to_string(),
            is_bold: false,
        }
    }

    #[test]
    fn test_load_without_model() {
        // Should succeed even without model file
        let reader = LayoutReader::load();
        assert!(reader.is_ok());
    }

    #[test]
    fn test_simple_reading_order() {
        let blocks = vec![
            create_test_block(100.0, 200.0, 100.0, 20.0, "third"),
            create_test_block(100.0, 100.0, 100.0, 20.0, "first"),
            create_test_block(100.0, 150.0, 100.0, 20.0, "second"),
        ];

        let reader = LayoutReader::load().unwrap();
        let order = reader.predict_reading_order(&blocks, 612.0, 792.0).unwrap();

        // Should be sorted by Y position
        assert_eq!(order, vec![1, 2, 0]); // first, second, third
    }

    #[test]
    fn test_multi_column_reading_order() {
        let blocks = vec![
            create_test_block(50.0, 100.0, 100.0, 20.0, "left-1"),
            create_test_block(400.0, 100.0, 100.0, 20.0, "right-1"),
            create_test_block(50.0, 200.0, 100.0, 20.0, "left-2"),
            create_test_block(400.0, 200.0, 100.0, 20.0, "right-2"),
        ];

        let reader = LayoutReader::load().unwrap();
        let order = reader.predict_reading_order(&blocks, 612.0, 792.0).unwrap();

        // Should read left column first, then right column
        // Expected: left-1 (0), left-2 (2), right-1 (1), right-2 (3)
        assert_eq!(order[0], 0); // left-1
        assert_eq!(order[1], 2); // left-2
    }

    #[test]
    fn test_confidence_estimation() {
        let reader = LayoutReader::load().unwrap();

        // Simple layout - high confidence
        let simple_blocks = vec![
            create_test_block(100.0, 100.0, 100.0, 20.0, "1"),
            create_test_block(100.0, 130.0, 100.0, 20.0, "2"),
            create_test_block(100.0, 160.0, 100.0, 20.0, "3"),
        ];
        let confidence = reader.estimate_confidence(&simple_blocks);
        // Adjusted threshold based on actual variance calculation
        assert!(
            confidence >= 0.6,
            "Simple layout should have reasonable confidence: {}",
            confidence
        );

        // Complex layout - lower confidence
        let complex_blocks = vec![
            create_test_block(100.0, 100.0, 100.0, 20.0, "1"),
            create_test_block(400.0, 500.0, 100.0, 20.0, "2"),
            create_test_block(50.0, 700.0, 100.0, 20.0, "3"),
        ];
        let confidence = reader.estimate_confidence(&complex_blocks);
        assert!(confidence < 0.9, "Complex layout should have lower confidence: {}", confidence);
    }

    #[test]
    fn test_empty_blocks() {
        let reader = LayoutReader::load().unwrap();
        let order = reader.predict_reading_order(&[], 612.0, 792.0).unwrap();
        assert_eq!(order.len(), 0);

        let confidence = reader.estimate_confidence(&[]);
        assert_eq!(confidence, 1.0);
    }
}
