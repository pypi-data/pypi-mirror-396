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

"""Line Segmentation Module for Document Layout Analysis.

This module provides deep learning models for segmenting text lines from
document images. It implements a U-Net architecture with a ResNet backbone
encoder, suitable for pixel-level binary classification (text line vs. background).

Architecture:
    Encoder: ResNet-style backbone (pre-trained or custom).
    Decoder: U-Net style upsampling with skip connections.
    Output: Binary segmentation map (probability of pixel belonging to a text line).
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from thulium.models.backbones.cnn_backbones import ResNetBackbone


class DoubleConv(nn.Module):
    """Double convolution block: (Conv -> BN -> ReLU) * 2."""

    def __init__(self, in_channels: int, out_channels: int) -> None:
        """Initialize the double convolution block.

        Args:
            in_channels: Number of input channels.
            out_channels: Number of output channels.
        """
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        return self.double_conv(x)


class UNetDecoderBlock(nn.Module):
    """U-Net decoder block with upsampling and skip connection."""

    def __init__(self, in_channels: int, out_channels: int) -> None:
        """Initialize decoder block.

        Args:
            in_channels: Number of input channels (from previous layer + skip).
            out_channels: Number of output channels.
        """
        super().__init__()
        self.up = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True)
        # Input channels are split between upsampled input and skip connection
        # We assume concatenation reduces channels by half for the convolution
        self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        """Forward pass with skip connection.

        Args:
            x1: Input from previous decoder layer.
            x2: Skip connection from encoder.

        Returns:
            Output tensor.
        """
        x1 = self.up(x1)

        # Handle size mismatch due to padding in encoder convolutions
        diffY = x2.size(2) - x1.size(2)
        diffX = x2.size(3) - x1.size(3)

        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2, diffY // 2, diffY - diffY // 2])

        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class LineSegmenter(nn.Module):
    """U-Net based Line Segmentation Model.

    Uses a ResNet backbone as the encoder and a U-Net decoder to generate
    pixel-wise segmentation maps for text lines.

    Attributes:
        encoder: ResNetBackbone for feature extraction.
        decoder_blocks: List of decoder blocks.
        final_conv: Final 1x1 convolution to produce class logits.
    """

    def __init__(
        self,
        in_channels: int = 3,
        num_classes: int = 1,
        backbone_name: str = "resnet18",
    ) -> None:
        """Initialize the line segmenter.

        Args:
            in_channels: Number of input image channels.
            num_classes: Number of output classes (1 for binary mask).
            backbone_name: Name of the ResNet backbone configuration.
        """
        super().__init__()

        # Encoder (ResNet Backbone)
        self.encoder = ResNetBackbone(
            in_channels=in_channels, config_name=backbone_name
        )
        
        # Get channel counts from backbone configuration
        # Assuming typical ResNet structure [64, 128, 256, 512]
        if backbone_name == "resnet18" or backbone_name == "resnet34":
             enc_channels = [64, 64, 128, 256, 512] # [stem, layer1, layer2, layer3, layer4]
        else:
             # Default generic fallback
             enc_channels = [64, 64, 128, 256, 512]

        self.up1 = UNetDecoderBlock(enc_channels[4] + enc_channels[3], 256)
        self.up2 = UNetDecoderBlock(256 + enc_channels[2], 128)
        self.up3 = UNetDecoderBlock(128 + enc_channels[1], 64)
        self.up4 = UNetDecoderBlock(64 + enc_channels[0], 64)

        self.final_conv = nn.Conv2d(64, num_classes, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass generating segmentation mask.

        Args:
            x: Input image tensor (B, C, H, W).

        Returns:
            Logits tensor (B, num_classes, H, W).
        """
        # Encoder path
        # We need to modify backbone forward to return intermediate features
        # For this implementation, we assume a custom forward logic or access to layers
        
        # Hack: manually running backbone layers to get skip connections
        # ideally ResNetBackbone would support returning intermediate features
        # We will assume ResNetBackbone structure: stem, stage1, stage2, stage3, stage4
        
        x0 = self.encoder.stem(x)    # Stride 2 or 4
        x1 = self.encoder.stage1(x0) # Stride 1 relative to x0
        x2 = self.encoder.stage2(x1) # Stride 2
        x3 = self.encoder.stage3(x2) # Stride 2
        x4 = self.encoder.stage4(x3) # Stride 2
        
        # Decoder path
        x = self.up1(x4, x3)
        x = self.up2(x, x2)
        x = self.up3(x, x1)
        x = self.up4(x, x0)
        
        logits = self.final_conv(x)
        
        # Upsample to original input size if needed
        # The U-Net above ends at 1/2 or 1/4 resolution depending on stem
        logits = F.interpolate(logits, scale_factor=2, mode="bilinear", align_corners=True) # Adjust scaling as needed
        # If input was H, W, stem reduced by 4, the up4 output is H/4. Two more upsamples needed or architecture adjust.
        # For simplicity in this demo, we interpolate to input size.
        if logits.shape[2:] != x.shape[2:]:
             logits = F.interpolate(logits, size=x.shape[2:], mode="bilinear", align_corners=True)

        return logits
