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

"""Image transformations for HTR preprocessing.

This module provides image transformation classes for preprocessing handwriting
images before recognition. All transforms follow a consistent interface and can
be composed using the Compose class.

The transformation pipeline typically includes:
    1. Grayscale conversion (if needed)
    2. Height normalization with aspect ratio preservation
    3. Optional padding/cropping to fixed width
    4. Tensor conversion and normalization

Classes:
    Transform: Abstract base class for all image transforms.
    Compose: Sequential composition of multiple transforms.
    ResizeToHeight: Resize maintaining aspect ratio to target height.
    Grayscale: Convert image to grayscale format.
    ToTensor: Convert PIL Image to numpy tensor (C, H, W).
    Normalize: Normalize tensor values with mean and std.

Example:
    Creating a standard preprocessing pipeline:

    >>> from thulium.data.transforms import (
    ...     Compose, Grayscale, ResizeToHeight, ToTensor, Normalize
    ... )
    >>> transform = Compose([
    ...     Grayscale(),
    ...     ResizeToHeight(64, target_width=256),
    ...     ToTensor(),
    ...     Normalize(mean=0.5, std=0.5),
    ... ])
    >>> processed = transform(pil_image)
    >>> print(processed.shape)
    (1, 64, 256)
"""

from __future__ import annotations

from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import numpy as np
from PIL import Image
from PIL import ImageOps


class Transform:
    """Abstract base class for image transforms.

    All transform classes should inherit from this base class and implement
    the __call__ method. Transforms are designed to be composable using the
    Compose class.

    Example:
        Subclassing Transform:

        >>> class MyTransform(Transform):
        ...     def __call__(self, img: Image.Image) -> Image.Image:
        ...         # Apply custom transformation
        ...         return img.rotate(90)
    """

    def __call__(
        self, img: Image.Image
    ) -> Union[Image.Image, np.ndarray]:
        """Apply the transform to an image.

        Args:
            img: Input PIL Image to transform.

        Returns:
            Transformed image, either as PIL Image or numpy array depending
            on the specific transform implementation.

        Raises:
            NotImplementedError: If called directly on base class.
        """
        raise NotImplementedError(
            "Subclasses must implement __call__ method"
        )


class Compose(Transform):
    """Compose multiple transforms into a sequential pipeline.

    Transforms are applied in order, with the output of each transform
    passed as input to the next.

    Attributes:
        transforms: List of Transform objects to apply sequentially.

    Example:
        >>> transform = Compose([
        ...     Grayscale(),
        ...     ResizeToHeight(64),
        ...     ToTensor(),
        ...     Normalize(mean=0.5, std=0.5),
        ... ])
        >>> output = transform(input_image)
    """

    def __init__(self, transforms: List[Transform]) -> None:
        """Initialize with a list of transforms.

        Args:
            transforms: List of Transform objects to compose. Transforms
                are applied in the order provided.
        """
        self.transforms = transforms

    def __call__(
        self, img: Image.Image
    ) -> Union[Image.Image, np.ndarray]:
        """Apply all transforms sequentially.

        Args:
            img: Input PIL Image.

        Returns:
            Transformed output after applying all transforms in sequence.
            The output type depends on the final transform in the pipeline.
        """
        for transform in self.transforms:
            img = transform(img)
        return img


class ResizeToHeight(Transform):
    """Resize image to fixed height while maintaining aspect ratio.

    This transform is essential for HTR where consistent height is required
    for batch processing, but varying widths correspond to different text
    lengths. Optionally pads or crops to achieve a target width.

    Attributes:
        target_height: Target height in pixels after resizing.
        target_width: Optional target width. If set, images are padded or
            resized to achieve this exact width.
        fill_color: Color used for padding when target_width exceeds the
            aspect-ratio-preserved width.

    Example:
        >>> # Variable width, fixed height
        >>> resize = ResizeToHeight(target_height=64)
        >>> output = resize(input_image)

        >>> # Fixed dimensions with padding
        >>> resize = ResizeToHeight(64, target_width=256, fill_color="white")
        >>> output = resize(input_image)
    """

    def __init__(
        self,
        target_height: int = 64,
        target_width: Optional[int] = None,
        fill_color: str = "white",
    ) -> None:
        """Initialize the resize transform.

        Args:
            target_height: Target height in pixels. Common values are
                32, 64, or 128 depending on model architecture.
            target_width: Optional fixed width. If None, width varies
                based on input aspect ratio. If set, images are padded
                on the right or resized to fit.
            fill_color: Color for padding when width adjustment is needed.
                Accepts any PIL color specification.
        """
        self.target_height = target_height
        self.target_width = target_width
        self.fill_color = fill_color

    def __call__(self, img: Image.Image) -> Image.Image:
        """Resize the image to target dimensions.

        Args:
            img: Input PIL Image of any size.

        Returns:
            Resized PIL Image with height equal to target_height.
            Width depends on target_width setting.
        """
        width, height = img.size

        # Scale to target height maintaining aspect ratio
        scale = self.target_height / height
        new_width = int(width * scale)
        img = img.resize(
            (new_width, self.target_height),
            Image.Resampling.BILINEAR,
        )

        if self.target_width is not None:
            if new_width < self.target_width:
                # Pad on the right to reach target width
                padding = self.target_width - new_width
                img = ImageOps.expand(
                    img,
                    border=(0, 0, padding, 0),
                    fill=self.fill_color,
                )
            elif new_width > self.target_width:
                # Resize down to fit (may distort slightly)
                img = img.resize(
                    (self.target_width, self.target_height),
                    Image.Resampling.BILINEAR,
                )

        return img


class Grayscale(Transform):
    """Convert image to grayscale.

    Useful for HTR preprocessing where color information is typically
    not relevant for handwriting recognition.

    Attributes:
        num_channels: Number of output channels. Use 1 for single-channel
            grayscale or 3 for grayscale converted to RGB format.

    Example:
        >>> # Single channel grayscale
        >>> gray = Grayscale(num_channels=1)
        >>> output = gray(rgb_image)
        >>> print(output.mode)
        'L'

        >>> # Grayscale in RGB format
        >>> gray = Grayscale(num_channels=3)
        >>> output = gray(rgb_image)
        >>> print(output.mode)
        'RGB'
    """

    def __init__(self, num_channels: int = 1) -> None:
        """Initialize grayscale transform.

        Args:
            num_channels: Number of output channels. Set to 1 for L mode
                (single channel), or 3 for grayscale in RGB format.
        """
        self.num_channels = num_channels

    def __call__(self, img: Image.Image) -> Image.Image:
        """Convert image to grayscale.

        Args:
            img: Input PIL Image in any color mode.

        Returns:
            Grayscale PIL Image in L mode (1 channel) or RGB mode
            (3 identical channels) based on num_channels setting.
        """
        img = img.convert("L")
        if self.num_channels == 3:
            img = img.convert("RGB")
        return img


class ToTensor(Transform):
    """Convert PIL Image to numpy tensor.

    Converts a PIL Image to a numpy array with shape (C, H, W) and values
    normalized to [0, 1] range. This is a common first step before applying
    Normalize transforms.

    Note:
        For PyTorch compatibility, you may want to convert the result to
        a torch.Tensor after this transform.

    Example:
        >>> to_tensor = ToTensor()
        >>> tensor = to_tensor(pil_image)
        >>> print(tensor.shape)
        (3, 64, 256)
        >>> print(tensor.min(), tensor.max())
        0.0 1.0
    """

    def __call__(self, img: Image.Image) -> np.ndarray:
        """Convert PIL Image to numpy tensor.

        Args:
            img: Input PIL Image in L (grayscale) or RGB mode.

        Returns:
            Numpy array with dtype float32, shape (C, H, W), and values
            in [0, 1] range where:
            - C is 1 for grayscale, 3 for RGB
            - H is image height
            - W is image width
        """
        arr = np.array(img, dtype=np.float32) / 255.0

        if arr.ndim == 2:
            # Grayscale: (H, W) -> (1, H, W)
            arr = arr[np.newaxis, :, :]
        else:
            # RGB: (H, W, C) -> (C, H, W)
            arr = arr.transpose(2, 0, 1)

        return arr


class Normalize(Transform):
    """Normalize tensor values with mean and standard deviation.

    Applies the transformation: output = (input - mean) / std

    This centers data around zero and scales to unit variance, which
    typically improves neural network training convergence.

    Attributes:
        mean: Mean value(s) for normalization. Can be scalar or per-channel.
        std: Standard deviation(s) for normalization. Can be scalar or
            per-channel.

    Example:
        >>> # Scalar normalization (same for all channels)
        >>> norm = Normalize(mean=0.5, std=0.5)
        >>> output = norm(tensor)  # Maps [0, 1] to [-1, 1]

        >>> # Per-channel normalization for RGB
        >>> norm = Normalize(
        ...     mean=(0.485, 0.456, 0.406),
        ...     std=(0.229, 0.224, 0.225),
        ... )
        >>> output = norm(rgb_tensor)
    """

    def __init__(
        self,
        mean: Union[float, Tuple[float, ...]] = 0.5,
        std: Union[float, Tuple[float, ...]] = 0.5,
    ) -> None:
        """Initialize normalization transform.

        Args:
            mean: Mean for normalization. If scalar, applied to all channels.
                If tuple, must match number of input channels.
            std: Standard deviation for normalization. If scalar, applied
                to all channels. If tuple, must match number of input channels.
        """
        self.mean = np.array(mean, dtype=np.float32)
        self.std = np.array(std, dtype=np.float32)

        # Reshape for broadcasting with (C, H, W) tensors
        if self.mean.ndim == 0:
            self.mean = self.mean.reshape(1, 1, 1)
        else:
            self.mean = self.mean.reshape(-1, 1, 1)

        if self.std.ndim == 0:
            self.std = self.std.reshape(1, 1, 1)
        else:
            self.std = self.std.reshape(-1, 1, 1)

    def __call__(self, tensor: np.ndarray) -> np.ndarray:
        """Normalize the input tensor.

        Args:
            tensor: Input numpy array of shape (C, H, W) with values
                typically in [0, 1] range.

        Returns:
            Normalized numpy array of same shape with transformed values.
        """
        return (tensor - self.mean) / self.std


__all__ = [
    "Compose",
    "Grayscale",
    "Normalize",
    "ResizeToHeight",
    "ToTensor",
    "Transform",
]
