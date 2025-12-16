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

"""Custom samplers for efficient HTR training.

This module provides custom PyTorch samplers optimized for handwriting text
recognition training. These samplers implement strategies that reduce training
time and improve convergence.

Key Features:
    - BucketingSampler: Groups samples by image width to minimize padding
      overhead, providing up to 2x training speedup.
    - CurriculumSampler: Implements curriculum learning by starting with
      simpler (shorter) samples and gradually introducing harder ones.

Classes:
    BucketingSampler: Width-aware bucketing to minimize padding waste.
    CurriculumSampler: Curriculum learning for improved convergence.

Example:
    Using BucketingSampler for efficient training:

    >>> from torch.utils.data import DataLoader
    >>> from thulium.data.samplers import BucketingSampler
    >>>
    >>> sampler = BucketingSampler(dataset, batch_size=32, shuffle=True)
    >>> loader = DataLoader(dataset, batch_sampler=sampler)

    Using CurriculumSampler for curriculum learning:

    >>> from thulium.data.samplers import CurriculumSampler
    >>>
    >>> sampler = CurriculumSampler(dataset, total_epochs=100)
    >>> for epoch in range(100):
    ...     sampler.set_epoch(epoch)
    ...     for batch in DataLoader(dataset, sampler=sampler):
    ...         train_step(batch)
"""

from __future__ import annotations

import logging
from typing import Callable
from typing import Iterator
from typing import List
from typing import Optional

import numpy as np
import torch
from torch.utils.data import Dataset
from torch.utils.data import Sampler

logger = logging.getLogger(__name__)


class BucketingSampler(Sampler[int]):
    """Sampler that groups samples by image width to minimize padding overhead.

    Bucketing can provide significant speedup during training (up to 2x)
    by reducing the amount of padding needed in each batch. Variable-width
    handwriting images benefit greatly from this approach.

    The sampler works in three phases:
        1. Sorts all sample indices by their image width.
        2. Groups sorted indices into batches of similar widths.
        3. Shuffles the batch order (not within batches) for stochasticity.

    Attributes:
        dataset: The PyTorch Dataset to sample from.
        batch_size: Number of samples per batch.
        shuffle: Whether to shuffle batch order between epochs.
        drop_last: Whether to drop the last incomplete batch.

    Example:
        >>> sampler = BucketingSampler(
        ...     dataset,
        ...     batch_size=32,
        ...     shuffle=True,
        ...     drop_last=True,
        ... )
        >>> loader = DataLoader(dataset, batch_sampler=sampler)
        >>> for batch in loader:
        ...     # Batch contains images of similar widths
        ...     train_step(batch)
    """

    def __init__(
        self,
        dataset: Dataset,
        batch_size: int,
        shuffle: bool = True,
        drop_last: bool = False,
        *,
        width_fn: Optional[Callable[[int], int]] = None,
    ) -> None:
        """Initialize the bucketing sampler.

        Args:
            dataset: PyTorch Dataset to sample from. Should have len() defined.
            batch_size: Number of samples per batch.
            shuffle: Whether to shuffle batch order between iterations.
                Set to True for training, False for evaluation.
            drop_last: Whether to drop the last incomplete batch if dataset
                size is not divisible by batch_size.
            width_fn: Optional function that takes a sample index and returns
                its image width. If None, the sampler attempts to get widths
                from dataset.get_metadata() or dataset.widths attributes.
        """
        super().__init__(dataset)
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.drop_last = drop_last
        self._width_fn = width_fn

        # Precompute widths for efficient bucketing
        self._widths = self._compute_widths()

    def _compute_widths(self) -> List[int]:
        """Compute sample widths for bucketing.

        Attempts to retrieve width information from the dataset using
        various methods. Falls back to uniform widths if unavailable.

        Returns:
            List of integer widths, one per sample in the dataset.
        """
        if self._width_fn is not None:
            return [self._width_fn(i) for i in range(len(self.dataset))]

        # Try to get widths from dataset metadata
        if hasattr(self.dataset, "get_metadata"):
            try:
                metadata = self.dataset.get_metadata()
                return [m.get("width", 100) for m in metadata]
            except Exception:
                pass

        if hasattr(self.dataset, "widths"):
            return list(self.dataset.widths)

        # Fallback: uniform widths (effectively disables bucketing)
        logger.debug("Width metadata not available, bucketing disabled")
        return [100] * len(self.dataset)

    def __iter__(self) -> Iterator[int]:
        """Iterate over sample indices in bucketed order.

        Returns:
            Iterator yielding sample indices grouped by similar widths.
        """
        n = len(self.dataset)
        indices = list(range(n))

        # Check if bucketing is useful (multiple unique widths)
        unique_widths = len(set(self._widths))
        if unique_widths > 1:
            return self._bucketed_iter(indices)
        else:
            return self._standard_iter(indices)

    def _bucketed_iter(self, indices: List[int]) -> Iterator[int]:
        """Generate iteration order using bucketing strategy.

        Sorts indices by width, creates batches, and shuffles batch order.

        Args:
            indices: List of all sample indices to process.

        Yields:
            Sample indices in bucketed order.
        """
        # Sort by width for bucketing
        sorted_indices = sorted(indices, key=lambda x: self._widths[x])

        # Create batches of similar widths
        batches = [
            sorted_indices[i : i + self.batch_size]
            for i in range(0, len(sorted_indices), self.batch_size)
        ]

        # Optionally drop last incomplete batch
        if self.drop_last and batches and len(batches[-1]) < self.batch_size:
            batches = batches[:-1]

        # Shuffle batch order (not within batches)
        if self.shuffle:
            np.random.shuffle(batches)

        # Flatten and yield
        for batch in batches:
            yield from batch

    def _standard_iter(self, indices: List[int]) -> Iterator[int]:
        """Generate standard (non-bucketed) iteration order.

        Used when bucketing is not beneficial (all samples have same width).

        Args:
            indices: List of all sample indices.

        Returns:
            Iterator over shuffled or sequential indices.
        """
        if self.shuffle:
            generator = torch.Generator()
            generator.manual_seed(
                int(torch.empty((), dtype=torch.int64).random_().item())
            )
            perm = torch.randperm(len(indices), generator=generator)
            indices = [indices[i] for i in perm.tolist()]

        if self.drop_last:
            n_batches = len(indices) // self.batch_size
            indices = indices[: n_batches * self.batch_size]

        return iter(indices)

    def __len__(self) -> int:
        """Return the number of samples that will be yielded.

        Returns:
            Total sample count, accounting for drop_last if enabled.
        """
        n = len(self.dataset)
        if self.drop_last:
            return (n // self.batch_size) * self.batch_size
        return n


class CurriculumSampler(Sampler[int]):
    """Sampler implementing curriculum learning for HTR training.

    Curriculum learning starts with simpler (typically shorter) samples
    and gradually introduces more complex (longer) samples as training
    progresses. This strategy often improves convergence and final accuracy.

    The curriculum is controlled by the training epoch:
        - Early epochs: Only easy samples (short sequences)
        - Middle epochs: Mix of easy and medium difficulty
        - Late epochs: Full dataset including difficult samples

    Attributes:
        dataset: PyTorch Dataset to sample from.
        total_epochs: Total number of training epochs for scheduling.
        epoch: Current training epoch (set via set_epoch()).

    Example:
        >>> sampler = CurriculumSampler(dataset, total_epochs=100)
        >>> for epoch in range(100):
        ...     sampler.set_epoch(epoch)
        ...     for batch in DataLoader(dataset, sampler=sampler):
        ...         train_step(batch)
        ...     print(f"Epoch {epoch}: sampled {len(sampler)} items")
    """

    def __init__(
        self,
        dataset: Dataset,
        total_epochs: int = 100,
        *,
        difficulty_fn: Optional[Callable[[int], float]] = None,
    ) -> None:
        """Initialize the curriculum sampler.

        Args:
            dataset: PyTorch Dataset to sample from.
            total_epochs: Total epochs for curriculum scheduling. The
                curriculum transitions linearly from easy to hard samples
                over this many epochs.
            difficulty_fn: Optional function mapping sample index to a
                difficulty score in [0, 1]. If None, uses sequence length
                as a proxy for difficulty.
        """
        super().__init__(dataset)
        self.dataset = dataset
        self.total_epochs = total_epochs
        self.epoch = 0
        self._difficulty_fn = difficulty_fn

        # Precompute difficulty scores for all samples
        self._difficulties = self._compute_difficulties()

    def _compute_difficulties(self) -> List[float]:
        """Compute difficulty scores for each sample.

        Attempts to use provided difficulty_fn, otherwise falls back to
        using sequence length as a proxy for difficulty.

        Returns:
            List of difficulty scores in [0.0, 1.0], one per sample.
        """
        if self._difficulty_fn is not None:
            return [self._difficulty_fn(i) for i in range(len(self.dataset))]

        # Default: use sequence length as difficulty proxy
        if hasattr(self.dataset, "samples"):
            lengths = [len(s[1]) for s in self.dataset.samples]
            max_len = max(lengths) if lengths else 1
            return [length / max_len for length in lengths]

        # Fallback: uniform difficulty
        return [0.5] * len(self.dataset)

    def set_epoch(self, epoch: int) -> None:
        """Set the current epoch for curriculum scheduling.

        Must be called at the start of each epoch to update the
        curriculum state.

        Args:
            epoch: Current epoch number (0-indexed).
        """
        self.epoch = epoch

    def __iter__(self) -> Iterator[int]:
        """Iterate with curriculum-based sample selection.

        Filters samples based on difficulty threshold determined by
        current epoch progress.

        Returns:
            Iterator over sample indices, filtered by curriculum.
        """
        # Compute fraction of training complete and set threshold
        progress = min(1.0, (self.epoch + 1) / self.total_epochs)
        threshold = progress  # Linear curriculum schedule

        # Filter samples by difficulty threshold
        indices = [
            i
            for i, difficulty in enumerate(self._difficulties)
            if difficulty <= threshold
        ]

        # Always include at least 20% of samples for stable gradients
        min_samples = max(1, len(self.dataset) // 5)
        if len(indices) < min_samples:
            sorted_by_diff = sorted(
                range(len(self.dataset)),
                key=lambda x: self._difficulties[x],
            )
            indices = sorted_by_diff[:min_samples]

        # Shuffle for stochastic training
        np.random.shuffle(indices)

        return iter(indices)

    def __len__(self) -> int:
        """Return dataset size (may not reflect actual samples yielded).

        Returns:
            Total dataset size. Note: actual samples yielded depends on
            current epoch and curriculum state.
        """
        return len(self.dataset)


__all__ = [
    "BucketingSampler",
    "CurriculumSampler",
]
