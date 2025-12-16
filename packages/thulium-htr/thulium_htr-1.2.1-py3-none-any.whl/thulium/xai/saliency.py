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

"""Saliency map generation for HTR model interpretability.

This module provides tools to compute and visualize saliency maps,
showing which input pixels influence model predictions.

Methods:
    - Gradient saliency
    - Integrated gradients
    - SmoothGrad
    - GradCAM for attention visualization

Example:
    >>> from thulium.xai import SaliencyGenerator
    >>> generator = SaliencyGenerator(model)
    >>> saliency_map = generator.compute_gradient_saliency(image)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List
from typing import Literal
from typing import Optional
from typing import Tuple

import numpy as np

logger = logging.getLogger(__name__)

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available. Saliency generation will be limited.")


@dataclass
class SaliencyConfig:
    """Configuration for saliency map generation.
    
    Attributes:
        method: Saliency method ('gradient', 'integrated', 'smoothgrad', 'gradcam').
        num_steps: Number of integration steps for integrated gradients.
        noise_level: Noise std for SmoothGrad.
        num_samples: Number of samples for SmoothGrad.
        absolute: Use absolute value of gradients.
        normalize: Normalize output to [0, 1].
    """
    method: str = "gradient"
    num_steps: int = 50
    noise_level: float = 0.1
    num_samples: int = 25
    absolute: bool = True
    normalize: bool = True


class SaliencyGenerator:
    """
    Generator for saliency maps explaining model predictions.
    
    Saliency maps highlight input regions that most influence the model's
    output, providing visual explanations for predictions.
    
    Mathematical Formulation:
    
    **Gradient Saliency:**
    
    For input x and output y:
    
        S(x) = |\\frac{\\partial y}{\\partial x}|
    
    **Integrated Gradients:**
    
    For baseline x' and input x:
    
        IG(x) = (x - x') \\cdot \\int_{\\alpha=0}^{1} \\frac{\\partial F(x' + \\alpha(x-x'))}{\\partial x} d\\alpha
    
    **SmoothGrad:**
    
    Average gradients over noisy samples:
    
        SG(x) = \\frac{1}{N} \\sum_{i=1}^{N} \\frac{\\partial y}{\\partial (x + \\epsilon_i)}
    
    where \\epsilon_i \\sim \\mathcal{N}(0, \\sigma^2)
    
    Attributes:
        model: HTR model for analysis.
        config: Saliency generation configuration.
    """
    
    def __init__(
        self,
        model,
        config: Optional[SaliencyConfig] = None,
    ):
        """Initialize saliency generator.
        
        Args:
            model: PyTorch model for saliency analysis.
            config: Configuration for saliency computation.
        """
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch required for saliency generation")
        
        self.model = model
        self.config = config or SaliencyConfig()
        self.model.eval()
    
    def compute(
        self,
        image: "torch.Tensor",
        target_idx: Optional[int] = None,
        method: Optional[str] = None,
    ) -> np.ndarray:
        """
        Compute saliency map for input image.
        
        Args:
            image: Input image tensor [1, C, H, W].
            target_idx: Target class index. If None, uses argmax.
            method: Override config method.
            
        Returns:
            Saliency map as numpy array [H, W].
        """
        method = method or self.config.method
        
        if method == "gradient":
            return self.compute_gradient_saliency(image, target_idx)
        elif method == "integrated":
            return self.compute_integrated_gradients(image, target_idx)
        elif method == "smoothgrad":
            return self.compute_smoothgrad(image, target_idx)
        elif method == "gradcam":
            return self.compute_gradcam(image, target_idx)
        else:
            raise ValueError(f"Unknown saliency method: {method}")
    
    def compute_gradient_saliency(
        self,
        image: "torch.Tensor",
        target_idx: Optional[int] = None,
    ) -> np.ndarray:
        """
        Compute vanilla gradient saliency.
        
        Args:
            image: Input image tensor.
            target_idx: Target class index.
            
        Returns:
            Gradient saliency map.
        """
        image = image.clone().requires_grad_(True)
        
        output = self.model(image)
        
        if target_idx is None:
            target_idx = output.argmax(dim=-1)[0, 0].item()
        
        # Backward pass
        self.model.zero_grad()
        target = output[0, :, target_idx].sum()
        target.backward()
        
        # Get gradient
        gradient = image.grad.data.cpu().numpy()
        
        # Process
        saliency = self._process_saliency(gradient)
        return saliency
    
    def compute_integrated_gradients(
        self,
        image: "torch.Tensor",
        target_idx: Optional[int] = None,
        baseline: Optional["torch.Tensor"] = None,
    ) -> np.ndarray:
        """
        Compute integrated gradients.
        
        Args:
            image: Input image tensor.
            target_idx: Target class index.
            baseline: Baseline image (default: zeros).
            
        Returns:
            Integrated gradients saliency map.
        """
        if baseline is None:
            baseline = torch.zeros_like(image)
        
        # Create interpolation steps
        steps = self.config.num_steps
        alphas = torch.linspace(0, 1, steps).view(-1, 1, 1, 1)
        
        # Expand for batch processing
        delta = image - baseline
        interpolated = baseline + alphas * delta
        
        # Compute gradients at each step
        gradients = []
        for interp in interpolated:
            interp = interp.unsqueeze(0).requires_grad_(True)
            output = self.model(interp)
            
            if target_idx is None:
                target_idx = output.argmax(dim=-1)[0, 0].item()
            
            self.model.zero_grad()
            target = output[0, :, target_idx].sum()
            target.backward()
            
            gradients.append(interp.grad.data.cpu())
        
        # Average gradients and multiply by input difference
        avg_gradients = torch.stack(gradients).mean(dim=0)
        integrated = (delta.cpu() * avg_gradients).numpy()
        
        return self._process_saliency(integrated)
    
    def compute_smoothgrad(
        self,
        image: "torch.Tensor",
        target_idx: Optional[int] = None,
    ) -> np.ndarray:
        """
        Compute SmoothGrad saliency.
        
        Args:
            image: Input image tensor.
            target_idx: Target class index.
            
        Returns:
            SmoothGrad saliency map.
        """
        n_samples = self.config.num_samples
        noise_level = self.config.noise_level
        
        gradients = []
        for _ in range(n_samples):
            # Add noise
            noise = torch.randn_like(image) * noise_level
            noisy_image = (image + noise).requires_grad_(True)
            
            output = self.model(noisy_image)
            
            if target_idx is None:
                target_idx = output.argmax(dim=-1)[0, 0].item()
            
            self.model.zero_grad()
            target = output[0, :, target_idx].sum()
            target.backward()
            
            gradients.append(noisy_image.grad.data.cpu())
        
        avg_gradient = torch.stack(gradients).mean(dim=0).numpy()
        return self._process_saliency(avg_gradient)
    
    def compute_gradcam(
        self,
        image: "torch.Tensor",
        target_idx: Optional[int] = None,
        layer_name: Optional[str] = None,
    ) -> np.ndarray:
        """
        Compute GradCAM visualization.
        
        Args:
            image: Input image tensor.
            target_idx: Target class index.
            layer_name: Name of layer for CAM (default: last conv).
            
        Returns:
            GradCAM heatmap.
        """
        # Hook for capturing activations and gradients
        activations = {}
        gradients = {}
        
        def forward_hook(module, input, output):
            activations['value'] = output
        
        def backward_hook(module, grad_input, grad_output):
            gradients['value'] = grad_output[0]
        
        # Find target layer
        target_layer = None
        for name, module in self.model.named_modules():
            if isinstance(module, (nn.Conv2d,)):
                target_layer = module
                target_name = name
        
        if target_layer is None:
            logger.warning("No conv layer found for GradCAM")
            return self.compute_gradient_saliency(image, target_idx)
        
        # Register hooks
        handle_fwd = target_layer.register_forward_hook(forward_hook)
        handle_bwd = target_layer.register_full_backward_hook(backward_hook)
        
        try:
            # Forward pass
            output = self.model(image)
            
            if target_idx is None:
                target_idx = output.argmax(dim=-1)[0, 0].item()
            
            # Backward pass
            self.model.zero_grad()
            target = output[0, :, target_idx].sum()
            target.backward()
            
            # Compute CAM
            activation = activations['value']
            gradient = gradients['value']
            
            weights = gradient.mean(dim=(2, 3), keepdim=True)
            cam = (weights * activation).sum(dim=1, keepdim=True)
            cam = F.relu(cam)
            
            # Upsample to input size
            cam = F.interpolate(
                cam, size=image.shape[2:], 
                mode='bilinear', align_corners=False
            )
            
            cam = cam.squeeze().cpu().numpy()
            
        finally:
            handle_fwd.remove()
            handle_bwd.remove()
        
        return self._process_saliency(cam, squeeze=False)
    
    def _process_saliency(
        self,
        saliency: np.ndarray,
        squeeze: bool = True,
    ) -> np.ndarray:
        """Process raw saliency values."""
        if squeeze and saliency.ndim > 2:
            # Sum over channels
            if saliency.ndim == 4:
                saliency = saliency[0]
            saliency = np.abs(saliency).sum(axis=0)
        
        if self.config.absolute:
            saliency = np.abs(saliency)
        
        if self.config.normalize:
            smin, smax = saliency.min(), saliency.max()
            if smax > smin:
                saliency = (saliency - smin) / (smax - smin)
        
        return saliency.astype(np.float32)


# Exports
__all__ = [
    'SaliencyGenerator',
    'SaliencyConfig',
]
