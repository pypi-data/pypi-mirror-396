# Examples

Example scripts and notebooks demonstrating Thulium usage.

## Jupyter Notebooks

| Notebook | Description |
|----------|-------------|
| [00_quickstart.ipynb](00_quickstart.ipynb) | Quick start tutorial |
| [01_basic_recognition.ipynb](01_basic_recognition.ipynb) | Basic HTR examples |
| [02_benchmarking.ipynb](02_benchmarking.ipynb) | Model benchmarking |
| [03_error_analysis.ipynb](03_error_analysis.ipynb) | Error analysis tools |

## Python Scripts

| Example | Description |
|---------|-------------|
| [recognize_multilingual.py](recognize_multilingual.py) | Multilingual recognition demo |
| [recognize_scandinavian.py](recognize_scandinavian.py) | Scandinavian languages |
| [recognize_baltic.py](recognize_baltic.py) | Baltic languages |
| [recognize_caucasus.py](recognize_caucasus.py) | Caucasus languages |

## Running Examples

```bash
# Install Thulium
pip install thulium

# Run an example
python examples/recognize_multilingual.py
```

## Quick Examples

### Basic Recognition

```python
from thulium import recognize_image

result = recognize_image("handwriting.png", language="en")
print(result.text)
```

### Batch Processing

```python
from thulium import HTRPipeline

pipeline = HTRPipeline.from_pretrained("thulium-base")
results = pipeline.recognize_batch(["page1.png", "page2.png"])
```

### With Confidence

```python
result = recognize_image("document.png", language="de")
print(f"Text: {result.text}")
print(f"Confidence: {result.confidence:.2%}")
```

## See Also

- [Getting Started](../docs/getting_started.md) — Installation
- [API Reference](../docs/api/reference.md) — Full API docs
