# Error Analysis

Tools for analyzing recognition errors.

## Overview

Detailed error analysis helps identify model weaknesses and guide
improvements. Thulium provides tools for:

- **Confusion Matrices** — Character-level confusion
- **Top-K Errors** — Most frequent mistakes
- **Metric Breakdown** — Per-character/word metrics

## Error Analyzer

### Basic Usage

```python
from thulium.xai.error_analysis import ErrorAnalyzer

predictions = ["helo world", "tset", "exampl"]
ground_truth = ["hello world", "test", "example"]

# Get aggregate metrics
metrics = ErrorAnalyzer.summarize_metrics(predictions, ground_truth)
print(f"CER: {metrics['CER']:.2%}")
print(f"WER: {metrics['WER']:.2%}")
print(f"SER: {metrics['SER']:.2%}")
```

### Top-K Errors

Find the most frequent errors.

```python
errors = ErrorAnalyzer.analyze_top_k_errors(
    predictions=predictions,
    ground_truth=ground_truth,
    k=10,
)

for error in errors:
    print(f"'{error['ground_truth']}' → '{error['prediction']}' "
          f"({error['count']} times, CER={error['cer']:.2%})")
```

### Common Error Patterns

| Error Type | Example | Cause |
|------------|---------|-------|
| Substitution | a → o | Visual similarity |
| Deletion | hello → helo | Merged strokes |
| Insertion | cat → caat | Broken strokes |
| Transposition | the → teh | Rushed writing |

## Confidence Analysis

### Expected Calibration Error

```python
from thulium.xai.confidence_analysis import ConfidenceAnalyzer

ece = ConfidenceAnalyzer.compute_ece(probs, labels, n_bins=10)
print(f"ECE: {ece:.4f}")
```

## CLI

```bash
thulium analyze predictions.txt ground_truth.txt --top-k 20
```

## See Also

- [Attention and Saliency](attention_and_saliency.md) — Visualization
- [Metrics](../evaluation/metrics.md) — Metric definitions
