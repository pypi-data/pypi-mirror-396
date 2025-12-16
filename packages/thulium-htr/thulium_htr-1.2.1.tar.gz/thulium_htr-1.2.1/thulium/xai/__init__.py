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

"""Explainable AI tools for Thulium HTR.

This module provides interpretability and visualization tools to explain
model predictions, analyze recognition errors, and understand model behavior.

Submodules:
    saliency: Gradient-based saliency map generation.
    attention_viz: Attention map visualization utilities.
    confidence_analysis: Confidence calibration and analysis.
    error_analysis: Character-level error analysis tools.

Classes:
    SaliencyGenerator: Generate saliency maps for model interpretability.
    SaliencyConfig: Configuration for saliency map generation.

Example:
    Generating saliency maps:

    >>> from thulium.xai import SaliencyGenerator, SaliencyConfig
    >>> config = SaliencyConfig(method="integrated_gradients")
    >>> generator = SaliencyGenerator(model, config=config)
    >>> saliency_map = generator.compute(image, target_text="hello")
    >>> generator.visualize(image, saliency_map).save("saliency.png")
"""

from __future__ import annotations

from thulium.xai.saliency import SaliencyConfig
from thulium.xai.saliency import SaliencyGenerator

__all__ = [
    "SaliencyConfig",
    "SaliencyGenerator",
]
