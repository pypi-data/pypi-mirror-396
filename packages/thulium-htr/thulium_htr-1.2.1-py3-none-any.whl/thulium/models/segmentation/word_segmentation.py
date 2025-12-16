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

"""Word Segmentation Module.

This module provides models for segmenting individual words within a text line.
Accurate word segmentation is crucial for word-based recognition pipelines
and for handling languages where spaces are not explicit delimiters.

Architecture:
    1D-U-Net: Treating the line as a 1D sequence and predicting word boundaries.
    Alternative: Regression head on top of a CNN backbone to predict bounding boxes.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from thulium.models.sequence.lstm_heads import BiLSTMHead


class WordBoundaryPredictor(nn.Module):
    """Predicts word boundaries from line images.

    This model treats word segmentation as a sequence labeling task.
    It inputs a text line image and outputs a probability sequence indicating
    whether each column (or frame) corresponds to a word character, space, or boundary.

    Architecture:
        CNN Backbone (Feature Extractor) -> BiLSTM (Context) -> Linear (Classifier)
    """

    def __init__(
        self,
        input_channels: int = 3,
        hidden_size: int = 128,
        num_layers: int = 2,
    ) -> None:
        """Initialize the word boundary predictor.

        Args:
            input_channels: Number of input image channels.
            hidden_size: LSTM hidden state size.
            num_layers: Number of LSTM layers.
        """
        super().__init__()

        # Simple CNN feature extractor for 1D sequence generation
        self.cnn = nn.Sequential(
            nn.Conv2d(input_channels, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(4, 2)),  # Striding H=4, W=2
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(4, 2)),  # Pooling vertical mostly
        )

        self.lstm = BiLSTMHead(
            input_size=128,  # Assuming H collapsed to 1 after pooling or we pool it
            hidden_size=hidden_size,
            num_layers=num_layers,
        )

        # Output: 3 classes (0=Background/Space, 1=Word)
        self.classifier = nn.Linear(hidden_size * 2, 2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x: Input line image (B, C, H, W).

        Returns:
            Logits (B, W', 2) where W' is reduced width.
        """
        # CNN features
        features = self.cnn(x)  # (B, 128, H', W')

        # Collapse height
        features = features.mean(dim=2)  # (B, 128, W')
        features = features.transpose(1, 2)  # (B, W', 128)

        # Sequence modeling
        seq_features, _ = self.lstm(features)

        # Classification
        logits = self.classifier(seq_features)

        return logits
