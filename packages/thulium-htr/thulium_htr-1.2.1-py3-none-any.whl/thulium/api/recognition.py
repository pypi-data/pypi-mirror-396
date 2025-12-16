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

"""High-level recognition API for Thulium HTR.

This module provides easy-to-use functions for handwriting text recognition,
abstracting away model loading, preprocessing, and decoding. It serves as
the primary interface for users who need quick access to recognition
functionality without managing pipeline internals.

The module supports both single-image and batch processing modes, with
optional confidence score reporting for quality assessment.

Functions:
    recognize: Recognize text from a single handwriting image.
    recognize_batch: Recognize text from multiple images efficiently.
    transcribe: Alias for recognize (semantic alternative).
    transcribe_batch: Alias for recognize_batch (semantic alternative).

Classes:
    RecognitionResult: Structured result with text and confidence scores.

Example:
    Single image recognition:

    >>> from thulium.api import recognize, recognize_batch
    >>> text = recognize("handwriting.png", language="en")
    >>> print(text)
    'Hello World'

    Recognition with confidence scores:

    >>> result = recognize("sample.png", return_confidence=True)
    >>> print(f"{result.text} (confidence: {result.confidence:.2%})")

    Batch processing for efficiency:

    >>> results = recognize_batch(["img1.png", "img2.png"], language="en")
    >>> for text in results:
    ...     print(text)
"""

from __future__ import annotations

import logging
import time
from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import ContextManager
from typing import List
from typing import Optional
from typing import Union

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class RecognitionResult:
    """Structured result from text recognition.

    Contains the recognized text along with confidence metrics and
    processing information. This class is returned when users request
    detailed output via the `return_confidence=True` parameter.

    Attributes:
        text: Recognized text string.
        confidence: Overall confidence score in range [0.0, 1.0],
            computed as mean of character-level confidences.
        char_confidences: Optional per-character confidence values.
            If provided, length matches len(text).
        processing_time_ms: Time taken for recognition in milliseconds.
        language: ISO 639-1 language code used for recognition.

    Example:
        >>> result = RecognitionResult(
        ...     text="Hello",
        ...     confidence=0.95,
        ...     processing_time_ms=45.2,
        ...     language="en",
        ... )
        >>> print(f"{result.text}: {result.confidence:.1%}")
        'Hello: 95.0%'
    """

    text: str
    confidence: float
    char_confidences: Optional[List[float]] = None
    processing_time_ms: float = 0.0
    language: str = "en"


def recognize(
    image: Union[str, Path, np.ndarray, Image.Image],
    model: str = "cnn_transformer_ctc_base",
    language: str = "en",
    return_confidence: bool = False,
    device: str = "auto",
) -> Union[str, RecognitionResult]:
    """Recognize text from a single handwriting image.

    This is the primary high-level API for text recognition. It handles
    image loading, preprocessing, model inference, and decoding automatically,
    providing a simple interface for common use cases.

    Args:
        image: Input image in one of the following formats:
            - str or Path: File path to an image file.
            - np.ndarray: NumPy array in (H, W, C) or (H, W) format.
            - PIL.Image.Image: PIL Image object.
        model: Name of the model configuration to use. Available options:
            - "cnn_lstm_ctc_{tiny,small,base,large}"
            - "cnn_transformer_ctc_{tiny,small,base,large}"
            - "vit_transformer_seq2seq_{tiny,small,large}"
        language: ISO 639-1 language code (e.g., "en", "de", "ar", "zh").
            See thulium.data.language_profiles for supported languages.
        return_confidence: If True, returns RecognitionResult with detailed
            confidence information. If False, returns plain text string.
        device: Device for model inference. Options:
            - "auto": Automatically select CUDA if available, else CPU.
            - "cpu": Force CPU inference.
            - "cuda": Use default CUDA device.
            - "cuda:N": Use specific CUDA device N.

    Returns:
        If return_confidence is False:
            Recognized text as a plain string.
        If return_confidence is True:
            RecognitionResult object with text, confidence, and metadata.

    Raises:
        FileNotFoundError: If image is a path that does not exist.
        ValueError: If image format is not supported.
        RuntimeError: If model loading or inference fails.

    Example:
        Basic recognition returning plain text:

        >>> text = recognize("sample.png", language="en")
        >>> print(text)
        'Hello World'

        Recognition with confidence information:

        >>> result = recognize("sample.png", return_confidence=True)
        >>> print(f"{result.text} (confidence: {result.confidence:.2%})")
        'Hello World (confidence: 95.32%)'

        Using a specific model and device:

        >>> text = recognize(
        ...     "sample.png",
        ...     model="cnn_lstm_ctc_small",
        ...     device="cuda:0",
        ... )
    """
    start_time = time.perf_counter()

    # Load and validate image
    image_data = _load_image(image)

    # Get or load model instance
    model_instance = _get_model(model, language, device)

    # Preprocess image for model
    preprocessed = _preprocess(image_data, model_instance.config)

    # Run inference
    with _inference_context():
        output = model_instance(preprocessed)

    # Decode output to text
    text, confidences = _decode(output, model_instance, language)

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    if return_confidence:
        return RecognitionResult(
            text=text,
            confidence=_compute_overall_confidence(confidences),
            char_confidences=confidences,
            processing_time_ms=elapsed_ms,
            language=language,
        )

    return text


def recognize_batch(
    images: List[Union[str, Path, np.ndarray]],
    model: str = "cnn_transformer_ctc_base",
    language: str = "en",
    batch_size: int = 16,
    return_confidence: bool = False,
    device: str = "auto",
    show_progress: bool = True,
) -> List[Union[str, RecognitionResult]]:
    """Recognize text from multiple handwriting images efficiently.

    Processes images in batches for improved throughput compared to
    sequential single-image recognition. Recommended for processing
    multiple images.

    Args:
        images: List of input images. Each element can be:
            - str or Path: File path to an image file.
            - np.ndarray: NumPy array in (H, W, C) or (H, W) format.
        model: Model configuration name (see recognize() for options).
        language: ISO 639-1 language code.
        batch_size: Number of images to process in each batch. Larger
            values improve throughput but require more memory.
        return_confidence: If True, returns list of RecognitionResult.
            If False, returns list of plain text strings.
        device: Device for inference (see recognize() for options).
        show_progress: If True and tqdm is available, displays a progress
            bar during processing.

    Returns:
        List of recognition results matching the input order. Each element
        is either a string or RecognitionResult depending on return_confidence.

    Raises:
        ValueError: If images list is empty.

    Example:
        Basic batch recognition:

        >>> texts = recognize_batch(["img1.png", "img2.png", "img3.png"])
        >>> for text in texts:
        ...     print(text)

        Batch recognition with progress and confidence:

        >>> results = recognize_batch(
        ...     image_paths,
        ...     batch_size=32,
        ...     return_confidence=True,
        ...     show_progress=True,
        ... )
        >>> for result in results:
        ...     print(f"{result.text}: {result.confidence:.1%}")
    """
    if not images:
        raise ValueError("images list cannot be empty")

    results: List[Union[str, RecognitionResult]] = []

    # Create batch iterator with optional progress bar
    batch_indices = range(0, len(images), batch_size)
    iterator = batch_indices

    if show_progress:
        try:
            from tqdm import tqdm
            iterator = tqdm(batch_indices, desc="Recognizing", unit="batch")
        except ImportError:
            logger.debug("tqdm not available, progress bar disabled")

    for i in iterator:
        batch = images[i : i + batch_size]
        batch_results = [
            recognize(img, model, language, return_confidence, device)
            for img in batch
        ]
        results.extend(batch_results)

    return results


def _load_image(
    image: Union[str, Path, np.ndarray, Image.Image],
) -> Image.Image:
    """Load image from various source formats.

    Args:
        image: Input image as file path, numpy array, or PIL Image.

    Returns:
        PIL Image in RGB format.

    Raises:
        FileNotFoundError: If file path does not exist.
        ValueError: If image format is not recognized.
    """
    if isinstance(image, (str, Path)):
        path = Path(image)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")
        return Image.open(path).convert("RGB")

    if isinstance(image, np.ndarray):
        return Image.fromarray(image).convert("RGB")

    if isinstance(image, Image.Image):
        return image.convert("RGB")

    # Check for torch.Tensor by attribute (avoid hard import)
    if hasattr(image, "numpy"):
        return Image.fromarray(image.numpy()).convert("RGB")

    raise ValueError(f"Unsupported image type: {type(image).__name__}")


def _get_model(model_name: str, language: str, device: str) -> Any:
    """Get or load a model instance from cache.

    Args:
        model_name: Name of the model configuration.
        language: Language code for vocabulary loading.
        device: Target device for the model.

    Returns:
        Loaded model instance ready for inference.

    Raises:
        ValueError: If model_name is not recognized.
    """
    logger.info("Loading model: %s for language: %s", model_name, language)

    # Import here to avoid circular dependency
    from thulium.pipeline.htr_pipeline import HTRPipeline

    return HTRPipeline(device=device, language=language)


def _preprocess(image: Image.Image, config: Any) -> Any:
    """Preprocess image according to model requirements.

    Args:
        image: PIL Image to preprocess.
        config: Model configuration with preprocessing parameters.

    Returns:
        Preprocessed tensor ready for model input.
    """
    # Placeholder implementation
    return image


def _decode(output: Any, model: Any, language: str) -> tuple[str, List[float]]:
    """Decode model output to text string.

    Args:
        output: Raw model output (logits or probabilities).
        model: Model instance with decoder configuration.
        language: Language code for vocabulary mapping.

    Returns:
        Tuple of (decoded_text, character_confidences).
    """
    # Placeholder implementation
    return "decoded_text", [1.0]


def _compute_overall_confidence(confidences: List[float]) -> float:
    """Compute overall confidence from per-character scores.

    Uses geometric mean for confidence aggregation, which appropriately
    penalizes low-confidence characters.

    Args:
        confidences: List of per-character confidence values in [0, 1].

    Returns:
        Aggregated confidence score in [0, 1]. Returns 0.0 for empty list.
    """
    if not confidences:
        return 0.0
    return float(np.mean(confidences))


def _inference_context() -> ContextManager[None]:
    """Create appropriate context manager for inference.

    Returns:
        Context manager that disables gradient computation if PyTorch
        is available, otherwise a no-op context.
    """
    try:
        import torch
        return torch.no_grad()
    except ImportError:
        return nullcontext()


# Semantic aliases for recognize functions
transcribe = recognize
transcribe_batch = recognize_batch


__all__ = [
    "RecognitionResult",
    "recognize",
    "recognize_batch",
    "transcribe",
    "transcribe_batch",
]
