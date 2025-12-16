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

"""Checkpoint management utilities for model training.

This module provides comprehensive checkpointing functionality including:
- Best model tracking based on validation metrics
- Periodic checkpoint saving
- Checkpoint rotation (keeping only N recent)
- Training state resumption
- Checkpoint metadata and versioning

Example:
    >>> manager = CheckpointManager(
    ...     save_dir="checkpoints/experiment_1",
    ...     save_best=True,
    ...     best_metric="val_cer",
    ...     keep_last=3
    ... )
    >>> for epoch in range(100):
    ...     metrics = trainer.validate(val_loader)
    ...     manager.save(model, optimizer, scheduler, epoch, metrics)
    >>> # Resume training
    >>> state = manager.load_latest(model, optimizer, scheduler)
"""
from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional

import torch
import torch.nn as nn
import torch.optim as optim

logger = logging.getLogger(__name__)


@dataclass
class CheckpointConfig:
    """Configuration for checkpoint management.
    
    Attributes:
        save_dir: Directory to save checkpoints.
        save_every: Save checkpoint every N epochs.
        keep_last: Number of recent checkpoints to keep (0 for unlimited).
        save_best: Whether to save best model based on metric.
        best_metric: Metric name for best model tracking.
        best_mode: 'min' or 'max' for metric optimization direction.
        save_optimizer: Whether to include optimizer state.
        save_scheduler: Whether to include scheduler state.
    """
    save_dir: str = "checkpoints"
    save_every: int = 5
    keep_last: int = 3
    save_best: bool = True
    best_metric: str = "val_cer"
    best_mode: Literal["min", "max"] = "min"
    save_optimizer: bool = True
    save_scheduler: bool = True


class CheckpointManager:
    """
    Comprehensive checkpoint management for model training.
    
    Handles saving, loading, and rotation of training checkpoints with
    support for best model tracking and training resumption.
    
    Attributes:
        save_dir: Path to checkpoint directory.
        save_every: Epoch interval for saving.
        keep_last: Number of checkpoints to retain.
        save_best: Whether to track best model.
        best_metric: Metric for best model selection.
        best_mode: Optimization direction ('min' or 'max').
    """
    
    def __init__(
        self,
        save_dir: str = "checkpoints",
        save_every: int = 5,
        keep_last: int = 3,
        save_best: bool = True,
        best_metric: str = "val_cer",
        best_mode: str = "min",
        save_optimizer: bool = True,
        save_scheduler: bool = True,
    ):
        """Initialize checkpoint manager.
        
        Args:
            save_dir: Directory for saving checkpoints.
            save_every: Save checkpoint every N epochs.
            keep_last: Keep only the last N checkpoints (0 for unlimited).
            save_best: Whether to save the best model separately.
            best_metric: Metric name for best model tracking.
            best_mode: 'min' or 'max' for metric optimization.
            save_optimizer: Include optimizer state in checkpoints.
            save_scheduler: Include scheduler state in checkpoints.
        """
        self.save_dir = Path(save_dir)
        self.save_every = save_every
        self.keep_last = keep_last
        self.save_best = save_best
        self.best_metric = best_metric
        self.best_mode = best_mode
        self.save_optimizer = save_optimizer
        self.save_scheduler = save_scheduler
        
        # Create directory
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Best model tracking
        self.best_score = float("inf") if best_mode == "min" else float("-inf")
        self.best_epoch = -1
        
        # Checkpoint history
        self._checkpoint_files: List[Path] = []
        
        # Load existing checkpoints
        self._scan_existing_checkpoints()
        
        logger.info(f"CheckpointManager initialized. Save dir: {self.save_dir}")
    
    def _scan_existing_checkpoints(self):
        """Scan save directory for existing checkpoints."""
        pattern = "checkpoint_epoch_*.pt"
        self._checkpoint_files = sorted(
            self.save_dir.glob(pattern),
            key=lambda p: int(p.stem.split("_")[-1])
        )
        if self._checkpoint_files:
            logger.info(f"Found {len(self._checkpoint_files)} existing checkpoints")
    
    def save(
        self,
        model: nn.Module,
        optimizer: optim.Optimizer = None,
        scheduler=None,
        epoch: int = 0,
        metrics: Dict[str, float] = None,
        scaler=None,
        extra_state: Dict[str, Any] = None,
    ) -> Optional[Path]:
        """Save a training checkpoint.
        
        Args:
            model: PyTorch model to save.
            optimizer: Optional optimizer to save state from.
            scheduler: Optional scheduler to save state from.
            epoch: Current epoch number.
            metrics: Dictionary of validation metrics.
            scaler: Optional GradScaler for mixed precision.
            extra_state: Additional state to include.
            
        Returns:
            Path to saved checkpoint, or None if not saved this epoch.
        """
        metrics = metrics or {}
        
        # Check if we should save this epoch
        should_save_periodic = (epoch + 1) % self.save_every == 0
        
        # Check if this is the best model
        is_best = False
        if self.save_best and self.best_metric in metrics:
            score = metrics[self.best_metric]
            if self.best_mode == "min" and score < self.best_score:
                self.best_score = score
                self.best_epoch = epoch
                is_best = True
            elif self.best_mode == "max" and score > self.best_score:
                self.best_score = score
                self.best_epoch = epoch
                is_best = True
        
        if not should_save_periodic and not is_best:
            return None
        
        # Build checkpoint state
        state = {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "metrics": metrics,
            "best_score": self.best_score,
            "best_epoch": self.best_epoch,
            "timestamp": datetime.now().isoformat(),
            "version": "1.2.0",
        }
        
        if self.save_optimizer and optimizer is not None:
            state["optimizer_state_dict"] = optimizer.state_dict()
        
        if self.save_scheduler and scheduler is not None:
            state["scheduler_state_dict"] = scheduler.state_dict()
        
        if scaler is not None:
            state["scaler_state_dict"] = scaler.state_dict()
        
        if extra_state:
            state["extra_state"] = extra_state
        
        # Save periodic checkpoint
        checkpoint_path = None
        if should_save_periodic:
            checkpoint_path = self.save_dir / f"checkpoint_epoch_{epoch:04d}.pt"
            torch.save(state, checkpoint_path)
            self._checkpoint_files.append(checkpoint_path)
            logger.info(f"Saved checkpoint: {checkpoint_path}")
            
            # Rotate old checkpoints
            self._rotate_checkpoints()
        
        # Save best model separately
        if is_best:
            best_path = self.save_dir / "best_model.pt"
            torch.save(state, best_path)
            logger.info(
                f"New best model saved! {self.best_metric}: {self.best_score:.6f} at epoch {epoch}"
            )
            
            # Also save metadata
            metadata = {
                "epoch": epoch,
                "metric": self.best_metric,
                "score": self.best_score,
                "timestamp": state["timestamp"],
            }
            metadata_path = self.save_dir / "best_model_metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
        
        return checkpoint_path
    
    def _rotate_checkpoints(self):
        """Remove old checkpoints keeping only keep_last most recent."""
        if self.keep_last <= 0:
            return
        
        while len(self._checkpoint_files) > self.keep_last:
            old_checkpoint = self._checkpoint_files.pop(0)
            if old_checkpoint.exists():
                old_checkpoint.unlink()
                logger.debug(f"Removed old checkpoint: {old_checkpoint}")
    
    def load_latest(
        self,
        model: nn.Module,
        optimizer: optim.Optimizer = None,
        scheduler=None,
        scaler=None,
    ) -> Optional[Dict[str, Any]]:
        """Load the most recent checkpoint.
        
        Args:
            model: Model to load state into.
            optimizer: Optional optimizer to load state into.
            scheduler: Optional scheduler to load state into.
            scaler: Optional GradScaler to load state into.
            
        Returns:
            Checkpoint state dictionary, or None if no checkpoint found.
        """
        if not self._checkpoint_files:
            logger.info("No checkpoints found to load")
            return None
        
        latest_path = self._checkpoint_files[-1]
        return self.load(latest_path, model, optimizer, scheduler, scaler)
    
    def load_best(
        self,
        model: nn.Module,
        optimizer: optim.Optimizer = None,
        scheduler=None,
        scaler=None,
    ) -> Optional[Dict[str, Any]]:
        """Load the best model checkpoint.
        
        Args:
            model: Model to load state into.
            optimizer: Optional optimizer to load state into.
            scheduler: Optional scheduler to load state into.
            scaler: Optional GradScaler to load state into.
            
        Returns:
            Checkpoint state dictionary, or None if no best checkpoint found.
        """
        best_path = self.save_dir / "best_model.pt"
        if not best_path.exists():
            logger.warning("No best model checkpoint found")
            return None
        
        return self.load(best_path, model, optimizer, scheduler, scaler)
    
    def load(
        self,
        checkpoint_path: Path,
        model: nn.Module,
        optimizer: optim.Optimizer = None,
        scheduler=None,
        scaler=None,
    ) -> Dict[str, Any]:
        """Load a specific checkpoint.
        
        Args:
            checkpoint_path: Path to checkpoint file.
            model: Model to load state into.
            optimizer: Optional optimizer to load state into.
            scheduler: Optional scheduler to load state into.
            scaler: Optional GradScaler to load state into.
            
        Returns:
            Checkpoint state dictionary.
            
        Raises:
            FileNotFoundError: If checkpoint file does not exist.
        """
        checkpoint_path = Path(checkpoint_path)
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        
        state = torch.load(checkpoint_path, map_location="cpu")
        
        # Load model state
        model.load_state_dict(state["model_state_dict"])
        logger.info(f"Loaded model state from epoch {state['epoch']}")
        
        # Load optimizer state
        if optimizer is not None and "optimizer_state_dict" in state:
            optimizer.load_state_dict(state["optimizer_state_dict"])
            logger.debug("Loaded optimizer state")
        
        # Load scheduler state
        if scheduler is not None and "scheduler_state_dict" in state:
            scheduler.load_state_dict(state["scheduler_state_dict"])
            logger.debug("Loaded scheduler state")
        
        # Load scaler state
        if scaler is not None and "scaler_state_dict" in state:
            scaler.load_state_dict(state["scaler_state_dict"])
            logger.debug("Loaded GradScaler state")
        
        # Restore manager state
        self.best_score = state.get("best_score", self.best_score)
        self.best_epoch = state.get("best_epoch", self.best_epoch)
        
        return state
    
    @classmethod
    def from_config(cls, config: CheckpointConfig) -> "CheckpointManager":
        """Create CheckpointManager from configuration.
        
        Args:
            config: CheckpointConfig with settings.
            
        Returns:
            Configured CheckpointManager instance.
        """
        return cls(
            save_dir=config.save_dir,
            save_every=config.save_every,
            keep_last=config.keep_last,
            save_best=config.save_best,
            best_metric=config.best_metric,
            best_mode=config.best_mode,
            save_optimizer=config.save_optimizer,
            save_scheduler=config.save_scheduler,
        )
