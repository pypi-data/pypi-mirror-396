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

"""End-to-end HTR model wrapper.

This module provides the HTRModel class that composes backbone, sequence head,
and decoder components into a complete end-to-end HTR system.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

import torch
import torch.nn as nn
import yaml

from thulium.models.backbones.cnn_backbones import ResNetBackbone
from thulium.models.sequence.lstm_heads import BiLSTMHead
from thulium.models.decoders.ctc_decoder import CTCDecoder

logger = logging.getLogger(__name__)


class HTRModel(nn.Module):
    """End-to-end Handwritten Text Recognition Model.

    Composes a backbone (feature extractor), sequence head (context modeling),
    and decoder (alignment and prediction) into a unified model for HTR.

    Architecture:
        Image -> Backbone -> Sequence Head -> Decoder -> Text

    Attributes:
        backbone: CNN or ViT feature extractor.
        head: BiLSTM or Transformer sequence model.
        decoder: CTC or attention-based decoder.
        criterion: Training loss function.

    Example:
        >>> model = HTRModel(num_classes=100)
        >>> images = torch.randn(4, 3, 64, 256)
        >>> log_probs = model(images)  # (T, B, num_classes+1)
    """

    def __init__(
        self,
        num_classes: int = 100,
        backbone_config: Optional[Dict[str, Any]] = None,
        head_config: Optional[Dict[str, Any]] = None,
        decoder_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the HTR model.

        Args:
            num_classes: Number of output classes (vocabulary size).
            backbone_config: Configuration for the backbone network.
            head_config: Configuration for the sequence head.
            decoder_config: Configuration for the decoder.
        """
        super().__init__()

        backbone_config = backbone_config or {}
        head_config = head_config or {}
        decoder_config = decoder_config or {}

        # Backbone (Feature Extractor)
        backbone_channels = backbone_config.get("output_channels", 256)
        self.backbone = ResNetBackbone(
            config_name=backbone_config.get("config_name", "resnet_small"),
        )

        # Sequence Head (Context Modeling)
        hidden_size = head_config.get("hidden_size", 256)
        self.head = BiLSTMHead(
            input_size=self.backbone.output_channels,
            hidden_size=hidden_size,
            num_layers=head_config.get("num_layers", 2),
            dropout=head_config.get("dropout", 0.1),
        )

        # Decoder (Alignment & Prediction)
        self.decoder = CTCDecoder(
            input_size=self.head.output_dim,
            num_classes=num_classes,
            blank_index=0,
        )

        # Loss Function
        self.criterion = nn.CTCLoss(blank=0, zero_infinity=True)

        logger.info(
            "Initialized HTRModel: backbone=%s, hidden=%d, classes=%d",
            backbone_config.get("config_name", "default"),
            hidden_size,
            num_classes,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass for inference.

        Args:
            x: Input images of shape (B, C, H, W).

        Returns:
            Log-probabilities of shape (T, B, num_classes+1) for CTC.
        """
        # Feature extraction
        features = self.backbone(x)  # (B, C, H', W')

        # Collapse height dimension for sequence modeling
        B, C, H, W = features.shape
        features = features.mean(dim=2)  # (B, C, W)
        features = features.transpose(1, 2)  # (B, W, C)

        # Sequence modeling
        sequence, _ = self.head(features)  # (B, W, hidden*2)

        # Decoding
        log_probs = self.decoder(sequence)  # (B, W, num_classes+1)

        # Transpose for CTC: (T, B, C)
        log_probs = log_probs.transpose(0, 1)

        return log_probs

    def training_step(
        self,
        images: torch.Tensor,
        targets: torch.Tensor,
        target_lengths: torch.Tensor,
    ) -> Dict[str, torch.Tensor]:
        """Perform a single training step.

        Args:
            images: Input images of shape (B, C, H, W).
            targets: Flattened target sequences.
            target_lengths: Length of each target sequence.

        Returns:
            Dictionary containing the loss value.
        """
        log_probs = self(images)  # (T, B, C)
        T, B, _ = log_probs.shape
        input_lengths = torch.full(
            size=(B,), fill_value=T, dtype=torch.long, device=images.device
        )

        loss = self.criterion(log_probs, targets, input_lengths, target_lengths)
        return {"loss": loss}

    def validation_step(
        self,
        images: torch.Tensor,
        targets: torch.Tensor,
        target_lengths: torch.Tensor,
    ) -> Dict[str, Any]:
        """Perform a single validation step.

        Args:
            images: Input images of shape (B, C, H, W).
            targets: Flattened target sequences.
            target_lengths: Length of each target sequence.

        Returns:
            Dictionary containing loss and metrics.
        """
        log_probs = self(images)  # (T, B, C)
        T, B, _ = log_probs.shape
        input_lengths = torch.full(
            size=(B,), fill_value=T, dtype=torch.long, device=images.device
        )

        loss = self.criterion(log_probs, targets, input_lengths, target_lengths)

        # Decode predictions
        decoded_preds = self.decoder.decode_greedy(log_probs.transpose(0, 1))

        return {"loss": loss, "predictions": decoded_preds}

    @classmethod
    def from_config(cls, config_path: str) -> HTRModel:
        """Create model from a YAML configuration file.

        Args:
            config_path: Path to the YAML configuration file.

        Returns:
            Configured HTRModel instance.
        """
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)

        model_cfg = cfg.get("model", {})
        return cls(
            num_classes=model_cfg.get("num_classes", 100),
            backbone_config=model_cfg.get("backbone", {}),
            head_config=model_cfg.get("head", {}),
            decoder_config=model_cfg.get("decoder", {}),
        )
