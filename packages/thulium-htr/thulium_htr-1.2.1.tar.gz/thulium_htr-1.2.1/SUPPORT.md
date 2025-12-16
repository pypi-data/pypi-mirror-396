# Support

## Getting Help

### Documentation

Start with our documentation:

- [Getting Started](docs/getting_started.md) — Installation and quick start
- [API Reference](docs/api/reference.md) — Complete API documentation
- [FAQ](#frequently-asked-questions) — Common questions

### Community Support

- [GitHub Discussions](https://github.com/thulium-dev/thulium/discussions) — Questions and ideas
- [GitHub Issues](https://github.com/thulium-dev/thulium/issues) — Bug reports

### Before Asking

1. Search existing issues and discussions
2. Check the documentation
3. Prepare a minimal reproducible example

## Frequently Asked Questions

### Installation

**Q: Why do I get a "torch not found" error?**

A: Install PyTorch separately first:
```bash
pip install torch torchvision
pip install thulium
```

**Q: How do I use GPU acceleration?**

A: Install with GPU extras:
```bash
pip install thulium[gpu]
```

### Usage

**Q: What languages are supported?**

A: 52+ languages. See [Language Support](docs/models/language_support.md).

**Q: How do I improve accuracy?**

A: Try:
1. Use a larger model (`thulium-large`)
2. Enable language model (`use_language_model=True`)
3. Preprocess images (deskew, binarize)

**Q: Why is inference slow?**

A: Ensure GPU is detected:
```python
import torch
print(torch.cuda.is_available())  # Should be True
```

### Training

**Q: How much data do I need?**

A: Minimum recommendations:
- Fine-tuning: 1,000+ samples
- Training from scratch: 10,000+ samples

**Q: Can I train on my own alphabet?**

A: Yes, see [Training Guide](docs/training/training_guide.md).

## Reporting Issues

When reporting bugs, include:

1. Thulium version: `python -c "import thulium; print(thulium.__version__)"`
2. Python version: `python --version`
3. OS and hardware
4. Full error traceback
5. Minimal code to reproduce

## Feature Requests

Open a [GitHub Discussion](https://github.com/thulium-dev/thulium/discussions)
with the "Ideas" category.
