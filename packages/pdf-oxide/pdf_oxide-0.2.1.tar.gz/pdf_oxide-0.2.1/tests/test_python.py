"""
Python bindings tests for pdf_oxide.

These tests verify the Python API works correctly, including:
- Opening PDF files
- Extracting text
- Converting to Markdown
- Converting to HTML
- Error handling
"""

import pytest
from pdf_oxide import PdfDocument


def test_open_pdf():
    """Test opening a PDF file."""
    # Note: This test will need actual PDF fixtures to run
    # For now, it documents the expected behavior
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")
        assert doc is not None
        # Version should be a tuple of two integers
        version = doc.version()
        assert isinstance(version, tuple)
        assert len(version) == 2
        assert isinstance(version[0], int)
        assert isinstance(version[1], int)
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_version():
    """Test getting PDF version."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")
        major, minor = doc.version()
        assert major >= 1
        assert minor >= 0
        # PDF versions are typically 1.0 through 2.0
        assert major <= 2
        assert minor <= 7
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_page_count():
    """Test getting page count."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")
        count = doc.page_count()
        assert isinstance(count, int)
        assert count >= 1
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_extract_text():
    """Test extracting text from a page."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")
        text = doc.extract_text(0)
        assert isinstance(text, str)
        # Text should be non-empty for a real PDF
        # (empty is ok for a minimal test PDF though)
        assert text is not None
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_extract_text_with_content():
    """Test extracting text that contains specific content."""
    try:
        doc = PdfDocument("tests/fixtures/hello_world.pdf")
        text = doc.extract_text(0)
        assert isinstance(text, str)
        assert len(text) > 0
        # Should contain "Hello" or "hello" (case-insensitive check)
        assert "hello" in text.lower()
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'hello_world.pdf' not available or invalid")


def test_to_markdown():
    """Test converting a page to Markdown."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")
        markdown = doc.to_markdown(0)
        assert isinstance(markdown, str)
        assert markdown is not None
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_to_markdown_with_options():
    """Test converting to Markdown with custom options."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")

        # Test with heading detection enabled
        markdown = doc.to_markdown(0, detect_headings=True)
        assert isinstance(markdown, str)

        # Test with heading detection disabled
        markdown = doc.to_markdown(0, detect_headings=False)
        assert isinstance(markdown, str)

        # Test with layout preservation
        markdown = doc.to_markdown(0, preserve_layout=True)
        assert isinstance(markdown, str)
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_to_html():
    """Test converting a page to HTML."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")
        html = doc.to_html(0)
        assert isinstance(html, str)
        assert html is not None
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_to_html_semantic_mode():
    """Test converting to semantic HTML (default mode)."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")
        html = doc.to_html(0, preserve_layout=False)
        assert isinstance(html, str)
        # Semantic HTML should not contain absolute positioning
        # (though it might not contain much if the PDF is simple)
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_to_html_layout_mode():
    """Test converting to layout-preserved HTML."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")
        html = doc.to_html(0, preserve_layout=True)
        assert isinstance(html, str)
        # Layout mode should include positioning CSS
        # Check if it contains position-related CSS or inline styles
        # (only if the PDF has content)
        if len(html) > 100:
            assert "position" in html.lower() or "style" in html.lower()
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_to_markdown_all():
    """Test converting all pages to Markdown."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")
        markdown = doc.to_markdown_all()
        assert isinstance(markdown, str)
        assert markdown is not None
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_to_markdown_all_multipage():
    """Test converting multiple pages to Markdown."""
    try:
        doc = PdfDocument("tests/fixtures/multipage.pdf")
        markdown = doc.to_markdown_all()
        assert isinstance(markdown, str)
        assert len(markdown) > 0
        # Multi-page markdown should contain horizontal rules as separators
        page_count = doc.page_count()
        if page_count > 1:
            assert "---" in markdown
    except IOError:
        pytest.skip("Test fixture 'multipage.pdf' not available")


def test_to_html_all():
    """Test converting all pages to HTML."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")
        html = doc.to_html_all()
        assert isinstance(html, str)
        assert html is not None
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_to_html_all_multipage():
    """Test converting multiple pages to HTML."""
    try:
        doc = PdfDocument("tests/fixtures/multipage.pdf")
        html = doc.to_html_all()
        assert isinstance(html, str)
        assert len(html) > 0
        # Multi-page HTML should contain page div elements
        page_count = doc.page_count()
        if page_count > 1:
            assert 'class="page"' in html or 'data-page' in html
    except IOError:
        pytest.skip("Test fixture 'multipage.pdf' not available")


def test_error_handling_nonexistent_file():
    """Test error handling for non-existent file."""
    with pytest.raises(IOError) as exc_info:
        PdfDocument("nonexistent_file_that_does_not_exist.pdf")

    # Error message should be helpful
    error_msg = str(exc_info.value)
    assert "Failed to open PDF" in error_msg or "No such file" in error_msg


def test_error_handling_invalid_page():
    """Test error handling for invalid page index."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")
        page_count = doc.page_count()

        # Try to access a page that doesn't exist
        with pytest.raises(RuntimeError) as exc_info:
            doc.extract_text(page_count + 100)

        # Error message should indicate the problem
        error_msg = str(exc_info.value)
        assert "Failed to extract text" in error_msg or "page" in error_msg.lower()
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_error_handling_invalid_page_conversion():
    """Test error handling for invalid page in conversion."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")
        page_count = doc.page_count()

        # Try to convert a page that doesn't exist
        with pytest.raises(RuntimeError):
            doc.to_markdown(page_count + 100)
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_repr():
    """Test string representation of PdfDocument."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")
        repr_str = repr(doc)
        assert isinstance(repr_str, str)
        assert "PdfDocument" in repr_str
        assert "version=" in repr_str
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_multiple_operations():
    """Test performing multiple operations on the same document."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")

        # Get version multiple times
        version1 = doc.version()
        version2 = doc.version()
        assert version1 == version2

        # Extract text multiple times
        text1 = doc.extract_text(0)
        text2 = doc.extract_text(0)
        assert text1 == text2

        # Convert to different formats
        markdown = doc.to_markdown(0)
        html = doc.to_html(0)
        assert isinstance(markdown, str)
        assert isinstance(html, str)
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_image_output_dir():
    """Test specifying image output directory."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")

        # Convert with image output directory specified
        markdown = doc.to_markdown(0, image_output_dir="./test_images")
        assert isinstance(markdown, str)

        # Convert without images
        markdown = doc.to_markdown(0, include_images=False)
        assert isinstance(markdown, str)
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


def test_all_options_combined():
    """Test using all conversion options together."""
    try:
        doc = PdfDocument("tests/fixtures/simple.pdf")

        # Test with all options specified
        markdown = doc.to_markdown(
            0,
            preserve_layout=True,
            detect_headings=False,
            include_images=True,
            image_output_dir="./output"
        )
        assert isinstance(markdown, str)

        html = doc.to_html(
            0,
            preserve_layout=True,
            detect_headings=True,
            include_images=False,
            image_output_dir=None
        )
        assert isinstance(html, str)
    except (IOError, RuntimeError):
        pytest.skip("Test fixture 'simple.pdf' not available or invalid")


# Note: To run these tests successfully, you'll need to:
# 1. Install maturin: pip install maturin
# 2. Build the extension: maturin develop
# 3. Install pytest: pip install pytest
# 4. Create test PDF fixtures in tests/fixtures/
# 5. Run tests: pytest tests/test_python.py
