//! PDF annotations support.
//!
//! Provides access to PDF annotations including text notes, highlights,
//! comments, and other markup.

use crate::document::PdfDocument;
use crate::error::Result;
use crate::object::Object;

/// A PDF annotation.
#[derive(Debug, Clone)]
pub struct Annotation {
    /// Type of annotation (Text, Highlight, Link, etc.)
    pub annotation_type: String,

    /// Annotation subtype if available
    pub subtype: Option<String>,

    /// Text contents of the annotation
    pub contents: Option<String>,

    /// Rectangle bounds [x1, y1, x2, y2]
    pub rect: Option<[f64; 4]>,

    /// Author/creator of the annotation
    pub author: Option<String>,

    /// Creation date
    pub creation_date: Option<String>,

    /// Subject of the annotation
    pub subject: Option<String>,

    /// Link destination (for Link annotations)
    /// PDF Spec: ISO 32000-1:2008, Section 12.3.2 - Destinations
    pub destination: Option<LinkDestination>,

    /// Link action (for Link annotations)
    /// PDF Spec: ISO 32000-1:2008, Section 12.6 - Actions
    pub action: Option<LinkAction>,
}

/// Link destination within a PDF document.
///
/// Specifies a location within the PDF to navigate to.
#[derive(Debug, Clone, PartialEq)]
pub enum LinkDestination {
    /// Named destination (string reference to destination dictionary)
    Named(String),
    /// Explicit destination: [page fit_type params...]
    Explicit {
        /// Target page number (0-indexed)
        page: u32,
        /// Fit type (XYZ, Fit, FitH, FitV, FitR, FitB, FitBH, FitBV)
        fit_type: String,
        /// Additional parameters (coordinates, zoom factor, etc.)
        params: Vec<f32>,
    },
}

/// Link action associated with an annotation.
///
/// Specifies what happens when the annotation is activated.
#[derive(Debug, Clone, PartialEq)]
pub enum LinkAction {
    /// URI action - navigate to a web URL
    Uri(String),
    /// GoTo action - navigate to a destination within the document
    GoTo(LinkDestination),
    /// GoToR action - navigate to a destination in another document
    GoToRemote {
        /// File specification
        file: String,
        /// Destination in remote file
        destination: Option<LinkDestination>,
    },
    /// Other action types (Launch, Named, etc.)
    Other {
        /// Action type (/S field)
        action_type: String,
    },
}

impl PdfDocument {
    /// Get all annotations for a specific page.
    ///
    /// Returns a list of annotations (comments, highlights, notes, etc.)
    /// present on the specified page.
    ///
    /// # Arguments
    ///
    /// * `page_index` - Zero-based page index
    ///
    /// # Returns
    ///
    /// - `Ok(Vec<Annotation>)` - List of annotations (may be empty)
    /// - `Err` - Error accessing page or annotations
    ///
    /// # Example
    ///
    /// ```no_run
    /// use pdf_oxide::PdfDocument;
    ///
    /// let mut doc = PdfDocument::open("sample.pdf")?;
    /// let annotations = doc.get_annotations(0)?;
    ///
    /// for annot in annotations {
    ///     if let Some(contents) = annot.contents {
    ///         println!("Comment: {}", contents);
    ///     }
    /// }
    /// # Ok::<(), pdf_oxide::error::Error>(())
    /// ```
    pub fn get_annotations(&mut self, page_index: usize) -> Result<Vec<Annotation>> {
        // Get the page reference
        let page_ref = self.get_page_ref(page_index)?;
        let page_obj = self.load_object(page_ref)?;

        // Get annotations array
        let annots = match page_obj.as_dict() {
            Some(dict) => match dict.get("Annots") {
                Some(Object::Array(arr)) => arr.clone(),
                Some(Object::Reference(annot_ref)) => {
                    // Annotations can be indirect
                    match self.load_object(*annot_ref)? {
                        Object::Array(arr) => arr,
                        _ => return Ok(Vec::new()),
                    }
                },
                _ => return Ok(Vec::new()), // No annotations
            },
            None => return Ok(Vec::new()),
        };

        let mut result = Vec::new();

        // Parse each annotation
        for annot_obj in annots {
            let annot_ref = match annot_obj {
                Object::Reference(r) => r,
                _ => continue, // Skip non-references
            };

            if let Ok(annotation) = self.parse_annotation(annot_ref) {
                result.push(annotation);
            }
        }

        Ok(result)
    }

    /// Parse a single annotation object.
    fn parse_annotation(&mut self, annot_ref: crate::object::ObjectRef) -> Result<Annotation> {
        let annot_obj = self.load_object(annot_ref)?;

        let dict = annot_obj.as_dict().ok_or_else(|| {
            crate::error::Error::InvalidPdf("Annotation is not a dictionary".to_string())
        })?;

        // Get annotation type and subtype
        let annotation_type = dict
            .get("Type")
            .and_then(|t| t.as_name())
            .unwrap_or("Unknown")
            .to_string();

        let subtype = dict
            .get("Subtype")
            .and_then(|s| s.as_name())
            .map(|s| s.to_string());

        // Get contents (text)
        let contents = dict.get("Contents").and_then(|c| match c {
            Object::String(s) => Some(String::from_utf8_lossy(s).to_string()),
            _ => None,
        });

        // Get rectangle
        let rect = dict.get("Rect").and_then(|r| match r {
            Object::Array(arr) if arr.len() == 4 => {
                let mut rect_arr = [0.0; 4];
                for (i, obj) in arr.iter().enumerate() {
                    rect_arr[i] = match obj {
                        Object::Integer(n) => *n as f64,
                        Object::Real(f) => *f,
                        _ => 0.0,
                    };
                }
                Some(rect_arr)
            },
            _ => None,
        });

        // Get author/title (T field)
        let author = dict.get("T").and_then(|t| match t {
            Object::String(s) => Some(String::from_utf8_lossy(s).to_string()),
            _ => None,
        });

        // Get creation date
        let creation_date = dict.get("CreationDate").and_then(|d| match d {
            Object::String(s) => Some(String::from_utf8_lossy(s).to_string()),
            _ => None,
        });

        // Get subject
        let subject = dict.get("Subj").and_then(|s| match s {
            Object::String(s) => Some(String::from_utf8_lossy(s).to_string()),
            _ => None,
        });

        // Parse link-specific fields if this is a Link annotation
        let (destination, action) = if subtype.as_deref() == Some("Link") {
            let dest = dict
                .get("Dest")
                .and_then(|d| self.parse_destination(d).ok());
            let act = dict.get("A").and_then(|a| self.parse_action(a).ok());
            (dest, act)
        } else {
            (None, None)
        };

        Ok(Annotation {
            annotation_type,
            subtype,
            contents,
            rect,
            author,
            creation_date,
            subject,
            destination,
            action,
        })
    }

    /// Parse a destination object.
    ///
    /// PDF Spec: ISO 32000-1:2008, Section 12.3.2 - Destinations
    fn parse_destination(&mut self, dest_obj: &Object) -> Result<LinkDestination> {
        match dest_obj {
            // Named destination (string or name)
            Object::String(s) => Ok(LinkDestination::Named(String::from_utf8_lossy(s).to_string())),
            Object::Name(n) => Ok(LinkDestination::Named(n.clone())),
            // Explicit destination array: [page /FitType ...]
            Object::Array(arr) if !arr.is_empty() => {
                // First element is page reference or page number
                let page = match &arr[0] {
                    Object::Integer(n) => *n as u32,
                    Object::Reference(r) => {
                        // Resolve page reference to page index
                        // For now, just use object ID as approximation
                        r.id
                    },
                    _ => 0,
                };

                // Second element is fit type
                let fit_type = if arr.len() > 1 {
                    arr[1].as_name().unwrap_or("Fit").to_string()
                } else {
                    "Fit".to_string()
                };

                // Remaining elements are parameters
                let params: Vec<f32> = arr
                    .iter()
                    .skip(2)
                    .filter_map(|obj| match obj {
                        Object::Integer(i) => Some(*i as f32),
                        Object::Real(r) => Some(*r as f32),
                        _ => None,
                    })
                    .collect();

                Ok(LinkDestination::Explicit {
                    page,
                    fit_type,
                    params,
                })
            },
            Object::Reference(r) => {
                // Indirect destination - load and parse
                let dest_loaded = self.load_object(*r)?;
                self.parse_destination(&dest_loaded)
            },
            _ => Err(crate::error::Error::InvalidPdf("Invalid destination format".to_string())),
        }
    }

    /// Parse an action dictionary.
    ///
    /// PDF Spec: ISO 32000-1:2008, Section 12.6 - Actions
    fn parse_action(&mut self, action_obj: &Object) -> Result<LinkAction> {
        // Resolve reference if needed
        let action = if let Object::Reference(r) = action_obj {
            self.load_object(*r)?
        } else {
            action_obj.clone()
        };

        let dict = action.as_dict().ok_or_else(|| {
            crate::error::Error::InvalidPdf("Action is not a dictionary".to_string())
        })?;

        // Get action type (/S field)
        let action_type = dict.get("S").and_then(|s| s.as_name()).ok_or_else(|| {
            crate::error::Error::InvalidPdf("Action missing /S field".to_string())
        })?;

        match action_type {
            "URI" => {
                // URI action - extract URL
                let uri = dict
                    .get("URI")
                    .and_then(|u| match u {
                        Object::String(s) => Some(String::from_utf8_lossy(s).to_string()),
                        _ => None,
                    })
                    .ok_or_else(|| {
                        crate::error::Error::InvalidPdf("URI action missing /URI field".to_string())
                    })?;

                Ok(LinkAction::Uri(uri))
            },
            "GoTo" => {
                // GoTo action - navigate within document
                let dest_obj = dict.get("D").ok_or_else(|| {
                    crate::error::Error::InvalidPdf("GoTo action missing /D field".to_string())
                })?;

                let destination = self.parse_destination(dest_obj)?;
                Ok(LinkAction::GoTo(destination))
            },
            "GoToR" => {
                // GoToR action - navigate to remote document
                let file = dict
                    .get("F")
                    .and_then(|f| match f {
                        Object::String(s) => Some(String::from_utf8_lossy(s).to_string()),
                        Object::Dictionary(d) => {
                            // File specification dictionary
                            d.get("F").and_then(|f| match f {
                                Object::String(s) => Some(String::from_utf8_lossy(s).to_string()),
                                _ => None,
                            })
                        },
                        _ => None,
                    })
                    .ok_or_else(|| {
                        crate::error::Error::InvalidPdf("GoToR action missing /F field".to_string())
                    })?;

                let destination = dict.get("D").and_then(|d| self.parse_destination(d).ok());

                Ok(LinkAction::GoToRemote { file, destination })
            },
            other => {
                // Other action types (Launch, Named, etc.)
                Ok(LinkAction::Other {
                    action_type: other.to_string(),
                })
            },
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_annotation_creation() {
        let annot = Annotation {
            annotation_type: "Annot".to_string(),
            subtype: Some("Text".to_string()),
            contents: Some("This is a comment".to_string()),
            rect: Some([100.0, 200.0, 150.0, 250.0]),
            author: Some("John Doe".to_string()),
            creation_date: Some("D:20231030120000".to_string()),
            subject: Some("Review".to_string()),
            destination: None,
            action: None,
        };

        assert_eq!(annot.annotation_type, "Annot");
        assert_eq!(annot.subtype, Some("Text".to_string()));
        assert_eq!(annot.contents, Some("This is a comment".to_string()));
        assert!(annot.rect.is_some());
    }
}
