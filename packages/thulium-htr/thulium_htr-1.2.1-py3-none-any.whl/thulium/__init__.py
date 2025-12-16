# Copyright 2025 Thulium Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Thulium: State-of-the-art multilingual handwriting text recognition.

Thulium is a production-grade Python library for handwriting text recognition
(HTR) supporting 56+ languages across Latin, Cyrillic, Arabic, CJK, and Indic
scripts. The library provides a complete pipeline from raw image input to
structured text output, with support for various model architectures,
training utilities, and evaluation tools.

Key Features:
    - Multiple model architectures: CNN-LSTM-CTC, CNN-Transformer-CTC,
      ViT-Transformer-Seq2Seq with capacity-scaled variants (tiny to large).
    - Comprehensive language support with script-specific preprocessing
      and language model integration.
    - Advanced training utilities: early stopping, checkpointing, mixed
      precision training, and curriculum learning.
    - Production-ready evaluation: CER/WER metrics, calibration analysis,
      robustness testing, and comprehensive benchmarking.
    - Explainability tools: attention visualization, saliency maps,
      confidence analysis, and error attribution.

Modules:
    api: High-level recognition API for single images and batches.
    cli: Command-line interface for training, evaluation, and inference.
    data: Dataset loaders, transforms, and language profile definitions.
    evaluation: Metrics, benchmarking, and reporting utilities.
    models: Neural network architectures (backbones, heads, decoders).
    pipeline: End-to-end recognition pipelines.
    training: Training loops, losses, optimizers, and schedulers.
    xai: Explainability and interpretability tools.

Example:
    Basic text recognition from an image file:

    >>> from thulium.api import recognize
    >>> text = recognize("handwriting.png", language="en")
    >>> print(text)
    'Hello World'

    Batch recognition with confidence scores:

    >>> from thulium.api import recognize_batch
    >>> results = recognize_batch(
    ...     ["img1.png", "img2.png"],
    ...     language="de",
    ...     return_confidence=True,
    ... )
    >>> for result in results:
    ...     print(f"{result.text} ({result.confidence:.2%})")

For more information, see https://github.com/olaflaitinen/Thulium.
"""

from __future__ import annotations

from thulium.version import __version__

__all__ = ["__version__"]
