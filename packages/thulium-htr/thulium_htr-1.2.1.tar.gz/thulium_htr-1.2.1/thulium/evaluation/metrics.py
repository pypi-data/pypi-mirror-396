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

"""Evaluation metrics for handwriting text recognition.

This module provides implementations of standard metrics used to evaluate
HTR system performance. All edit-distance based metrics use the Levenshtein
distance algorithm for efficiency.

Mathematical Definitions:
    Character Error Rate (CER):
        CER = (S + D + I) / N

    where:
        - S = number of character substitutions
        - D = number of character deletions
        - I = number of character insertions
        - N = total characters in reference

    Word Error Rate (WER):
        WER = (S_w + D_w + I_w) / N_w

    Same formula applied at word level (whitespace-tokenized).

    Sequence Error Rate (SER):
        SER = 1 if reference != hypothesis else 0

    Binary indicator of exact match (0% or 100% per sample).

Classes:
    EditOperations: Detailed breakdown of edit operations.
    LatencyMeter: Utility for measuring inference latency statistics.

Functions:
    cer: Compute Character Error Rate for a single pair.
    wer: Compute Word Error Rate for a single pair.
    ser: Compute Sequence Error Rate for a single pair.
    cer_wer_batch: Compute micro-averaged CER/WER for a batch.
    edit_distance: Compute raw Levenshtein distance.
    get_edit_operations: Get detailed operation breakdown.
    precision_recall_f1: Compute detection metrics.
    throughput: Calculate processing throughput.

Example:
    >>> from thulium.evaluation.metrics import cer, wer, cer_wer_batch
    >>> # Single pair evaluation
    >>> c = cer("hello", "hallo")
    >>> print(f"CER: {c:.2%}")
    'CER: 20.00%'

    >>> # Batch evaluation
    >>> refs = ["hello world", "goodbye"]
    >>> hyps = ["helo world", "goodby"]
    >>> batch_cer, batch_wer = cer_wer_batch(refs, hyps)
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

def _levenshtein_distance(s1: str, s2: str) -> int:
    """Compute Levenshtein edit distance between two strings.

    Internal implementation that avoids external dependencies.

    Args:
        s1: First string.
        s2: Second string.

    Returns:
        Minimum number of single-character edits to transform s1 to s2.
    """
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def cer(reference: str, hypothesis: str) -> float:
    """Compute Character Error Rate (CER) between two strings.

    CER measures the character-level edit distance between the reference
    and hypothesis, normalized by the reference length.

    Mathematical Definition:
        CER = edit_distance(reference, hypothesis) / len(reference)

    Args:
        reference: Ground truth text string.
        hypothesis: Predicted text string.

    Returns:
        CER value in range [0.0, 1.0] or greater if insertions exceed
        the reference length. Returns:
        - 1.0 if reference is empty but hypothesis is not.
        - 0.0 if both strings are empty (perfect match).

    Example:
        >>> cer("hello", "hallo")
        0.2
        >>> cer("hello", "hello")
        0.0
        >>> cer("", "text")
        1.0
    """
    if not reference:
        return 1.0 if hypothesis else 0.0

    distance = _levenshtein_distance(reference, hypothesis)
    return float(distance) / len(reference)


def wer(reference: str, hypothesis: str) -> float:
    """Compute Word Error Rate (WER) between two strings.

    WER measures the word-level edit distance between the reference
    and hypothesis, normalized by the reference word count. Words are
    defined by splitting on whitespace.

    Args:
        reference: Ground truth text string.
        hypothesis: Predicted text string.

    Returns:
        WER value in range [0.0, 1.0] or greater if insertions exceed
        the reference word count.

    Example:
        >>> wer("the quick fox", "the fast fox")
        0.333...
        >>> wer("hello world", "hello world")
        0.0
    """
    ref_words = reference.split()
    hyp_words = hypothesis.split()

    if not ref_words:
        return 1.0 if hyp_words else 0.0

    distance = _levenshtein_distance(ref_words, hyp_words)
    return float(distance) / len(ref_words)


def ser(reference: str, hypothesis: str) -> float:
    """Compute Sequence Error Rate (SER) between two strings.

    SER is a binary metric indicating whether the sequences are identical.
    Also known as sentence error rate for sentence-level evaluation.

    Args:
        reference: Ground truth text string.
        hypothesis: Predicted text string.

    Returns:
        1.0 if strings differ, 0.0 if identical.

    Example:
        >>> ser("hello", "hello")
        0.0
        >>> ser("hello", "hallo")
        1.0
    """
    return 1.0 if reference != hypothesis else 0.0


def edit_distance(reference: str, hypothesis: str) -> int:
    """Compute the Levenshtein edit distance between two strings.

    The edit distance is the minimum number of single-character edits
    (insertions, deletions, substitutions) required to transform
    the hypothesis into the reference.

    Args:
        reference: Target string.
        hypothesis: Source string to transform.

    Returns:
        Non-negative integer edit distance.

    Example:
        >>> edit_distance("kitten", "sitting")
        3
    """
    return _levenshtein_distance(reference, hypothesis)


def cer_wer_batch(
    references: List[str],
    hypotheses: List[str],
) -> Tuple[float, float]:
    """Compute CER and WER for a batch of samples.

    Computes micro-averaged metrics, where errors and lengths are summed
    across all samples before computing the rate. This gives more weight
    to longer sequences.

    Args:
        references: List of ground truth strings.
        hypotheses: List of predicted strings. Must have same length as
            references.

    Returns:
        Tuple of (micro-averaged CER, micro-averaged WER).

    Raises:
        ValueError: If references and hypotheses have different lengths.

    Example:
        >>> refs = ["hello", "world"]
        >>> hyps = ["helo", "world"]
        >>> c, w = cer_wer_batch(refs, hyps)
        >>> print(f"CER: {c:.2%}, WER: {w:.2%}")
    """
    if len(references) != len(hypotheses):
        raise ValueError(
            f"References and hypotheses must have same length, "
            f"got {len(references)} and {len(hypotheses)}"
        )

    total_char_dist = 0
    total_chars = 0
    total_word_dist = 0
    total_words = 0

    for ref, hyp in zip(references, hypotheses):
        total_char_dist += _levenshtein_distance(ref, hyp)
        total_chars += len(ref)

        ref_words = ref.split()
        hyp_words = hyp.split()
        total_word_dist += _levenshtein_distance(ref_words, hyp_words)
        total_words += len(ref_words)

    batch_cer = total_char_dist / total_chars if total_chars > 0 else 0.0
    batch_wer = total_word_dist / total_words if total_words > 0 else 0.0

    return batch_cer, batch_wer


@dataclass
class EditOperations:
    """Detailed breakdown of edit operations between two sequences.

    This class provides insight into the types of errors made during
    recognition, which is useful for error analysis and debugging.

    Attributes:
        substitutions: Number of character substitutions required.
        deletions: Number of character deletions required.
        insertions: Number of character insertions required.
        matches: Number of matching characters.

    Example:
        >>> ops = get_edit_operations("hello", "helo")
        >>> print(f"Deletions: {ops.deletions}")
        'Deletions: 1'
    """

    substitutions: int
    deletions: int
    insertions: int
    matches: int

    @property
    def total_errors(self) -> int:
        """Return total number of edit operations.

        Returns:
            Sum of substitutions, deletions, and insertions.
        """
        return self.substitutions + self.deletions + self.insertions

    @property
    def total_reference(self) -> int:
        """Return total reference length.

        Returns:
            Sum of substitutions, deletions, and matches (original chars).
        """
        return self.substitutions + self.deletions + self.matches


def get_edit_operations(reference: str, hypothesis: str) -> EditOperations:
    """Compute detailed edit operation counts between two strings.

    Uses dynamic programming to compute the minimum edit distance and
    traces back through the alignment to count individual operations.

    Args:
        reference: Ground truth string.
        hypothesis: Predicted string.

    Returns:
        EditOperations with counts of each operation type.

    Example:
        >>> ops = get_edit_operations("hello", "hallo")
        >>> print(f"Subs: {ops.substitutions}, Matches: {ops.matches}")
        'Subs: 1, Matches: 4'
    """
    m, n = len(reference), len(hypothesis)

    # Build dynamic programming table
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if reference[i - 1] == hypothesis[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # deletion
                    dp[i][j - 1],      # insertion
                    dp[i - 1][j - 1],  # substitution
                )

    # Trace back to count operations
    subs = dels = ins = matches = 0
    i, j = m, n

    while i > 0 or j > 0:
        if i > 0 and j > 0 and reference[i - 1] == hypothesis[j - 1]:
            matches += 1
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            subs += 1
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            dels += 1
            i -= 1
        else:
            ins += 1
            j -= 1

    return EditOperations(
        substitutions=subs,
        deletions=dels,
        insertions=ins,
        matches=matches,
    )


def precision_recall_f1(
    true_positives: int,
    false_positives: int,
    false_negatives: int,
) -> Tuple[float, float, float]:
    """Compute precision, recall, and F1 score.

    Used for detection tasks such as line detection or word detection
    where the task is to identify specific regions.

    Args:
        true_positives: Number of correctly detected items.
        false_positives: Number of incorrectly detected items (false alarms).
        false_negatives: Number of missed items.

    Returns:
        Tuple of (precision, recall, F1), each in range [0.0, 1.0].

    Example:
        >>> p, r, f1 = precision_recall_f1(tp=80, fp=10, fn=20)
        >>> print(f"Precision: {p:.2%}, Recall: {r:.2%}, F1: {f1:.2%}")
    """
    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 0.0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 0.0
    )
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return precision, recall, f1


class LatencyMeter:
    """Utility for measuring inference latency with statistics.

    Tracks timing measurements and provides aggregate statistics including
    mean, standard deviation, and percentiles for performance analysis.

    Attributes:
        times: List of recorded latency measurements in milliseconds.

    Example:
        >>> meter = LatencyMeter()
        >>> for sample in dataset:
        ...     with meter.measure():
        ...         result = model(sample)
        >>> print(f"Mean: {meter.mean_ms:.2f}ms, P95: {meter.p95_ms:.2f}ms")
    """

    def __init__(self) -> None:
        """Initialize an empty latency meter."""
        self.times: List[float] = []
        self._start_time: Optional[float] = None

    def start(self) -> None:
        """Start timing measurement.

        Call stop() to record the elapsed time.
        """
        self._start_time = time.perf_counter()

    def stop(self) -> float:
        """Stop timing and record elapsed time.

        Returns:
            Elapsed time in milliseconds.

        Raises:
            RuntimeError: If start() was not called first.
        """
        if self._start_time is None:
            raise RuntimeError("Timer not started. Call start() first.")
        elapsed = (time.perf_counter() - self._start_time) * 1000
        self.times.append(elapsed)
        self._start_time = None
        return elapsed

    def measure(self) -> "_LatencyContext":
        """Create a context manager for timing a code block.

        Returns:
            Context manager that times the enclosed block.

        Example:
            >>> with meter.measure():
            ...     result = expensive_operation()
        """
        return _LatencyContext(self)

    @property
    def count(self) -> int:
        """Return number of recorded measurements.

        Returns:
            Count of recorded timing samples.
        """
        return len(self.times)

    @property
    def mean_ms(self) -> float:
        """Return mean latency in milliseconds.

        Returns:
            Arithmetic mean of all recorded times.
        """
        return sum(self.times) / len(self.times) if self.times else 0.0

    @property
    def std_ms(self) -> float:
        """Return standard deviation of latency in milliseconds.

        Returns:
            Population standard deviation of recorded times.
        """
        if len(self.times) < 2:
            return 0.0
        mean = self.mean_ms
        variance = sum((t - mean) ** 2 for t in self.times) / len(self.times)
        return variance ** 0.5

    @property
    def p95_ms(self) -> float:
        """Return 95th percentile latency in milliseconds.

        Returns:
            95th percentile of recorded times.
        """
        if not self.times:
            return 0.0
        sorted_times = sorted(self.times)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[min(idx, len(sorted_times) - 1)]

    @property
    def p99_ms(self) -> float:
        """Return 99th percentile latency in milliseconds.

        Returns:
            99th percentile of recorded times.
        """
        if not self.times:
            return 0.0
        sorted_times = sorted(self.times)
        idx = int(len(sorted_times) * 0.99)
        return sorted_times[min(idx, len(sorted_times) - 1)]

    def summary(self) -> Dict[str, float]:
        """Return dictionary of summary statistics.

        Returns:
            Dictionary with count, mean_ms, std_ms, p95_ms, p99_ms.
        """
        return {
            "count": self.count,
            "mean_ms": self.mean_ms,
            "std_ms": self.std_ms,
            "p95_ms": self.p95_ms,
            "p99_ms": self.p99_ms,
        }


class _LatencyContext:
    """Context manager helper for LatencyMeter.measure()."""

    def __init__(self, meter: LatencyMeter) -> None:
        """Initialize context with parent meter.

        Args:
            meter: Parent LatencyMeter instance.
        """
        self.meter = meter

    def __enter__(self) -> "_LatencyContext":
        """Start timing when entering context.

        Returns:
            Self for potential access in with statement.
        """
        self.meter.start()
        return self

    def __exit__(self, *args: object) -> None:
        """Stop timing when exiting context.

        Args:
            *args: Exception info (ignored).
        """
        self.meter.stop()


def throughput(num_samples: int, total_time_s: float) -> float:
    """Calculate throughput in samples per second.

    Args:
        num_samples: Number of samples processed.
        total_time_s: Total processing time in seconds.

    Returns:
        Throughput in samples per second. Returns 0.0 if time is
        zero or negative.

    Example:
        >>> t = throughput(num_samples=1000, total_time_s=10.0)
        >>> print(f"{t:.1f} samples/sec")
        '100.0 samples/sec'
    """
    if total_time_s <= 0:
        return 0.0
    return num_samples / total_time_s


__all__ = [
    "EditOperations",
    "LatencyMeter",
    "cer",
    "cer_wer_batch",
    "edit_distance",
    "get_edit_operations",
    "precision_recall_f1",
    "ser",
    "throughput",
    "wer",
]
