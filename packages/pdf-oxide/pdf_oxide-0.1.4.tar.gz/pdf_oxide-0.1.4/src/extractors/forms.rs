//! AcroForm field extraction.
//!
//! Extracts form fields from PDF documents that use AcroForms (Interactive Forms).
//! See ISO 32000-1:2008, Section 12.7 - Interactive Forms.

use crate::document::PdfDocument;
use crate::error::{Error, Result};
use crate::object::Object;

/// A form field extracted from a PDF AcroForm.
#[derive(Debug, Clone)]
pub struct FormField {
    /// Field name from /T key
    pub name: String,
    /// Field type from /FT key
    pub field_type: FieldType,
    /// Field value from /V key
    pub value: FieldValue,
    /// Tooltip/description from /TU key
    pub tooltip: Option<String>,
    /// Full qualified name (for hierarchical fields)
    pub full_name: String,
    /// Field bounding box from /Rect key [x1, y1, x2, y2]
    pub bounds: Option<[f64; 4]>,
}

/// Field type from /FT key in field dictionary.
#[derive(Debug, Clone, PartialEq)]
pub enum FieldType {
    /// Button field (/Btn) - checkbox, radio button, push button
    Button,
    /// Text field (/Tx) - single or multi-line text
    Text,
    /// Choice field (/Ch) - list box or combo box
    Choice,
    /// Signature field (/Sig)
    Signature,
    /// Unknown/unrecognized field type
    Unknown(String),
}

/// Field value from /V key in field dictionary.
#[derive(Debug, Clone)]
pub enum FieldValue {
    /// Text string value
    Text(String),
    /// Boolean value (for checkboxes)
    Boolean(bool),
    /// Name value (for radio buttons, choice fields)
    Name(String),
    /// Array of values (for multi-select list boxes)
    Array(Vec<String>),
    /// No value present
    None,
}

/// AcroForm extractor.
pub struct FormExtractor;

impl FormExtractor {
    /// Helper function to resolve an Object (handles indirect references).
    ///
    /// If the object is an indirect reference, loads it. Otherwise returns clone.
    fn resolve_object(doc: &mut PdfDocument, obj: &Object) -> Result<Object> {
        if let Some(ref_val) = obj.as_reference() {
            doc.load_object(ref_val)
        } else {
            Ok(obj.clone())
        }
    }

    /// Decode a PDF string that may be UTF-16BE (with BOM) or PDFDocEncoding.
    ///
    /// Per ISO 32000-1:2008, Section 7.9.2.2 - Text String Type:
    /// - If bytes start with 0xFE 0xFF, the string is UTF-16BE with BOM
    /// - Otherwise, it's PDFDocEncoding (superset of ISO Latin-1)
    fn decode_text_string(bytes: &[u8]) -> Option<String> {
        if bytes.len() >= 2 && bytes[0] == 0xFE && bytes[1] == 0xFF {
            // UTF-16BE with BOM
            let utf16_bytes = &bytes[2..]; // Skip BOM

            // Convert bytes to u16 pairs (big-endian)
            let utf16_pairs: Vec<u16> = utf16_bytes
                .chunks_exact(2)
                .map(|chunk| u16::from_be_bytes([chunk[0], chunk[1]]))
                .collect();

            String::from_utf16(&utf16_pairs).ok()
        } else {
            // PDFDocEncoding - use proper character mapping
            // ISO 32000-1:2008, Appendix D.2, Table D.2
            Some(
                bytes
                    .iter()
                    .filter_map(|&b| crate::fonts::font_dict::pdfdoc_encoding_lookup(b))
                    .collect(),
            )
        }
    }

    /// Extract all form fields from a PDF document.
    ///
    /// This function:
    /// 1. Gets the document catalog
    /// 2. Looks for /AcroForm dictionary
    /// 3. Extracts /Fields array
    /// 4. Recursively processes field hierarchy
    ///
    /// # Arguments
    ///
    /// * `doc` - The PDF document to extract fields from
    ///
    /// # Returns
    ///
    /// A vector of form fields, or an error if extraction fails.
    ///
    /// # Example
    ///
    /// ```no_run
    /// use pdf_oxide::document::PdfDocument;
    /// use pdf_oxide::extractors::forms::FormExtractor;
    ///
    /// let mut doc = PdfDocument::open("form.pdf")?;
    /// let fields = FormExtractor::extract_fields(&mut doc)?;
    ///
    /// for field in &fields {
    ///     println!("Field: {} = {:?}", field.name, field.value);
    /// }
    /// # Ok::<(), pdf_oxide::error::Error>(())
    /// ```
    pub fn extract_fields(doc: &mut PdfDocument) -> Result<Vec<FormField>> {
        // Get document catalog
        let catalog = doc.catalog()?;
        let catalog_dict = catalog
            .as_dict()
            .ok_or_else(|| Error::InvalidPdf("Catalog is not a dictionary".to_string()))?;

        // Check if AcroForm exists
        let acroform_ref = match catalog_dict.get("AcroForm") {
            Some(obj) => obj,
            None => {
                // No AcroForm in this document
                return Ok(Vec::new());
            },
        };

        // Resolve AcroForm dictionary
        let acroform = Self::resolve_object(doc, acroform_ref)?;
        let acroform_dict = acroform
            .as_dict()
            .ok_or_else(|| Error::InvalidPdf("AcroForm is not a dictionary".to_string()))?;

        // Get Fields array
        let fields_ref = match acroform_dict.get("Fields") {
            Some(obj) => obj,
            None => {
                // AcroForm exists but has no fields
                return Ok(Vec::new());
            },
        };

        // Resolve fields array
        let fields_obj = Self::resolve_object(doc, fields_ref)?;
        let fields_array = fields_obj
            .as_array()
            .ok_or_else(|| Error::InvalidPdf("AcroForm /Fields is not an array".to_string()))?;

        // Extract fields recursively
        let mut result = Vec::new();
        for field_ref in fields_array {
            Self::extract_field_recursive(doc, field_ref, "", &mut result)?;
        }

        Ok(result)
    }

    /// Recursively extract a field and its children.
    ///
    /// PDF forms can have hierarchical field structure using /Kids arrays.
    /// This function handles:
    /// - Terminal fields (with /FT and /V)
    /// - Non-terminal fields (with /Kids but no /FT)
    /// - Inherited properties from parent fields
    ///
    /// # Arguments
    ///
    /// * `doc` - The PDF document
    /// * `field_ref` - Reference to the field object
    /// * `parent_name` - Full qualified name of parent field (for hierarchy)
    /// * `result` - Vector to accumulate extracted fields
    fn extract_field_recursive(
        doc: &mut PdfDocument,
        field_ref: &Object,
        parent_name: &str,
        result: &mut Vec<FormField>,
    ) -> Result<()> {
        // Resolve field dictionary
        let field = Self::resolve_object(doc, field_ref)?;
        let field_dict = match field.as_dict() {
            Some(d) => d,
            None => return Ok(()), // Skip if not a dictionary
        };

        // Get field name from /T (partial name)
        let partial_name = field_dict
            .get("T")
            .and_then(|obj| Self::resolve_object(doc, obj).ok())
            .and_then(|obj| obj.as_string().map(|s| s.to_vec()))
            .and_then(|bytes| Self::decode_text_string(&bytes))
            .unwrap_or_default();

        // Build full qualified name
        let full_name = if parent_name.is_empty() {
            partial_name.clone()
        } else if partial_name.is_empty() {
            parent_name.to_string()
        } else {
            format!("{}.{}", parent_name, partial_name)
        };

        // Check if this field has children
        if let Some(kids_ref) = field_dict.get("Kids") {
            // This is a non-terminal field - process children
            let kids = Self::resolve_object(doc, kids_ref)?;
            if let Some(kids_array) = kids.as_array() {
                for kid_ref in kids_array {
                    Self::extract_field_recursive(doc, kid_ref, &full_name, result)?;
                }
            }
        }

        // Extract field type
        let field_type = field_dict
            .get("FT")
            .and_then(|obj| Self::resolve_object(doc, obj).ok())
            .and_then(|obj| obj.as_name().map(|s| s.to_string()))
            .map(|name| Self::parse_field_type(&name))
            .unwrap_or(FieldType::Unknown("".to_string()));

        // Skip if no field type (non-terminal field with only Kids)
        if matches!(field_type, FieldType::Unknown(ref s) if s.is_empty()) {
            return Ok(());
        }

        // Extract field value
        let value = field_dict
            .get("V")
            .and_then(|obj| Self::resolve_object(doc, obj).ok())
            .map(|obj| Self::parse_field_value(&obj, &field_type))
            .unwrap_or(FieldValue::None);

        // Extract tooltip
        let tooltip = field_dict
            .get("TU")
            .and_then(|obj| Self::resolve_object(doc, obj).ok())
            .and_then(|obj| obj.as_string().map(|s| s.to_vec()))
            .and_then(|bytes| Self::decode_text_string(&bytes));

        // Extract field bounds from /Rect [x1, y1, x2, y2]
        let bounds = field_dict
            .get("Rect")
            .and_then(|obj| Self::resolve_object(doc, obj).ok())
            .and_then(|obj| obj.as_array().cloned())
            .and_then(|arr| {
                if arr.len() == 4 {
                    let mut coords = Vec::with_capacity(4);
                    for item in &arr {
                        let val = match item {
                            Object::Integer(i) => Some(*i as f64),
                            Object::Real(f) => Some(*f),
                            _ => None,
                        }?;
                        coords.push(val);
                    }
                    Some([coords[0], coords[1], coords[2], coords[3]])
                } else {
                    None
                }
            });

        // Create form field
        let form_field = FormField {
            name: partial_name,
            field_type,
            value,
            tooltip,
            full_name,
            bounds,
        };

        result.push(form_field);
        Ok(())
    }

    /// Parse field type from /FT value.
    fn parse_field_type(ft: &str) -> FieldType {
        match ft {
            "Btn" => FieldType::Button,
            "Tx" => FieldType::Text,
            "Ch" => FieldType::Choice,
            "Sig" => FieldType::Signature,
            _ => FieldType::Unknown(ft.to_string()),
        }
    }

    /// Parse field value from /V object.
    fn parse_field_value(obj: &Object, field_type: &FieldType) -> FieldValue {
        match obj {
            Object::String(bytes) => {
                // Text string value - may be UTF-16BE or PDFDocEncoding
                if let Some(text) = Self::decode_text_string(bytes) {
                    FieldValue::Text(text)
                } else {
                    FieldValue::None
                }
            },
            Object::Name(name) => {
                // Name value (for radio buttons, choice fields)
                if *field_type == FieldType::Button {
                    // For checkboxes, common values are /Yes or /Off
                    if name == "Yes" || name == "On" {
                        FieldValue::Boolean(true)
                    } else if name == "No" || name == "Off" {
                        FieldValue::Boolean(false)
                    } else {
                        FieldValue::Name(name.clone())
                    }
                } else {
                    FieldValue::Name(name.clone())
                }
            },
            Object::Array(array) => {
                // Array of values (for multi-select list boxes)
                let values: Vec<String> = array
                    .iter()
                    .filter_map(|item| match item {
                        Object::String(bytes) => Self::decode_text_string(bytes),
                        Object::Name(name) => Some(name.clone()),
                        _ => None,
                    })
                    .collect();
                FieldValue::Array(values)
            },
            Object::Boolean(b) => {
                // Boolean value
                FieldValue::Boolean(*b)
            },
            _ => FieldValue::None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_field_type() {
        assert_eq!(FormExtractor::parse_field_type("Btn"), FieldType::Button);
        assert_eq!(FormExtractor::parse_field_type("Tx"), FieldType::Text);
        assert_eq!(FormExtractor::parse_field_type("Ch"), FieldType::Choice);
        assert_eq!(FormExtractor::parse_field_type("Sig"), FieldType::Signature);
        assert!(matches!(FormExtractor::parse_field_type("Unknown"), FieldType::Unknown(_)));
    }

    #[test]
    fn test_parse_field_value_string() {
        let obj = Object::String(b"John Doe".to_vec());
        let value = FormExtractor::parse_field_value(&obj, &FieldType::Text);
        assert!(matches!(value, FieldValue::Text(ref s) if s == "John Doe"));
    }

    #[test]
    fn test_parse_field_value_boolean() {
        // Test checkbox "Yes" name
        let obj = Object::Name("Yes".to_string());
        let value = FormExtractor::parse_field_value(&obj, &FieldType::Button);
        assert!(matches!(value, FieldValue::Boolean(true)));

        // Test checkbox "Off" name
        let obj = Object::Name("Off".to_string());
        let value = FormExtractor::parse_field_value(&obj, &FieldType::Button);
        assert!(matches!(value, FieldValue::Boolean(false)));
    }

    #[test]
    fn test_parse_field_value_array() {
        let obj = Object::Array(vec![
            Object::String(b"Option1".to_vec()),
            Object::String(b"Option2".to_vec()),
        ]);
        let value = FormExtractor::parse_field_value(&obj, &FieldType::Choice);
        assert!(matches!(
            value,
            FieldValue::Array(ref v) if v.len() == 2 && v[0] == "Option1"
        ));
    }
}
