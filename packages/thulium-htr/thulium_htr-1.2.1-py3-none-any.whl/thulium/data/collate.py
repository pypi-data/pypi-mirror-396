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

"""Collation functions for HTR data loading.

This module provides collation functions that handle dynamic padding of
images and text sequences for batch processing during training. Collation
is necessary because handwriting images and transcriptions have variable
lengths that must be padded to form uniform tensors.

Classes:
    HTRCollate: Configurable collation function for HTR training batches.

Protocols:
    Tokenizer: Protocol defining the interface for text tokenization.

Example:
    Using HTRCollate with PyTorch DataLoader:

    >>> from torch.utils.data import DataLoader
    >>> from thulium.data.collate import HTRCollate
    >>>
    >>> collate_fn = HTRCollate(tokenizer=my_tokenizer, padding_value=0)
    >>> dataloader = DataLoader(
    ...     dataset,
    ...     batch_size=32,
    ...     collate_fn=collate_fn,
    ... )
    >>> for batch in dataloader:
    ...     images = batch["images"]  # (B, C, H_max, W_max)
    ...     targets = batch["targets"]  # (B, L_max)
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Protocol
from typing import Tuple

import torch
from torch.nn.utils.rnn import pad_sequence


class Tokenizer(Protocol):
    """Protocol defining the interface for text tokenization.

    Any tokenizer used with HTRCollate must implement this interface,
    allowing the collation function to convert text strings to integer
    label sequences.

    Example:
        Implementing a tokenizer:

        >>> class MyTokenizer:
        ...     def __init__(self, vocab: Dict[str, int]):
        ...         self.vocab = vocab
        ...
        ...     def text_to_labels(self, text: str) -> List[int]:
        ...         return [self.vocab.get(c, 0) for c in text]
    """

    def text_to_labels(self, text: str) -> List[int]:
        """Convert text string to a list of integer label indices.

        Args:
            text: Input text string to tokenize.

        Returns:
            List of integer indices corresponding to characters or tokens.
        """
        ...


class HTRCollate:
    """Collation function for HTR training batches.

    Handles dynamic padding of variable-size images and text sequences to
    create uniform batches suitable for neural network training. Images are
    zero-padded to the maximum dimensions in the batch, and text sequences
    are padded with a configurable padding value.

    Batch Output Structure:
        - images: Tensor of shape [B, C, H_max, W_max] with zero padding.
        - targets: Tensor of shape [B, L_max] with padding_value padding.
        - lengths: Tensor of shape [B] containing original target lengths.
        - image_widths: Tensor of shape [B] containing original image widths.

    Attributes:
        tokenizer: Optional tokenizer for converting text to indices.
            If None, expects 'text' field to already be encoded as indices.
        padding_value: Integer value used for padding target sequences.
            Typically the CTC blank index (0) or a dedicated padding token.

    Example:
        >>> tokenizer = CharacterTokenizer(vocab)
        >>> collate_fn = HTRCollate(tokenizer=tokenizer, padding_value=0)
        >>>
        >>> dataloader = DataLoader(
        ...     dataset,
        ...     batch_size=32,
        ...     collate_fn=collate_fn,
        ...     num_workers=4,
        ... )
    """

    def __init__(
        self,
        tokenizer: Optional[Tokenizer] = None,
        padding_value: int = 0,
    ) -> None:
        """Initialize the collation function.

        Args:
            tokenizer: Optional tokenizer implementing the Tokenizer protocol.
                Used to convert 'text' strings to integer indices. If None,
                the 'text' field in samples must already be encoded as
                lists of integers or tensors.
            padding_value: Integer value used for padding target sequences
                to uniform length. Common choices:
                - 0: Typical for CTC loss (blank index).
                - -100: PyTorch convention for ignored positions.
        """
        self.tokenizer = tokenizer
        self.padding_value = padding_value

    def __call__(
        self, batch: List[Optional[Dict[str, Any]]]
    ) -> Dict[str, torch.Tensor]:
        """Collate a batch of samples into padded tensors.

        Handles None samples (failed loads) by filtering them out.
        Pads images and targets to uniform sizes within the batch.

        Args:
            batch: List of sample dictionaries, each containing:
                - 'image': Tensor of shape [C, H, W].
                - 'text': String or encoded tensor of labels.
                May contain None entries for failed samples.

        Returns:
            Dictionary containing:
                - 'images': Tensor [B, C, H_max, W_max] of padded images.
                - 'targets': Tensor [B, L_max] of padded label sequences.
                - 'lengths': Tensor [B] of original target lengths.
                - 'image_widths': Tensor [B] of original image widths.
            Returns empty dict if all samples failed.
        """
        # Filter out failed samples (None entries)
        batch = [sample for sample in batch if sample is not None]
        if not batch:
            return {}

        # Process images
        images = [item["image"] for item in batch]
        padded_images, image_widths = self._pad_images(images)

        # Process targets
        targets, lengths = self._encode_targets(batch)
        padded_targets = pad_sequence(
            targets,
            batch_first=True,
            padding_value=self.padding_value,
        )

        return {
            "images": padded_images,
            "targets": padded_targets,
            "lengths": torch.tensor(lengths, dtype=torch.long),
            "image_widths": torch.tensor(image_widths, dtype=torch.long),
        }

    def _pad_images(
        self, images: List[torch.Tensor]
    ) -> Tuple[torch.Tensor, List[int]]:
        """Pad images to uniform size within the batch.

        Zero-pads all images to the maximum height and width in the batch.
        Padding is applied to the bottom and right edges.

        Args:
            images: List of image tensors, each with shape [C, H, W].
                All images must have the same number of channels.

        Returns:
            Tuple of:
                - Padded images tensor of shape [B, C, H_max, W_max].
                - List of original widths for each image.
        """
        max_height = max(img.shape[1] for img in images)
        max_width = max(img.shape[2] for img in images)
        num_channels = images[0].shape[0]

        padded = torch.zeros(
            len(images),
            num_channels,
            max_height,
            max_width,
            dtype=images[0].dtype,
        )
        widths: List[int] = []

        for i, img in enumerate(images):
            _, height, width = img.shape
            padded[i, :, :height, :width] = img
            widths.append(width)

        return padded, widths

    def _encode_targets(
        self, batch: List[Dict[str, Any]]
    ) -> Tuple[List[torch.Tensor], List[int]]:
        """Encode target texts to tensors.

        Converts text strings to integer tensors using the configured
        tokenizer, or passes through already-encoded targets.

        Args:
            batch: List of sample dictionaries with 'text' field.

        Returns:
            Tuple of:
                - List of 1D target tensors (variable length).
                - List of original lengths for each target.
        """
        targets: List[torch.Tensor] = []
        lengths: List[int] = []

        for item in batch:
            text = item["text"]

            if self.tokenizer is not None:
                encoded = self.tokenizer.text_to_labels(text)
                tensor = torch.tensor(encoded, dtype=torch.long)
            elif isinstance(text, torch.Tensor):
                tensor = text
            else:
                tensor = torch.tensor(text, dtype=torch.long)

            targets.append(tensor)
            lengths.append(len(tensor))

        return targets, lengths


__all__ = [
    "HTRCollate",
    "Tokenizer",
]
