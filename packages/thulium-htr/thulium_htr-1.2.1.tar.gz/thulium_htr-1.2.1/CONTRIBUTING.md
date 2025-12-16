# Contributing to Thulium

Thank you for your interest in contributing to Thulium! This document provides
guidelines for contributing to the project.

## Code of Conduct

All contributors must adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Issues

Before filing an issue:

1. Search existing issues to avoid duplicates
2. Use the issue template and provide:
   - Thulium version (`thulium.__version__`)
   - Python version
   - Operating system
   - Minimal reproducible example
   - Full error traceback

### Submitting Changes

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes** following our style guide
4. **Write tests** for new functionality
5. **Run checks** before submitting:
   ```bash
   pytest tests/
   mypy thulium/
   ruff check thulium/
   ```
6. **Submit a pull request** with a clear description

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/thulium.git
cd thulium

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Style Guide

All code must follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

Key requirements:

- **Type annotations** for all public functions
- **Docstrings** with Args, Returns, Raises sections
- **Imports** ordered: `__future__`, stdlib, third-party, local
- **Line length** maximum 88 characters
- **`from __future__ import annotations`** in all modules

## Pull Request Checklist

- [ ] Code follows the style guide
- [ ] All tests pass locally
- [ ] New functionality includes tests
- [ ] Documentation updated if needed
- [ ] Changelog entry added for user-facing changes
- [ ] Commit messages are clear and descriptive

## Review Process

1. A maintainer will review your PR within 5 business days
2. Address any requested changes
3. Once approved, a maintainer will merge your PR

## License

By contributing, you agree that your contributions will be licensed under the
Apache 2.0 License.
