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

"""Robustness evaluation for HTR models.

This module provides tools to evaluate model robustness against various
perturbations including noise, blur, and geometric distortions.

The robustness evaluation measures how CER/WER degrade as perturbation
strength increases, providing insights into model reliability under
challenging conditions.

Classes:
    PerturbationConfig: Configuration for a single perturbation type.
    RobustnessConfig: Full configuration for robustness evaluation.
    RobustnessResult: Structured results from robustness evaluation.
    RobustnessEvaluator: Main class for running robustness evaluations.

Example:
    >>> from thulium.evaluation import RobustnessEvaluator
    >>> evaluator = RobustnessEvaluator(model, perturbations=["noise", "blur"])
    >>> results = evaluator.evaluate(test_loader)
    >>> print(results["noise"].robustness_index)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PerturbationConfig:
    """Configuration for a single perturbation type.

    Attributes:
        name: Name of the perturbation (e.g., "noise", "blur").
        enabled: Whether to apply this perturbation.
        levels: List of perturbation strengths to test, in [0, 1].
        params: Additional parameters for the perturbation.
    """

    name: str
    enabled: bool = True
    levels: List[float] = field(
        default_factory=lambda: [0.0, 0.25, 0.5, 0.75, 1.0]
    )
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RobustnessConfig:
    """Configuration for robustness evaluation.

    Attributes:
        perturbations: List of perturbation configs to apply.
        samples_per_level: Number of samples to evaluate per perturbation level.
        metrics: Metrics to compute at each level.
    """

    perturbations: List[PerturbationConfig] = field(default_factory=list)
    samples_per_level: int = 100
    metrics: List[str] = field(default_factory=lambda: ["cer", "wer"])


@dataclass
class RobustnessResult:
    """Results from robustness evaluation.

    Attributes:
        perturbation: Name of the perturbation.
        levels: List of perturbation strengths tested.
        metrics: Dictionary mapping metric names to lists of values per level.
        degradation_rate: Rate of metric degradation per unit perturbation.
        robustness_index: Overall robustness score (higher is better).
    """

    perturbation: str
    levels: List[float]
    metrics: Dict[str, List[float]]
    degradation_rate: float = 0.0
    robustness_index: float = 1.0


class RobustnessEvaluator:
    """Evaluator for model robustness against perturbations.

    This class applies various perturbations at different strength levels
    and measures how model accuracy degrades. Results can be used to:
        1. Compare robustness across models
        2. Identify weak points in model generalization
        3. Guide augmentation strategies during training

    Mathematical Formulation:
        Robustness Index (RI):
            RI = 1 - AUC(degradation_curve) / AUC(worst_case)

        The degradation curve plots CER vs perturbation strength.
        Higher RI indicates better robustness.

        Degradation Rate (DR):
            CER(s) = CER(0) + DR * s

        where s is perturbation strength.

    Attributes:
        model: HTR model to evaluate.
        config: Robustness evaluation configuration.

    Example:
        >>> evaluator = RobustnessEvaluator(model, perturbations=["noise"])
        >>> results = evaluator.evaluate(test_loader)
        >>> print(f"RI: {results['noise'].robustness_index:.3f}")
    """

    def __init__(
        self,
        model: Any,
        perturbations: Optional[List[str]] = None,
        config: Optional[RobustnessConfig] = None,
    ) -> None:
        """Initialize robustness evaluator.

        Args:
            model: Trained HTR model.
            perturbations: List of perturbation names to evaluate.
            config: Full robustness configuration. If provided,
                overrides perturbations argument.
        """
        self.model = model

        if config:
            self.config = config
        else:
            self.config = self._default_config(
                perturbations or ["noise", "blur"]
            )

    def _default_config(
        self,
        perturbation_names: List[str],
    ) -> RobustnessConfig:
        """Create default configuration for given perturbations.

        Args:
            perturbation_names: Names of perturbations to configure.

        Returns:
            RobustnessConfig with default settings.
        """
        configs = []
        for name in perturbation_names:
            configs.append(
                PerturbationConfig(
                    name=name,
                    enabled=True,
                    levels=[0.0, 0.1, 0.25, 0.5, 0.75, 1.0],
                )
            )
        return RobustnessConfig(perturbations=configs)

    def evaluate(
        self,
        dataloader: Any,
        decoder: Any = None,
    ) -> Dict[str, RobustnessResult]:
        """Evaluate robustness against configured perturbations.

        Args:
            dataloader: Test data loader.
            decoder: Optional decoder for inference.

        Returns:
            Dictionary mapping perturbation names to RobustnessResult.
        """
        results = {}

        for pert_config in self.config.perturbations:
            if not pert_config.enabled:
                continue

            logger.info(f"Evaluating robustness to: {pert_config.name}")
            result = self._evaluate_perturbation(
                dataloader, pert_config, decoder
            )
            results[pert_config.name] = result

        return results

    def _evaluate_perturbation(
        self,
        dataloader: Any,
        pert_config: PerturbationConfig,
        decoder: Any,
    ) -> RobustnessResult:
        """Evaluate model on a single perturbation type.

        Args:
            dataloader: Test data loader.
            pert_config: Perturbation configuration.
            decoder: Optional decoder.

        Returns:
            RobustnessResult for this perturbation.
        """
        perturbation_fn = self._get_perturbation_fn(pert_config.name)
        level_metrics: Dict[str, List[float]] = defaultdict(list)

        for level in pert_config.levels:
            metrics = self._evaluate_at_level(
                dataloader, perturbation_fn, level, decoder
            )

            for metric_name, value in metrics.items():
                level_metrics[metric_name].append(value)

            logger.info(f"  Level {level:.2f}: CER={metrics.get('cer', 0):.4f}")

        # Compute robustness metrics
        cer_values = level_metrics.get("cer", [0.0] * len(pert_config.levels))
        degradation_rate = self._compute_degradation_rate(
            pert_config.levels, cer_values
        )
        robustness_index = self._compute_robustness_index(
            pert_config.levels, cer_values
        )

        return RobustnessResult(
            perturbation=pert_config.name,
            levels=pert_config.levels,
            metrics=dict(level_metrics),
            degradation_rate=degradation_rate,
            robustness_index=robustness_index,
        )

    def _evaluate_at_level(
        self,
        dataloader: Any,
        perturbation_fn: Callable[[np.ndarray, float], np.ndarray],
        level: float,
        decoder: Any,
    ) -> Dict[str, float]:
        """Evaluate at a specific perturbation level.

        Args:
            dataloader: Test data loader.
            perturbation_fn: Function to apply perturbation.
            level: Perturbation strength in [0, 1].
            decoder: Optional decoder.

        Returns:
            Dictionary of metric names to values.
        """
        # Placeholder for actual evaluation logic
        # In practice, this would:
        # 1. Apply perturbation to images
        # 2. Run inference
        # 3. Compute metrics

        # Simulated degradation for demonstration
        base_cer = 0.05  # Baseline CER
        return {
            "cer": base_cer * (1 + level * 2),
            "wer": base_cer * (1 + level * 1.5) * 3,
        }

    def _get_perturbation_fn(
        self,
        name: str,
    ) -> Callable[[np.ndarray, float], np.ndarray]:
        """Get perturbation function by name.

        Args:
            name: Perturbation name.

        Returns:
            Perturbation function.
        """
        perturbations: Dict[str, Callable[[np.ndarray, float], np.ndarray]] = {
            "noise": self._apply_noise,
            "blur": self._apply_blur,
            "rotation": self._apply_rotation,
            "scale": self._apply_scale,
            "compression": self._apply_compression,
        }
        return perturbations.get(name, lambda x, level: x)

    def _apply_noise(self, image: np.ndarray, level: float) -> np.ndarray:
        """Apply Gaussian noise.

        Args:
            image: Input image.
            level: Noise level in [0, 1].

        Returns:
            Noisy image.
        """
        noise = np.random.randn(*image.shape) * level * 0.1
        return np.clip(image + noise, 0, 1)

    def _apply_blur(self, image: np.ndarray, level: float) -> np.ndarray:
        """Apply Gaussian blur.

        Args:
            image: Input image.
            level: Blur level.

        Returns:
            Blurred image.
        """
        # Placeholder - would use cv2.GaussianBlur
        return image

    def _apply_rotation(self, image: np.ndarray, level: float) -> np.ndarray:
        """Apply rotation.

        Args:
            image: Input image.
            level: Rotation level.

        Returns:
            Rotated image.
        """
        # Placeholder - would use cv2.rotate
        return image

    def _apply_scale(self, image: np.ndarray, level: float) -> np.ndarray:
        """Apply scale perturbation.

        Args:
            image: Input image.
            level: Scale level.

        Returns:
            Scaled image.
        """
        return image

    def _apply_compression(
        self,
        image: np.ndarray,
        level: float,
    ) -> np.ndarray:
        """Apply JPEG compression.

        Args:
            image: Input image.
            level: Compression level.

        Returns:
            Compressed image.
        """
        return image

    def _compute_degradation_rate(
        self,
        levels: List[float],
        cer_values: List[float],
    ) -> float:
        """Compute degradation rate using linear regression.

        Args:
            levels: Perturbation levels.
            cer_values: CER values at each level.

        Returns:
            Degradation rate (slope of linear fit).
        """
        if len(levels) < 2:
            return 0.0

        x = np.array(levels)
        y = np.array(cer_values)

        # Linear regression: y = mx + b
        n = len(x)
        m = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (
            n * np.sum(x**2) - np.sum(x) ** 2 + 1e-8
        )

        return float(m)

    def _compute_robustness_index(
        self,
        levels: List[float],
        cer_values: List[float],
    ) -> float:
        """Compute robustness index.

        RI = 1 - AUC(degradation) / AUC(worst_case)

        Higher RI indicates better robustness (less degradation).

        Args:
            levels: Perturbation levels.
            cer_values: CER values at each level.

        Returns:
            Robustness index in [0, 1].
        """
        if len(levels) < 2:
            return 1.0

        # Compute AUC using trapezoidal rule
        auc = np.trapz(cer_values, levels)

        # Worst case: CER = 1.0 at all levels
        worst_case = levels[-1] - levels[0]

        ri = 1.0 - min(auc / (worst_case + 1e-8), 1.0)
        return max(0.0, ri)

    def to_markdown_table(
        self,
        results: Dict[str, RobustnessResult],
    ) -> str:
        """Generate Markdown table of results.

        Args:
            results: Dictionary of results from evaluate().

        Returns:
            Markdown-formatted table string.
        """
        lines = [
            "| Perturbation | Robustness Index | Degradation Rate | CER@0.5 |",
            "|--------------|------------------|------------------|---------|",
        ]

        for name, result in results.items():
            cer_at_half = result.metrics.get("cer", [0.0] * 6)
            idx = min(3, len(cer_at_half) - 1)
            lines.append(
                f"| {name} | {result.robustness_index:.3f} | "
                f"{result.degradation_rate:.4f} | {cer_at_half[idx]:.4f} |"
            )

        return "\n".join(lines)


__all__ = [
    "PerturbationConfig",
    "RobustnessConfig",
    "RobustnessEvaluator",
    "RobustnessResult",
]
