"""Type stubs for pdf_oxide"""

from typing import Optional, Tuple

class PdfDocument:
    """
    PDF document reader and converter.

    Provides functionality for parsing PDFs, extracting text,
    and converting to various output formats.

    Example:
        >>> doc = PdfDocument("sample.pdf")
        >>> print(doc.version())
        (1, 7)
        >>> text = doc.extract_text(0)
    """

    def __init__(self, path: str) -> None:
        """
        Open a PDF file.

        Args:
            path: Path to the PDF file

        Raises:
            IOError: If the file cannot be opened or is not a valid PDF

        Example:
            >>> doc = PdfDocument("sample.pdf")
        """
        ...

    def version(self) -> Tuple[int, int]:
        """
        Get PDF version.

        Returns:
            Tuple of (major, minor) version numbers, e.g. (1, 7) for PDF 1.7

        Example:
            >>> doc = PdfDocument("sample.pdf")
            >>> major, minor = doc.version()
            >>> print(f"PDF {major}.{minor}")
        """
        ...

    def page_count(self) -> int:
        """
        Get the number of pages in the document.

        Returns:
            Number of pages

        Raises:
            RuntimeError: If page count cannot be determined

        Example:
            >>> doc = PdfDocument("sample.pdf")
            >>> print(f"Pages: {doc.page_count()}")
        """
        ...

    def extract_text(self, page: int) -> str:
        """
        Extract text from a page.

        Args:
            page: Page index (0-based)

        Returns:
            Extracted text as a string

        Raises:
            RuntimeError: If text extraction fails or page index is invalid

        Example:
            >>> doc = PdfDocument("sample.pdf")
            >>> text = doc.extract_text(0)
            >>> print(text[:100])
        """
        ...

    def to_markdown(
        self,
        page: int,
        preserve_layout: bool = False,
        detect_headings: bool = True,
        include_images: bool = True,
        image_output_dir: Optional[str] = None,
    ) -> str:
        """
        Convert a page to Markdown format.

        Args:
            page: Page index (0-based)
            preserve_layout: If True, preserve visual layout (default: False)
            detect_headings: If True, detect headings based on font size (default: True)
            include_images: If True, include images in output (default: True)
            image_output_dir: Directory to save images, or None to skip saving (default: None)

        Returns:
            Markdown text

        Raises:
            RuntimeError: If conversion fails

        Example:
            >>> doc = PdfDocument("paper.pdf")
            >>> markdown = doc.to_markdown(0, detect_headings=True)
            >>> with open("output.md", "w") as f:
            ...     f.write(markdown)
        """
        ...

    def to_html(
        self,
        page: int,
        preserve_layout: bool = False,
        detect_headings: bool = True,
        include_images: bool = True,
        image_output_dir: Optional[str] = None,
    ) -> str:
        """
        Convert a page to HTML format.

        Args:
            page: Page index (0-based)
            preserve_layout: If True, preserve visual layout with CSS positioning (default: False)
            detect_headings: If True, detect headings based on font size (default: True)
            include_images: If True, include images in output (default: True)
            image_output_dir: Directory to save images, or None to skip saving (default: None)

        Returns:
            HTML text

        Raises:
            RuntimeError: If conversion fails

        Example:
            >>> doc = PdfDocument("paper.pdf")
            >>> html = doc.to_html(0, preserve_layout=False)
            >>> with open("output.html", "w") as f:
            ...     f.write(html)
        """
        ...

    def to_markdown_all(
        self,
        preserve_layout: bool = False,
        detect_headings: bool = True,
        include_images: bool = True,
        image_output_dir: Optional[str] = None,
    ) -> str:
        """
        Convert all pages to Markdown format.

        Pages are separated by horizontal rules (---).

        Args:
            preserve_layout: If True, preserve visual layout (default: False)
            detect_headings: If True, detect headings based on font size (default: True)
            include_images: If True, include images in output (default: True)
            image_output_dir: Directory to save images, or None to skip saving (default: None)

        Returns:
            Markdown text containing all pages

        Raises:
            RuntimeError: If conversion fails

        Example:
            >>> doc = PdfDocument("book.pdf")
            >>> markdown = doc.to_markdown_all(detect_headings=True)
            >>> with open("book.md", "w") as f:
            ...     f.write(markdown)
        """
        ...

    def to_html_all(
        self,
        preserve_layout: bool = False,
        detect_headings: bool = True,
        include_images: bool = True,
        image_output_dir: Optional[str] = None,
    ) -> str:
        """
        Convert all pages to HTML format.

        Each page is wrapped in a div.page element with a data-page attribute.

        Args:
            preserve_layout: If True, preserve visual layout with CSS positioning (default: False)
            detect_headings: If True, detect headings based on font size (default: True)
            include_images: If True, include images in output (default: True)
            image_output_dir: Directory to save images, or None to skip saving (default: None)

        Returns:
            HTML text containing all pages

        Raises:
            RuntimeError: If conversion fails

        Example:
            >>> doc = PdfDocument("book.pdf")
            >>> html = doc.to_html_all(preserve_layout=True)
            >>> with open("book.html", "w") as f:
            ...     f.write(html)
        """
        ...

    def __repr__(self) -> str:
        """
        String representation of the document.

        Returns:
            Representation showing PDF version
        """
        ...

__version__: str
__all__: list[str]
