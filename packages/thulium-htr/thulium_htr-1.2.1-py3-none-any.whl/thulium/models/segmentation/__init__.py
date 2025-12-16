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

"""Segmentation models for HTR preprocessing.

This module provides neural network models for text line and word segmentation,
which are essential preprocessing steps for handwriting text recognition.

Submodules:
    line_segmentation: Text line detection and extraction.
    word_segmentation: Word boundary detection.

Classes:
    LineSegmenter: U-Net based line segmentation model.
    WordSegmenter: Word boundary detection model.

Example:
    >>> from thulium.models.segmentation import LineSegmenter
    >>> segmenter = LineSegmenter(in_channels=3)
    >>> line_mask = segmenter(page_image)
"""

from __future__ import annotations

__all__: list[str] = []
