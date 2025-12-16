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

"""Recognition pipelines for Thulium HTR.

This module provides end-to-end recognition pipelines that combine
preprocessing, model inference, and postprocessing into unified workflows.
Pipelines abstract away the complexity of individual components, providing
a simple interface for text recognition.

Submodules:
    config: Pipeline configuration management.
    htr_pipeline: Main HTR pipeline implementation.
    segmentation_pipeline: Page layout analysis and line segmentation.
    form_pipeline: Structured form and table processing.
    multi_language_pipeline: Language-agnostic recognition.

Classes:
    HTRPipeline: Standard text-line recognition pipeline.

Example:
    Basic pipeline usage:

    >>> from thulium.pipeline import HTRPipeline
    >>> pipeline = HTRPipeline.from_pretrained("cnn_transformer_ctc_base")
    >>> result = pipeline.process(image, language="en")
    >>> print(result.full_text)
    'The quick brown fox'

    Custom configuration:

    >>> from thulium.pipeline import HTRPipeline
    >>> config = {"backbone": "resnet18", "decoder": "ctc"}
    >>> pipeline = HTRPipeline(config)
"""

from __future__ import annotations

__all__: list[str] = []
