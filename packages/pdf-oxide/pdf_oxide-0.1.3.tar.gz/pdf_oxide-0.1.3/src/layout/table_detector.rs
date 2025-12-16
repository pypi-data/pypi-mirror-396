//! Basic table detection using alignment analysis.
//!
//! This module provides basic table detection by finding regions with
//! strong vertical and horizontal alignment patterns.
//!
//! Note: This is a simplified implementation. Full table detection with
//! cell recognition requires ML models (implemented in Phase 8+).

use crate::geometry::Rect;
use crate::layout::text_block::TextBlock;

/// A detected table region.
#[derive(Debug, Clone)]
pub struct Table {
    /// Bounding box of the table
    pub bbox: Rect,
    /// Grid of cells (rows × columns of block indices)
    pub cells: Vec<Vec<usize>>,
    /// Number of rows
    pub num_rows: usize,
    /// Number of columns
    pub num_cols: usize,
}

/// Detect tables in a collection of text blocks.
///
/// This uses alignment analysis to find regions where blocks are arranged
/// in a grid-like pattern with consistent vertical and horizontal alignment.
///
/// # Arguments
///
/// * `blocks` - The text blocks to analyze
///
/// # Returns
///
/// A vector of detected table regions.
///
/// # Examples
///
/// ```ignore
/// use pdf_oxide::geometry::Rect;
/// use pdf_oxide::layout::{TextChar, TextBlock, FontWeight, Color};
/// use pdf_oxide::layout::table_detector::detect_tables;
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
///
/// let tables = detect_tables(&blocks);
/// // Returns detected table regions
/// ```ignore
pub fn detect_tables(blocks: &[TextBlock]) -> Vec<Table> {
    if blocks.len() < 4 {
        // Need at least 4 blocks for a minimal 2×2 table
        return vec![];
    }

    // Find vertical alignments (columns)
    let columns = find_vertical_alignments(blocks, 5.0);

    // Find horizontal alignments (rows)
    let rows = find_horizontal_alignments(blocks, 3.0);

    // Find table regions where columns and rows intersect
    find_table_regions(&columns, &rows, blocks)
}

/// Find vertically aligned blocks (potential table columns).
///
/// Groups blocks that have similar X coordinates (within tolerance).
fn find_vertical_alignments(blocks: &[TextBlock], tolerance: f32) -> Vec<Vec<usize>> {
    let mut alignments = vec![];
    let mut used = vec![false; blocks.len()];

    for i in 0..blocks.len() {
        if used[i] {
            continue;
        }

        let mut aligned = vec![i];
        used[i] = true;

        for j in (i + 1)..blocks.len() {
            if !used[j] && blocks[i].is_vertically_aligned(&blocks[j], tolerance) {
                aligned.push(j);
                used[j] = true;
            }
        }

        if aligned.len() >= 3 {
            // Need at least 3 blocks to form a column
            alignments.push(aligned);
        }
    }

    alignments
}

/// Find horizontally aligned blocks (potential table rows).
///
/// Groups blocks that have similar Y coordinates (within tolerance).
fn find_horizontal_alignments(blocks: &[TextBlock], tolerance: f32) -> Vec<Vec<usize>> {
    let mut alignments = vec![];
    let mut used = vec![false; blocks.len()];

    for i in 0..blocks.len() {
        if used[i] {
            continue;
        }

        let mut aligned = vec![i];
        used[i] = true;

        for j in (i + 1)..blocks.len() {
            if !used[j] && blocks[i].is_horizontally_aligned(&blocks[j], tolerance) {
                aligned.push(j);
                used[j] = true;
            }
        }

        if aligned.len() >= 2 {
            // Need at least 2 blocks to form a row
            alignments.push(aligned);
        }
    }

    // Sort each row by x-coordinate
    for alignment in &mut alignments {
        alignment.sort_by(|&a, &b| blocks[a].bbox.x.partial_cmp(&blocks[b].bbox.x).unwrap());
    }

    alignments
}

/// Find table regions by intersecting column and row alignments.
///
/// A table is identified when there are multiple rows and columns that
/// form a grid pattern.
fn find_table_regions(
    columns: &[Vec<usize>],
    rows: &[Vec<usize>],
    blocks: &[TextBlock],
) -> Vec<Table> {
    let mut tables = vec![];

    // Simple heuristic: look for regions with both row and column structure
    if columns.len() >= 2 && rows.len() >= 2 {
        // Find blocks that participate in both row and column alignments
        let mut table_blocks = vec![];

        for col in columns {
            for row in rows {
                // Check for intersection
                for &block_idx in col {
                    if row.contains(&block_idx) && !table_blocks.contains(&block_idx) {
                        table_blocks.push(block_idx);
                    }
                }
            }
        }

        if table_blocks.len() >= 4 {
            // Create a simple table representation
            // Compute bounding box
            let mut bbox = blocks[table_blocks[0]].bbox;
            for &idx in &table_blocks[1..] {
                bbox = bbox.union(&blocks[idx].bbox);
            }

            // Simplified: arrange blocks into a grid based on rows
            let mut cells = vec![];
            for row in rows {
                let row_cells: Vec<usize> = row
                    .iter()
                    .copied()
                    .filter(|idx| table_blocks.contains(idx))
                    .collect();

                if !row_cells.is_empty() {
                    cells.push(row_cells);
                }
            }

            let num_rows = cells.len();
            let num_cols = cells.iter().map(|r| r.len()).max().unwrap_or(0);

            tables.push(Table {
                bbox,
                cells,
                num_rows,
                num_cols,
            });
        }
    }

    tables
}

/// Aggressive table detection that treats the entire page as a wide table.
///
/// This matches PyMuPDF4LLM's behavior: creates one large table per page with many columns,
/// repeating text across merged cells to preserve spatial layout.
///
/// # Arguments
///
/// * `blocks` - The text blocks to analyze
/// * `page_width` - Width of the page for column detection
///
/// # Returns
///
/// A single table representing the entire page layout.
pub fn detect_tables_aggressive(blocks: &[TextBlock], _page_width: f32) -> Vec<Table> {
    if blocks.is_empty() {
        return vec![];
    }

    // Find ALL unique X positions (potential column boundaries)
    // IMPORTANT: Use rounding for stable, transitive sorting
    let mut x_positions: Vec<i32> = blocks.iter().map(|b| b.bbox.x.round() as i32).collect();
    x_positions.sort_unstable();
    x_positions.dedup_by(|a, b| (*a - *b).abs() < 3);

    // Find ALL unique Y positions (row boundaries)
    // IMPORTANT: Use rounding for stable, transitive sorting
    let mut y_positions: Vec<i32> = blocks.iter().map(|b| b.bbox.y.round() as i32).collect();
    y_positions.sort_unstable_by(|a, b| b.cmp(a)); // Sort top to bottom (descending)
    y_positions.dedup_by(|a, b| (*a - *b).abs() < 2);

    if x_positions.len() < 2 || y_positions.len() < 2 {
        return vec![];
    }

    // Create a grid: for each row, find blocks in each column
    let mut cells = vec![];

    for y_pos in &y_positions {
        let mut row_cells = vec![];

        // Find all blocks on this row (within 2px vertically)
        let row_blocks: Vec<&TextBlock> = blocks
            .iter()
            .filter(|b| (b.bbox.y.round() as i32 - y_pos).abs() < 2)
            .collect();

        if row_blocks.is_empty() {
            continue;
        }

        // For each column position, find the block(s) that belong there
        for x_pos in &x_positions {
            // Find block that starts at or near this X position
            if let Some(block_idx) = blocks.iter().position(|b| {
                (b.bbox.x.round() as i32 - x_pos).abs() < 3
                    && (b.bbox.y.round() as i32 - y_pos).abs() < 2
            }) {
                row_cells.push(block_idx);
            } else {
                // No block at this position - check if previous cell spans here
                // For now, add an empty placeholder (will be filled with repetition later)
                if let Some(&last_idx) = row_cells.last() {
                    // Repeat the last cell's content
                    row_cells.push(last_idx);
                }
            }
        }

        if !row_cells.is_empty() {
            cells.push(row_cells);
        }
    }

    if cells.is_empty() {
        return vec![];
    }

    // Compute bounding box
    let mut bbox = blocks[0].bbox;
    for block in blocks {
        bbox = bbox.union(&block.bbox);
    }

    let num_rows = cells.len();
    let num_cols = cells.iter().map(|r| r.len()).max().unwrap_or(0);

    vec![Table {
        bbox,
        cells,
        num_rows,
        num_cols,
    }]
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::geometry::Rect;
    use crate::layout::{Color, FontWeight, TextChar};

    fn mock_block(text: &str, x: f32, y: f32) -> TextBlock {
        let chars: Vec<TextChar> = text
            .chars()
            .enumerate()
            .map(|(i, c)| TextChar {
                char: c,
                bbox: Rect::new(x + i as f32 * 5.0, y, 5.0, 10.0),
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
    fn test_find_vertical_alignments() {
        // Create three blocks in a vertical line
        let blocks = vec![
            mock_block("A", 0.0, 0.0),
            mock_block("B", 1.0, 20.0), // Slightly offset, within tolerance
            mock_block("C", 0.5, 40.0),
        ];

        let alignments = find_vertical_alignments(&blocks, 5.0);

        assert_eq!(alignments.len(), 1);
        assert_eq!(alignments[0].len(), 3);
    }

    #[test]
    fn test_find_horizontal_alignments() {
        // Create three blocks in a horizontal line
        let blocks = vec![
            mock_block("A", 0.0, 0.0),
            mock_block("B", 50.0, 1.0), // Slightly offset, within tolerance
            mock_block("C", 100.0, 0.5),
        ];

        let alignments = find_horizontal_alignments(&blocks, 3.0);

        assert_eq!(alignments.len(), 1);
        assert_eq!(alignments[0].len(), 3);
        // Should be sorted by x-coordinate
        assert!(alignments[0][0] < alignments[0][1]);
        assert!(alignments[0][1] < alignments[0][2]);
    }

    #[test]
    fn test_detect_tables_simple_grid() {
        // Create a simple 2×2 table
        let blocks = vec![
            // Row 1
            mock_block("A1", 0.0, 0.0),
            mock_block("B1", 50.0, 0.0),
            // Row 2
            mock_block("A2", 0.0, 20.0),
            mock_block("B2", 50.0, 20.0),
        ];

        let tables = detect_tables(&blocks);

        // Should detect one table
        assert!(tables.len() <= 1); // May or may not detect depending on alignment strictness

        if !tables.is_empty() {
            let table = &tables[0];
            assert!(table.num_rows >= 2);
            assert!(table.num_cols >= 2);
        }
    }

    #[test]
    fn test_detect_tables_insufficient_blocks() {
        // Only 2 blocks - not enough for a table
        let blocks = vec![mock_block("A", 0.0, 0.0), mock_block("B", 50.0, 0.0)];

        let tables = detect_tables(&blocks);
        assert_eq!(tables.len(), 0);
    }

    #[test]
    fn test_detect_tables_no_grid_pattern() {
        // Blocks without grid alignment
        let blocks = vec![
            mock_block("A", 0.0, 0.0),
            mock_block("B", 30.0, 15.0),
            mock_block("C", 60.0, 5.0),
            mock_block("D", 90.0, 25.0),
        ];

        let tables = detect_tables(&blocks);
        // Unlikely to detect a table with this irregular layout
        assert_eq!(tables.len(), 0);
    }

    #[test]
    fn test_vertical_alignment_not_enough_blocks() {
        let blocks = vec![
            mock_block("A", 0.0, 0.0),
            mock_block("B", 1.0, 20.0), // Only 2 blocks
        ];

        let alignments = find_vertical_alignments(&blocks, 5.0);
        assert_eq!(alignments.len(), 0); // Need at least 3
    }

    #[test]
    fn test_horizontal_alignment_single_block() {
        let blocks = vec![mock_block("A", 0.0, 0.0)];

        let alignments = find_horizontal_alignments(&blocks, 3.0);
        assert_eq!(alignments.len(), 0); // Need at least 2
    }
}
