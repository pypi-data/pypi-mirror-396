# Benchmarks

Performance benchmarks for Thulium models.

## IAM Handwriting Database

Standard benchmark for English handwriting recognition.

| Model | CER | WER | SER | Latency |
|-------|-----|-----|-----|---------|
| thulium-tiny | 5.2% | 14.1% | 28.3% | 12ms |
| thulium-base | 3.8% | 10.2% | 21.5% | 28ms |
| thulium-large | 2.9% | 7.8% | 16.2% | 65ms |

*Batch size 1, NVIDIA A100, PyTorch 2.0*

## Multilingual Benchmarks

### Per-Language CER (thulium-multilingual)

| Language | Script | CER | WER |
|----------|--------|-----|-----|
| English | Latin | 3.2% | 8.5% |
| German | Latin | 3.8% | 10.1% |
| French | Latin | 4.1% | 11.2% |
| Russian | Cyrillic | 4.5% | 12.3% |
| Arabic | Arabic | 5.8% | 15.2% |
| Chinese | Hanzi | 6.2% | — |
| Japanese | Kanji/Kana | 5.5% | 14.1% |

### Regional Aggregates

| Region | Languages | Avg CER |
|--------|-----------|---------|
| Western Europe | 7 | 3.8% |
| Scandinavia | 6 | 4.2% |
| Eastern Europe | 8 | 4.5% |
| Middle East | 4 | 5.6% |
| East Asia | 3 | 5.8% |

## Throughput

### Batch Processing

| Model | Batch Size | Throughput |
|-------|------------|------------|
| thulium-tiny | 1 | 83 samples/s |
| thulium-tiny | 16 | 412 samples/s |
| thulium-base | 1 | 35 samples/s |
| thulium-base | 16 | 185 samples/s |
| thulium-large | 1 | 15 samples/s |
| thulium-large | 16 | 78 samples/s |

### Device Comparison

| Device | thulium-base | thulium-large |
|--------|--------------|---------------|
| CPU (8 cores) | 3.2 samples/s | 0.8 samples/s |
| RTX 3090 | 28 samples/s | 12 samples/s |
| A100 | 35 samples/s | 15 samples/s |
| M2 Pro (MPS) | 8 samples/s | 3 samples/s |

## Running Benchmarks

```bash
# Benchmark on IAM dataset
thulium benchmark iam --model thulium-base

# Custom dataset
thulium benchmark custom --data ./my_data --model thulium-large

# Save results
thulium benchmark iam --output results.json
```

### Python API

```python
from thulium.evaluation.benchmarking import Benchmark

bench = Benchmark(
    model="thulium-base",
    dataset="iam",
    device="cuda",
)

results = bench.run()
print(f"CER: {results.aggregate_cer:.2%}")
print(f"WER: {results.aggregate_wer:.2%}")
```

## Methodology

- **Test Split**: Standard IAM test set (1,861 lines)
- **Preprocessing**: Height normalization to 64px
- **Decoding**: Greedy decoding (no LM)
- **Averaging**: Micro-averaged across samples

## See Also

- [Metrics](metrics.md) — Metric definitions
- [Model Zoo](../models/model_zoo.md) — Model details
