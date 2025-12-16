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

"""Attention map visualization for explainable AI.

This module provides utilities for visualizing attention weights from
Transformer and Seq2Seq models, enabling interpretation of model
behavior during handwriting recognition.

Classes:
    AttentionVisualizer: Overlay and grid visualization of attention maps.

Example:
    >>> from thulium.xai.attention_maps import AttentionVisualizer
    >>> blended = AttentionVisualizer.overlay_attention(image, attention_weights)
"""

from __future__ import annotations

import io
from typing import List
from typing import Optional
from typing import Union

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

class AttentionVisualizer:
    """
    Visualizes attention maps for Seq2Seq/Transformer models.
    """
    
    @staticmethod
    def overlay_attention(
        image: np.ndarray, 
        attention_weights: np.ndarray, 
        alpha: float = 0.6,
        colormap: int = cv2.COLORMAP_JET
    ) -> np.ndarray:
        """
        Overlay attention heatmap on the original image.
        
        Args:
            image: [H, W, 3] or [H, W] numpy array (uint8)
            attention_weights: [H, W] or [L] numpy array (0.0 to 1.0)
            alpha: Transparency of the heatmap
        
        Returns:
            Blended image [H, W, 3]
        """
        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
        H, W = image.shape[:2]
        
        # Resize attention mask to match image
        # Attention usually comes in smaller grid or sequence length 
        attn_resized = cv2.resize(attention_weights, (W, H))
        
        # Normalize to 0-255
        attn_norm = (attn_resized - np.min(attn_resized)) / (np.max(attn_resized) - np.min(attn_resized) + 1e-8)
        attn_uint8 = (attn_norm * 255).astype(np.uint8)
        
        # Apply colormap
        heatmap = cv2.applyColorMap(attn_uint8, colormap)
        
        # Blend
        blended = cv2.addWeighted(heatmap, alpha, image, 1 - alpha, 0)
        return blended

    @staticmethod
    def plot_attention_grid(
        image: np.ndarray,
        attentions: List[np.ndarray],
        tokens: List[str],
        save_path: Optional[str] = None
    ):
        """
        Plot a grid of attention maps, one for each predicted token.
        
        Args:
            image: Original input image
            attentions: List of attention weights [H', W'] for each token
            tokens: List of predicted tokens matching attentions
        """
        n = len(tokens)
        cols = 5
        rows = (n + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(15, 3 * rows))
        axes = axes.flatten()
        
        for i in range(n):
            ax = axes[i]
            blended = AttentionVisualizer.overlay_attention(image, attentions[i])
            ax.imshow(cv2.cvtColor(blended, cv2.COLOR_BGR2RGB))
            ax.set_title(f"Token: '{tokens[i]}'")
            ax.axis('off')
            
        # Hide empty subplots
        for i in range(n, len(axes)):
            axes[i].axis('off')
            
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            return fig
