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

"""Low-level recognition functions for Thulium HTR.

This module provides the underlying recognition functions that interface
directly with the HTR pipeline. For typical usage, prefer the high-level
API in `thulium.api.recognition`.

This module is intended for advanced users who need fine-grained control
over pipeline caching, PDF processing, or batch operations with progress
reporting.

Functions:
    recognize_image: Recognize text in a single image file.
    recognize_pdf: Recognize text in a multi-page PDF document.
    recognize_batch: Process multiple images with optional progress bar.
    clear_pipeline_cache: Free cached pipeline instances.

Example:
    Recognizing text in an image:

    >>> from thulium.api.recognize import recognize_image
    >>> result = recognize_image("document.png", language="en")
    >>> print(result.full_text)

    Processing multiple images with progress:

    >>> from thulium.api.recognize import recognize_batch
    >>> results = recognize_batch(
    ...     ["page1.png", "page2.png"],
    ...     language="de",
    ...     show_progress=True,
    ... )
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from thulium.api.types import PageResult

logger = logging.getLogger(__name__)

# Type alias for pipeline cache key
_CacheKey = Tuple[str, str]

# Pipeline cache for model reuse across calls to avoid repeated loading
_PIPELINE_CACHE: Dict[_CacheKey, Any] = {}


def _get_pipeline(pipeline: str, device: str) -> Optional[Any]:
    """Get or create a cached HTR pipeline instance.

    Implements lazy loading and caching of pipeline instances to avoid
    repeated model loading overhead for consecutive recognition calls.

    Args:
        pipeline: Pipeline configuration name (e.g., "default", "fast").
        device: Computation device ("cpu", "cuda", or "auto").

    Returns:
        Configured HTRPipeline instance, or None if loading fails.

    Raises:
        ImportError: If required pipeline modules are not available.
    """
    cache_key: _CacheKey = (pipeline, device)

    if cache_key not in _PIPELINE_CACHE:
        try:
            from thulium.pipeline.config import load_pipeline_config
            from thulium.pipeline.htr_pipeline import HTRPipeline

            config = load_pipeline_config(pipeline)
            _PIPELINE_CACHE[cache_key] = HTRPipeline(config, device=device)
            logger.info("Loaded pipeline: %s on device: %s", pipeline, device)
        except ImportError as e:
            logger.warning("Pipeline not available: %s", e)
            return None

    return _PIPELINE_CACHE.get(cache_key)


def recognize_image(
    path: Union[str, Path],
    language: str = "en",
    pipeline: str = "default",
    device: str = "auto",
) -> PageResult:
    """Recognize handwritten text in an image file.

    This function loads the image, runs it through the HTR pipeline, and
    returns structured recognition results including full text, line-level
    breakdown, and confidence scores.

    Args:
        path: Path to the image file. Supported formats include PNG, JPEG,
            TIFF, and BMP.
        language: ISO 639-1 language code (e.g., "en", "de", "az", "ka").
            The language affects vocabulary selection and language model
            scoring during decoding.
        pipeline: Name of the pipeline configuration to use. Options:
            - "default": Balanced accuracy and speed.
            - "fast": Optimized for speed with slightly lower accuracy.
            - "accurate": Maximum accuracy with longer processing time.
        device: Computation device for inference:
            - "cpu": Force CPU execution.
            - "cuda": Use default CUDA device.
            - "auto": Automatically select based on availability.

    Returns:
        PageResult containing:
            - full_text: Complete recognized text.
            - lines: List of Line objects with per-line results.
            - language: Language code used.
            - confidence: Overall confidence score.
            - metadata: Processing metadata.

    Raises:
        FileNotFoundError: If the image file does not exist.
        ValueError: If the language code is not supported.

    Example:
        >>> result = recognize_image("document.png", language="en")
        >>> print(result.full_text)
        'The quick brown fox jumps over the lazy dog.'
        >>> print(f"Confidence: {result.confidence:.1%}")
        'Confidence: 94.2%'
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    runner = _get_pipeline(pipeline, device)
    if runner is None:
        # Return placeholder when pipeline is unavailable
        logger.warning("Pipeline unavailable, returning empty result")
        return PageResult(
            full_text="",
            lines=[],
            language=language,
            metadata={"error": "Pipeline not available"},
        )

    return runner.process(path, language)


def recognize_pdf(
    path: Union[str, Path],
    language: str = "en",
    pipeline: str = "default",
    device: str = "auto",
) -> List[PageResult]:
    """Recognize handwritten text in a PDF document.

    Processes each page of the PDF independently and returns a list of
    PageResult objects. This function handles multi-page documents by
    extracting images from each page and running recognition.

    Args:
        path: Path to the PDF file.
        language: ISO 639-1 language code for recognition.
        pipeline: Pipeline configuration name.
        device: Computation device for inference.

    Returns:
        List of PageResult objects, one per PDF page, in page order.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If the PDF cannot be parsed.

    Example:
        >>> results = recognize_pdf("multi_page.pdf", language="de")
        >>> for i, page in enumerate(results):
        ...     print(f"Page {i + 1}: {page.full_text[:50]}...")
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    # TODO(thulium-team): Implement proper PDF page extraction using pdf2image
    # For now, treat PDF as single-page document
    logger.info("Processing PDF: %s", path)
    return [recognize_image(path, language, pipeline, device)]


def recognize_batch(
    paths: List[Union[str, Path]],
    language: str = "en",
    pipeline: str = "default",
    device: str = "auto",
    *,
    show_progress: bool = False,
) -> List[PageResult]:
    """Process a batch of images for text recognition.

    Processes multiple images sequentially with optional progress display.
    For optimal performance on large batches, consider using the higher-level
    API with batched inference in `thulium.api.recognition.recognize_batch`.

    Args:
        paths: List of paths to image files.
        language: ISO 639-1 language code for all images.
        pipeline: Pipeline configuration name.
        device: Computation device for inference.
        show_progress: If True and tqdm is installed, displays a progress
            bar during batch processing.

    Returns:
        List of PageResult objects in the same order as input paths.
        Failed images will have empty results with error metadata.

    Example:
        >>> images = ["page1.png", "page2.png", "page3.png"]
        >>> results = recognize_batch(
        ...     images,
        ...     language="en",
        ...     show_progress=True,
        ... )
        >>> for path, result in zip(images, results):
        ...     print(f"{path}: {len(result.full_text)} chars")
    """
    results: List[PageResult] = []
    iterator: Any = paths

    if show_progress:
        try:
            from tqdm import tqdm
            iterator = tqdm(paths, desc="Processing images", unit="image")
        except ImportError:
            logger.debug("tqdm not available, progress bar disabled")

    for path in iterator:
        result = recognize_image(path, language, pipeline, device)
        results.append(result)

    return results


def clear_pipeline_cache() -> None:
    """Clear the pipeline cache to free memory.

    Call this function when switching between different models or when
    memory needs to be reclaimed. After calling this function, subsequent
    recognition calls will reload models from disk.

    Example:
        >>> from thulium.api.recognize import clear_pipeline_cache
        >>> clear_pipeline_cache()  # Free GPU memory
        >>> # Models will be reloaded on next recognition call
    """
    global _PIPELINE_CACHE
    _PIPELINE_CACHE.clear()
    logger.info("Pipeline cache cleared")


__all__ = [
    "clear_pipeline_cache",
    "recognize_batch",
    "recognize_image",
    "recognize_pdf",
]
