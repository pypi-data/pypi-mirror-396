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

"""Data loading and preprocessing utilities for Thulium HTR.

This module provides the data infrastructure for training and evaluating
handwriting recognition models. It includes dataset classes for common
HTR benchmarks, data loaders with efficient batching strategies, and
preprocessing utilities for image augmentation and text normalization.

Submodules:
    datasets: PyTorch Dataset implementations for IAM, RIMES, and custom
        data formats. Supports both line-level and word-level recognition.
    loaders: DataLoader factories with support for bucketing by sequence
        length and curriculum sampling strategies.
    transforms: Image preprocessing pipelines including resizing, padding,
        normalization, and augmentation (elastic distortion, noise injection).
    samplers: Custom sampling strategies for balanced training across
        different script types and difficulty levels.
    collate: Collation functions for variable-length image sequences,
        handling padding and batch construction.
    language_profiles: Character sets, tokenization rules, and language-
        specific configurations for 56+ supported languages.
    noise_injection: Data augmentation through realistic noise patterns
        including salt-and-pepper, Gaussian blur, and ink bleeding.

Classes:
    LanguageProfile: Language-specific configuration for character sets
        and preprocessing.

Functions:
    get_language_profile: Retrieve language configuration by ISO 639-1 code.
    list_supported_languages: List all supported language codes.

Example:
    Getting a language profile for English:

    >>> from thulium.data import get_language_profile, list_supported_languages
    >>> profile = get_language_profile("en")
    >>> print(f"{profile.name}: {profile.script}")
    'English: Latin'
    >>> print(f"Vocabulary size: {profile.get_vocab_size()}")
    'Vocabulary size: 80'

    Listing available languages:

    >>> languages = list_supported_languages()
    >>> print(f"Supported: {len(languages)} languages")
    'Supported: 56 languages'
"""

from __future__ import annotations

from thulium.data.language_profiles import get_language_profile
from thulium.data.language_profiles import LanguageProfile
from thulium.data.language_profiles import list_supported_languages

__all__ = [
    "LanguageProfile",
    "get_language_profile",
    "list_supported_languages",
]
