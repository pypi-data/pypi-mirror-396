//! ONNX model loading and inference.
//!
//! This module provides a wrapper around tract-onnx for loading and running
//! ONNX models on CPU.

use crate::error::{Error, Result};
use std::path::Path;
use tract_onnx::prelude::*;

/// Type alias for the tract model plan to reduce complexity.
type TractPlan = SimplePlan<TypedFact, Box<dyn TypedOp>, Graph<TypedFact, Box<dyn TypedOp>>>;

/// Wrapper for ONNX models using tract inference engine.
///
/// # Example
///
/// ```ignore
/// use pdf_oxide::ml::OnnxModel;
/// use std::path::Path;
///
/// let model = OnnxModel::load_from_file(Path::new("models/model.onnx"))?;
/// let output = model.run(input_tensors)?;
/// ```
#[derive(Debug)]
pub struct OnnxModel {
    model: TractPlan,
    input_names: Vec<String>,
    output_names: Vec<String>,
}

impl OnnxModel {
    /// Load ONNX model from file and optimize for CPU inference.
    ///
    /// # Arguments
    ///
    /// * `path` - Path to the ONNX model file
    ///
    /// # Returns
    ///
    /// Returns a loaded and optimized model ready for inference.
    ///
    /// # Errors
    ///
    /// Returns an error if:
    /// - The file doesn't exist or can't be read
    /// - The model format is invalid
    /// - Optimization fails
    pub fn load_from_file(path: &Path) -> Result<Self> {
        // Verify file exists
        if !path.exists() {
            return Err(Error::Unsupported(format!(
                "Model file not found: {}. Run `python scripts/convert_models.py` to generate models.",
                path.display()
            )));
        }

        // Load ONNX model
        let model = tract_onnx::onnx()
            .model_for_path(path)
            .map_err(|e| Error::Unsupported(format!("Failed to load ONNX model: {}", e)))?;

        // Optimize for CPU inference
        let model = model
            .into_optimized()
            .map_err(|e| Error::Unsupported(format!("Failed to optimize model: {}", e)))?;

        // Build runnable plan
        let model = model
            .into_runnable()
            .map_err(|e| Error::Unsupported(format!("Failed to build runnable model: {}", e)))?;

        // Extract input and output names for debugging
        let input_names = model
            .model()
            .inputs
            .iter()
            .map(|outlet| model.model().node(outlet.node).name.clone())
            .collect();

        let output_names = model
            .model()
            .outputs
            .iter()
            .map(|outlet| model.model().node(outlet.node).name.clone())
            .collect();

        Ok(Self {
            model,
            input_names,
            output_names,
        })
    }

    /// Run inference with input tensors.
    ///
    /// # Arguments
    ///
    /// * `inputs` - Input tensors in the order expected by the model
    ///
    /// # Returns
    ///
    /// Returns output tensors from the model.
    ///
    /// # Errors
    ///
    /// Returns an error if inference fails (e.g., wrong input shapes, types).
    pub fn run(&self, inputs: TVec<TValue>) -> Result<TVec<TValue>> {
        self.model
            .run(inputs)
            .map_err(|e| Error::Unsupported(format!("Inference failed: {}", e)))
    }

    /// Get the names of input nodes (for debugging).
    pub fn input_names(&self) -> &[String] {
        &self.input_names
    }

    /// Get the names of output nodes (for debugging).
    pub fn output_names(&self) -> &[String] {
        &self.output_names
    }

    /// Get the model plan for advanced usage.
    pub fn plan(&self) -> &TractPlan {
        &self.model
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_load_nonexistent_model() {
        let result = OnnxModel::load_from_file(Path::new("nonexistent.onnx"));
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("not found"));
    }

    #[test]
    fn test_model_loader_error_message() {
        let result = OnnxModel::load_from_file(Path::new("missing.onnx"));
        match result {
            Err(Error::Unsupported(msg)) => {
                assert!(msg.contains("convert_models.py"));
            },
            _ => panic!("Expected Unsupported error"),
        }
    }
}
