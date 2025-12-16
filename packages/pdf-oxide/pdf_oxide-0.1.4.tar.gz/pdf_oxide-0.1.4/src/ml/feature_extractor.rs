//! Feature extraction for ML models.
//!
//! This module extracts features from text blocks for use in ML models,
//! including spatial features, text features, and normalized bounding boxes.

use crate::layout::text_block::TextBlock;
use ndarray::{Array1, Array2};

/// Extracts features from text blocks for ML models.
///
/// # Example
///
/// ```ignore
/// use pdf_oxide::ml::FeatureExtractor;
///
/// let extractor = FeatureExtractor::new(612.0, 792.0);
/// let spatial_features = extractor.extract_spatial_features(&blocks);
/// let bbox_features = extractor.extract_bbox_features(&blocks);
/// ```
pub struct FeatureExtractor {
    page_width: f32,
    page_height: f32,
}

impl FeatureExtractor {
    /// Create a new feature extractor for a page.
    ///
    /// # Arguments
    ///
    /// * `page_width` - Width of the page in points
    /// * `page_height` - Height of the page in points
    pub fn new(page_width: f32, page_height: f32) -> Self {
        Self {
            page_width,
            page_height,
        }
    }

    /// Extract normalized spatial features for each block.
    ///
    /// Returns an (n × 8) array where each row contains:
    /// - Column 0: x0 (normalized to \[0, 1\])
    /// - Column 1: y0 (normalized to \[0, 1\])
    /// - Column 2: x1 (normalized to \[0, 1\])
    /// - Column 3: y1 (normalized to \[0, 1\])
    /// - Column 4: width (normalized to \[0, 1\])
    /// - Column 5: height (normalized to \[0, 1\])
    /// - Column 6: font_size (normalized, assuming max 24pt)
    /// - Column 7: bold_flag (0.0 or 1.0)
    ///
    /// # Arguments
    ///
    /// * `blocks` - Text blocks to extract features from
    ///
    /// # Returns
    ///
    /// Array of shape (n_blocks, 8) with normalized features
    pub fn extract_spatial_features(&self, blocks: &[TextBlock]) -> Array2<f32> {
        let n = blocks.len();
        let mut features = Array2::zeros((n, 8));

        for (i, block) in blocks.iter().enumerate() {
            // Normalize positions to [0, 1]
            let x0 = block.bbox.x / self.page_width;
            let y0 = block.bbox.y / self.page_height;
            let x1 = (block.bbox.x + block.bbox.width) / self.page_width;
            let y1 = (block.bbox.y + block.bbox.height) / self.page_height;

            // Clamp to valid range
            let x0 = x0.clamp(0.0, 1.0);
            let y0 = y0.clamp(0.0, 1.0);
            let x1 = x1.clamp(0.0, 1.0);
            let y1 = y1.clamp(0.0, 1.0);

            features[[i, 0]] = x0;
            features[[i, 1]] = y0;
            features[[i, 2]] = x1;
            features[[i, 3]] = y1;
            features[[i, 4]] = block.bbox.width / self.page_width;
            features[[i, 5]] = block.bbox.height / self.page_height;

            // Normalize font size (assuming typical range 6-24pt)
            features[[i, 6]] = (block.avg_font_size / 24.0).min(2.0);

            // Bold flag
            features[[i, 7]] = if block.is_bold { 1.0 } else { 0.0 };
        }

        features
    }

    /// Extract text features for tokenization.
    ///
    /// Returns a vector of strings, one per block.
    ///
    /// # Arguments
    ///
    /// * `blocks` - Text blocks to extract text from
    ///
    /// # Returns
    ///
    /// Vector of text strings
    pub fn extract_text_features(&self, blocks: &[TextBlock]) -> Vec<String> {
        blocks.iter().map(|b| b.text.clone()).collect()
    }

    /// Convert bounding boxes to LayoutLM format.
    ///
    /// LayoutLM expects bounding boxes normalized to \[0, 1000\] range.
    ///
    /// Returns an (n × 4) array where each row contains:
    /// - Column 0: x0 (in \[0, 1000\])
    /// - Column 1: y0 (in \[0, 1000\])
    /// - Column 2: x1 (in \[0, 1000\])
    /// - Column 3: y1 (in \[0, 1000\])
    ///
    /// # Arguments
    ///
    /// * `blocks` - Text blocks to extract bounding boxes from
    ///
    /// # Returns
    ///
    /// Array of shape (n_blocks, 4) with LayoutLM-format bounding boxes
    pub fn extract_bbox_features(&self, blocks: &[TextBlock]) -> Array2<i64> {
        let n = blocks.len();
        let mut bboxes = Array2::zeros((n, 4));

        for (i, block) in blocks.iter().enumerate() {
            // LayoutLM expects bbox in [0, 1000] range
            let x0 = (block.bbox.x / self.page_width * 1000.0) as i64;
            let y0 = (block.bbox.y / self.page_height * 1000.0) as i64;
            let x1 = ((block.bbox.x + block.bbox.width) / self.page_width * 1000.0) as i64;
            let y1 = ((block.bbox.y + block.bbox.height) / self.page_height * 1000.0) as i64;

            // Clamp to valid range [0, 1000]
            bboxes[[i, 0]] = x0.clamp(0, 1000);
            bboxes[[i, 1]] = y0.clamp(0, 1000);
            bboxes[[i, 2]] = x1.clamp(0, 1000);
            bboxes[[i, 3]] = y1.clamp(0, 1000);
        }

        bboxes
    }

    /// Extract font size features as a 1D array.
    ///
    /// # Arguments
    ///
    /// * `blocks` - Text blocks to extract font sizes from
    ///
    /// # Returns
    ///
    /// 1D array of normalized font sizes
    pub fn extract_font_sizes(&self, blocks: &[TextBlock]) -> Array1<f32> {
        blocks
            .iter()
            .map(|b| (b.avg_font_size / 24.0).min(2.0))
            .collect()
    }

    /// Extract bold flags as a 1D array.
    ///
    /// # Arguments
    ///
    /// * `blocks` - Text blocks to check for bold text
    ///
    /// # Returns
    ///
    /// 1D array of 0.0 (not bold) or 1.0 (bold)
    pub fn extract_bold_flags(&self, blocks: &[TextBlock]) -> Array1<f32> {
        blocks
            .iter()
            .map(|b| if b.is_bold { 1.0 } else { 0.0 })
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::geometry::Rect;
    use crate::layout::text_block::{Color, FontWeight, TextBlock, TextChar};

    fn create_test_block(
        x: f32,
        y: f32,
        width: f32,
        height: f32,
        font_size: f32,
        is_bold: bool,
    ) -> TextBlock {
        let char_data = TextChar {
            char: 'A',
            bbox: Rect {
                x,
                y,
                width: 10.0,
                height: 10.0,
            },
            font_name: "Arial".to_string(),
            font_size,
            font_weight: if is_bold {
                FontWeight::Bold
            } else {
                FontWeight::Normal
            },
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
            text: "Test".to_string(),
            avg_font_size: font_size,
            dominant_font: "Arial".to_string(),
            is_bold,
        }
    }

    #[test]
    fn test_spatial_features() {
        let blocks = vec![
            create_test_block(0.0, 0.0, 100.0, 20.0, 12.0, false),
            create_test_block(100.0, 50.0, 150.0, 30.0, 18.0, true),
        ];

        let extractor = FeatureExtractor::new(612.0, 792.0);
        let features = extractor.extract_spatial_features(&blocks);

        assert_eq!(features.shape(), &[2, 8]);

        // Check normalization
        assert!(features[[0, 0]] >= 0.0 && features[[0, 0]] <= 1.0); // x0
        assert!(features[[0, 1]] >= 0.0 && features[[0, 1]] <= 1.0); // y0

        // Check bold flag
        assert_eq!(features[[0, 7]], 0.0); // not bold
        assert_eq!(features[[1, 7]], 1.0); // bold
    }

    #[test]
    fn test_bbox_features() {
        let blocks = vec![
            create_test_block(0.0, 0.0, 100.0, 20.0, 12.0, false),
            create_test_block(612.0, 792.0, 10.0, 10.0, 12.0, false), // At page edge
        ];

        let extractor = FeatureExtractor::new(612.0, 792.0);
        let bboxes = extractor.extract_bbox_features(&blocks);

        assert_eq!(bboxes.shape(), &[2, 4]);

        // All values should be in [0, 1000]
        for i in 0..bboxes.shape()[0] {
            for j in 0..bboxes.shape()[1] {
                assert!(bboxes[[i, j]] >= 0 && bboxes[[i, j]] <= 1000);
            }
        }

        // Block at origin should have bbox starting at 0
        assert_eq!(bboxes[[0, 0]], 0);
        assert_eq!(bboxes[[0, 1]], 0);

        // Block at page edge should be clamped to 1000
        assert_eq!(bboxes[[1, 0]], 1000);
        assert_eq!(bboxes[[1, 1]], 1000);
    }

    #[test]
    fn test_text_features() {
        let mut block1 = create_test_block(0.0, 0.0, 100.0, 20.0, 12.0, false);
        block1.text = "First block".to_string();

        let mut block2 = create_test_block(100.0, 50.0, 150.0, 30.0, 18.0, true);
        block2.text = "Second block".to_string();

        let blocks = vec![block1, block2];

        let extractor = FeatureExtractor::new(612.0, 792.0);
        let texts = extractor.extract_text_features(&blocks);

        assert_eq!(texts.len(), 2);
        assert_eq!(texts[0], "First block");
        assert_eq!(texts[1], "Second block");
    }

    #[test]
    fn test_empty_blocks() {
        let blocks: Vec<TextBlock> = vec![];
        let extractor = FeatureExtractor::new(612.0, 792.0);

        let spatial = extractor.extract_spatial_features(&blocks);
        assert_eq!(spatial.shape(), &[0, 8]);

        let bboxes = extractor.extract_bbox_features(&blocks);
        assert_eq!(bboxes.shape(), &[0, 4]);

        let texts = extractor.extract_text_features(&blocks);
        assert_eq!(texts.len(), 0);
    }

    #[test]
    fn test_font_size_normalization() {
        let blocks = vec![
            create_test_block(0.0, 0.0, 100.0, 20.0, 12.0, false),
            create_test_block(0.0, 0.0, 100.0, 20.0, 24.0, false),
            create_test_block(0.0, 0.0, 100.0, 20.0, 48.0, false), // Very large
        ];

        let extractor = FeatureExtractor::new(612.0, 792.0);
        let features = extractor.extract_spatial_features(&blocks);

        // 12pt -> 0.5
        assert!((features[[0, 6]] - 0.5).abs() < 0.01);

        // 24pt -> 1.0
        assert!((features[[1, 6]] - 1.0).abs() < 0.01);

        // 48pt -> capped at 2.0
        assert!((features[[2, 6]] - 2.0).abs() < 0.01);
    }
}
