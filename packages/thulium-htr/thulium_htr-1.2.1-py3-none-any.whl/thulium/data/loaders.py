# Copyright 2025 Thulium Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Data loading utilities for images and PDF documents.

This module provides functions for loading images and PDF documents into
PIL Image format for processing by the HTR pipeline. It handles file
I/O, format conversion, and provides a unified interface for different
document types.

Functions:
    load_image: Load a single image file into PIL format.
    load_pdf_pages: Convert PDF pages to PIL Images using pdf2image.
    load_document: Automatically detect file type and load appropriately.
    is_pdf_supported: Check if PDF loading is available.

Module Constants:
    _PDF_AVAILABLE: Boolean indicating pdf2image availability.

Example:
    Loading different document types:

    >>> from thulium.data.loaders import load_image, load_document
    >>> # Single image
    >>> img = load_image("handwriting.png")
    >>> print(f"Image size: {img.size}")
    'Image size: (800, 600)'

    >>> # PDF document (returns list of images)
    >>> pages = load_document("document.pdf")
    >>> print(f"Loaded {len(pages)} pages")
    'Loaded 3 pages'
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union

from PIL import Image

logger = logging.getLogger(__name__)

# Optional PDF support - pdf2image requires poppler installation
try:
    import pdf2image
    _PDF_AVAILABLE: bool = True
except ImportError:
    pdf2image = None  # type: ignore[assignment]
    _PDF_AVAILABLE: bool = False


def load_image(path: Union[str, Path]) -> Image.Image:
    """Load an image from disk into PIL format.

    Supports common image formats including PNG, JPEG, TIFF, BMP, and WebP.
    The image is converted to RGB mode for consistent processing.

    Args:
        path: Path to the image file. Can be a string or Path object.

    Returns:
        PIL Image in RGB mode with fully loaded pixel data.

    Raises:
        FileNotFoundError: If the image file does not exist at the
            specified path.
        IOError: If the image cannot be loaded or decoded due to
            corruption or unsupported format.

    Example:
        >>> img = load_image("document.png")
        >>> print(img.mode, img.size)
        'RGB (1024, 768)'
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    try:
        img = Image.open(path)
        img.load()  # Ensure image data is fully loaded into memory
        return img.convert("RGB")
    except Exception as e:
        logger.error("Failed to load image %s: %s", path, e)
        raise IOError(f"Failed to load image: {path}") from e


def load_pdf_pages(
    path: Union[str, Path],
    dpi: int = 300,
    *,
    first_page: int = 1,
    last_page: Optional[int] = None,
) -> List[Image.Image]:
    """Convert a PDF file into a list of PIL Images.

    Rasterizes each page of the PDF at the specified resolution. Requires
    the pdf2image library and poppler system dependencies to be installed.

    Args:
        path: Path to the PDF file.
        dpi: Resolution for rasterization in dots per inch. Higher values
            produce clearer images but require more memory. Common values:
            - 150: Fast processing, lower quality.
            - 300: Standard quality (default).
            - 600: High quality for small text.
        first_page: First page number to convert (1-indexed). Defaults to 1.
        last_page: Last page number to convert (inclusive). If None,
            converts all pages from first_page to the end.

    Returns:
        List of PIL Images in RGB mode, one per converted page.

    Raises:
        ImportError: If pdf2image is not installed or poppler is not
            available on the system.
        FileNotFoundError: If the PDF file does not exist.
        RuntimeError: If PDF conversion fails due to corruption or
            unsupported PDF features.

    Example:
        >>> pages = load_pdf_pages("document.pdf", dpi=200)
        >>> print(f"Loaded {len(pages)} pages")
        'Loaded 5 pages'

        >>> # Load only pages 2-4
        >>> subset = load_pdf_pages("document.pdf", first_page=2, last_page=4)
    """
    if not _PDF_AVAILABLE:
        raise ImportError(
            "pdf2image is required for PDF loading. "
            "Install with: pip install pdf2image\n"
            "Also ensure poppler is installed on your system."
        )

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    try:
        return pdf2image.convert_from_path(
            str(path),
            dpi=dpi,
            first_page=first_page,
            last_page=last_page,
        )
    except Exception as e:
        logger.error("Failed to convert PDF %s: %s", path, e)
        raise RuntimeError(f"PDF conversion failed: {path}") from e


def load_document(path: Union[str, Path]) -> List[Image.Image]:
    """Load a document as a list of images.

    Automatically detects the file type based on extension and uses the
    appropriate loading method. PDF files are converted to multiple images
    (one per page), while image files return a single-element list.

    This function provides a unified interface for document processing
    without requiring the caller to handle different file types explicitly.

    Args:
        path: Path to the document file (image or PDF).

    Returns:
        List of PIL Images in RGB mode. Single images return a list with
        one element; PDFs return one image per page.

    Raises:
        FileNotFoundError: If the document file does not exist.
        ImportError: If loading a PDF and pdf2image is not available.
        IOError: If the file cannot be loaded.

    Example:
        >>> # Works with both images and PDFs
        >>> images = load_document("input.pdf")
        >>> for i, img in enumerate(images):
        ...     img.save(f"page_{i:03d}.png")

        >>> # Single image returns list with one element
        >>> images = load_document("photo.jpg")
        >>> assert len(images) == 1
    """
    path = Path(path)

    if path.suffix.lower() == ".pdf":
        return load_pdf_pages(path)
    else:
        return [load_image(path)]


def is_pdf_supported() -> bool:
    """Check if PDF loading is supported in the current environment.

    PDF support requires the pdf2image Python package and poppler system
    utilities to be installed.

    Returns:
        True if pdf2image is available and PDF loading will work,
        False otherwise.

    Example:
        >>> if is_pdf_supported():
        ...     pages = load_pdf_pages("document.pdf")
        ... else:
        ...     print("PDF support not available")
    """
    return _PDF_AVAILABLE


__all__ = [
    "is_pdf_supported",
    "load_document",
    "load_image",
    "load_pdf_pages",
]
