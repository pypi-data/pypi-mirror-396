# API Reference

Complete API documentation for Thulium.

## High-Level API

### `recognize_image`

Recognize text from a single image.

```python
from thulium import recognize_image

result = recognize_image(
    image_path: str | Path,
    language: str = "en",
    pipeline_name: str = "default",
    device: str = "auto",
) -> RecognitionResult
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image_path` | `str \| Path` | required | Path to image file |
| `language` | `str` | `"en"` | ISO 639-1 language code |
| `pipeline_name` | `str` | `"default"` | Pipeline configuration |
| `device` | `str` | `"auto"` | `"cpu"`, `"cuda"`, or `"auto"` |

**Returns:** `RecognitionResult`

**Example:**

```python
result = recognize_image("letter.png", language="de")
print(result.text)
print(f"Confidence: {result.confidence:.2%}")
```

---

### `recognize_pdf`

Recognize text from a PDF document.

```python
from thulium import recognize_pdf

results = recognize_pdf(
    pdf_path: str | Path,
    language: str = "en",
    pages: list[int] | None = None,
) -> list[RecognitionResult]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pdf_path` | `str \| Path` | required | Path to PDF file |
| `language` | `str` | `"en"` | ISO 639-1 language code |
| `pages` | `list[int] \| None` | `None` | Pages to process (all if None) |

---

## Classes

### `RecognitionResult`

Result of text recognition.

```python
@dataclass
class RecognitionResult:
    full_text: str          # Complete recognized text
    lines: list[LineResult] # Per-line results
    confidence: float       # Overall confidence (0.0-1.0)
    language: str           # Language used
    processing_time_ms: float
```

### `LineResult`

Single line recognition result.

```python
@dataclass
class LineResult:
    text: str               # Recognized text
    confidence: float       # Line confidence
    bbox: tuple[int, int, int, int]  # Bounding box (x, y, w, h)
```

---

### `HTRPipeline`

End-to-end HTR pipeline for batch processing.

```python
from thulium import HTRPipeline

pipeline = HTRPipeline.from_pretrained(
    model_name: str,
    device: str = "auto",
    **kwargs,
) -> HTRPipeline
```

**Methods:**

| Method | Description |
|--------|-------------|
| `recognize(image)` | Recognize single image |
| `recognize_batch(images)` | Batch recognition |
| `to(device)` | Move to device |

**Example:**

```python
pipeline = HTRPipeline.from_pretrained("thulium-base")
results = pipeline.recognize_batch(["p1.png", "p2.png"])
```

---

## Language Profiles

### `get_language_profile`

Get language configuration.

```python
from thulium.data.language_profiles import get_language_profile

profile = get_language_profile(language_code: str) -> LanguageProfile
```

### `list_supported_languages`

List all supported language codes.

```python
from thulium.data.language_profiles import list_supported_languages

languages = list_supported_languages() -> list[str]
# Returns: ['en', 'de', 'fr', 'ja', ...]
```

---

## Metrics

### `cer`

Character Error Rate.

```python
from thulium.evaluation.metrics import cer

error_rate = cer(reference: str, hypothesis: str) -> float
# Returns: 0.0 to 1.0+
```

### `wer`

Word Error Rate.

```python
from thulium.evaluation.metrics import wer

error_rate = wer(reference: str, hypothesis: str) -> float
```

### `cer_wer_batch`

Batch CER/WER computation.

```python
from thulium.evaluation.metrics import cer_wer_batch

batch_cer, batch_wer = cer_wer_batch(
    references: list[str],
    hypotheses: list[str],
) -> tuple[float, float]
```

---

## See Also

- [CLI Usage](cli_usage.md) — Command-line interface
- [Getting Started](../getting_started.md) — Installation and quick start
