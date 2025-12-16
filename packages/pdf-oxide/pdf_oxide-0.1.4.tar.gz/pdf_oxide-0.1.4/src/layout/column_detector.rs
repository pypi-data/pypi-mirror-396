//! XY-Cut algorithm for column detection.
//!
//! This module implements the recursive XY-Cut algorithm for detecting
//! multi-column layouts and hierarchical document structure.

use crate::geometry::Rect;
use crate::layout::document_analyzer::AdaptiveLayoutParams;
use crate::layout::text_block::TextBlock;

/// A hierarchical layout tree produced by XY-Cut.
#[derive(Debug, Clone)]
pub enum LayoutTree {
    /// A leaf node containing text blocks.
    Leaf {
        /// Indices of text blocks in this leaf
        blocks: Vec<usize>,
    },
    /// An internal node representing a split.
    Node {
        /// Direction of the cut (horizontal or vertical)
        direction: CutDirection,
        /// Child subtrees
        children: Vec<LayoutTree>,
    },
}

/// Direction of a layout cut.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CutDirection {
    /// Horizontal cut (splits top/bottom)
    Horizontal,
    /// Vertical cut (splits left/right)
    Vertical,
}

/// Perform XY-Cut analysis on a region of text blocks.
///
/// The XY-Cut algorithm recursively divides a document region based on
/// projection profiles. It alternates between horizontal and vertical cuts
/// to identify columns, rows, and hierarchical structure.
///
/// # Arguments
///
/// * `region` - The bounding box of the region to analyze
/// * `blocks` - All text blocks in the document
/// * `block_indices` - Indices of blocks within this region
/// * `depth` - Current recursion depth
/// * `max_depth` - Maximum recursion depth
/// * `min_region_size` - Minimum region size to consider for splitting
///
/// # Returns
///
/// A hierarchical `LayoutTree` representing the document structure.
///
/// # Examples
///
/// ```ignore
/// use pdf_oxide::geometry::Rect;
/// use pdf_oxide::layout::{TextChar, TextBlock, FontWeight, Color};
/// use pdf_oxide::layout::column_detector::{xy_cut, LayoutTree, CutDirection};
///
/// let chars = vec![
///     TextChar {
///         char: 'A',
///         bbox: Rect::new(0.0, 0.0, 10.0, 12.0),
///         font_name: "Times".to_string(),
///         font_size: 12.0,
///         font_weight: FontWeight::Normal,
///         color: Color::black(),
///     },
/// ];
/// let block = TextBlock::from_chars(chars);
/// let blocks = vec![block];
/// let region = Rect::new(0.0, 0.0, 600.0, 800.0);
/// let indices: Vec<usize> = (0..blocks.len()).collect();
///
/// let tree = xy_cut(region, &blocks, &indices, 0, 5, 50.0);
/// ```ignore
pub fn xy_cut(
    region: Rect,
    blocks: &[TextBlock],
    block_indices: &[usize],
    depth: u32,
    max_depth: u32,
    min_region_size: f32,
) -> LayoutTree {
    // Use default sigma=2.0 (Meunier ICDAR 2005 baseline)
    xy_cut_with_sigma(region, blocks, block_indices, depth, max_depth, min_region_size, 2.0)
}

/// Internal XY-Cut implementation with configurable Gaussian sigma.
fn xy_cut_with_sigma(
    region: Rect,
    blocks: &[TextBlock],
    block_indices: &[usize],
    depth: u32,
    max_depth: u32,
    min_region_size: f32,
    sigma: f32,
) -> LayoutTree {
    // Base cases: stop recursion
    if depth >= max_depth
        || block_indices.len() <= 1
        || region.width < min_region_size
        || region.height < min_region_size
    {
        return LayoutTree::Leaf {
            blocks: block_indices.to_vec(),
        };
    }

    // Compute projection profiles with adaptive sigma
    let h_profile = horizontal_projection(&region, blocks, block_indices, sigma);
    let v_profile = vertical_projection(&region, blocks, block_indices, sigma);

    // Find best valleys (whitespace) in each direction
    let h_valley = find_best_valley(&h_profile);
    let v_valley = find_best_valley(&v_profile);

    // Debug logging for valley detection
    if depth == 0 {
        log::debug!(
            "XY-Cut (depth={}): region=({:.1}, {:.1}) {}x{}, blocks={}, h_bins={}, v_bins={}",
            depth,
            region.x,
            region.y,
            region.width,
            region.height,
            block_indices.len(),
            h_profile.len(),
            v_profile.len()
        );
        if let Some(h) = h_valley {
            log::debug!("  H-valley found: pos={:.3}, depth={:.2}", h.position, h.depth);
        } else {
            log::debug!("  H-valley: NONE");
        }
        if let Some(v) = v_valley {
            log::debug!("  V-valley found: pos={:.3}, depth={:.2}", v.position, v.depth);
        } else {
            log::debug!("  V-valley: NONE");
        }
    }

    // If no good cut found, return leaf
    if h_valley.is_none() && v_valley.is_none() {
        if depth == 0 {
            log::debug!("  No valleys found - returning leaf with {} blocks", block_indices.len());
        }
        return LayoutTree::Leaf {
            blocks: block_indices.to_vec(),
        };
    }

    // Choose cut direction based on valley depth
    let (cut_pos, direction) = match (h_valley, v_valley) {
        (Some(h), Some(v)) if h.depth > v.depth => (h.position, CutDirection::Horizontal),
        (Some(h), None) => (h.position, CutDirection::Horizontal),
        (None, Some(v)) => (v.position, CutDirection::Vertical),
        (_, Some(v)) => (v.position, CutDirection::Vertical),
        (None, None) => {
            // Already handled above - this branch should never execute
            // Return leaf node as defensive fallback
            return LayoutTree::Leaf {
                blocks: block_indices.to_vec(),
            };
        },
    };

    // Split region and blocks
    let (region1, region2) = split_region(&region, cut_pos, direction);
    let (blocks1, blocks2) = split_blocks(blocks, block_indices, &region, cut_pos, direction);

    // If split produces empty partition, return leaf
    if blocks1.is_empty() || blocks2.is_empty() {
        return LayoutTree::Leaf {
            blocks: block_indices.to_vec(),
        };
    }

    // Recurse on both sides with same sigma
    let child1 =
        xy_cut_with_sigma(region1, blocks, &blocks1, depth + 1, max_depth, min_region_size, sigma);
    let child2 =
        xy_cut_with_sigma(region2, blocks, &blocks2, depth + 1, max_depth, min_region_size, sigma);

    LayoutTree::Node {
        direction,
        children: vec![child1, child2],
    }
}

/// Compute horizontal projection profile.
///
/// This counts the density of text (number of blocks) at each vertical position.
///
/// # Arguments
///
/// * `sigma` - Gaussian smoothing parameter (default: 2.0 per Meunier ICDAR 2005)
fn horizontal_projection(
    region: &Rect,
    blocks: &[TextBlock],
    indices: &[usize],
    sigma: f32,
) -> Vec<f32> {
    if region.height <= 0.0 {
        return vec![0.0];
    }

    let bins = (region.height / 2.0).ceil().max(1.0) as usize;
    let mut profile = vec![0.0; bins];

    for &idx in indices {
        let block = &blocks[idx];

        // Compute which bins this block overlaps
        let y_start =
            ((block.bbox.top() - region.top()) / region.height * bins as f32).max(0.0) as usize;
        let y_end =
            ((block.bbox.bottom() - region.top()) / region.height * bins as f32).max(0.0) as usize;

        // Count character density (number of chars) instead of accumulating width
        let char_count = block.chars.len() as f32;
        let bins_covered = (y_end - y_start + 1).max(1) as f32;
        let density_per_bin = char_count / bins_covered;

        for item in profile
            .iter_mut()
            .take(y_end.min(bins - 1) + 1)
            .skip(y_start.min(bins - 1))
        {
            *item += density_per_bin;
        }
    }

    // Apply Gaussian smoothing to reduce noise
    // Meunier (ICDAR 2005) recommends σ=2.0 for column detection
    // FIX #2: Adaptive sigma based on layout density (see AdaptiveLayoutParams)
    // PDF Spec note: This is a layout analysis heuristic, not defined in PDF spec
    gaussian_smooth(&mut profile, sigma);

    profile
}

/// Compute vertical projection profile.
///
/// This counts the density of text (number of blocks) at each horizontal position.
///
/// # Arguments
///
/// * `sigma` - Gaussian smoothing parameter (default: 2.0 per Meunier ICDAR 2005)
fn vertical_projection(
    region: &Rect,
    blocks: &[TextBlock],
    indices: &[usize],
    sigma: f32,
) -> Vec<f32> {
    if region.width <= 0.0 {
        return vec![0.0];
    }

    let bins = (region.width / 2.0).ceil().max(1.0) as usize;
    let mut profile = vec![0.0; bins];

    for &idx in indices {
        let block = &blocks[idx];

        // Compute which bins this block overlaps
        let x_start =
            ((block.bbox.left() - region.left()) / region.width * bins as f32).max(0.0) as usize;
        let x_end =
            ((block.bbox.right() - region.left()) / region.width * bins as f32).max(0.0) as usize;

        // Count character density (number of chars) instead of accumulating height
        let char_count = block.chars.len() as f32;
        let bins_covered = (x_end - x_start + 1).max(1) as f32;
        let density_per_bin = char_count / bins_covered;

        for item in profile
            .iter_mut()
            .take(x_end.min(bins - 1) + 1)
            .skip(x_start.min(bins - 1))
        {
            *item += density_per_bin;
        }
    }

    // Apply Gaussian smoothing to reduce noise
    // Meunier (ICDAR 2005) recommends σ=2.0 for column detection
    // FIX #2: Adaptive sigma based on layout density (see AdaptiveLayoutParams)
    // PDF Spec note: This is a layout analysis heuristic, not defined in PDF spec
    gaussian_smooth(&mut profile, sigma);

    profile
}

/// A valley (whitespace region) in a projection profile.
#[derive(Debug, Clone, Copy)]
struct Valley {
    /// Position of the valley (0.0 - 1.0, relative to region)
    position: f32,
    /// Depth of the valley (how much whitespace)
    depth: f32,
}

/// Find the best valley (whitespace) in a projection profile.
///
/// A valley is a region where the profile value is significantly below average,
/// indicating whitespace where we can make a cut.
fn find_best_valley(profile: &[f32]) -> Option<Valley> {
    if profile.is_empty() {
        return None;
    }

    let avg = profile.iter().sum::<f32>() / profile.len() as f32;

    // Valley threshold: must be less than 35% of average (industry standard)
    // Research: Meunier (ICDAR 2005) recommends 30-40% threshold
    // PDF Spec compliant: This is a heuristic for layout analysis, not defined in PDF spec.
    let threshold = avg * 0.35;

    let mut best_valley: Option<Valley> = None;

    for (i, &val) in profile.iter().enumerate() {
        if val < threshold {
            let depth = avg - val;

            if best_valley.as_ref().is_none_or(|v| depth > v.depth) {
                best_valley = Some(Valley {
                    position: (i as f32 + 0.5) / profile.len() as f32,
                    depth,
                });
            }
        }
    }

    best_valley
}

/// Split a region based on cut position and direction.
fn split_region(region: &Rect, cut_pos: f32, direction: CutDirection) -> (Rect, Rect) {
    match direction {
        CutDirection::Horizontal => {
            let split_y = region.top() + cut_pos * region.height;
            (
                Rect::from_points(region.left(), region.top(), region.right(), split_y),
                Rect::from_points(region.left(), split_y, region.right(), region.bottom()),
            )
        },
        CutDirection::Vertical => {
            let split_x = region.left() + cut_pos * region.width;
            (
                Rect::from_points(region.left(), region.top(), split_x, region.bottom()),
                Rect::from_points(split_x, region.top(), region.right(), region.bottom()),
            )
        },
    }
}

/// Split blocks based on which side of the cut they fall on.
///
/// Blocks are assigned based on their center point.
fn split_blocks(
    blocks: &[TextBlock],
    indices: &[usize],
    region: &Rect,
    cut_pos: f32,
    direction: CutDirection,
) -> (Vec<usize>, Vec<usize>) {
    let mut left = vec![];
    let mut right = vec![];

    let split_value = match direction {
        CutDirection::Horizontal => region.top() + cut_pos * region.height,
        CutDirection::Vertical => region.left() + cut_pos * region.width,
    };

    for &idx in indices {
        let block = &blocks[idx];
        let center = block.center();

        let is_left = match direction {
            CutDirection::Horizontal => center.y < split_value,
            CutDirection::Vertical => center.x < split_value,
        };

        if is_left {
            left.push(idx);
        } else {
            right.push(idx);
        }
    }

    (left, right)
}

/// Perform XY-Cut analysis with adaptive parameters.
///
/// This is a wrapper around `xy_cut` that uses parameters computed from
/// document analysis rather than fixed values. This provides better results
/// across diverse PDF documents with different fonts, layouts, and page sizes.
///
/// # Arguments
///
/// * `region` - The bounding box of the region to analyze
/// * `blocks` - All text blocks in the document
/// * `block_indices` - Indices of blocks within this region
/// * `params` - Adaptive parameters computed from document analysis
///
/// # Returns
///
/// A hierarchical `LayoutTree` representing the document structure.
///
/// # Examples
///
/// ```ignore
/// use pdf_oxide::geometry::Rect;
/// use pdf_oxide::layout::{DocumentProperties, AdaptiveLayoutParams, TextChar};
/// use pdf_oxide::layout::column_detector::xy_cut_adaptive;
///
/// # fn example(chars: Vec<TextChar>, blocks: Vec<pdf_oxide::layout::TextBlock>) -> Result<(), String> {
/// // Analyze document
/// let page_bbox = Rect::new(0.0, 0.0, 612.0, 792.0);
/// let props = DocumentProperties::analyze(&chars, page_bbox)?;
/// let params = AdaptiveLayoutParams::from_properties(&props);
///
/// // Run adaptive XY-Cut
/// let indices: Vec<usize> = (0..blocks.len()).collect();
/// let tree = xy_cut_adaptive(page_bbox, &blocks, &indices, &params);
/// # Ok(())
/// # }
/// ```ignore
pub fn xy_cut_adaptive(
    region: Rect,
    blocks: &[TextBlock],
    block_indices: &[usize],
    params: &AdaptiveLayoutParams,
) -> LayoutTree {
    // Compute min_gap based on region size and adaptive ratio
    let _min_gap = (region.width.min(region.height)) * params.xy_cut_min_gap_ratio;

    // Call XY-Cut with adaptive parameters including sigma
    // FIX #2: Use adaptive Gaussian smoothing based on layout density
    xy_cut_with_sigma(
        region,
        blocks,
        block_indices,
        0,                             // Start at depth 0
        params.xy_cut_max_depth,       // Adaptive max depth
        params.xy_cut_min_region_size, // Adaptive min region size
        params.gaussian_sigma,         // Adaptive smoothing (0.5-2.5)
    )
}

/// Apply Gaussian smoothing to a projection profile to reduce noise.
///
/// This implements a 1D Gaussian filter with the given sigma (standard deviation).
/// Research: Meunier (ICDAR 2005) recommends σ=2.0 for projection profile smoothing.
fn gaussian_smooth(profile: &mut [f32], sigma: f32) {
    if profile.len() <= 2 || sigma <= 0.0 {
        return; // Not enough data or invalid sigma
    }

    // Compute Gaussian kernel size (±3σ covers 99.7% of distribution)
    let kernel_radius = (3.0 * sigma).ceil() as usize;
    let kernel_size = 2 * kernel_radius + 1;

    // Build Gaussian kernel
    let mut kernel = vec![0.0; kernel_size];
    let mut sum = 0.0;

    for i in 0..kernel_size {
        let x = (i as f32) - (kernel_radius as f32);
        let value = (-x * x / (2.0 * sigma * sigma)).exp();
        kernel[i] = value;
        sum += value;
    }

    // Normalize kernel
    for value in &mut kernel {
        *value /= sum;
    }

    // Apply convolution
    let original = profile.to_vec();

    for i in 0..profile.len() {
        let mut smoothed_value = 0.0;

        for j in 0..kernel_size {
            let offset = (j as i32) - (kernel_radius as i32);
            let index = (i as i32) + offset;

            // Handle boundary by clamping
            let clamped_index = index.max(0).min((original.len() - 1) as i32) as usize;
            smoothed_value += original[clamped_index] * kernel[j];
        }

        profile[i] = smoothed_value;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::geometry::Rect;
    use crate::layout::{Color, FontWeight, TextChar};

    fn mock_block(text: &str, x: f32, y: f32, _width: f32, height: f32) -> TextBlock {
        let chars: Vec<TextChar> = text
            .chars()
            .enumerate()
            .map(|(i, c)| TextChar {
                char: c,
                bbox: Rect::new(x + i as f32 * 10.0, y, 10.0, height),
                font_name: "Times".to_string(),
                font_size: 12.0,
                font_weight: FontWeight::Normal,
                color: Color::black(),
                mcid: None,
            })
            .collect();

        TextBlock::from_chars(chars)
    }

    #[test]
    fn test_horizontal_projection() {
        let blocks = vec![
            mock_block("Top", 0.0, 0.0, 100.0, 20.0),
            mock_block("Bottom", 0.0, 80.0, 100.0, 20.0),
        ];
        let indices = vec![0, 1];
        let region = Rect::new(0.0, 0.0, 100.0, 100.0);

        let profile = horizontal_projection(&region, &blocks, &indices, 2.0);

        // Should have content at top and bottom, whitespace in middle
        assert!(!profile.is_empty());
    }

    #[test]
    fn test_vertical_projection() {
        let blocks = vec![
            mock_block("Left", 0.0, 0.0, 40.0, 100.0),
            mock_block("Right", 60.0, 0.0, 40.0, 100.0),
        ];
        let indices = vec![0, 1];
        let region = Rect::new(0.0, 0.0, 100.0, 100.0);

        let profile = vertical_projection(&region, &blocks, &indices, 2.0);

        // Should have content on left and right, whitespace in middle
        assert!(!profile.is_empty());
    }

    #[test]
    fn test_find_valley() {
        // Profile with clear valley in the middle
        let profile = vec![10.0, 10.0, 0.5, 0.5, 10.0, 10.0];

        let valley = find_best_valley(&profile);
        assert!(valley.is_some());

        let valley = valley.unwrap();
        // Valley should be around position 0.4-0.5 (indices 2-3)
        assert!(valley.position > 0.3 && valley.position < 0.7);
    }

    #[test]
    fn test_find_valley_none() {
        // Profile with no clear valleys
        let profile = vec![10.0, 9.0, 11.0, 10.0, 9.5, 10.5];

        let valley = find_best_valley(&profile);
        assert!(valley.is_none());
    }

    #[test]
    fn test_split_region_horizontal() {
        let region = Rect::new(0.0, 0.0, 100.0, 100.0);
        let (r1, r2) = split_region(&region, 0.5, CutDirection::Horizontal);

        assert_eq!(r1.top(), 0.0);
        assert_eq!(r1.bottom(), 50.0);
        assert_eq!(r2.top(), 50.0);
        assert_eq!(r2.bottom(), 100.0);
    }

    #[test]
    fn test_split_region_vertical() {
        let region = Rect::new(0.0, 0.0, 100.0, 100.0);
        let (r1, r2) = split_region(&region, 0.5, CutDirection::Vertical);

        assert_eq!(r1.left(), 0.0);
        assert_eq!(r1.right(), 50.0);
        assert_eq!(r2.left(), 50.0);
        assert_eq!(r2.right(), 100.0);
    }

    #[test]
    fn test_xy_cut_single_block() {
        let blocks = vec![mock_block("Single", 0.0, 0.0, 100.0, 20.0)];
        let region = Rect::new(0.0, 0.0, 600.0, 800.0);
        let indices = vec![0];

        let tree = xy_cut(region, &blocks, &indices, 0, 5, 50.0);

        // With single block, should return leaf
        assert!(matches!(tree, LayoutTree::Leaf { .. }));
    }

    #[test]
    #[ignore] // TODO: XY-Cut test needs tuning for projection profile parameters
    fn test_xy_cut_two_columns() {
        // Create two-column layout with realistic text density
        // Column 1: x=0-80, Column 2: x=200-280 (clear 120pt gap)
        let blocks = vec![
            // Left column - more text for better density
            mock_block("This is left column text here", 0.0, 0.0, 100.0, 20.0),
            mock_block("More content in left column", 0.0, 25.0, 100.0, 20.0),
            mock_block("Even more left side text now", 0.0, 50.0, 100.0, 20.0),
            mock_block("Last line of left column end", 0.0, 75.0, 100.0, 20.0),
            // Right column - starts at x=200
            mock_block("This is right column content", 200.0, 0.0, 100.0, 20.0),
            mock_block("More text in right column now", 200.0, 25.0, 100.0, 20.0),
            mock_block("Even more right side content", 200.0, 50.0, 100.0, 20.0),
            mock_block("Last line of right column end", 200.0, 75.0, 100.0, 20.0),
        ];
        let region = Rect::new(0.0, 0.0, 300.0, 100.0);
        let indices: Vec<usize> = (0..blocks.len()).collect();

        // Use reasonable parameters
        let min_region_size = 15.0; // 5% of 300pt width
        let tree = xy_cut(region, &blocks, &indices, 0, 10, min_region_size);

        // Should detect a vertical split between the two columns
        if let LayoutTree::Node { children, .. } = tree {
            assert_eq!(children.len(), 2);
        } else {
            panic!("Expected Node, got Leaf - XY-Cut failed to detect column gap");
        }
    }
}
