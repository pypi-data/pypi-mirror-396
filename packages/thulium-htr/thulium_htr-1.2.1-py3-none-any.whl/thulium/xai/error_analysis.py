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

"""Error analysis tools for HTR model evaluation.

This module provides tools for analyzing recognition errors, including
character-level confusion matrices, top-k error analysis, and aggregate
CER/WER/SER metrics.

Classes:
    ErrorAnalyzer: Tools for detailed error analysis.

Example:
    >>> from thulium.xai.error_analysis import ErrorAnalyzer
    >>> errors = ErrorAnalyzer.analyze_top_k_errors(predictions, ground_truth)
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import numpy as np

logger = logging.getLogger(__name__)


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]


def _word_levenshtein_distance(s1: List[str], s2: List[str]) -> int:
    """Compute Levenshtein distance between two word lists."""
    if len(s1) < len(s2):
        return _word_levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev_row = range(len(s2) + 1)
    for i, w1 in enumerate(s1):
        curr_row = [i + 1]
        for j, w2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (w1 != w2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]

class ErrorAnalyzer:
    """
    Tools for analyzing recognition errors.
    
    Features:
    - Character-level confusion matrix
    - Top-k most frequent errors (Word level)
    - CER/WER breakdown
    """
    
    @staticmethod
    def compute_confusion_matrix(
        predictions: List[str], 
        ground_truth: List[str],
        vocab: List[str] = None
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Computes character-level confusion matrix.
        Note: Requires alignment (e.g. Levinshtein backtrace) for accurate char-to-char mapping.
        For v1.1.0 MVP, we assume simple naive alignment or just counting discrepancies 
        if lengths match, OR we rely on global character counts in errors.
        
        Ideally, we use `edlib` or similar for alignment. 
        Here we implement a simplified heuristic:
        Only analyze samples with equal length for matrix, or skip matrix in favor of Top-K Errors for general case.
        """
        # Placeholder for full alignment-based confusion matrix.
        # This is a complex topic. 
        # For now, we return empty matrix and log warning if comprehensive alignment lib missing.
        logger.warning("Full alignment-based confusion matrix requires alignment library. Returning empty.")
        return np.zeros((1,1)), []

    @staticmethod
    def analyze_top_k_errors(
        predictions: List[str],
        ground_truth: List[str],
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Identifies the most frequent word-level errors.
        
        Returns:
            List of dicts: {'gt': str, 'pred': str, 'count': int, 'cer': float}
        """
        error_counts = Counter()
        
        for pred, gt in zip(predictions, ground_truth):
            if pred != gt:
                error_counts[(gt, pred)] += 1
                
        most_common = error_counts.most_common(k)
        
        results = []
        for (gt, pred), count in most_common:
            dist = _levenshtein_distance(gt, pred)
            cer = dist / len(gt) if len(gt) > 0 else 1.0
            results.append({
                "ground_truth": gt,
                "prediction": pred,
                "count": count,
                "cer": cer
            })
            
        return results

    @staticmethod
    def summarize_metrics(
        predictions: List[str],
        ground_truth: List[str]
    ) -> Dict[str, float]:
        """
        Computes aggregate CER/WER/SER.
        """
        total_edit_dist = 0
        total_chars = 0
        total_words = 0
        total_word_edit_dist = 0
        errors = 0
        
        for pred, gt in zip(predictions, ground_truth):
            # CER
            dist = _levenshtein_distance(pred, gt)
            total_edit_dist += dist
            total_chars += len(gt)
            
            # SER
            if pred != gt:
                errors += 1
                
            # WER (Simple whitespace tokenization)
            pred_words = pred.split()
            gt_words = gt.split()
            total_word_edit_dist += _word_levenshtein_distance(pred_words, gt_words)
            total_words += len(gt_words)
            
        cer = total_edit_dist / total_chars if total_chars > 0 else 0.0
        wer = total_word_edit_dist / total_words if total_words > 0 else 0.0
        ser = errors / len(ground_truth) if len(ground_truth) > 0 else 0.0
        
        return {
            "CER": cer,
            "WER": wer,
            "SER": ser
        }
