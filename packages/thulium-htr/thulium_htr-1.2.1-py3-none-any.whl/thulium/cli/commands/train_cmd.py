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

"""Training Command Module.

This module implements the `train` command for the Thulium CLI.
It handles model training configuration, data loading setup, and the
execution of the training loop using the HTRTrainer.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import typer
import yaml
from torch.utils.data import DataLoader

from thulium.data.collate import HTRCollate
from thulium.data.datasets import FolderDataset
from thulium.data.samplers import BucketingSampler
from thulium.models.wrappers.htr_model import HTRModel
from thulium.training.trainer import HTRTrainer

logger = logging.getLogger(__name__)

app = typer.Typer(help="Train HTR models.")


def _load_config(path: Path) -> Dict[str, Any]:
    """Load and validate training configuration."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error("Failed to load configuration file %s: %s", path, e)
        raise typer.Exit(1)


@app.command(name="run")
def train_command(
    config: Path = typer.Option(
        ...,
        exists=True,
        help="Path to the training configuration YAML file.",
        resolve_path=True,
    ),
    data_dir: Path = typer.Option(
        ...,
        exists=True,
        file_okay=False,
        help="Root directory containing training data.",
        resolve_path=True,
    ),
    output_dir: Path = typer.Option(
        "checkpoints",
        help="Directory to save model checkpoints and logs.",
        writable=True,
        resolve_path=True,
    ),
) -> None:
    """
    Start the training process for a Thulium HTR model.

    This command expects a YAML configuration file defining the model architecture,
    training hyperparameters, and dataset parameters.
    """
    logger.info("Initializing training run...")
    logger.info("Configuration: %s", config)
    logger.info("Data Directory: %s", data_dir)
    logger.info("Output Directory: %s", output_dir)

    # 1. Load Configuration
    cfg = _load_config(config)
    train_cfg = cfg.get("training", {})
    
    # 2. Setup Data
    logger.info("Setting up datasets...")
    # TODO: Add support for LMDB and other dataset formats via config
    train_root = data_dir / "train"
    val_root = data_dir / "val"
    
    if not train_root.exists():
         logger.error("Training data directory not found: %s", train_root)
         raise typer.Exit(1)

    train_ds = FolderDataset(
        root=str(train_root),
        label_file=str(train_root / "labels.txt"),
    )
    val_ds = FolderDataset(
        root=str(val_root),
        label_file=str(val_root / "labels.txt") if (val_root / "labels.txt").exists() else None,
    )

    logger.info("Training samples: %d", len(train_ds))
    logger.info("Validation samples: %d", len(val_ds))

    # 3. Setup Loaders
    collate_fn = HTRCollate()
    
    batch_size = train_cfg.get("batch_size", 32)
    num_workers = train_cfg.get("num_workers", 4)
    
    train_sampler = BucketingSampler(train_ds, batch_size=batch_size)
    
    train_loader = DataLoader(
        train_ds,
        batch_sampler=train_sampler,
        num_workers=num_workers,
        collate_fn=collate_fn,
        pin_memory=True,
    )
    
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        collate_fn=collate_fn,
    )

    # 4. Initialize Model
    logger.info("Initializing model architecture...")
    model = HTRModel.from_config(str(config))
    
    # TODO: Verify model compatibility with dataset vocab size

    # 5. Initialize Trainer
    logger.info("Setting up trainer...")
    trainer = HTRTrainer(
        model=model,
        optimizer=train_cfg.get("optimizer", "AdamW"),
        lr=float(train_cfg.get("lr", 3e-4)),
        scheduler=train_cfg.get("scheduler", "cosine"),
        warmup_steps=train_cfg.get("warmup_steps", 1000),
        output_dir=str(output_dir),
        mixed_precision=train_cfg.get("mixed_precision", True),
    )

    # 6. Training Loop
    epochs = train_cfg.get("epochs", 100)
    save_every = train_cfg.get("save_every", 5)
    
    logger.info("Starting training for %d epochs...", epochs)
    try:
        for epoch in range(1, epochs + 1):
            train_metrics = trainer.train_epoch(train_loader, epoch)
            val_metrics = trainer.validate(val_loader, epoch)
            
            logger.info("Epoch %d Results | Train Loss: %.4f | Val Loss: %.4f | Val CER: %.4f",
                        epoch, train_metrics["loss"], val_metrics["loss"], val_metrics.get("cer", 1.0))

            if epoch % save_every == 0:
                trainer.save_checkpoint(f"checkpoint_epoch_{epoch}.pt")
                
    except KeyboardInterrupt:
        logger.warning("Training interrupted by user. Saving emergency checkpoint...")
        trainer.save_checkpoint("interrupted_checkpoint.pt")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("Training crashed: %s", e)
        # Attempt save
        trainer.save_checkpoint("crash_checkpoint.pt")
        raise e

    logger.info("Training completed successfully.")
