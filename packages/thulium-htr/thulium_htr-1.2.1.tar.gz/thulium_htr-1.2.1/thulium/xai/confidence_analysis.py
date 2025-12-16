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

"""Confidence analysis tools for HTR model calibration.

This module provides tools for analyzing model confidence and calibration,
including Expected Calibration Error (ECE) and reliability diagrams.

Classes:
    ConfidenceAnalyzer: Compute ECE, MCE, and reliability diagram data.

Example:
    >>> from thulium.xai.confidence_analysis import ConfidenceAnalyzer
    >>> ece = ConfidenceAnalyzer.compute_ece(probs, labels)
"""

from __future__ import annotations

import logging
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import numpy as np
import torch

logger = logging.getLogger(__name__)

class ConfidenceAnalyzer:
    """
    Tools for analyzing model confidence and calibration.
    
    Metrics:
    - ECE (Expected Calibration Error)
    - MCE (Maximum Calibration Error)
    - Reliability Diagram Data
    """
    
    @staticmethod
    def compute_ece(probs: np.ndarray, labels: np.ndarray, n_bins: int = 10) -> float:
        """
        Computes Expected Calibration Error (ECE).
        
        Formula:
        ECE = sum( (B_m / N) * | acc(B_m) - conf(B_m) | )
        Where B_m is the m-th bin.
        
        Args:
            probs: Predicted probabilities for the predicted class [N]
            labels: True binary correction (1 if correct, 0 if wrong) [N]
            n_bins: Number of bins for calibration
        """
        if len(probs) != len(labels):
            raise ValueError("Probs and labels must have same length")
            
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        n_total = len(probs)
        
        for i in range(n_bins):
            # Bin mask
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i+1]
            in_bin = (probs > bin_lower) & (probs <= bin_upper)
            prop_in_bin = np.mean(in_bin)
            
            if prop_in_bin > 0:
                accuracy_in_bin = np.mean(labels[in_bin])
                avg_confidence_in_bin = np.mean(probs[in_bin])
                ece += np.abs(accuracy_in_bin - avg_confidence_in_bin) * prop_in_bin
                
        return ece

    @staticmethod
    def compute_reliability_diagram(probs: np.ndarray, labels: np.ndarray, n_bins: int = 10) -> Dict[str, List[float]]:
        """
        Generates data for plotting a Reliability Diagram.
        
        Returns:
            Dict with 'accuracies', 'confidences', 'counts' per bin.
        """
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        accuracies = []
        confidences = []
        counts = []
        
        for i in range(n_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i+1]
            in_bin = (probs > bin_lower) & (probs <= bin_upper)
            
            count = np.sum(in_bin)
            counts.append(int(count))
            
            if count > 0:
                accuracies.append(float(np.mean(labels[in_bin])))
                confidences.append(float(np.mean(probs[in_bin])))
            else:
                accuracies.append(0.0)
                confidences.append(0.0)
                
        return {
            "accuracies": accuracies,
            "confidences": confidences,
            "counts": counts,
            "bins": bin_boundaries.tolist()
        }

    @staticmethod
    def Sequence_confidence(log_probs: torch.Tensor, pad_idx: int = 0) -> List[float]:
        """
        Computes sequence-level confidence scores (e.g., average log-prob or min probability).
        
        Args:
            log_probs: [T, B, C]
        """
        # Softmax to get probs
        probs = torch.softmax(log_probs, dim=-1)
        max_probs, _ = torch.max(probs, dim=-1) # [T, B]
        
        # Simple average confidence per sequence (ignoring masking for simplicity in v1.1.0 MVP)
        # Ideally, mask by sequence length.
        seq_confs = torch.mean(max_probs, dim=0).cpu().tolist()
        return seq_confs
