# Development Guide

Set up a development environment for contributing to Thulium.

## Prerequisites

- Python 3.9+
- Git
- CUDA toolkit (optional, for GPU)

## Setup

### Clone Repository

```bash
git clone https://github.com/thulium-dev/thulium.git
cd thulium
```

### Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### Install Dependencies

```bash
# Development installation
pip install -e ".[dev]"

# With GPU support
pip install -e ".[dev,gpu]"
```

### Verify Installation

```bash
python -c "import thulium; print(thulium.__version__)"
pytest tests/ -v
```

## Project Structure

```
thulium/
├── thulium/          # Main package
│   ├── api/          # High-level API
│   ├── data/         # Data loading
│   ├── models/       # Neural networks
│   ├── pipeline/     # End-to-end pipelines
│   ├── training/     # Training utilities
│   ├── evaluation/   # Metrics
│   ├── xai/          # Explainability
│   └── cli/          # Command line
├── tests/            # Test suite
├── docs/             # Documentation
├── examples/         # Usage examples
└── config/           # Configuration files
```

## Development Workflow

### 1. Create Branch

```bash
git checkout -b feature/your-feature
```

### 2. Make Changes

Follow the [Style Guide](style_guide.md).

### 3. Run Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_metrics.py -v

# With coverage
pytest --cov=thulium tests/
```

### 4. Run Linters

```bash
# Type checking
mypy thulium/

# Code style
ruff check thulium/

# Import sorting
isort --check-only thulium/
```

### 5. Format Code

```bash
ruff format thulium/
isort thulium/
```

### 6. Submit PR

```bash
git push origin feature/your-feature
```

## Testing

### Unit Tests

```python
# tests/test_metrics.py
import pytest
from thulium.evaluation.metrics import cer

def test_cer_identical():
    assert cer("hello", "hello") == 0.0

def test_cer_different():
    assert cer("hello", "hallo") == 0.2
```

### Integration Tests

```python
# tests/test_pipeline.py
def test_pipeline_e2e(sample_image):
    from thulium import recognize_image
    result = recognize_image(sample_image, language="en")
    assert result.text is not None
```

## Documentation

### Build Docs Locally

```bash
cd docs
mkdocs serve
```

### Write Documentation

- Use Markdown with Google style
- Include code examples
- Add cross-references

## See Also

- [Style Guide](style_guide.md) — Code style
- [Contributing](../../CONTRIBUTING.md) — Contribution process
