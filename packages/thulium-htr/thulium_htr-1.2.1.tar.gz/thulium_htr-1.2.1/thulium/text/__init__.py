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

"""Text processing utilities for Thulium HTR.

This module provides text normalization and processing functions for
preprocessing ground truth labels and postprocessing model output.

Modules:
    normalization: Script-specific text normalization (Latin, Arabic, CJK).

Functions:
    normalize_text: Main normalization function with language-specific handling.
    normalize_unicode: Unicode canonicalization (NFC/NFD/NFKC/NFKD).
    normalize_whitespace: Whitespace standardization.
    normalize_punctuation: Punctuation normalization.
    strip_diacritics: Diacritical mark removal.

Typical usage example:
    >>> from thulium.text import normalize_text
    >>> normalized = normalize_text("Hello  World", language="en")
    >>> print(normalized)  # "Hello World"
"""

from thulium.text.normalization import (
    normalize_text,
    normalize_unicode,
    normalize_whitespace,
    normalize_punctuation,
    strip_diacritics,
    NormalizationConfig,
)

__all__ = [
    "normalize_text",
    "normalize_unicode",
    "normalize_whitespace",
    "normalize_punctuation",
    "strip_diacritics",
    "NormalizationConfig",
]
