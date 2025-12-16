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

"""Early stopping utility for training with patience-based stopping.

This module provides a flexible early stopping implementation that monitors
validation metrics and stops training when no improvement is observed.

Mathematical Formulation:
    
    Let m_t be the validation metric at epoch t. Define the best metric as:
    
        m* = min(m_1, m_2, ..., m_t)  for minimization
        m* = max(m_1, m_2, ..., m_t)  for maximization
    
    Training stops when:
    
        t - t* > patience
    
    where t* is the epoch at which m* was achieved.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from dataclasses import field
from typing import Literal
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class EarlyStoppingConfig:
    """Configuration for early stopping.
    
    Attributes:
        patience: Number of epochs to wait for improvement before stopping.
        min_delta: Minimum change in monitored metric to qualify as improvement.
        metric: Name of the metric to monitor (e.g., 'val_cer', 'val_loss').
        mode: Whether to minimize ('min') or maximize ('max') the metric.
        restore_best: Whether to restore model weights from best epoch.
        verbose: Whether to log early stopping status messages.
    """
    patience: int = 10
    min_delta: float = 0.0
    metric: str = "val_cer"
    mode: Literal["min", "max"] = "min"
    restore_best: bool = True
    verbose: bool = True


class EarlyStopping:
    """
    Early stopping to terminate training when validation metric stops improving.
    
    This implementation supports both minimization and maximization objectives,
    configurable patience, and optional model weight restoration.
    
    Example:
        >>> early_stopping = EarlyStopping(patience=10, metric="val_cer", mode="min")
        >>> for epoch in range(100):
        ...     metrics = trainer.validate(val_loader)
        ...     if early_stopping(metrics, model):
        ...         print(f"Stopping at epoch {epoch}")
        ...         break
        >>> # Restore best weights
        >>> early_stopping.restore_best_weights(model)
    
    Attributes:
        patience: Number of epochs without improvement before stopping.
        min_delta: Minimum improvement threshold.
        metric: Metric name to monitor.
        mode: 'min' or 'max' for minimization or maximization.
    """
    
    def __init__(
        self,
        patience: int = 10,
        min_delta: float = 0.0,
        metric: str = "val_cer",
        mode: str = "min",
        restore_best: bool = True,
        verbose: bool = True,
    ):
        """Initialize early stopping.
        
        Args:
            patience: Number of epochs to wait for improvement.
            min_delta: Minimum change to qualify as improvement.
            metric: Name of metric to monitor.
            mode: 'min' or 'max' for minimization or maximization.
            restore_best: Whether to save and restore best weights.
            verbose: Whether to log status messages.
        """
        self.patience = patience
        self.min_delta = min_delta
        self.metric = metric
        self.mode = mode
        self.restore_best = restore_best
        self.verbose = verbose
        
        self.best_score: Optional[float] = None
        self.best_epoch: int = 0
        self.counter: int = 0
        self.best_weights: Optional[dict] = None
        self.stopped_epoch: int = 0
        
        # Set comparison function based on mode
        if mode == "min":
            self.is_better = lambda current, best: current < best - min_delta
            self.best_score = float("inf")
        else:
            self.is_better = lambda current, best: current > best + min_delta
            self.best_score = float("-inf")
    
    def __call__(self, metrics: dict, model=None, epoch: int = 0) -> bool:
        """Check if training should stop.
        
        Args:
            metrics: Dictionary containing the monitored metric.
            model: Optional model to save best weights from.
            epoch: Current epoch number for logging.
            
        Returns:
            True if training should stop, False otherwise.
        """
        score = metrics.get(self.metric)
        
        if score is None:
            logger.warning(f"Metric '{self.metric}' not found in metrics. Skipping early stopping check.")
            return False
        
        if math.isnan(score) or math.isinf(score):
            logger.warning(f"Metric '{self.metric}' is NaN or Inf. Considering as no improvement.")
            self.counter += 1
        elif self.is_better(score, self.best_score):
            # Improvement detected
            if self.verbose:
                improvement = self.best_score - score if self.mode == "min" else score - self.best_score
                logger.info(
                    f"EarlyStopping: {self.metric} improved from {self.best_score:.6f} to {score:.6f} "
                    f"(delta: {improvement:.6f})"
                )
            
            self.best_score = score
            self.best_epoch = epoch
            self.counter = 0
            
            # Save best weights
            if self.restore_best and model is not None:
                self.best_weights = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            # No improvement
            self.counter += 1
            if self.verbose:
                logger.info(
                    f"EarlyStopping: No improvement in {self.metric}. "
                    f"Best: {self.best_score:.6f}, Current: {score:.6f}. "
                    f"Patience: {self.counter}/{self.patience}"
                )
        
        # Check if we should stop
        if self.counter >= self.patience:
            self.stopped_epoch = epoch
            if self.verbose:
                logger.info(
                    f"EarlyStopping: Stopping training. No improvement for {self.patience} epochs. "
                    f"Best {self.metric}: {self.best_score:.6f} at epoch {self.best_epoch}"
                )
            return True
        
        return False
    
    def restore_best_weights(self, model) -> bool:
        """Restore model weights from the best epoch.
        
        Args:
            model: PyTorch model to restore weights to.
            
        Returns:
            True if weights were restored, False if no best weights saved.
        """
        if self.best_weights is not None:
            model.load_state_dict(self.best_weights)
            logger.info(f"Restored best model weights from epoch {self.best_epoch}")
            return True
        else:
            logger.warning("No best weights saved. Cannot restore.")
            return False
    
    def reset(self):
        """Reset early stopping state for a new training run."""
        if self.mode == "min":
            self.best_score = float("inf")
        else:
            self.best_score = float("-inf")
        self.best_epoch = 0
        self.counter = 0
        self.best_weights = None
        self.stopped_epoch = 0
    
    @property
    def should_stop(self) -> bool:
        """Check if training should stop based on current state."""
        return self.counter >= self.patience
    
    @classmethod
    def from_config(cls, config: EarlyStoppingConfig) -> "EarlyStopping":
        """Create EarlyStopping instance from configuration object.
        
        Args:
            config: EarlyStoppingConfig with settings.
            
        Returns:
            Configured EarlyStopping instance.
        """
        return cls(
            patience=config.patience,
            min_delta=config.min_delta,
            metric=config.metric,
            mode=config.mode,
            restore_best=config.restore_best,
            verbose=config.verbose,
        )
