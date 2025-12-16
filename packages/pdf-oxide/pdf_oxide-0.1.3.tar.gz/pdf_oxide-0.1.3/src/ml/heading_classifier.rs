//! ML-based heading classification.
//!
//! This module uses a transformer-based model to classify text blocks
//! as headings (H1, H2, H3) or body text.

use crate::error::Result;
use crate::layout::heading_detector::HeadingLevel;
use crate::layout::text_block::TextBlock;
use crate::ml::model_loader::OnnxModel;
use std::path::Path;

/// ML-based heading classifier.
///
/// # Architecture
///
/// Uses a fine-tuned DistilBERT model for text classification:
/// - Input: Text content + styling features
/// - Output: 5-class classification (H1, H2, H3, Body, Small)
///
/// # Simplified Implementation
///
/// For MVP, this uses rule-based classification instead of full transformer inference
/// (which would require tokenization, attention masks, and complex post-processing).
/// The model loading infrastructure is in place for future enhancement.
///
/// # Example
///
/// ```ignore
/// use pdf_oxide::ml::HeadingClassifier;
///
/// let classifier = HeadingClassifier::load()?;
/// let levels = classifier.classify(&blocks)?;
/// ```
pub struct HeadingClassifier {
    model: Option<OnnxModel>,
}

impl HeadingClassifier {
    /// Load heading classifier model from disk.
    ///
    /// # Returns
    ///
    /// Returns a HeadingClassifier instance. If the model file doesn't exist,
    /// the classifier will fall back to rule-based classification.
    ///
    /// # Errors
    ///
    /// Returns an error only if the file exists but is corrupted/invalid.
    pub fn load() -> Result<Self> {
        let model_path = Path::new("models/heading_classifier_int8.onnx");

        let model = if model_path.exists() {
            match OnnxModel::load_from_file(model_path) {
                Ok(m) => {
                    log::info!("HeadingClassifier model loaded successfully");
                    Some(m)
                },
                Err(e) => {
                    log::warn!("Failed to load HeadingClassifier model: {}", e);
                    log::warn!("Falling back to rule-based heading detection");
                    None
                },
            }
        } else {
            log::info!("HeadingClassifier model not found, using rule-based classification");
            None
        };

        Ok(Self { model })
    }

    /// Classify text blocks as headings or body text.
    ///
    /// # Arguments
    ///
    /// * `blocks` - Text blocks to classify
    ///
    /// # Returns
    ///
    /// Returns a vector of HeadingLevel, one per block.
    ///
    /// # Algorithm
    ///
    /// Currently uses rule-based classification:
    /// 1. Analyze font size relative to body text
    /// 2. Check for bold/uppercase styling
    /// 3. Consider text length (headings are typically short)
    ///
    /// Future: Use fine-tuned transformer model for semantic understanding.
    pub fn classify(&self, blocks: &[TextBlock]) -> Result<Vec<HeadingLevel>> {
        let mut levels = Vec::with_capacity(blocks.len());

        for block in blocks {
            let level = self.classify_single(block)?;
            levels.push(level);
        }

        Ok(levels)
    }

    /// Classify a single text block.
    ///
    /// # Arguments
    ///
    /// * `block` - Text block to classify
    ///
    /// # Returns
    ///
    /// Returns the predicted HeadingLevel.
    fn classify_single(&self, block: &TextBlock) -> Result<HeadingLevel> {
        // Extract features for classification
        let font_size = block.avg_font_size;
        let is_bold = block.is_bold;
        let text_length = block.text.len();
        let is_uppercase = self.is_mostly_uppercase(&block.text);
        let is_short = text_length < 100;

        // Rule-based classification
        // These thresholds are heuristics based on common PDF formatting
        let level = if font_size > 24.0 && is_bold {
            // Very large and bold -> H1
            HeadingLevel::H1
        } else if font_size > 18.0 && (is_bold || is_uppercase) && is_short {
            // Large, styled, and short -> H2
            HeadingLevel::H2
        } else if font_size > 14.0 && (is_bold || is_uppercase) && is_short {
            // Medium-large, styled, and short -> H3
            HeadingLevel::H3
        } else if font_size < 8.0 {
            // Very small -> footnotes, captions, etc.
            HeadingLevel::Small
        } else {
            // Everything else -> body text
            HeadingLevel::Body
        };

        Ok(level)
    }

    /// Check if text is mostly uppercase.
    ///
    /// # Arguments
    ///
    /// * `text` - Text to check
    ///
    /// # Returns
    ///
    /// Returns true if more than 70% of letters are uppercase.
    fn is_mostly_uppercase(&self, text: &str) -> bool {
        let letters: Vec<char> = text.chars().filter(|c| c.is_alphabetic()).collect();

        if letters.is_empty() {
            return false;
        }

        let uppercase_count = letters.iter().filter(|c| c.is_uppercase()).count();
        let ratio = uppercase_count as f32 / letters.len() as f32;

        ratio > 0.7
    }

    /// Check if ML model is loaded and available.
    pub fn has_model(&self) -> bool {
        self.model.is_some()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::geometry::Rect;
    use crate::layout::text_block::{Color, FontWeight, TextBlock, TextChar};

    fn create_test_block(font_size: f32, is_bold: bool, text: &str) -> TextBlock {
        let char_data = TextChar {
            char: 'A',
            bbox: Rect {
                x: 0.0,
                y: 0.0,
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
                x: 0.0,
                y: 0.0,
                width: 100.0,
                height: 20.0,
            },
            text: text.to_string(),
            avg_font_size: font_size,
            dominant_font: "Arial".to_string(),
            is_bold,
        }
    }

    #[test]
    fn test_load_without_model() {
        // Should succeed even without model file
        let classifier = HeadingClassifier::load();
        assert!(classifier.is_ok());
    }

    #[test]
    fn test_h1_classification() {
        let classifier = HeadingClassifier::load().unwrap();

        // Large, bold text -> H1
        let block = create_test_block(28.0, true, "Introduction");
        let level = classifier.classify_single(&block).unwrap();
        assert_eq!(level, HeadingLevel::H1);
    }

    #[test]
    fn test_h2_classification() {
        let classifier = HeadingClassifier::load().unwrap();

        // Medium-large, bold, short -> H2
        let block = create_test_block(20.0, true, "Methods");
        let level = classifier.classify_single(&block).unwrap();
        assert_eq!(level, HeadingLevel::H2);
    }

    #[test]
    fn test_h3_classification() {
        let classifier = HeadingClassifier::load().unwrap();

        // Slightly larger, bold, short -> H3
        let block = create_test_block(15.0, true, "Subsection");
        let level = classifier.classify_single(&block).unwrap();
        assert_eq!(level, HeadingLevel::H3);
    }

    #[test]
    fn test_body_classification() {
        let classifier = HeadingClassifier::load().unwrap();

        // Normal size, not bold, longer text -> Body
        let block = create_test_block(
            12.0,
            false,
            "This is a paragraph of body text that should be classified as body content.",
        );
        let level = classifier.classify_single(&block).unwrap();
        assert_eq!(level, HeadingLevel::Body);
    }

    #[test]
    fn test_small_classification() {
        let classifier = HeadingClassifier::load().unwrap();

        // Very small text -> Small (footnotes, captions)
        let block = create_test_block(7.0, false, "Figure 1. Sample caption");
        let level = classifier.classify_single(&block).unwrap();
        assert_eq!(level, HeadingLevel::Small);
    }

    #[test]
    fn test_uppercase_heading() {
        let classifier = HeadingClassifier::load().unwrap();

        // Uppercase text with moderate size -> H2 or H3 depending on size
        let block = create_test_block(18.0, false, "RESULTS");
        let level = classifier.classify_single(&block).unwrap();
        // Should be a heading (not Body)
        assert!(matches!(level, HeadingLevel::H2 | HeadingLevel::H3));
    }

    #[test]
    fn test_batch_classification() {
        let classifier = HeadingClassifier::load().unwrap();

        let blocks = vec![
            create_test_block(28.0, true, "Title"),
            create_test_block(20.0, true, "Section"),
            create_test_block(12.0, false, "Body text here."),
            create_test_block(7.0, false, "Footnote"),
        ];

        let levels = classifier.classify(&blocks).unwrap();

        assert_eq!(levels.len(), 4);
        assert_eq!(levels[0], HeadingLevel::H1);
        assert_eq!(levels[1], HeadingLevel::H2);
        assert_eq!(levels[2], HeadingLevel::Body);
        assert_eq!(levels[3], HeadingLevel::Small);
    }

    #[test]
    fn test_mostly_uppercase() {
        let classifier = HeadingClassifier::load().unwrap();

        assert!(classifier.is_mostly_uppercase("INTRODUCTION"));
        assert!(classifier.is_mostly_uppercase("METHODS AND RESULTS")); // Fully uppercase
        assert!(!classifier.is_mostly_uppercase("This is mostly lowercase"));
        assert!(!classifier.is_mostly_uppercase("123456")); // No letters
    }
}
