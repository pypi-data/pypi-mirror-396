"""
Multi-Language Pipeline - Language-aware routing and processing.

This module provides the MultiLanguagePipeline class that manages
recognition across multiple languages, including automatic language
detection and optimal pipeline selection.
"""

from typing import Union, Optional, List, Dict
from pathlib import Path
import logging

from thulium.api.types import PageResult
from thulium.data.language_profiles import (
    get_language_profile,
    list_supported_languages,
    get_languages_by_script,
    LanguageProfile,
    UnsupportedLanguageError,
)
from thulium.pipeline.htr_pipeline import HTRPipeline


logger = logging.getLogger(__name__)


class MultiLanguagePipeline:
    """
    Pipeline supporting automatic language detection and multi-language processing.

    This class provides a higher-level abstraction over the base HTRPipeline,
    adding support for:
    - Automatic language detection (placeholder for future LID model)
    - Language-specific pipeline routing
    - Multi-language document processing
    - Script-based grouping for shared models

    The pipeline maintains a cache of language-specific sub-pipelines to
    avoid reloading models for frequently used languages.

    Attributes:
        device: Computation device.
        default_language: Fallback language when detection fails.
        pipeline_cache: Cache of initialized language-specific pipelines.

    Example:
        >>> from thulium.pipeline.multi_language_pipeline import MultiLanguagePipeline
        >>> pipeline = MultiLanguagePipeline()
        >>> result = pipeline.process("document.png", language="auto")
    """

    def __init__(
        self,
        device: str = "auto",
        default_language: str = "en",
        cache_size: int = 5
    ):
        """
        Initialize the multi-language pipeline.

        Args:
            device: Computation device ('cpu', 'cuda', or 'auto').
            default_language: Fallback language code when detection fails.
            cache_size: Maximum number of pipelines to cache.
        """
        self.device = device
        self.default_language = default_language
        self.cache_size = cache_size
        self.pipeline_cache: Dict[str, HTRPipeline] = {}

        logger.info(
            "Initialized MultiLanguagePipeline with default_language=%s",
            default_language
        )

    def process(
        self,
        image_path: Union[str, Path],
        language: str = "auto"
    ) -> PageResult:
        """
        Process an image with language-aware recognition.

        If language is set to 'auto', the pipeline will attempt to detect
        the language (currently falls back to default with a warning).

        Args:
            image_path: Path to the input image.
            language: Language code or 'auto' for detection.

        Returns:
            PageResult containing recognized text.

        Raises:
            UnsupportedLanguageError: If the specified language is not supported.
        """
        # Handle auto-detection
        if language == "auto":
            language = self._detect_language(image_path)
            logger.info("Auto-detected language: %s", language)

        # Get or create pipeline for this language
        pipeline = self._get_pipeline(language)

        # Process image
        return pipeline.process(image_path, language=language)

    def process_batch(
        self,
        image_paths: List[Union[str, Path]],
        language: str = "auto"
    ) -> List[PageResult]:
        """
        Process multiple images with the same language setting.

        Args:
            image_paths: List of paths to input images.
            language: Language code or 'auto' for detection.

        Returns:
            List of PageResult objects.
        """
        return [
            self.process(path, language=language)
            for path in image_paths
        ]

    def _detect_language(self, image_path: Union[str, Path]) -> str:
        """
        Detect the language of text in an image.

        This is a placeholder implementation. In production, this would
        use a trained language identification model.

        Args:
            image_path: Path to the input image.

        Returns:
            Detected language code.
        """
        logger.warning(
            "Language detection not yet implemented. "
            "Using default language: %s",
            self.default_language
        )
        return self.default_language

    def _get_pipeline(self, language: str) -> HTRPipeline:
        """
        Get or create a pipeline for the specified language.

        This method manages the pipeline cache to avoid repeatedly
        loading models for the same language.

        Args:
            language: Language code.

        Returns:
            HTRPipeline configured for the language.
        """
        if language not in self.pipeline_cache:
            # Evict oldest entry if cache is full
            if len(self.pipeline_cache) >= self.cache_size:
                oldest = next(iter(self.pipeline_cache))
                del self.pipeline_cache[oldest]
                logger.debug("Evicted pipeline for %s from cache", oldest)

            # Create new pipeline
            profile = get_language_profile(language)
            config = self._get_config_for_language(profile)
            self.pipeline_cache[language] = HTRPipeline(
                config=config,
                device=self.device,
                language=language
            )
            logger.info("Created pipeline for %s", language)

        return self.pipeline_cache[language]

    def _get_config_for_language(self, profile: LanguageProfile) -> dict:
        """
        Get appropriate configuration for a language profile.

        This method selects the best configuration based on the language's
        script and region.

        Args:
            profile: LanguageProfile for the target language.

        Returns:
            Configuration dictionary.
        """
        # Placeholder: return default config
        # In production, load appropriate YAML config
        return {
            "language": {"code": profile.code},
            "model": {"backbone": {"type": "cnn_resnet"}},
            "decoder": {"type": "ctc", "beam_width": 10},
        }

    def get_supported_languages(self) -> List[str]:
        """Return list of all supported language codes."""
        return list_supported_languages()

    def get_languages_for_script(self, script: str) -> List[str]:
        """Return languages using a specific script."""
        return get_languages_by_script(script)
