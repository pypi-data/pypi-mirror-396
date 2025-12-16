# Evaluation Metrics

Metrics for evaluating handwriting recognition accuracy.

## Character Error Rate (CER)

The primary metric for HTR evaluation.

### Definition

$$
\text{CER} = \frac{S + D + I}{N}
$$

Where:
- **S** = Substitutions (characters replaced)
- **D** = Deletions (characters missing from hypothesis)
- **I** = Insertions (extra characters in hypothesis)
- **N** = Total characters in reference

### Interpretation

| CER | Quality |
|-----|---------|
| < 1% | Excellent |
| 1-3% | Good |
| 3-5% | Acceptable |
| 5-10% | Poor |
| > 10% | Very Poor |

### Usage

```python
from thulium.evaluation.metrics import cer

error = cer(reference="hello world", hypothesis="helo wrold")
print(f"CER: {error:.2%}")  # Output: CER: 18.18%
```

## Word Error Rate (WER)

Word-level error rate for text quality assessment.

### Definition

$$
\text{WER} = \frac{S_w + D_w + I_w}{N_w}
$$

Same formula as CER but applied at word level (whitespace-tokenized).

### Usage

```python
from thulium.evaluation.metrics import wer

error = wer(reference="the quick fox", hypothesis="the fast fox")
print(f"WER: {error:.2%}")  # Output: WER: 33.33%
```

## Sequence Error Rate (SER)

Binary error metric for exact match evaluation.

### Definition

$$
\text{SER} = \begin{cases} 0 & \text{if reference = hypothesis} \\ 1 & \text{otherwise} \end{cases}
$$

### Usage

```python
from thulium.evaluation.metrics import ser

error = ser(reference="hello", hypothesis="hello")
print(f"SER: {error}")  # Output: SER: 0.0
```

## Batch Metrics

Compute metrics over multiple samples.

```python
from thulium.evaluation.metrics import cer_wer_batch

references = ["hello", "world", "test"]
hypotheses = ["helo", "world", "tset"]

batch_cer, batch_wer = cer_wer_batch(references, hypotheses)
print(f"Batch CER: {batch_cer:.2%}")
print(f"Batch WER: {batch_wer:.2%}")
```

## Edit Distance

Raw edit distance without normalization.

```python
from thulium.evaluation.metrics import edit_distance

dist = edit_distance(reference="kitten", hypothesis="sitting")
print(f"Edit distance: {dist}")  # Output: 3
```

## Edit Operations

Detailed breakdown of errors.

```python
from thulium.evaluation.metrics import get_edit_operations

ops = get_edit_operations(reference="hello", hypothesis="hallo")
print(f"Substitutions: {ops.substitutions}")
print(f"Insertions: {ops.insertions}")
print(f"Deletions: {ops.deletions}")
print(f"Matches: {ops.matches}")
```

## Precision, Recall, F1

For detection tasks (line/word detection).

```python
from thulium.evaluation.metrics import precision_recall_f1

p, r, f1 = precision_recall_f1(
    true_positives=80,
    false_positives=10,
    false_negatives=20
)
print(f"Precision: {p:.2%}, Recall: {r:.2%}, F1: {f1:.2%}")
```

## See Also

- [Benchmarks](benchmarks.md) — Model performance benchmarks
- [Robustness](robustness.md) — Noise robustness testing
