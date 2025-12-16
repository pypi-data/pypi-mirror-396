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

"""High-level recognition API for Thulium HTR.

This module provides simplified interfaces for text recognition from images,
abstracting away model loading, preprocessing, and decoding complexity. It
serves as the primary entry point for users who want quick and easy access
to Thulium's handwriting recognition capabilities.

Functions:
    recognize: Recognize text from a single handwriting image.
    recognize_batch: Recognize text from multiple images with batched inference.
    transcribe: Alias for recognize (semantic alternative).
    transcribe_batch: Alias for recognize_batch (semantic alternative).

Classes:
    RecognitionResult: Structured result containing text and confidence scores.

Example:
    Basic usage with a single image:

    >>> from thulium.api import recognize
    >>> text = recognize("handwriting.png", language="en")
    >>> print(text)
    'Hello World'

    Getting confidence scores along with the text:

    >>> result = recognize("sample.png", return_confidence=True)
    >>> print(f"Text: {result.text}, Confidence: {result.confidence:.2%}")
    'Text: Hello World, Confidence: 95.32%'

    Batch processing multiple images:

    >>> from thulium.api import recognize_batch
    >>> texts = recognize_batch(["img1.png", "img2.png"], language="de")
    >>> for text in texts:
    ...     print(text)
"""

from __future__ import annotations

from thulium.api.recognition import RecognitionResult
from thulium.api.recognition import recognize
from thulium.api.recognition import recognize_batch
from thulium.api.recognition import transcribe
from thulium.api.recognition import transcribe_batch

__all__ = [
    "RecognitionResult",
    "recognize",
    "recognize_batch",
    "transcribe",
    "transcribe_batch",
]
