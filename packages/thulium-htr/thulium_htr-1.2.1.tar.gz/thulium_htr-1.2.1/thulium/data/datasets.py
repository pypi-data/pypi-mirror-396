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

"""Dataset classes for HTR training and evaluation.

This module provides PyTorch Dataset implementations for common handwriting
text recognition data formats. It supports standard benchmarks (IAM, RIMES)
as well as custom data loaded from directories with label files.

Classes:
    HTRDataset: Base dataset class for image-text pairs with transform support.
    FolderDataset: Dataset loading samples from a directory with label file.
    IAMDataset: Specialized dataset for IAM Handwriting Database format.

Module Design:
    All dataset classes follow PyTorch's Dataset interface and return
    dictionaries with 'image', 'text', and 'path' keys. Images are loaded
    lazily on access, and transforms are applied per-sample.

Example:
    Creating a custom dataset from image-text pairs:

    >>> from thulium.data.datasets import HTRDataset
    >>> samples = [("img1.png", "Hello"), ("img2.png", "World")]
    >>> dataset = HTRDataset(samples)
    >>> sample = dataset[0]
    >>> print(sample["text"])
    'Hello'

    Loading from IAM format:

    >>> from thulium.data.datasets import IAMDataset
    >>> dataset = IAMDataset(root="data/iam", split="train", level="line")
    >>> print(f"Loaded {len(dataset)} samples")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from torch.utils.data import Dataset

from thulium.data.loaders import load_image

logger = logging.getLogger(__name__)


class HTRDataset(Dataset):
    """Base dataset class for handwriting text recognition.

    Loads image-text pairs from a list of samples. Each sample consists of
    a path to an image file and its corresponding text transcription. The
    dataset supports optional transforms for both images and text labels.

    Attributes:
        samples: List of (image_path, text_label) tuples representing the
            complete dataset.
        transform: Optional callable to apply to loaded images. Common
            transforms include resizing, normalization, and augmentation.
        target_transform: Optional callable to apply to text labels. Can be
            used for text normalization or encoding to indices.

    Example:
        >>> samples = [
        ...     ("img1.png", "Hello"),
        ...     ("img2.png", "World"),
        ...     ("img3.png", "Test"),
        ... ]
        >>> dataset = HTRDataset(samples, transform=my_image_transform)
        >>> sample = dataset[0]
        >>> print(sample["text"])
        'Hello'
        >>> print(type(sample["image"]))
        <class 'PIL.Image.Image'>
    """

    def __init__(
        self,
        samples: List[Tuple[str, str]],
        transform: Optional[Callable[[Any], Any]] = None,
        target_transform: Optional[Callable[[str], Any]] = None,
    ) -> None:
        """Initialize the HTR dataset.

        Args:
            samples: List of (image_path, text_label) tuples. Each image_path
                should be a valid path to an image file.
            transform: Optional callable that takes a PIL Image and returns
                a transformed version. Applied to each image on access.
            target_transform: Optional callable that takes a string and returns
                a transformed version. Applied to text labels on access.
        """
        self.samples = samples
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self) -> int:
        """Return the number of samples in the dataset.

        Returns:
            Integer count of samples.
        """
        return len(self.samples)

    def __getitem__(self, idx: int) -> Optional[Dict[str, Any]]:
        """Get a sample by index.

        Loads the image from disk and applies any configured transforms.
        Images are loaded lazily to conserve memory.

        Args:
            idx: Sample index in range [0, len(dataset)).

        Returns:
            Dictionary containing:
                - 'image': The loaded and transformed image.
                - 'text': The text label (possibly transformed).
                - 'path': Original image path as string.
            Returns None if image loading fails.

        Raises:
            IndexError: If idx is outside the valid range.
        """
        if idx < 0 or idx >= len(self.samples):
            raise IndexError(
                f"Index {idx} out of range [0, {len(self.samples)})"
            )

        img_path, text = self.samples[idx]

        try:
            image = load_image(img_path)
        except Exception as e:
            logger.warning("Failed to load image %s: %s", img_path, e)
            return None

        if self.transform is not None:
            image = self.transform(image)

        if self.target_transform is not None:
            text = self.target_transform(text)

        return {"image": image, "text": text, "path": img_path}


class FolderDataset(HTRDataset):
    """Dataset loading samples from a directory with separate label file.

    Expects a directory containing image files and a separate text file
    with labels in tab-separated format. Each line in the label file maps
    a filename to its transcription.

    Label File Format:
        filename1.jpg<TAB>Ground Truth Text
        filename2.jpg<TAB>Another Line of Text

    Attributes:
        root: Root directory containing image files.
        label_file: Path to the labels file used to load this dataset.

    Example:
        >>> dataset = FolderDataset(
        ...     root="data/images",
        ...     label_file="data/labels.txt",
        ...     transform=my_transform,
        ... )
        >>> print(f"Loaded {len(dataset)} samples")
        'Loaded 1000 samples'
    """

    def __init__(
        self,
        root: str,
        label_file: str,
        transform: Optional[Callable[[Any], Any]] = None,
        target_transform: Optional[Callable[[str], Any]] = None,
        *,
        delimiter: str = "\t",
    ) -> None:
        """Initialize the folder dataset.

        Parses the label file and constructs sample tuples for all entries.
        Logs warnings for malformed lines that cannot be parsed.

        Args:
            root: Root directory containing image files. Image paths in the
                label file are resolved relative to this directory.
            label_file: Path to the labels file containing filename-label pairs.
            transform: Optional image transform callable.
            target_transform: Optional text transform callable.
            delimiter: Character(s) separating filename from label in the
                label file. Defaults to tab character. Falls back to space
                if tab splitting fails.

        Raises:
            FileNotFoundError: If label_file does not exist.
        """
        label_path = Path(label_file)
        if not label_path.exists():
            raise FileNotFoundError(f"Label file not found: {label_file}")

        root_path = Path(root)
        samples: List[Tuple[str, str]] = []

        with open(label_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                parts = line.split(delimiter, maxsplit=1)
                if len(parts) != 2:
                    # Try space delimiter as fallback
                    parts = line.split(maxsplit=1)

                if len(parts) == 2:
                    filename, label = parts
                    img_path = root_path / filename.strip()
                    samples.append((str(img_path), label.strip()))
                else:
                    logger.warning(
                        "Skipping malformed line %d in %s: %s",
                        line_num,
                        label_file,
                        line[:50],
                    )

        logger.info("Loaded %d samples from %s", len(samples), label_file)
        super().__init__(samples, transform, target_transform)


class IAMDataset(HTRDataset):
    """Dataset for IAM Handwriting Database format.

    Supports both line-level and word-level recognition tasks using the
    standard IAM directory structure. The IAM database is one of the most
    widely used benchmarks for offline handwriting recognition.

    IAM Directory Structure:
        root/
        ├── lines/          # Line images organized by form ID
        │   └── a01/
        │       └── a01-000/
        │           └── a01-000-00.png
        ├── words/          # Word images organized by form ID
        ├── ascii/          # Ground truth transcriptions
        │   ├── lines.txt   # Line-level labels
        │   └── words.txt   # Word-level labels
        └── splits/         # Train/val/test splits
            ├── train.txt
            ├── val.txt
            └── test.txt

    Attributes:
        root: Root directory of the IAM dataset.
        split: Dataset split being used ('train', 'val', or 'test').
        level: Recognition level ('line' or 'word').

    Example:
        >>> dataset = IAMDataset(
        ...     root="data/iam",
        ...     split="train",
        ...     level="line",
        ...     transform=preprocess_transform,
        ... )
        >>> print(f"Training set: {len(dataset)} lines")
    """

    def __init__(
        self,
        root: str,
        split: str = "train",
        level: str = "line",
        transform: Optional[Callable[[Any], Any]] = None,
        target_transform: Optional[Callable[[str], Any]] = None,
    ) -> None:
        """Initialize the IAM dataset.

        Args:
            root: Root directory of the IAM dataset containing lines/,
                words/, and ascii/ subdirectories.
            split: Dataset split to load. One of 'train', 'val', or 'test'.
            level: Recognition granularity level. Either 'line' for full
                text lines or 'word' for individual words.
            transform: Optional image transform callable.
            target_transform: Optional text transform callable.

        Raises:
            ValueError: If split is not one of 'train', 'val', 'test'.
            ValueError: If level is not one of 'line', 'word'.
            FileNotFoundError: If root directory does not exist.
        """
        if split not in ("train", "val", "test"):
            raise ValueError(f"split must be 'train', 'val', or 'test', got {split}")
        if level not in ("line", "word"):
            raise ValueError(f"level must be 'line' or 'word', got {level}")

        self.root = Path(root)
        self.split = split
        self.level = level

        if not self.root.exists():
            raise FileNotFoundError(f"IAM root directory not found: {root}")

        samples = self._load_iam_samples()
        super().__init__(samples, transform, target_transform)

    def _load_iam_samples(self) -> List[Tuple[str, str]]:
        """Load samples from IAM format files.

        Parses the appropriate lines.txt or words.txt file and filters
        by the configured split.

        Returns:
            List of (image_path, transcription_text) tuples.
        """
        # TODO(thulium-team): Implement full IAM parsing logic
        # In production, this would:
        # 1. Read lines.txt or words.txt based on self.level
        # 2. Parse the IAM format (| separated fields)
        # 3. Filter by split using splits/train.txt, etc.
        # 4. Construct full image paths
        samples: List[Tuple[str, str]] = []
        logger.info(
            "Loading IAM %s split at %s level from %s",
            self.split,
            self.level,
            self.root,
        )
        return samples


__all__ = [
    "FolderDataset",
    "HTRDataset",
    "IAMDataset",
]
