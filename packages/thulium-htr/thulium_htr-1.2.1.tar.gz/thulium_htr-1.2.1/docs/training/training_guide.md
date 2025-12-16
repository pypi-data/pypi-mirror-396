# Training Guide

Train custom HTR models with Thulium.

## Prerequisites

```bash
pip install thulium[training]
```

## Dataset Preparation

### Directory Structure

```
data/
├── train/
│   ├── images/
│   │   ├── 001.png
│   │   └── ...
│   └── labels.txt
├── val/
│   └── ...
└── test/
    └── ...
```

### Labels Format

Each line: `image_filename text`

```
001.png Hello world
002.png This is a sample
003.png More handwriting
```

### Dataset Configuration

```yaml
# config/data.yaml
dataset:
  type: custom
  train_dir: data/train
  val_dir: data/val
  test_dir: data/test
  
preprocessing:
  height: 64
  min_width: 32
  max_width: 512
  normalize: true
```

## Training Configuration

### Full Configuration

```yaml
# config/train.yaml
model:
  backbone:
    type: resnet
    config_name: resnet_small
  head:
    type: bilstm
    hidden_size: 256
    num_layers: 2
    dropout: 0.1
  decoder:
    type: ctc
    blank_index: 0

training:
  epochs: 100
  batch_size: 32
  optimizer:
    type: adamw
    lr: 3e-4
    weight_decay: 0.01
  scheduler:
    type: cosine
    warmup_epochs: 5
  mixed_precision: true
  gradient_clip: 1.0

early_stopping:
  patience: 10
  metric: val_cer
  mode: min

checkpointing:
  save_dir: checkpoints/
  save_every: 5
  keep_last: 3
  save_best: true
```

## Running Training

### CLI

```bash
thulium train config/train.yaml --output-dir runs/exp1
```

### Python API

```python
from thulium.training import HTRTrainer
from thulium.models.wrappers import HTRModel
from thulium.data import create_dataloader

# Create model
model = HTRModel.from_config("config/train.yaml")

# Create dataloaders
train_loader = create_dataloader("data/train", batch_size=32)
val_loader = create_dataloader("data/val", batch_size=32)

# Create trainer
trainer = HTRTrainer(
    model=model,
    lr=3e-4,
    device="cuda",
    mixed_precision=True,
)

# Train
for epoch in range(100):
    train_metrics = trainer.train_epoch(train_loader, epoch)
    val_metrics = trainer.validate(val_loader, epoch)
    
    print(f"Epoch {epoch}: CER={val_metrics['val_cer']:.2%}")
```

## Data Augmentation

```yaml
augmentation:
  enabled: true
  transforms:
    - type: random_rotation
      degrees: 3
    - type: random_scale
      range: [0.9, 1.1]
    - type: gaussian_noise
      std: 0.05
    - type: random_brightness
      range: [0.8, 1.2]
```

## Monitoring

### TensorBoard

```bash
tensorboard --logdir runs/
```

### Weights & Biases

```yaml
logging:
  wandb:
    enabled: true
    project: thulium-training
    entity: your-org
```

## Checkpointing

```python
from thulium.training import CheckpointManager

manager = CheckpointManager(
    save_dir="checkpoints/",
    save_best=True,
    best_metric="val_cer",
)

# Save
manager.save(model, optimizer, scheduler, epoch, metrics)

# Load
manager.load_best(model, optimizer)
```

## Multi-GPU Training

```bash
# DataParallel
thulium train config.yaml --gpus 0,1,2,3

# DistributedDataParallel
torchrun --nproc_per_node=4 -m thulium.cli.main train config.yaml
```

## See Also

- [Self-Supervised](self_supervised.md) — SSL pretraining
- [Model Zoo](../models/model_zoo.md) — Pretrained models
- [Metrics](../evaluation/metrics.md) — Evaluation metrics
