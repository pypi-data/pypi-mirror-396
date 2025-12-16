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

"""Evaluation metrics and benchmarking utilities for Thulium HTR.

This module provides comprehensive evaluation capabilities for handwriting
recognition models, including standard accuracy metrics, calibration analysis,
robustness testing, and benchmark reporting.

Submodules:
    metrics: Standard recognition metrics including Character Error Rate (CER),
        Word Error Rate (WER), and Sequence Error Rate (SER).
    calibration: Expected Calibration Error (ECE) analysis and temperature
        scaling for confidence calibration.
    robustness: Perturbation testing, noise sensitivity analysis, and
        degradation curves for model robustness evaluation.
    benchmarking: Benchmark runner for systematic evaluation across multiple
        datasets and configurations.
    reporting: Report generation in multiple formats (JSON, HTML, LaTeX)
        with automatic visualization.

Classes:
    CalibrationAnalyzer: Analyzes model confidence calibration.
    CalibrationResult: Structured calibration analysis results.
    RobustnessEvaluator: Evaluates model robustness to input perturbations.
    RobustnessResult: Structured robustness evaluation results.

Functions:
    cer: Compute Character Error Rate between two strings.
    wer: Compute Word Error Rate between two strings.
    ser: Compute Sequence Error Rate (exact match indicator).
    cer_wer_batch: Compute CER and WER for a batch of samples.
    edit_distance: Compute Levenshtein edit distance.

Example:
    Computing recognition metrics:

    >>> from thulium.evaluation import cer, wer, cer_wer_batch
    >>> error = cer("hello world", "helo world")
    >>> print(f"CER: {error:.2%}")
    'CER: 10.00%'

    >>> # Batch evaluation
    >>> references = ["hello", "world"]
    >>> hypotheses = ["helo", "word"]
    >>> c, w = cer_wer_batch(references, hypotheses)
    >>> print(f"CER: {c:.2%}, WER: {w:.2%}")

    Calibration analysis:

    >>> from thulium.evaluation import CalibrationAnalyzer
    >>> analyzer = CalibrationAnalyzer(num_bins=10)
    >>> result = analyzer.analyze(confidences, accuracies)
    >>> print(f"ECE: {result.ece:.4f}")
"""

from __future__ import annotations

from thulium.evaluation.calibration import CalibrationAnalyzer
from thulium.evaluation.calibration import CalibrationResult
from thulium.evaluation.metrics import cer
from thulium.evaluation.metrics import cer_wer_batch
from thulium.evaluation.metrics import edit_distance
from thulium.evaluation.metrics import ser
from thulium.evaluation.metrics import wer
from thulium.evaluation.robustness import RobustnessEvaluator
from thulium.evaluation.robustness import RobustnessResult

__all__ = [
    # Calibration
    "CalibrationAnalyzer",
    "CalibrationResult",
    # Metrics
    "cer",
    "cer_wer_batch",
    "edit_distance",
    "ser",
    "wer",
    # Robustness
    "RobustnessEvaluator",
    "RobustnessResult",
]
