"""
Data loading utilities for images and PDF documents.
"""

from pathlib import Path
from typing import List, Union, Optional
import numpy as np
from PIL import Image
import logging

# Optional dependencies
try:
    import pdf2image
except ImportError:
    pdf2image = None

logger = logging.getLogger(__name__)

def load_image(path: Union[str, Path]) -> Image.Image:
    """
    Load an image from disk.

    Args:
        path: Path to the image file.

    Returns:
        PIL.Image in RGB mode.
    """
    try:
        img = Image.open(path)
        img.load()  # Ensure it's loaded
        return img.convert("RGB")
    except Exception as e:
        logger.error(f"Failed to load image at {path}: {e}")
        raise

def load_pdf_pages(path: Union[str, Path], dpi: int = 300) -> List[Image.Image]:
    """
    Convert a PDF file into a list of PIL Images (one per page).

    Args:
        path: Path to the PDF file.
        dpi: Resolution for rasterization.

    Returns:
        List of PIL Images.
    """
    if pdf2image is None:
        raise ImportError("pdf2image is required for PDF loading. Install it via pip install pdf2image")
    
    try:
        return pdf2image.convert_from_path(str(path), dpi=dpi)
    except Exception as e:
        logger.error(f"Failed to convert PDF at {path}: {e}")
        raise

def load_document(path: Union[str, Path]) -> List[Image.Image]:
    """
    Generic loader that handles both images and PDFs.

    Args:
        path: Path to file.

    Returns:
        List of PIL Images (length 1 for single images).
    """
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        return load_pdf_pages(p)
    else:
        return [load_image(p)]
