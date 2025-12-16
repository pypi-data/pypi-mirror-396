//! Configuration for PDF processing.

// use std::path::PathBuf; // Will be used later

/// PDF processing configuration.
#[derive(Debug, Clone)]
pub struct PdfConfig {
    /// Enable ML features.
    pub use_ml: bool,

    /// Enable table detection ML.
    pub table_ml: bool,

    /// Enable OCR.
    pub ocr: bool,
}

impl Default for PdfConfig {
    fn default() -> Self {
        Self::new()
    }
}

impl PdfConfig {
    /// Create new configuration with defaults.
    pub fn new() -> Self {
        Self {
            use_ml: false,
            table_ml: false,
            ocr: false,
        }
    }

    /// Enable ML features.
    pub fn with_ml(mut self, enable: bool) -> Self {
        self.use_ml = enable;
        self
    }

    /// Enable table detection ML.
    pub fn with_table_ml(mut self, enable: bool) -> Self {
        self.table_ml = enable;
        self
    }

    /// Enable OCR.
    pub fn with_ocr(mut self, enable: bool) -> Self {
        self.ocr = enable;
        self
    }
}
