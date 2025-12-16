"""
Image transformations and augmentations for HTR.
"""

from typing import Tuple, List
import numpy as np
from PIL import Image, ImageOps

class Transform:
    """Base class for transforms."""
    def __call__(self, img: Image.Image) -> Image.Image:
        raise NotImplementedError

class ResizeAndPad(Transform):
    """
    Resize image to target height while maintaining aspect ratio, 
    then pad to target width or divisible width.
    """
    def __init__(self, target_height: int = 128, target_width: Optional[int] = None):
        self.target_height = target_height
        self.target_width = target_width

    def __call__(self, img: Image.Image) -> Image.Image:
        w, h = img.size
        # Scale to fixed height
        scale = self.target_height / h
        new_w = int(w * scale)
        img = img.resize((new_w, self.target_height), Image.Resampling.BILINEAR)

        if self.target_width:
            # Pad if needed
            if new_w < self.target_width:
                pad_w = self.target_width - new_w
                img = ImageOps.expand(img, border=(0, 0, pad_w, 0), fill="white")
            elif new_w > self.target_width:
                # Resize to fit? Or crop? For HTR usually we support variable width
                img = img.resize((self.target_width, self.target_height), Image.Resampling.BILINEAR)
        return img

def normalize_tensor(img_tensor: np.ndarray) -> np.ndarray:
    """
    Normalize image tensor (0-255) to (-1, 1).
    Args:
        img_tensor: numpy array of shape (C, H, W) or (H, W, C)
    """
    return (img_tensor.astype(np.float32) / 127.5) - 1.0
