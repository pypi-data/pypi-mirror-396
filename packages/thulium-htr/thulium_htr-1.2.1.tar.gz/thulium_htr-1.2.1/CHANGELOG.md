# Changelog

All notable changes to Thulium are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2025-12-12

### Added
- **PyTorch Hub Support**: Load models directly via `torch.hub.load('olaflaitinen/Thulium', ...)`
- **Documentation Overhaul**: Complete rewrite of all documentation to Google Open Source standards
- **Interactive Notebooks**: Added Colab-ready notebooks for quickstart, benchmarking, and error analysis
- **Professional Standards**: Added SECURITY.md, SUPPORT.md, AUTHORS.md, and CITATION.cff
- **GitHub Automation**: Added workflows for documentation deployment and PyPI publishing

### Changed
- Standardized all Python files with proper type annotations (PEP 561 compliance)
- Updated repository structure to match professional Python library standards
- Improved error handling in CLI commands

## [1.2.0] - 2025-12-11

### Added
- Initial support for PyTorch Hub configuration
- Expanded language support to 52+ languages
- ONNX export for production deployment
- Confidence calibration utilities

## [1.1.0] - 2025-01-15

### Added
- ViT backbone support with patch-based encoding
- Transformer sequence heads as alternative to LSTM
- Attention decoder for language model integration
- 52+ language profiles with script-aware processing
- XAI module: saliency maps, attention visualization, error analysis
- Comprehensive benchmarking suite with per-language metrics
- Early stopping and checkpoint management utilities
- N-gram and neural language models for decoding

### Changed
- Upgraded minimum PyTorch version to 2.0+
- Refactored evaluation metrics with self-contained Levenshtein implementation
- Improved documentation to Google Python Style Guide standards

### Fixed
- Memory leak in batch decoding with long sequences
- Incorrect WER calculation for languages without spaces

## [1.0.0] - 2024-12-01

### Added
- Initial release
- ResNet CNN backbones (18, 34, 50 variants)
- BiLSTM sequence modeling
- CTC decoder with beam search
- Support for English, German, French, Spanish
- Basic CLI for recognition and training
- IAM and custom dataset loaders

### Security
- Input validation for all file operations
- Secure model loading with hash verification

---

[Unreleased]: https://github.com/thulium-dev/thulium/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/thulium-dev/thulium/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/thulium-dev/thulium/releases/tag/v1.0.0
