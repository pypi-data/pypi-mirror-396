# Self-Supervised Learning

Self-supervised pretraining techniques for HTR.

## Overview

Self-supervised learning (SSL) enables pretraining on unlabeled handwriting
images, reducing the need for expensive manual transcriptions.

## Techniques

### Masked Image Modeling (MIM)

Inspired by BERT, randomly mask patches and predict them.

```python
from thulium.training.ssl import MaskedImageModeling

ssl_task = MaskedImageModeling(
    patch_size=8,
    mask_ratio=0.75,
)

loss = ssl_task(model, unlabeled_images)
```

### Contrastive Learning

Learn representations by contrasting similar/different samples.

```python
from thulium.training.ssl import ContrastiveLearning

ssl_task = ContrastiveLearning(
    temperature=0.07,
    augmentations=["crop", "rotate", "noise"],
)

loss = ssl_task(model, unlabeled_images)
```

### Handwriting-Specific Tasks

#### Stroke Order Prediction

Predict the temporal order of strokes.

#### Writer Identification

Learn writer-invariant features.

#### Script Classification

Classify writing script (Latin, Cyrillic, etc).

## Pretraining Pipeline

```yaml
# config/pretrain.yaml
ssl:
  method: mim
  epochs: 100
  batch_size: 256
  
model:
  backbone:
    type: vit
    patch_size: 8
    
data:
  unlabeled_dir: data/unlabeled/
  augmentation: true
```

```bash
thulium pretrain config/pretrain.yaml
```

## Fine-tuning

After pretraining, fine-tune on labeled data:

```python
# Load pretrained backbone
model = HTRModel.from_pretrained("pretrained_backbone.pt")

# Fine-tune on labeled data
trainer = HTRTrainer(model, lr=1e-4)
trainer.fine_tune(labeled_dataloader, epochs=50)
```

## Results

| Pretraining | Labeled Data | CER |
|-------------|--------------|-----|
| None | 100% | 3.8% |
| MIM | 10% | 4.2% |
| MIM | 50% | 3.5% |
| Contrastive | 10% | 4.5% |

## See Also

- [Training Guide](training_guide.md) — Supervised training
- [Architecture](../architecture.md) — Model components
