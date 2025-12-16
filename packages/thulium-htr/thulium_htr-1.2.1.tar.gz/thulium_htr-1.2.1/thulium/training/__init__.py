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

"""Training utilities for Thulium HTR.

This module provides training utilities including early stopping, checkpoint
management, learning rate scheduling, and training loop helpers.

Submodules:
    early_stopping: Patience-based training termination.
    checkpointing: Model checkpoint saving and loading.
    curriculum: Curriculum learning strategies.
    losses: Custom loss functions for HTR.
    optimizers: Optimizer configurations and factories.
    schedulers: Learning rate schedulers.
    trainer: Main training loop implementation.

Classes:
    EarlyStopping: Patience-based training termination.
    EarlyStoppingConfig: Configuration for early stopping.
    CheckpointManager: Model checkpoint saving and loading.
    CheckpointConfig: Configuration for checkpoint management.

Example:
    Basic training setup:

    >>> from thulium.training import EarlyStopping, CheckpointManager
    >>> early_stopping = EarlyStopping(patience=10, metric="val_cer")
    >>> checkpoint_mgr = CheckpointManager(save_dir="./checkpoints")
    >>>
    >>> for epoch in range(100):
    ...     metrics = train_epoch(model, train_loader)
    ...     if early_stopping(metrics):
    ...         break
    ...     checkpoint_mgr.save(model, epoch, metrics)
"""

from __future__ import annotations

from thulium.training.checkpointing import CheckpointConfig
from thulium.training.checkpointing import CheckpointManager
from thulium.training.early_stopping import EarlyStopping
from thulium.training.early_stopping import EarlyStoppingConfig

__all__ = [
    "CheckpointConfig",
    "CheckpointManager",
    "EarlyStopping",
    "EarlyStoppingConfig",
]
