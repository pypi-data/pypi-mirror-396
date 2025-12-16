//! Machine learning integration (optional).
//!
//! This module provides ML-enhanced PDF analysis capabilities including:
//! - Layout-aware reading order prediction
//! - ML-based heading classification
//! - Feature extraction for transformer models
//!
//! All ML features are optional and gated behind the `ml` feature flag.
//!
//! # Architecture
//!
//! - Uses tract-onnx for CPU-only inference
//! - Models are quantized to INT8 for performance
//! - Graceful fallback to classical algorithms if models fail
//!
//! # Example
//!
//! ```ignore
//! use pdf_oxide::ml::layout_reader::LayoutReader;
//!
//! let reader = LayoutReader::load()?;
//! let order = reader.predict_reading_order(&blocks, page_width, page_height)?;
//! ```

#[cfg(feature = "ml")]
pub mod feature_extractor;
#[cfg(feature = "ml")]
pub mod heading_classifier;
#[cfg(feature = "ml")]
pub mod layout_reader;
#[cfg(feature = "ml")]
pub mod model_loader;

// Re-export main types when ML is enabled
#[cfg(feature = "ml")]
pub use feature_extractor::FeatureExtractor;
#[cfg(feature = "ml")]
pub use heading_classifier::HeadingClassifier;
#[cfg(feature = "ml")]
pub use layout_reader::LayoutReader;
#[cfg(feature = "ml")]
pub use model_loader::OnnxModel;
