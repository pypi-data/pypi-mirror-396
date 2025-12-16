# Attention and Saliency Visualization

Tools for visualizing model attention and saliency maps.

## Overview

Understanding what the model "sees" helps debug errors and build trust.
Thulium provides multiple visualization techniques:

- **Attention Maps** — Where the model looks for each output character
- **Saliency Maps** — Which input pixels influence predictions
- **GradCAM** — Class activation mapping

## Attention Visualization

### Overlay Attention

Overlay attention weights on the input image.

```python
from thulium.xai.attention_maps import AttentionVisualizer
import cv2

# Get attention from model
attention_weights = model.get_attention(image)

# Create visualization
viz = AttentionVisualizer.overlay_attention(
    image=image,
    attention_weights=attention_weights,
    alpha=0.6,
    colormap=cv2.COLORMAP_JET,
)

# Save
cv2.imwrite("attention.png", viz)
```

### Per-Character Attention Grid

Visualize attention for each predicted character.

```python
AttentionVisualizer.plot_attention_grid(
    image=image,
    attentions=per_char_attentions,
    tokens=["H", "e", "l", "l", "o"],
    save_path="attention_grid.png",
)
```

## Saliency Maps

### Gradient Saliency

Simple input gradients.

```python
from thulium.xai.saliency import SaliencyGenerator

generator = SaliencyGenerator(model)
saliency = generator.compute_gradient_saliency(image)
```

### Integrated Gradients

Accumulated gradients along input path.

```python
saliency = generator.compute_integrated_gradients(
    image,
    num_steps=50,
    baseline=None,  # Uses zeros
)
```

### SmoothGrad

Average gradients over noisy inputs.

```python
saliency = generator.compute_smoothgrad(
    image,
    num_samples=25,
    noise_level=0.1,
)
```

### GradCAM

Class activation mapping for CNN layers.

```python
saliency = generator.compute_gradcam(image)
```

## Configuration

```python
from thulium.xai.saliency import SaliencyConfig, SaliencyGenerator

config = SaliencyConfig(
    method="integrated",
    num_steps=50,
    absolute=True,
    normalize=True,
)

generator = SaliencyGenerator(model, config)
```

## Interpretation

| Pattern | Meaning |
|---------|---------|
| Focused on strokes | Good feature learning |
| Scattered attention | Possible confusion |
| Background activation | Noise sensitivity |

## See Also

- [Error Analysis](error_analysis.md) — Detailed error analysis
- [Architecture](../architecture.md) — Model components
