# Robustness Testing

Testing model robustness against noise and degradation.

## Overview

Real-world documents often contain:
- Noise from scanning
- Blur from poor focus
- Low contrast from faded ink
- Rotation from misalignment

Thulium includes tools to systematically test model robustness.

## Noise Types

### Gaussian Noise

Simulates sensor noise from scanning.

```python
from thulium.data.noise_injection import GaussianNoiseInjector

injector = GaussianNoiseInjector(mean=0, std=25)
noisy_image = injector(image)
```

### Salt and Pepper Noise

Simulates random pixel corruption.

```python
from thulium.data.noise_injection import SaltPepperNoiseInjector

injector = SaltPepperNoiseInjector(probability=0.01)
noisy_image = injector(image)
```

### Gaussian Blur

Simulates focus issues.

```python
from thulium.data.noise_injection import BlurInjector

injector = BlurInjector(kernel_size=5)
blurred_image = injector(image)
```

### Morphological Degradation

Simulates ink bleeding/fading.

```python
from thulium.data.noise_injection import MorphologicalDegradation

# Erosion (thin strokes)
degrader = MorphologicalDegradation(operation="erode", iterations=1)

# Dilation (thick strokes)
degrader = MorphologicalDegradation(operation="dilate", iterations=1)
```

## Robustness Metrics

### CER vs Noise Level

| Noise σ | CER | Δ CER |
|---------|-----|-------|
| 0 | 3.8% | — |
| 10 | 4.2% | +0.4% |
| 25 | 5.1% | +1.3% |
| 50 | 7.8% | +4.0% |

### CER vs Blur

| Kernel | CER | Δ CER |
|--------|-----|-------|
| 0 | 3.8% | — |
| 3 | 4.1% | +0.3% |
| 5 | 5.2% | +1.4% |
| 7 | 7.5% | +3.7% |

## Running Robustness Tests

```python
from thulium.evaluation.robustness import RobustnessTester

tester = RobustnessTester(
    model=pipeline,
    dataset=test_dataset,
)

# Test across noise levels
results = tester.run(
    noise_types=["gaussian", "blur", "salt_pepper"],
    levels=[0, 0.1, 0.2, 0.3, 0.5],
)

for level, metrics in results.items():
    print(f"Level {level}: CER={metrics['cer']:.2%}")
```

### CLI

```bash
thulium benchmark iam --robustness --noise-levels 0,0.1,0.25,0.5
```

## Best Practices

1. **Train with augmentation** — Include noise during training
2. **Test on realistic noise** — Use noise levels matching deployment
3. **Report degradation curves** — Show CER vs noise level
4. **Set deployment thresholds** — Define acceptable noise limits

## See Also

- [Benchmarks](benchmarks.md) — Clean benchmarks
- [Training Guide](../training/training_guide.md) — Augmentation config
