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

"""Calibration metrics for HTR models.

This module provides metrics to evaluate the calibration of model confidence
scores, ensuring that predicted probabilities match empirical accuracy.

A well-calibrated model has confidence scores that match the true probability
of correctness, which is critical for reliable uncertainty estimation in
production systems.

Key Metrics:
    ECE: Expected Calibration Error - weighted average of calibration gap
        across confidence bins.
    MCE: Maximum Calibration Error - worst-case calibration gap.
    Brier Score: Mean squared error between confidence and correctness.

Classes:
    CalibrationAnalyzer: Analyzer for computing calibration metrics.
    CalibrationResult: Structured results from calibration analysis.

Functions:
    temperature_scale: Apply temperature scaling for calibration.
    find_optimal_temperature: Find optimal temperature via grid search.

Example:
    >>> from thulium.evaluation import CalibrationAnalyzer
    >>> analyzer = CalibrationAnalyzer(num_bins=10)
    >>> result = analyzer.analyze(confidences, correct)
    >>> print(f"ECE: {result.ece:.4f}, MCE: {result.mce:.4f}")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CalibrationResult:
    """Results from calibration analysis.

    Attributes:
        ece: Expected Calibration Error in [0, 1].
        mce: Maximum Calibration Error in [0, 1].
        brier_score: Brier score in [0, 1].
        bin_confidences: Average confidence per bin.
        bin_accuracies: Average accuracy per bin.
        bin_counts: Number of samples per bin.
    """

    ece: float
    mce: float
    brier_score: float
    bin_confidences: List[float]
    bin_accuracies: List[float]
    bin_counts: List[int]


class CalibrationAnalyzer:
    """Analyzer for model calibration metrics.

    Calibration measures how well predicted confidences match actual
    accuracy. A perfectly calibrated model has Pr(correct | confidence=p) = p.

    Mathematical Formulation:
        Expected Calibration Error (ECE):
            ECE = sum_{m=1}^{M} (|B_m|/n) * |acc(B_m) - conf(B_m)|

        where:
            - M is the number of bins
            - B_m is the set of samples in bin m
            - acc(B_m) is the average accuracy in bin m
            - conf(B_m) is the average confidence in bin m

        Maximum Calibration Error (MCE):
            MCE = max_m |acc(B_m) - conf(B_m)|

    Attributes:
        num_bins: Number of bins for binned calibration metrics.
        strategy: Binning strategy ('uniform' or 'quantile').

    Example:
        >>> analyzer = CalibrationAnalyzer(num_bins=15, strategy="uniform")
        >>> result = analyzer.analyze(confidences, correct)
        >>> print(f"ECE: {result.ece:.4f}")
    """

    def __init__(
        self,
        num_bins: int = 10,
        strategy: str = "uniform",
    ) -> None:
        """Initialize calibration analyzer.

        Args:
            num_bins: Number of bins for ECE/MCE computation. More bins
                provide finer-grained analysis but require more samples.
            strategy: Binning strategy:
                - 'uniform': Equal-width bins (default).
                - 'quantile': Equal-count bins (adaptive widths).
        """
        self.num_bins = num_bins
        self.strategy = strategy

    def compute_ece(
        self,
        confidences: np.ndarray,
        correct: np.ndarray,
    ) -> float:
        """Compute Expected Calibration Error.

        Args:
            confidences: Array of confidence scores in [0, 1].
            correct: Binary array indicating correct predictions.

        Returns:
            ECE value in [0, 1]. Lower is better.
        """
        if len(confidences) == 0:
            return 0.0

        bins = self._get_bins(confidences)
        ece = 0.0
        n = len(confidences)

        for bin_lower, bin_upper in bins:
            mask = (confidences > bin_lower) & (confidences <= bin_upper)
            if mask.sum() == 0:
                continue

            bin_conf = confidences[mask].mean()
            bin_acc = correct[mask].mean()
            bin_size = mask.sum()

            ece += (bin_size / n) * abs(bin_acc - bin_conf)

        return float(ece)

    def compute_mce(
        self,
        confidences: np.ndarray,
        correct: np.ndarray,
    ) -> float:
        """Compute Maximum Calibration Error.

        Args:
            confidences: Array of confidence scores.
            correct: Binary array indicating correct predictions.

        Returns:
            MCE value in [0, 1]. Lower is better.
        """
        if len(confidences) == 0:
            return 0.0

        bins = self._get_bins(confidences)
        mce = 0.0

        for bin_lower, bin_upper in bins:
            mask = (confidences > bin_lower) & (confidences <= bin_upper)
            if mask.sum() == 0:
                continue

            bin_conf = confidences[mask].mean()
            bin_acc = correct[mask].mean()

            mce = max(mce, abs(bin_acc - bin_conf))

        return float(mce)

    def compute_brier_score(
        self,
        confidences: np.ndarray,
        correct: np.ndarray,
    ) -> float:
        """Compute Brier Score.

        Brier Score measures the mean squared difference between
        predicted probability and actual outcome.

        Args:
            confidences: Array of confidence scores.
            correct: Binary array indicating correct predictions.

        Returns:
            Brier score in [0, 1]. Lower is better.
        """
        if len(confidences) == 0:
            return 0.0

        return float(np.mean((confidences - correct) ** 2))

    def analyze(
        self,
        confidences: np.ndarray,
        correct: np.ndarray,
    ) -> CalibrationResult:
        """Perform full calibration analysis.

        Args:
            confidences: Array of confidence scores.
            correct: Binary array indicating correct predictions.

        Returns:
            CalibrationResult with all metrics and binned data.
        """
        confidences = np.asarray(confidences).flatten()
        correct = np.asarray(correct).flatten()

        bins = self._get_bins(confidences)

        bin_confidences = []
        bin_accuracies = []
        bin_counts = []

        for bin_lower, bin_upper in bins:
            mask = (confidences > bin_lower) & (confidences <= bin_upper)
            count = mask.sum()

            if count > 0:
                bin_confidences.append(float(confidences[mask].mean()))
                bin_accuracies.append(float(correct[mask].mean()))
            else:
                bin_confidences.append((bin_lower + bin_upper) / 2)
                bin_accuracies.append(0.0)
            bin_counts.append(int(count))

        return CalibrationResult(
            ece=self.compute_ece(confidences, correct),
            mce=self.compute_mce(confidences, correct),
            brier_score=self.compute_brier_score(confidences, correct),
            bin_confidences=bin_confidences,
            bin_accuracies=bin_accuracies,
            bin_counts=bin_counts,
        )

    def _get_bins(
        self,
        confidences: np.ndarray,
    ) -> List[Tuple[float, float]]:
        """Get bin boundaries based on strategy.

        Args:
            confidences: Array of confidence scores.

        Returns:
            List of (lower, upper) tuples for each bin.
        """
        if self.strategy == "uniform":
            edges = np.linspace(0, 1, self.num_bins + 1)
        else:  # quantile
            edges = np.percentile(
                confidences,
                np.linspace(0, 100, self.num_bins + 1),
            )

        return [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]

    def reliability_diagram_data(
        self,
        result: CalibrationResult,
    ) -> Dict[str, List[float]]:
        """Get data for plotting a reliability diagram.

        Args:
            result: CalibrationResult from analyze().

        Returns:
            Dictionary with 'confidences', 'accuracies', 'counts' lists.
        """
        return {
            "confidences": result.bin_confidences,
            "accuracies": result.bin_accuracies,
            "counts": result.bin_counts,
        }


def temperature_scale(
    logits: np.ndarray,
    temperature: float = 1.0,
) -> np.ndarray:
    """Apply temperature scaling to logits.

    Temperature scaling is a post-hoc calibration method:
        p'(y) = softmax(z / T)

    where T > 1 produces "softer" (less confident) predictions.

    Args:
        logits: Raw logit scores with shape (..., num_classes).
        temperature: Temperature parameter. T > 1 reduces confidence,
            T < 1 increases confidence.

    Returns:
        Calibrated probability distribution.

    Raises:
        ValueError: If temperature is not positive.
    """
    if temperature <= 0:
        raise ValueError("Temperature must be positive")

    scaled = logits / temperature
    exp_scaled = np.exp(scaled - np.max(scaled, axis=-1, keepdims=True))
    return exp_scaled / exp_scaled.sum(axis=-1, keepdims=True)


def find_optimal_temperature(
    logits: np.ndarray,
    labels: np.ndarray,
    range_t: Tuple[float, float] = (0.5, 5.0),
    num_steps: int = 50,
) -> float:
    """Find optimal temperature for calibration.

    Searches for temperature that minimizes NLL on validation set.

    Args:
        logits: Raw logits from model with shape (N, num_classes).
        labels: Ground truth labels with shape (N,).
        range_t: Temperature search range (min, max).
        num_steps: Number of temperatures to try.

    Returns:
        Optimal temperature value.
    """
    best_t = 1.0
    best_nll = float("inf")

    for t in np.linspace(range_t[0], range_t[1], num_steps):
        probs = temperature_scale(logits, t)
        nll = -np.mean(np.log(probs[np.arange(len(labels)), labels] + 1e-10))

        if nll < best_nll:
            best_nll = nll
            best_t = t

    return float(best_t)


__all__ = [
    "CalibrationAnalyzer",
    "CalibrationResult",
    "find_optimal_temperature",
    "temperature_scale",
]
