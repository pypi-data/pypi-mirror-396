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

"""Neural network model architectures for Thulium HTR.

This module provides the model building blocks for handwriting text recognition,
including backbone networks, sequence modeling heads, and decoder components.
The modular architecture allows mixing and matching components for different
use cases and performance requirements.

Submodules:
    backbones: Feature extraction networks (CNN, ViT).
    heads: Sequence modeling heads (LSTM, Transformer).
    decoders: Output decoders (CTC, Attention).
    language_models: Language model components for decoding.
    segmentation: Text line and word segmentation models.
    wrappers: High-level model wrappers.

Model Architectures:
    CNN-LSTM-CTC: Classic architecture for efficient inference.
        Best for: Real-time applications, limited compute.
    CNN-Transformer-CTC: Self-attention for longer sequences.
        Best for: Balanced accuracy/speed, medium-length text.
    ViT-Transformer-Seq2Seq: State-of-the-art Vision Transformer.
        Best for: Maximum accuracy, unconstrained compute.

Example:
    Building a custom model:

    >>> from thulium.models.backbones import ResNetBackbone
    >>> from thulium.models.heads import LSTMHead
    >>> from thulium.models.decoders import CTCDecoder
    >>>
    >>> backbone = ResNetBackbone(in_channels=1, output_channels=512)
    >>> head = LSTMHead(input_size=512, hidden_size=256)
    >>> decoder = CTCDecoder(vocab_size=100)
"""

from __future__ import annotations

__all__: list[str] = []
