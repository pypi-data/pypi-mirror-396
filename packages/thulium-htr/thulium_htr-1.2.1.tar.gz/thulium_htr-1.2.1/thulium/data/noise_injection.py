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

"""Noise injection utilities for robustness testing and data augmentation.

This module provides tools for synthetically degrading handwriting images to
test HTR model robustness under various noise conditions. These utilities
support both robustness evaluation and training-time data augmentation.

Supported Degradation Types:
    - Gaussian noise: Additive random noise simulating sensor noise.
    - Salt-and-pepper noise: Random white/black pixels simulating dust.
    - Blur effects: Gaussian blur simulating focus issues.
    - JPEG compression: Artifacts from lossy image compression.
    - Random occlusions: Rectangular regions covering parts of text.
    - Resolution degradation: Downscale/upscale simulating low-quality scans.

Classes:
    NoiseConfig: Configuration dataclass for noise parameters.
    RobustnessTester: Systematic testing utility for noise sensitivity.

Functions:
    add_gaussian_noise: Add Gaussian noise to an image.
    add_salt_pepper_noise: Add salt-and-pepper noise.
    add_blur: Apply Gaussian blur.
    add_jpeg_artifacts: Simulate JPEG compression artifacts.
    add_random_occlusion: Add rectangular occlusions.
    resize_and_restore: Simulate resolution loss.
    apply_random_noise: Apply multiple noise types based on config.

Example:
    Testing model robustness to Gaussian noise:

    >>> from thulium.data.noise_injection import add_gaussian_noise, NoiseConfig
    >>> import numpy as np
    >>>
    >>> # Add noise to image
    >>> noisy = add_gaussian_noise(image, std=0.05)
    >>>
    >>> # Apply multiple noise types
    >>> config = NoiseConfig(gaussian_std=0.02, jpeg_quality=75)
    >>> degraded = apply_random_noise(image, config)
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class NoiseConfig:
    """Configuration for noise injection parameters.

    This dataclass defines the parameters for various noise types that can
    be applied to handwriting images for robustness testing or augmentation.

    Attributes:
        gaussian_std: Standard deviation for Gaussian noise, relative to
            [0, 1] pixel value range. Common values: 0.01 (subtle) to 0.1
            (severe). Set to 0 to disable.
        salt_pepper_prob: Probability of each pixel being affected by
            salt-and-pepper noise. Common values: 0.01 to 0.05.
        jpeg_quality: JPEG quality for compression artifacts, range 1-100.
            Lower values create more artifacts. Set to 100 to disable.
        blur_kernel_size: Size of Gaussian blur kernel (must be odd).
            Larger values create more blur. Set to 1 to disable.
        occlusion_prob: Probability of adding rectangular occlusions.
        occlusion_size: (min_size, max_size) range for occlusion dimensions.

    Example:
        >>> config = NoiseConfig(
        ...     gaussian_std=0.02,
        ...     salt_pepper_prob=0.01,
        ...     jpeg_quality=80,
        ...     blur_kernel_size=3,
        ... )
        >>> degraded = apply_random_noise(image, config)
    """

    gaussian_std: float = 0.01
    salt_pepper_prob: float = 0.01
    jpeg_quality: int = 75
    blur_kernel_size: int = 3
    occlusion_prob: float = 0.1
    occlusion_size: Tuple[int, int] = (10, 50)


def add_gaussian_noise(
    image: np.ndarray,
    std: float = 0.01,
    mean: float = 0.0,
) -> np.ndarray:
    """Add Gaussian noise to an image.

    Adds random noise sampled from a normal distribution to simulate
    sensor noise and other acquisition artifacts.

    Args:
        image: Input image as numpy array. Shape can be (H, W) for grayscale
            or (H, W, C) for color. Supports uint8 [0-255] or float [0-1].
        std: Standard deviation of noise relative to [0, 1] value range.
            Typical values: 0.01 (subtle) to 0.1 (severe).
        mean: Mean of noise distribution. Typically 0 for unbiased noise.

    Returns:
        Noisy image with same dtype and shape as input.

    Example:
        >>> noisy = add_gaussian_noise(image, std=0.05)
        >>> # Add more subtle noise
        >>> slightly_noisy = add_gaussian_noise(image, std=0.01)
    """
    original_dtype = image.dtype

    # Convert to float [0, 1] for noise addition
    if image.dtype == np.uint8:
        image_float = image.astype(np.float32) / 255.0
    else:
        image_float = image.astype(np.float32)

    # Generate and add noise
    noise = np.random.normal(mean, std, image_float.shape).astype(np.float32)
    noisy = np.clip(image_float + noise, 0.0, 1.0)

    # Convert back to original dtype
    if original_dtype == np.uint8:
        return (noisy * 255).astype(np.uint8)
    return noisy


def add_salt_pepper_noise(
    image: np.ndarray,
    prob: float = 0.01,
    salt_value: float = 1.0,
    pepper_value: float = 0.0,
) -> np.ndarray:
    """Add salt-and-pepper noise to an image.

    Randomly sets pixels to extreme values (black or white) to simulate
    dust, dead pixels, or transmission errors.

    Args:
        image: Input image as numpy array. Shape (H, W) or (H, W, C).
        prob: Probability of each pixel being affected. Half of affected
            pixels become salt (white), half become pepper (black).
        salt_value: Value for salt (white) pixels. Typically 1.0 or 255.
        pepper_value: Value for pepper (black) pixels. Typically 0.0.

    Returns:
        Noisy image with same dtype and shape as input.

    Example:
        >>> noisy = add_salt_pepper_noise(image, prob=0.02)
    """
    original_dtype = image.dtype

    # Convert to float [0, 1]
    if image.dtype == np.uint8:
        image_float = image.astype(np.float32) / 255.0
        salt_value = 1.0
        pepper_value = 0.0
    else:
        image_float = image.astype(np.float32)

    # Create noise mask based on pixel positions
    noise_mask = np.random.random(image_float.shape[:2])
    noisy = image_float.copy()

    # Apply salt (white pixels)
    salt_mask = noise_mask < prob / 2
    noisy[salt_mask] = salt_value

    # Apply pepper (black pixels)
    pepper_mask = (noise_mask >= prob / 2) & (noise_mask < prob)
    noisy[pepper_mask] = pepper_value

    # Convert back to original dtype
    if original_dtype == np.uint8:
        return (noisy * 255).astype(np.uint8)
    return noisy


def add_blur(
    image: np.ndarray,
    kernel_size: int = 3,
    sigma: float = 1.0,
) -> np.ndarray:
    """Apply Gaussian blur to an image.

    Simulates focus issues, motion blur, or low-quality scanning.

    Args:
        image: Input image as numpy array.
        kernel_size: Size of the Gaussian kernel. Must be odd integer.
            Larger values create more blur.
        sigma: Standard deviation of the Gaussian kernel in pixels.

    Returns:
        Blurred image with same dtype and shape as input.

    Example:
        >>> blurred = add_blur(image, kernel_size=5, sigma=1.0)
    """
    try:
        import cv2
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
    except ImportError:
        # Fallback: simple box blur using numpy convolution
        logger.debug("cv2 not available, using fallback box blur")
        kernel = np.ones((kernel_size, kernel_size)) / (kernel_size * kernel_size)

        if len(image.shape) == 3:
            result = np.zeros_like(image)
            for c in range(image.shape[2]):
                result[:, :, c] = np.convolve(
                    image[:, :, c].flatten(),
                    kernel.flatten(),
                    mode="same",
                ).reshape(image.shape[:2])
            return result

        return np.convolve(
            image.flatten(), kernel.flatten(), mode="same"
        ).reshape(image.shape)


def add_jpeg_artifacts(
    image: np.ndarray,
    quality: int = 50,
) -> np.ndarray:
    """Add JPEG compression artifacts to an image.

    Simulates artifacts from lossy image compression, common in scanned
    documents or images transmitted over low-bandwidth connections.

    Args:
        image: Input image as numpy array.
        quality: JPEG quality level, range 1-100. Lower values create more
            visible compression artifacts. Typical values: 20 (severe) to
            80 (mild).

    Returns:
        Image with compression artifacts, same dtype and shape as input.

    Raises:
        ImportError: If PIL is not available (returns original image).

    Example:
        >>> compressed = add_jpeg_artifacts(image, quality=30)
    """
    try:
        from PIL import Image

        # Convert to uint8 for JPEG encoding
        if image.dtype == np.float32 or image.dtype == np.float64:
            image_uint8 = (image * 255).astype(np.uint8)
        else:
            image_uint8 = image

        # Compress and decompress via JPEG
        pil_image = Image.fromarray(image_uint8)
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        compressed = Image.open(buffer)

        result = np.array(compressed)

        # Convert back to original dtype
        if image.dtype == np.float32 or image.dtype == np.float64:
            return result.astype(np.float32) / 255.0
        return result
    except ImportError:
        logger.warning("PIL not available for JPEG artifacts")
        return image


def add_random_occlusion(
    image: np.ndarray,
    num_occlusions: int = 1,
    size_range: Tuple[int, int] = (10, 50),
    color: Optional[Union[int, Tuple[int, ...]]] = None,
) -> np.ndarray:
    """Add random rectangular occlusions to an image.

    Simulates objects covering parts of the text, such as fingers,
    stickers, or stamps on documents.

    Args:
        image: Input image as numpy array.
        num_occlusions: Number of rectangular occlusions to add.
        size_range: (min_size, max_size) range for occlusion dimensions
            in pixels. Each dimension is sampled independently.
        color: Fill color for occlusions. If None, uses random values.
            Can be int for grayscale or tuple for color images.

    Returns:
        Image with occlusions added.

    Example:
        >>> occluded = add_random_occlusion(image, num_occlusions=2)
        >>> # Black occlusions
        >>> occluded = add_random_occlusion(image, color=0)
    """
    occluded = image.copy()
    h, w = image.shape[:2]

    for _ in range(num_occlusions):
        # Random size within range
        size_h = np.random.randint(size_range[0], min(size_range[1], h))
        size_w = np.random.randint(size_range[0], min(size_range[1], w))

        # Random position
        y = np.random.randint(0, max(1, h - size_h))
        x = np.random.randint(0, max(1, w - size_w))

        # Generate fill value
        if color is None:
            if len(image.shape) == 3:
                fill = np.random.randint(
                    0, 256, size=(size_h, size_w, image.shape[2])
                )
            else:
                fill = np.random.randint(0, 256, size=(size_h, size_w))

            if image.dtype == np.float32 or image.dtype == np.float64:
                fill = fill.astype(np.float32) / 255.0
        else:
            fill = np.full(
                (size_h, size_w) + image.shape[2:], color, dtype=image.dtype
            )

        occluded[y : y + size_h, x : x + size_w] = fill

    return occluded


def resize_and_restore(
    image: np.ndarray,
    scale: float = 0.5,
) -> np.ndarray:
    """Downsample and upsample image to simulate resolution loss.

    Simulates low-resolution scanning or poor image quality by
    downscaling and then upscaling the image, losing fine details.

    Args:
        image: Input image as numpy array.
        scale: Scale factor for downsampling, in range (0, 1).
            Lower values create more quality loss.

    Returns:
        Image with resolution degradation.

    Example:
        >>> degraded = resize_and_restore(image, scale=0.25)
    """
    try:
        from PIL import Image as PILImage

        # Convert to uint8 for PIL
        if image.dtype == np.float32 or image.dtype == np.float64:
            image_uint8 = (image * 255).astype(np.uint8)
        else:
            image_uint8 = image

        pil_image = PILImage.fromarray(image_uint8)
        orig_size = pil_image.size

        # Downscale then upscale
        small_size = (int(orig_size[0] * scale), int(orig_size[1] * scale))
        small = pil_image.resize(small_size, PILImage.BILINEAR)
        restored = small.resize(orig_size, PILImage.BILINEAR)

        result = np.array(restored)

        # Convert back to original dtype
        if image.dtype == np.float32 or image.dtype == np.float64:
            return result.astype(np.float32) / 255.0
        return result
    except ImportError:
        logger.warning("PIL not available for resolution degradation")
        return image


def apply_random_noise(
    image: np.ndarray,
    config: NoiseConfig,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Apply multiple noise types based on configuration.

    Applies each noise type specified in the config to the image.
    Useful for data augmentation during training.

    Args:
        image: Input image as numpy array.
        config: NoiseConfig specifying noise parameters. Each noise type
            is applied if its parameter is non-zero/non-trivial.
        seed: Optional random seed for reproducibility.

    Returns:
        Image with all configured noise types applied.

    Example:
        >>> config = NoiseConfig(gaussian_std=0.02, jpeg_quality=80)
        >>> noisy = apply_random_noise(image, config, seed=42)
    """
    if seed is not None:
        np.random.seed(seed)

    result = image.copy()

    # Apply Gaussian noise
    if config.gaussian_std > 0:
        result = add_gaussian_noise(result, std=config.gaussian_std)

    # Apply salt-and-pepper noise
    if config.salt_pepper_prob > 0:
        result = add_salt_pepper_noise(result, prob=config.salt_pepper_prob)

    # Apply blur
    if config.blur_kernel_size > 1:
        result = add_blur(result, kernel_size=config.blur_kernel_size)

    # Apply JPEG artifacts
    if config.jpeg_quality < 100:
        result = add_jpeg_artifacts(result, quality=config.jpeg_quality)

    # Apply occlusion
    if config.occlusion_prob > 0 and np.random.random() < config.occlusion_prob:
        result = add_random_occlusion(result, size_range=config.occlusion_size)

    return result


class RobustnessTester:
    """Utility class for systematic robustness testing of HTR models.

    Provides methods to apply controlled degradations at various levels
    and measure the impact on recognition accuracy. Useful for understanding
    model sensitivity to different noise types.

    Attributes:
        pipeline: HTR pipeline instance for running recognition.
        results: List of result dictionaries from previous tests.

    Example:
        >>> tester = RobustnessTester(pipeline=my_pipeline)
        >>> results = tester.test_noise_level(
        ...     images=test_images,
        ...     references=ground_truth,
        ...     noise_type="gaussian",
        ...     levels=[0.01, 0.02, 0.05, 0.1],
        ... )
        >>> for r in results:
        ...     print(f"Noise {r['level']}: CER = {r.get('cer', 'N/A')}")
    """

    def __init__(self, pipeline: Optional[object] = None) -> None:
        """Initialize the robustness tester.

        Args:
            pipeline: HTR pipeline instance for recognition. Can be set
                later using set_pipeline().
        """
        self.pipeline = pipeline
        self.results: List[dict] = []

    def set_pipeline(self, pipeline: object) -> None:
        """Set the HTR pipeline for testing.

        Args:
            pipeline: HTR pipeline instance implementing process() method.
        """
        self.pipeline = pipeline

    def test_noise_level(
        self,
        images: List[np.ndarray],
        references: List[str],
        noise_type: str,
        levels: List[float],
        language: str = "en",
    ) -> List[dict]:
        """Test recognition accuracy at different noise levels.

        Applies specified noise type at each level to all images and
        measures recognition performance.

        Args:
            images: List of input images as numpy arrays.
            references: List of ground truth transcription strings.
            noise_type: Type of noise to apply. Options:
                - "gaussian": Gaussian noise with std = level
                - "blur": Gaussian blur with kernel_size = int(level)
                - "jpeg": JPEG compression with quality = int(level)
                - "resolution": Resolution scale factor = level
            levels: List of noise intensity levels to test.
            language: Language code for recognition.

        Returns:
            List of result dictionaries, one per level, containing:
                - noise_type: Type of noise applied.
                - level: Noise intensity level.
                - num_samples: Number of samples tested.

        Raises:
            ValueError: If pipeline is not set.
        """
        if self.pipeline is None:
            raise ValueError("Pipeline not set. Use set_pipeline() first.")

        results: List[dict] = []

        for level in levels:
            # Apply noise at this level to all images
            noisy_images = []
            for img in images:
                if noise_type == "gaussian":
                    noisy = add_gaussian_noise(img, std=level)
                elif noise_type == "blur":
                    noisy = add_blur(img, kernel_size=int(level))
                elif noise_type == "jpeg":
                    noisy = add_jpeg_artifacts(img, quality=int(level))
                elif noise_type == "resolution":
                    noisy = resize_and_restore(img, scale=level)
                else:
                    noisy = img
                noisy_images.append(noisy)

            # TODO(thulium-team): Run actual recognition and compute metrics
            # hypotheses = [self.pipeline.process(img).full_text for img in noisy_images]
            # cer, wer = compute_metrics(references, hypotheses)

            result = {
                "noise_type": noise_type,
                "level": level,
                "num_samples": len(images),
            }
            results.append(result)

        self.results.extend(results)
        return results


__all__ = [
    "NoiseConfig",
    "RobustnessTester",
    "add_blur",
    "add_gaussian_noise",
    "add_jpeg_artifacts",
    "add_random_occlusion",
    "add_salt_pepper_noise",
    "apply_random_noise",
    "resize_and_restore",
]
