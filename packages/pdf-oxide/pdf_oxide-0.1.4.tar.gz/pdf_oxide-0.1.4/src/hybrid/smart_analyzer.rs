//! Hybrid smart layout analyzer.
//!
//! This module orchestrates between classical and ML-based approaches
//! based on document complexity, providing the best balance of speed
//! and accuracy.

use crate::error::Result;
use crate::hybrid::complexity_estimator::{Complexity, ComplexityEstimator};
use crate::layout::heading_detector::{self, HeadingLevel};
use crate::layout::text_block::TextBlock;

#[cfg(feature = "ml")]
use crate::ml::heading_classifier::HeadingClassifier;
#[cfg(feature = "ml")]
use crate::ml::layout_reader::LayoutReader;

/// Smart layout analyzer that chooses between classical and ML approaches.
///
/// # Strategy
///
/// - **Simple documents**: Always use fast classical algorithms
/// - **Moderate documents**: Use classical for speed (both work well)
/// - **Complex documents**: Try ML first, fall back to classical if unavailable
///
/// # Example
///
/// ```ignore
/// use pdf_oxide::hybrid::SmartLayoutAnalyzer;
///
/// let analyzer = SmartLayoutAnalyzer::new();
/// let order = analyzer.determine_reading_order(&blocks, 612.0, 792.0)?;
/// let headings = analyzer.detect_headings(&blocks)?;
/// ```
pub struct SmartLayoutAnalyzer {
    #[cfg(feature = "ml")]
    layout_reader: Option<LayoutReader>,

    #[cfg(feature = "ml")]
    heading_classifier: Option<HeadingClassifier>,

    /// Complexity threshold for using ML (default: Moderate)
    complexity_threshold: Complexity,
}

impl SmartLayoutAnalyzer {
    /// Create a new smart analyzer.
    ///
    /// This attempts to load ML models if the `ml` feature is enabled.
    /// If models can't be loaded, the analyzer will fall back to classical methods.
    pub fn new() -> Self {
        Self {
            #[cfg(feature = "ml")]
            layout_reader: {
                match LayoutReader::load() {
                    Ok(reader) => Some(reader),
                    Err(e) => {
                        log::warn!("Failed to load LayoutReader: {}", e);
                        None
                    },
                }
            },

            #[cfg(feature = "ml")]
            heading_classifier: {
                match HeadingClassifier::load() {
                    Ok(classifier) => Some(classifier),
                    Err(e) => {
                        log::warn!("Failed to load HeadingClassifier: {}", e);
                        None
                    },
                }
            },

            complexity_threshold: Complexity::Moderate,
        }
    }

    /// Create a new analyzer with custom complexity threshold.
    ///
    /// # Arguments
    ///
    /// * `threshold` - Minimum complexity to use ML models
    ///
    /// # Example
    ///
    /// ```
    /// use pdf_oxide::hybrid::{SmartLayoutAnalyzer, Complexity};
    ///
    /// // Always use ML if available
    /// let analyzer = SmartLayoutAnalyzer::with_threshold(Complexity::Simple);
    ///
    /// // Only use ML for very complex documents
    /// let analyzer = SmartLayoutAnalyzer::with_threshold(Complexity::Complex);
    /// ```
    pub fn with_threshold(threshold: Complexity) -> Self {
        let mut analyzer = Self::new();
        analyzer.complexity_threshold = threshold;
        analyzer
    }

    /// Determine reading order for text blocks using best available method.
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
    ///
    /// # Algorithm
    ///
    /// 1. Estimate page complexity
    /// 2. If complexity >= threshold and ML available: use ML
    /// 3. Otherwise: use classical top-to-bottom, left-to-right
    pub fn determine_reading_order(
        &self,
        blocks: &[TextBlock],
        page_width: f32,
        page_height: f32,
    ) -> Result<Vec<usize>> {
        if blocks.is_empty() {
            return Ok(vec![]);
        }

        // Estimate complexity
        let complexity =
            ComplexityEstimator::estimate_page_complexity(blocks, page_width, page_height);

        log::debug!(
            "Page complexity: {:?} (threshold: {:?})",
            complexity,
            self.complexity_threshold
        );

        // Decide which approach to use
        #[cfg(feature = "ml")]
        {
            if complexity >= self.complexity_threshold {
                // Try ML first for complex documents
                if let Some(ref ml) = self.layout_reader {
                    match ml.predict_reading_order(blocks, page_width, page_height) {
                        Ok(order) => {
                            log::info!("Using ML reading order (complexity: {:?})", complexity);
                            return Ok(order);
                        },
                        Err(e) => {
                            log::warn!("ML reading order failed: {}, falling back to classical", e);
                        },
                    }
                }
            }
        }

        // Fallback to classical
        log::info!("Using classical reading order (complexity: {:?})", complexity);
        Ok(self.classical_reading_order(blocks))
    }

    /// Detect headings using best available method.
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
    /// 1. Try ML classifier if available (feature-gated)
    /// 2. Fall back to classical font-based detection
    pub fn detect_headings(&self, blocks: &[TextBlock]) -> Result<Vec<HeadingLevel>> {
        if blocks.is_empty() {
            return Ok(vec![]);
        }

        #[cfg(feature = "ml")]
        {
            // Try ML classifier first
            if let Some(ref classifier) = self.heading_classifier {
                match classifier.classify(blocks) {
                    Ok(levels) => {
                        log::info!("Using ML heading detection");
                        return Ok(levels);
                    },
                    Err(e) => {
                        log::warn!("ML heading detection failed: {}, falling back to classical", e);
                    },
                }
            }
        }

        // Fallback to classical
        log::info!("Using classical heading detection");
        Ok(heading_detector::detect_headings(blocks))
    }

    /// Get analyzer capabilities.
    ///
    /// # Returns
    ///
    /// Returns an AnalyzerCapabilities struct describing what features are available.
    pub fn capabilities(&self) -> AnalyzerCapabilities {
        AnalyzerCapabilities {
            has_ml_reading_order: cfg!(feature = "ml"),
            has_ml_heading_detection: cfg!(feature = "ml"),
            #[cfg(feature = "ml")]
            ml_models_loaded: self.layout_reader.is_some() && self.heading_classifier.is_some(),
            #[cfg(not(feature = "ml"))]
            ml_models_loaded: false,
            complexity_threshold: self.complexity_threshold,
        }
    }

    // Private helper methods

    /// Classical reading order: top-to-bottom, left-to-right.
    fn classical_reading_order(&self, blocks: &[TextBlock]) -> Vec<usize> {
        let mut order: Vec<usize> = (0..blocks.len()).collect();

        order.sort_by(|&a, &b| {
            let block_a = &blocks[a];
            let block_b = &blocks[b];

            // Sort by Y position (top to bottom), then X position (left to right)
            block_a
                .bbox
                .y
                .partial_cmp(&block_b.bbox.y)
                .unwrap()
                .then(block_a.bbox.x.partial_cmp(&block_b.bbox.x).unwrap())
        });

        order
    }
}

impl Default for SmartLayoutAnalyzer {
    fn default() -> Self {
        Self::new()
    }
}

/// Capabilities of the smart analyzer.
#[derive(Debug, Clone)]
pub struct AnalyzerCapabilities {
    /// Whether ML reading order is compiled in (feature flag)
    pub has_ml_reading_order: bool,

    /// Whether ML heading detection is compiled in (feature flag)
    pub has_ml_heading_detection: bool,

    /// Whether ML models are actually loaded and ready
    pub ml_models_loaded: bool,

    /// Complexity threshold for using ML
    pub complexity_threshold: Complexity,
}

impl AnalyzerCapabilities {
    /// Check if any ML capabilities are available.
    pub fn has_any_ml(&self) -> bool {
        self.ml_models_loaded
    }

    /// Get a human-readable description of capabilities.
    pub fn description(&self) -> String {
        if self.ml_models_loaded {
            format!("ML-enhanced (threshold: {:?})", self.complexity_threshold)
        } else if self.has_ml_reading_order || self.has_ml_heading_detection {
            "ML compiled but models not loaded (using classical)".to_string()
        } else {
            "Classical only (ML feature not enabled)".to_string()
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::geometry::Rect;
    use crate::layout::text_block::{Color, FontWeight, TextBlock, TextChar};

    fn create_test_block(x: f32, y: f32, text: &str) -> TextBlock {
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
            chars: vec![char_data],
            bbox: Rect {
                x,
                y,
                width: 100.0,
                height: 20.0,
            },
            text: text.to_string(),
            avg_font_size: 12.0,
            dominant_font: "Arial".to_string(),
            is_bold: false,
            mcid: None,
        }
    }

    #[test]
    fn test_create_analyzer() {
        let analyzer = SmartLayoutAnalyzer::new();
        let caps = analyzer.capabilities();

        // Should always have classical capabilities
        assert!(!caps.description().is_empty());
    }

    #[test]
    fn test_reading_order() {
        let analyzer = SmartLayoutAnalyzer::new();

        let blocks = vec![
            create_test_block(100.0, 200.0, "third"),
            create_test_block(100.0, 100.0, "first"),
            create_test_block(100.0, 150.0, "second"),
        ];

        let order = analyzer
            .determine_reading_order(&blocks, 612.0, 792.0)
            .unwrap();

        // Should be sorted by Y position
        assert_eq!(order, vec![1, 2, 0]);
    }

    #[test]
    fn test_heading_detection() {
        let analyzer = SmartLayoutAnalyzer::new();

        let blocks = vec![
            create_test_block(100.0, 100.0, "Test"),
            create_test_block(100.0, 130.0, "More text"),
        ];

        let headings = analyzer.detect_headings(&blocks).unwrap();

        // Should return a heading level for each block
        assert_eq!(headings.len(), 2);
    }

    #[test]
    fn test_empty_blocks() {
        let analyzer = SmartLayoutAnalyzer::new();

        let order = analyzer.determine_reading_order(&[], 612.0, 792.0).unwrap();
        assert_eq!(order.len(), 0);

        let headings = analyzer.detect_headings(&[]).unwrap();
        assert_eq!(headings.len(), 0);
    }

    #[test]
    fn test_with_threshold() {
        let analyzer = SmartLayoutAnalyzer::with_threshold(Complexity::Complex);
        let caps = analyzer.capabilities();

        assert_eq!(caps.complexity_threshold, Complexity::Complex);
    }

    #[test]
    fn test_capabilities() {
        let analyzer = SmartLayoutAnalyzer::new();
        let caps = analyzer.capabilities();

        // These depend on feature flags
        #[cfg(feature = "ml")]
        {
            assert!(caps.has_ml_reading_order);
            assert!(caps.has_ml_heading_detection);
        }

        #[cfg(not(feature = "ml"))]
        {
            assert!(!caps.has_ml_reading_order);
            assert!(!caps.has_ml_heading_detection);
            assert!(!caps.ml_models_loaded);
        }
    }

    #[test]
    fn test_classical_reading_order() {
        let analyzer = SmartLayoutAnalyzer::new();

        // Multi-column-like layout
        let blocks = vec![
            create_test_block(50.0, 100.0, "top-left"),
            create_test_block(400.0, 100.0, "top-right"),
            create_test_block(50.0, 200.0, "bottom-left"),
            create_test_block(400.0, 200.0, "bottom-right"),
        ];

        let order = analyzer.classical_reading_order(&blocks);

        // Classical: top-to-bottom, left-to-right
        // Should read: top-left, top-right, bottom-left, bottom-right
        assert_eq!(order[0], 0); // top-left
        assert_eq!(order[1], 1); // top-right
        assert_eq!(order[2], 2); // bottom-left
        assert_eq!(order[3], 3); // bottom-right
    }
}
