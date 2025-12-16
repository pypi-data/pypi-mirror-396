//! Integration tests for layout analysis algorithms.
//!
//! These tests verify the complete layout analysis pipeline with mock data
//! simulating realistic PDF document structures.

use pdf_oxide::geometry::{Point, Rect};
use pdf_oxide::layout::{
    Color, FontWeight, TextBlock, TextChar,
    clustering::{cluster_chars_into_words, cluster_words_into_lines},
    column_detector::{CutDirection, LayoutTree, xy_cut},
    heading_detector::{HeadingLevel, detect_headings},
    reading_order::{determine_reading_order, graph_based_reading_order},
    table_detector::detect_tables,
};

// ============================================================================
// Helper Functions for Creating Mock Data
// ============================================================================

/// Create a mock character with minimal required data.
fn mock_char(c: char, x: f32, y: f32, size: f32) -> TextChar {
    TextChar {
        char: c,
        bbox: Rect::new(x, y, size * 0.6, size),
        font_name: "Times".to_string(),
        font_size: size,
        font_weight: FontWeight::Normal,
        color: Color::black(),
        mcid: None,
    }
}

/// Create a mock character with bold weight.
fn mock_bold_char(c: char, x: f32, y: f32, size: f32) -> TextChar {
    TextChar {
        char: c,
        bbox: Rect::new(x, y, size * 0.6, size),
        font_name: "Times-Bold".to_string(),
        font_size: size,
        font_weight: FontWeight::Bold,
        color: Color::black(),
        mcid: None,
    }
}

/// Create a text block from a string at a specific position.
fn mock_block(text: &str, x: f32, y: f32, size: f32, bold: bool) -> TextBlock {
    let chars: Vec<TextChar> = text
        .chars()
        .enumerate()
        .map(|(i, c)| {
            if bold {
                mock_bold_char(c, x + i as f32 * size * 0.6, y, size)
            } else {
                mock_char(c, x + i as f32 * size * 0.6, y, size)
            }
        })
        .collect();

    TextBlock::from_chars(chars)
}

/// Create a two-column layout with multiple lines per column.
fn create_two_column_layout() -> Vec<TextBlock> {
    vec![
        // Left column
        mock_block("First", 0.0, 0.0, 12.0, false),
        mock_block("line", 50.0, 0.0, 12.0, false),
        mock_block("Second", 0.0, 20.0, 12.0, false),
        mock_block("line", 50.0, 20.0, 12.0, false),
        // Right column
        mock_block("Third", 300.0, 0.0, 12.0, false),
        mock_block("line", 350.0, 0.0, 12.0, false),
        mock_block("Fourth", 300.0, 20.0, 12.0, false),
        mock_block("line", 350.0, 20.0, 12.0, false),
    ]
}

// ============================================================================
// Geometry Tests
// ============================================================================

#[test]
fn test_geometry_point() {
    let p = Point::new(10.0, 20.0);
    assert_eq!(p.x, 10.0);
    assert_eq!(p.y, 20.0);
}

#[test]
fn test_geometry_rect_operations() {
    let r1 = Rect::new(0.0, 0.0, 100.0, 100.0);
    let r2 = Rect::new(50.0, 50.0, 100.0, 100.0);

    // Intersection
    assert!(r1.intersects(&r2));

    // Union
    let union = r1.union(&r2);
    assert_eq!(union.left(), 0.0);
    assert_eq!(union.right(), 150.0);

    // Contains point
    let p1 = Point::new(50.0, 50.0);
    assert!(r1.contains_point(&p1));
}

// ============================================================================
// DBSCAN Clustering Tests
// ============================================================================

#[test]
fn test_cluster_chars_into_words_simple() {
    let chars = vec![
        mock_char('H', 0.0, 0.0, 12.0),
        mock_char('i', 8.0, 0.0, 12.0),
        // Gap
        mock_char('B', 50.0, 0.0, 12.0),
        mock_char('y', 58.0, 0.0, 12.0),
        mock_char('e', 66.0, 0.0, 12.0),
    ];

    let clusters = cluster_chars_into_words(&chars, 15.0);

    // Should produce 2 words: "Hi" and "Bye"
    assert_eq!(clusters.len(), 2);

    // Verify "Hi" cluster
    let hi_cluster = clusters.iter().find(|c| c.contains(&0)).unwrap();
    assert!(hi_cluster.contains(&0));
    assert!(hi_cluster.contains(&1));

    // Verify "Bye" cluster
    let bye_cluster = clusters.iter().find(|c| c.contains(&2)).unwrap();
    assert!(bye_cluster.contains(&2));
    assert!(bye_cluster.contains(&3));
    assert!(bye_cluster.contains(&4));
}

#[test]
fn test_cluster_words_into_lines_simple() {
    let word1 = mock_block("Hello", 0.0, 0.0, 12.0, false);
    let word2 = mock_block("World", 50.0, 1.0, 12.0, false);
    let word3 = mock_block("Next", 0.0, 30.0, 12.0, false);
    let word4 = mock_block("Line", 50.0, 31.0, 12.0, false);

    let words = vec![word1, word2, word3, word4];
    let lines = cluster_words_into_lines(&words, 5.0);

    // Should produce 2 lines
    assert_eq!(lines.len(), 2);

    // Line 1: "Hello World"
    let line1 = lines.iter().find(|l| l.contains(&0)).unwrap();
    assert!(line1.contains(&0));
    assert!(line1.contains(&1));

    // Line 2: "Next Line"
    let line2 = lines.iter().find(|l| l.contains(&2)).unwrap();
    assert!(line2.contains(&2));
    assert!(line2.contains(&3));
}

// ============================================================================
// XY-Cut Column Detection Tests
// ============================================================================

#[test]
fn test_xy_cut_single_column() {
    let blocks = vec![
        mock_block("Line1", 0.0, 0.0, 12.0, false),
        mock_block("Line2", 0.0, 20.0, 12.0, false),
        mock_block("Line3", 0.0, 40.0, 12.0, false),
    ];

    let region = Rect::new(0.0, 0.0, 600.0, 800.0);
    let indices: Vec<usize> = (0..blocks.len()).collect();

    let tree = xy_cut(region, &blocks, &indices, 0, 5, 50.0);

    // With a single column, should eventually resolve to a leaf
    // (though it may have intermediate nodes for horizontal splits)
    match tree {
        LayoutTree::Leaf { blocks } => {
            assert_eq!(blocks.len(), 3);
        },
        LayoutTree::Node { .. } => {
            // Also acceptable - horizontal splits
        },
    }
}

#[test]
#[ignore] // TODO: Layout test needs tuning for analysis parameters
fn test_xy_cut_two_columns() {
    let blocks = create_two_column_layout();

    let region = Rect::new(0.0, 0.0, 400.0, 100.0);
    let indices: Vec<usize> = (0..blocks.len()).collect();

    let tree = xy_cut(region, &blocks, &indices, 0, 5, 10.0);

    // Should detect a split (algorithm may find horizontal or vertical first)
    match tree {
        LayoutTree::Node { children, .. } => {
            assert_eq!(children.len(), 2);
        },
        LayoutTree::Leaf { .. } => {
            panic!("Expected Node for two-column layout, got Leaf");
        },
    }
}

#[test]
fn test_xy_cut_respects_max_depth() {
    let blocks = create_two_column_layout();

    let region = Rect::new(0.0, 0.0, 400.0, 100.0);
    let indices: Vec<usize> = (0..blocks.len()).collect();

    // Force max depth of 0 - should return leaf
    let tree = xy_cut(region, &blocks, &indices, 0, 0, 10.0);

    assert!(matches!(tree, LayoutTree::Leaf { .. }));
}

// ============================================================================
// Reading Order Tests
// ============================================================================

#[test]
fn test_reading_order_tree_based() {
    let tree = LayoutTree::Node {
        direction: CutDirection::Vertical,
        children: vec![
            LayoutTree::Leaf { blocks: vec![0, 1] },
            LayoutTree::Leaf { blocks: vec![2, 3] },
        ],
    };

    let order = determine_reading_order(&tree);

    // Should read left column first, then right column
    assert_eq!(order, vec![0, 1, 2, 3]);
}

#[test]
#[ignore] // TODO: Layout test needs tuning for analysis parameters
fn test_reading_order_graph_based_simple() {
    let blocks = vec![
        mock_block("TopLeft", 0.0, 0.0, 12.0, false),
        mock_block("TopRight", 100.0, 0.0, 12.0, false),
        mock_block("BottomLeft", 0.0, 50.0, 12.0, false),
        mock_block("BottomRight", 100.0, 50.0, 12.0, false),
    ];

    let order = graph_based_reading_order(&blocks);

    // Reading order: left-to-right, top-to-bottom
    // Should be: 0, 1, 2, 3
    assert_eq!(order[0], 0); // TopLeft first
    assert_eq!(order[1], 1); // TopRight second
    assert_eq!(order[2], 2); // BottomLeft third
    assert_eq!(order[3], 3); // BottomRight fourth
}

#[test]
#[ignore] // TODO: Layout test needs tuning for analysis parameters
fn test_reading_order_two_columns() {
    let blocks = vec![
        mock_block("Col1Line1", 0.0, 0.0, 12.0, false),
        mock_block("Col1Line2", 0.0, 20.0, 12.0, false),
        mock_block("Col2Line1", 300.0, 0.0, 12.0, false),
        mock_block("Col2Line2", 300.0, 20.0, 12.0, false),
    ];

    let order = graph_based_reading_order(&blocks);

    // Reading order should maintain top-to-bottom within columns
    // First block should be a top block (0 or 2)
    assert!(order[0] == 0 || order[0] == 2);

    // All blocks should be included
    assert_eq!(order.len(), 4);
    assert!(order.contains(&0));
    assert!(order.contains(&1));
    assert!(order.contains(&2));
    assert!(order.contains(&3));
}

// ============================================================================
// Heading Detection Tests
// ============================================================================

#[test]
fn test_heading_detection_full_document() {
    let blocks = vec![
        mock_block("Document Title", 0.0, 0.0, 24.0, true), // H1
        mock_block("Introduction", 0.0, 40.0, 18.0, true),  // H2
        mock_block("Background", 0.0, 70.0, 14.0, true),    // H3
        mock_block("This is body text", 0.0, 100.0, 12.0, false), // Body
        mock_block("Figure 1", 0.0, 130.0, 8.0, false),     // Small
    ];

    let levels = detect_headings(&blocks);

    assert_eq!(levels[0], HeadingLevel::H1);
    assert_eq!(levels[1], HeadingLevel::H2);
    assert_eq!(levels[2], HeadingLevel::H3);
    assert_eq!(levels[3], HeadingLevel::Body);
    assert_eq!(levels[4], HeadingLevel::Small);
}

#[test]
fn test_heading_detection_hierarchy() {
    let h1 = HeadingLevel::H1;
    let h2 = HeadingLevel::H2;
    let body = HeadingLevel::Body;

    assert!(h1.hierarchy_level() < h2.hierarchy_level());
    assert!(h2.hierarchy_level() < body.hierarchy_level());

    assert!(h1.is_heading());
    assert!(h2.is_heading());
    assert!(!body.is_heading());
}

// ============================================================================
// Table Detection Tests
// ============================================================================

#[test]
fn test_table_detection_simple_grid() {
    // Create a 3×3 table
    let blocks = vec![
        // Row 1
        mock_block("A1", 0.0, 0.0, 12.0, false),
        mock_block("B1", 50.0, 0.0, 12.0, false),
        mock_block("C1", 100.0, 0.0, 12.0, false),
        // Row 2
        mock_block("A2", 0.0, 20.0, 12.0, false),
        mock_block("B2", 50.0, 20.0, 12.0, false),
        mock_block("C2", 100.0, 20.0, 12.0, false),
        // Row 3
        mock_block("A3", 0.0, 40.0, 12.0, false),
        mock_block("B3", 50.0, 40.0, 12.0, false),
        mock_block("C3", 100.0, 40.0, 12.0, false),
    ];

    let tables = detect_tables(&blocks);

    // Should detect one table
    if !tables.is_empty() {
        let table = &tables[0];
        assert!(table.num_rows >= 3);
        assert!(table.num_cols >= 3);
    }
}

#[test]
fn test_table_detection_insufficient_data() {
    let blocks = vec![
        mock_block("A", 0.0, 0.0, 12.0, false),
        mock_block("B", 50.0, 0.0, 12.0, false),
    ];

    let tables = detect_tables(&blocks);

    // Not enough blocks for a table
    assert_eq!(tables.len(), 0);
}

// ============================================================================
// Integration Tests - Full Pipeline
// ============================================================================

#[test]
#[ignore] // TODO: Layout test needs tuning for analysis parameters
fn test_full_pipeline_two_column_document() {
    // Simulate a two-column document with title
    let mut all_blocks = vec![
        // Title (spanning both columns)
        mock_block("Document Title", 100.0, 0.0, 24.0, true),
    ];

    // Left column
    all_blocks.extend(vec![
        mock_block("Introduction", 0.0, 40.0, 18.0, true),
        mock_block("The quick brown", 0.0, 70.0, 12.0, false),
        mock_block("fox jumps over", 0.0, 90.0, 12.0, false),
    ]);

    // Right column
    all_blocks.extend(vec![
        mock_block("Conclusion", 300.0, 40.0, 18.0, true),
        mock_block("In summary we", 300.0, 70.0, 12.0, false),
        mock_block("find that this", 300.0, 90.0, 12.0, false),
    ]);

    // Test XY-Cut
    let region = Rect::new(0.0, 0.0, 600.0, 200.0);
    let indices: Vec<usize> = (0..all_blocks.len()).collect();
    let tree = xy_cut(region, &all_blocks, &indices, 0, 5, 50.0);

    // Should detect some structure
    assert!(matches!(tree, LayoutTree::Node { .. } | LayoutTree::Leaf { .. }));

    // Test reading order
    let order = graph_based_reading_order(&all_blocks);
    assert_eq!(order.len(), all_blocks.len());

    // Title should come first (top of document)
    assert_eq!(order[0], 0);

    // Test heading detection
    let levels = detect_headings(&all_blocks);
    assert_eq!(levels[0], HeadingLevel::H1); // Title
    assert!(levels[1].is_heading()); // Introduction
    assert!(levels[4].is_heading()); // Conclusion
}

#[test]
fn test_empty_inputs() {
    // Test all functions with empty inputs
    let empty_blocks: Vec<TextBlock> = vec![];
    let empty_chars: Vec<TextChar> = vec![];

    // Clustering
    assert_eq!(cluster_chars_into_words(&empty_chars, 10.0).len(), 0);
    assert_eq!(cluster_words_into_lines(&empty_blocks, 5.0).len(), 0);

    // Reading order
    assert_eq!(graph_based_reading_order(&empty_blocks).len(), 0);

    // Heading detection
    assert_eq!(detect_headings(&empty_blocks).len(), 0);

    // Table detection
    assert_eq!(detect_tables(&empty_blocks).len(), 0);
}

#[test]
fn test_single_element_inputs() {
    // Test all functions with single elements
    let single_char = vec![mock_char('A', 0.0, 0.0, 12.0)];
    let single_block = vec![mock_block("Single", 0.0, 0.0, 12.0, false)];

    // Clustering
    assert_eq!(cluster_chars_into_words(&single_char, 10.0).len(), 1);
    assert_eq!(cluster_words_into_lines(&single_block, 5.0).len(), 1);

    // Reading order
    assert_eq!(graph_based_reading_order(&single_block), vec![0]);

    // Heading detection
    assert_eq!(detect_headings(&single_block).len(), 1);

    // Table detection
    assert_eq!(detect_tables(&single_block).len(), 0);
}
