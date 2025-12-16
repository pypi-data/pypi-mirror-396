"""
HTR Pipeline - Core handwriting text recognition orchestration.

This module provides the main HTRPipeline class that orchestrates the
complete workflow from raw image input to structured text output,
integrating preprocessing, segmentation, recognition, and postprocessing.
"""

from typing import Union, Optional
from pathlib import Path
import logging

from thulium.api.types import PageResult, Line
from thulium.data.loaders import load_image
from thulium.data.language_profiles import (
    get_language_profile,
    LanguageProfile,
    UnsupportedLanguageError,
)
from thulium.models.wrappers.htr_model import HTRModel


logger = logging.getLogger(__name__)


class HTRPipeline:
    """
    Orchestrates the handwriting text recognition pipeline.

    This class manages the complete HTR workflow including:
    - Image loading and preprocessing
    - Layout segmentation (line/word detection)
    - Text recognition via deep learning models
    - Language-aware decoding and postprocessing

    The pipeline is configurable via YAML configuration files and
    supports language-specific settings through the language profiles.

    Attributes:
        config: Pipeline configuration dictionary.
        device: Computation device ('cpu', 'cuda', or 'auto').
        model: The HTR model instance.
        language_profile: Optional cached language profile.

    Example:
        >>> from thulium.pipeline.htr_pipeline import HTRPipeline
        >>> from thulium.pipeline.config import load_pipeline_config
        >>> config = load_pipeline_config("default")
        >>> pipeline = HTRPipeline(config)
        >>> result = pipeline.process("document.png", language="en")
        >>> print(result.full_text)
    """

    def __init__(
        self,
        config: dict,
        device: str = "auto",
        language: Optional[str] = None
    ):
        """
        Initialize the HTR pipeline with configuration.

        Args:
            config: Pipeline configuration dictionary.
            device: Computation device ('cpu', 'cuda', or 'auto').
            language: Optional default language code.
        """
        self.config = config
        self.device = self._resolve_device(device)
        self.language_profile: Optional[LanguageProfile] = None

        # Load language profile if specified
        if language:
            self._load_language_profile(language)

        # Initialize model (stub - would load actual weights in production)
        num_classes = self._get_num_classes()
        self.model = HTRModel(num_classes=num_classes)

        logger.info(
            "Initialized HTRPipeline with device=%s, num_classes=%d",
            self.device,
            num_classes
        )

    def _resolve_device(self, device: str) -> str:
        """Resolve 'auto' device to actual device string."""
        if device == "auto":
            try:
                import torch
                return "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                return "cpu"
        return device

    def _load_language_profile(self, language: str) -> None:
        """
        Load and cache the language profile for the given code.

        Args:
            language: ISO 639-1 language code.

        Raises:
            UnsupportedLanguageError: If language is not supported.
        """
        self.language_profile = get_language_profile(language)
        logger.info(
            "Loaded language profile: %s (%s script)",
            self.language_profile.name,
            self.language_profile.script
        )

    def _get_num_classes(self) -> int:
        """
        Determine the number of output classes based on language profile.

        Returns:
            Number of classes for the decoder output layer.
        """
        if self.language_profile:
            return self.language_profile.get_vocab_size()
        # Default fallback for generic Latin
        return 100

    def process(
        self,
        image_path: Union[str, Path],
        language: str = "en"
    ) -> PageResult:
        """
        Run the full recognition pipeline on a single image.

        This method executes the complete pipeline:
        1. Load and preprocess the input image
        2. Perform layout segmentation (if enabled)
        3. Run text recognition on segments
        4. Apply language-aware decoding
        5. Postprocess and structure the output

        Args:
            image_path: Path to the input image file.
            language: Language code for recognition (e.g., 'en', 'az').

        Returns:
            PageResult containing recognized text and metadata.

        Raises:
            FileNotFoundError: If the image file does not exist.
            UnsupportedLanguageError: If the language is not supported.
        """
        image_path = Path(image_path)
        logger.info("Processing %s with language=%s", image_path, language)

        # Load language profile if different from cached
        if not self.language_profile or self.language_profile.code != language:
            self._load_language_profile(language)

        # Step 1: Load Image
        image = load_image(image_path)
        logger.debug("Loaded image: %dx%d", image.width, image.height)

        # Step 2: Preprocessing (placeholder)
        # In production, apply normalization, binarization, etc.

        # Step 3: Segmentation (placeholder)
        # Returns list of line bounding boxes
        # For now, treat entire image as single line
        lines = self._segment_lines(image)

        # Step 4: Recognition (placeholder)
        # Run HTR model on each segment
        recognized_lines = self._recognize_segments(lines, image)

        # Step 5: Construct output
        full_text = "\n".join([line.text for line in recognized_lines])

        return PageResult(
            full_text=full_text,
            lines=recognized_lines,
            language=language,
            metadata={
                "device": self.device,
                "language_profile": self.language_profile.name if self.language_profile else None,
                "script": self.language_profile.script if self.language_profile else None,
            }
        )

    def _segment_lines(self, image) -> list:
        """
        Segment the image into text lines.

        This is a placeholder implementation. In production, this would
        use a trained segmentation model (e.g., U-Net) to detect lines.

        Args:
            image: PIL Image object.

        Returns:
            List of bounding boxes for detected lines.
        """
        # Placeholder: return entire image as single line
        return [(0, 0, image.width, image.height)]

    def _recognize_segments(self, segments: list, image) -> list:
        """
        Run recognition on segmented regions.

        This is a placeholder implementation. In production, this would
        crop each segment and run the HTR model.

        Args:
            segments: List of bounding boxes (x, y, w, h).
            image: PIL Image object.

        Returns:
            List of Line objects with recognized text.
        """
        # Placeholder: return baseline text for each segment
        results = []
        for i, bbox in enumerate(segments):
            # In production: crop, preprocess, run model, decode
            text = f"[Thulium {self.language_profile.name if self.language_profile else 'Generic'} Line {i+1}]"
            results.append(
                Line(
                    text=text,
                    confidence=0.99,
                    bbox=bbox
                )
            )
        return results


def create_pipeline_from_config(
    config_name: str,
    device: str = "auto",
    language: Optional[str] = None
) -> HTRPipeline:
    """
    Create an HTR pipeline from a named configuration.

    This is a convenience factory function that loads the configuration
    and creates the pipeline instance.

    Args:
        config_name: Name of the configuration (e.g., 'htr_en_default').
        device: Computation device.
        language: Optional language override.

    Returns:
        Configured HTRPipeline instance.
    """
    from thulium.pipeline.config import load_pipeline_config
    config = load_pipeline_config(config_name)
    return HTRPipeline(config, device=device, language=language)
