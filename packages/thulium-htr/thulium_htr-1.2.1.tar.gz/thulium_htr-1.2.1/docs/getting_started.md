# Getting Started

This guide covers installation and basic usage of Thulium.

## Installation

### Requirements

- Python 3.9+
- PyTorch 2.0+

### From PyPI

```bash
pip install thulium
```

### With GPU Support

```bash
pip install thulium[gpu]
```

### From Source

```bash
git clone https://github.com/thulium-dev/thulium.git
cd thulium
pip install -e ".[dev]"
```

## Quick Start

### Single Image Recognition

```python
from thulium import recognize_image

result = recognize_image("document.png", language="en")
print(result.text)
print(f"Confidence: {result.confidence:.2%}")
```

### Batch Processing

```python
from thulium import HTRPipeline

pipeline = HTRPipeline.from_pretrained("thulium-base")
results = pipeline.recognize_batch(
    ["page1.png", "page2.png", "page3.png"],
    language="en"
)

for i, r in enumerate(results):
    print(f"Page {i+1}: {r.text[:50]}...")
```

### Multilingual Recognition

```python
from thulium import recognize_image

# German handwriting
result_de = recognize_image("german_letter.png", language="de")

# Japanese handwriting
result_ja = recognize_image("japanese_note.png", language="ja")

# Arabic handwriting (right-to-left)
result_ar = recognize_image("arabic_doc.png", language="ar")
```

## Configuration

### Pipeline Configuration

```python
from thulium import HTRPipeline

pipeline = HTRPipeline.from_pretrained(
    "thulium-base",
    device="cuda",           # or "cpu"
    beam_width=10,           # beam search width
    use_language_model=True, # enable LM rescoring
)
```

### Custom Models

```python
from thulium import HTRPipeline

pipeline = HTRPipeline.from_config("config/my_model.yaml")
```

## Command Line Interface

```bash
# Recognize a single image
thulium recognize image.png --language en

# Batch recognition
thulium recognize folder/ --language de --output results.json

# List supported languages
thulium profiles list
```

## Next Steps

- [Model Zoo](models/model_zoo.md) — Available pretrained models
- [Language Support](models/language_support.md) — 52+ supported languages
- [Training Guide](training/training_guide.md) — Train custom models
- [API Reference](api/reference.md) — Complete API documentation
