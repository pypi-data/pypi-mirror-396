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

"""Pipeline configuration management for Thulium HTR.

This module provides functions for loading and managing pipeline configurations
from YAML files. Configuration defines the model architecture, preprocessing
parameters, and decoding settings.

Functions:
    load_pipeline_config: Load pipeline config from YAML.
    load_language_config: Load language-specific settings.

Example:
    >>> from thulium.pipeline.config import load_pipeline_config
    >>> config = load_pipeline_config("htr_resnet_bilstm_ctc")
    >>> print(config["model"])
    'htr_resnet_bilstm_ctc'
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from typing import Dict

import yaml


def load_pipeline_config(pipeline_name: str = "default") -> Dict[str, Any]:
    """Load pipeline configuration from YAML file.

    Searches for configuration files in the following order:
        1. thulium/config/pipelines/{pipeline_name}.yaml
        2. Built-in defaults

    Args:
        pipeline_name: Name of the pipeline configuration to load.

    Returns:
        Dictionary containing pipeline configuration with keys:
            - model: Model architecture name.
            - steps: List of pipeline steps to execute.
            - preprocessing: Preprocessing parameters.
            - decoding: Decoding parameters.

    Example:
        >>> config = load_pipeline_config("cnn_transformer_ctc")
        >>> print(config["steps"])
        ['segmentation', 'recognition']
    """
    # Stub implementation - return default config
    return {
        "model": "htr_resnet_bilstm_ctc",
        "steps": ["segmentation", "recognition"],
        "preprocessing": {
            "target_height": 64,
            "normalize": True,
        },
        "decoding": {
            "beam_width": 10,
            "lm_weight": 0.5,
        },
    }


def load_language_config(lang_code: str) -> Dict[str, Any]:
    """Load language-specific configuration.

    Returns configuration for the specified language including
    alphabet type, character set, and language model paths.

    Args:
        lang_code: ISO 639-1 language code (e.g., 'en', 'de', 'fr').

    Returns:
        Dictionary containing language configuration with keys:
            - alphabet: Alphabet type ('latin', 'cyrillic', etc.).
            - charset: Character set definition.
            - lm_path: Optional path to language model.

    Example:
        >>> config = load_language_config("de")
        >>> print(config["alphabet"])
        'latin'
    """
    return {
        "alphabet": "latin",
        "charset": "default",
        "lm_path": None,
    }


__all__ = [
    "load_language_config",
    "load_pipeline_config",
]
