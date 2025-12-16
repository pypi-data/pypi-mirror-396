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

"""Type definitions for Thulium HTR API.

This module defines the core data structures used throughout the Thulium API
for representing recognition results at various granularity levels: individual
words, text lines, and complete pages. All types are designed for
JSON serialization and seamless integration with downstream processing.

Classes:
    BoundingBox: Immutable rectangular region coordinates for spatial layout.
    Word: Single word recognition result with confidence and position.
    Line: Text line recognition result containing words.
    PageResult: Full page recognition result with metadata.

Example:
    Creating and working with recognition results:

    >>> from thulium.api.types import BoundingBox, Line, PageResult
    >>> bbox = BoundingBox(x=10, y=20, width=100, height=30)
    >>> line = Line(text="Hello", confidence=0.95, bbox=bbox)
    >>> result = PageResult(
    ...     full_text="Hello",
    ...     lines=[line],
    ...     language="en",
    ... )
    >>> print(result.to_dict())
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple


@dataclass(frozen=True)
class BoundingBox:
    """Immutable rectangular bounding box coordinates.

    Represents a rectangular region in pixel coordinates, typically used
    for locating text elements within an image. The box is defined by its
    top-left corner (x, y) and dimensions (width, height).

    Attributes:
        x: Left edge x-coordinate in pixels.
        y: Top edge y-coordinate in pixels.
        width: Box width in pixels.
        height: Box height in pixels.

    Example:
        >>> bbox = BoundingBox(x=10, y=20, width=100, height=30)
        >>> coords = bbox.to_tuple()
        >>> print(coords)
        (10, 20, 100, 30)
    """

    x: int
    y: int
    width: int
    height: int

    def to_tuple(self) -> Tuple[int, int, int, int]:
        """Convert to (x, y, width, height) tuple format.

        Returns:
            A 4-tuple containing (x, y, width, height) coordinates.
        """
        return (self.x, self.y, self.width, self.height)

    @classmethod
    def from_tuple(cls, coords: Tuple[int, int, int, int]) -> BoundingBox:
        """Create BoundingBox from a coordinate tuple.

        Args:
            coords: A 4-tuple of (x, y, width, height) values.

        Returns:
            A new BoundingBox instance with the specified coordinates.

        Raises:
            ValueError: If coords does not contain exactly 4 elements.
        """
        if len(coords) != 4:
            raise ValueError(
                f"Expected 4 coordinates (x, y, width, height), got {len(coords)}"
            )
        return cls(x=coords[0], y=coords[1], width=coords[2], height=coords[3])


@dataclass
class Word:
    """Recognition result for a single word.

    Contains the recognized text, confidence score, spatial location,
    and optional per-character confidence values for detailed analysis.

    Attributes:
        text: Recognized text content of the word.
        confidence: Recognition confidence score in range [0.0, 1.0].
        bbox: Bounding box coordinates for spatial location.
        char_confidences: Optional per-character confidence scores.
            If provided, length should match len(text).

    Example:
        >>> from thulium.api.types import BoundingBox, Word
        >>> bbox = BoundingBox(x=10, y=20, width=50, height=15)
        >>> word = Word(
        ...     text="Hello",
        ...     confidence=0.98,
        ...     bbox=bbox,
        ...     char_confidences=[0.99, 0.97, 0.98, 0.99, 0.96],
        ... )
        >>> print(word.to_dict())
    """

    text: str
    confidence: float
    bbox: BoundingBox
    char_confidences: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation suitable for JSON encoding.
        """
        return {
            "text": self.text,
            "confidence": self.confidence,
            "bbox": self.bbox.to_tuple(),
            "char_confidences": self.char_confidences,
        }


@dataclass
class Line:
    """Recognition result for a text line.

    Represents a single line of text with its aggregate confidence score,
    spatial location, and optional word-level breakdown for detailed analysis.

    Attributes:
        text: Full text content of the line.
        confidence: Aggregate confidence score in range [0.0, 1.0].
        bbox: Bounding box of the entire line region.
        words: List of word-level recognition results. May be empty if
            word segmentation was not performed.

    Example:
        >>> from thulium.api.types import BoundingBox, Line
        >>> bbox = BoundingBox(x=10, y=20, width=200, height=30)
        >>> line = Line(text="Hello World", confidence=0.95, bbox=bbox)
        >>> print(line.text)
        'Hello World'
    """

    text: str
    confidence: float
    bbox: BoundingBox
    words: List[Word] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation suitable for JSON encoding.
        """
        return {
            "text": self.text,
            "confidence": self.confidence,
            "bbox": self.bbox.to_tuple(),
            "words": [word.to_dict() for word in self.words],
        }


@dataclass
class PageResult:
    """Recognition result for a full page or document.

    Contains the complete recognition output including full text, line-by-line
    breakdown, language information, and processing metadata. This is the
    primary output type returned by the HTR pipeline.

    Attributes:
        full_text: Complete text content of the page with lines joined by
            newline characters.
        lines: List of line-level recognition results in reading order.
        language: ISO 639-1 language code used for recognition (e.g., "en").
        confidence: Overall page confidence score in range [0.0, 1.0].
            Computed as average of line confidences.
        processing_time_ms: Total processing time in milliseconds.
        metadata: Additional metadata from the pipeline such as model name,
            device used, and preprocessing parameters.

    Example:
        >>> from thulium.api.types import PageResult
        >>> result = PageResult(
        ...     full_text="Hello World",
        ...     lines=[...],
        ...     language="en",
        ...     confidence=0.95,
        ...     processing_time_ms=123.4,
        ... )
        >>> print(f"Processed in {result.processing_time_ms:.1f}ms")
        'Processed in 123.4ms'
    """

    full_text: str
    lines: List[Line]
    language: str
    confidence: float = 0.0
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation suitable for JSON encoding with all
            nested objects also converted to dictionaries.
        """
        return {
            "full_text": self.full_text,
            "language": self.language,
            "confidence": self.confidence,
            "processing_time_ms": self.processing_time_ms,
            "lines": [line.to_dict() for line in self.lines],
            "metadata": self.metadata,
        }

    @property
    def word_count(self) -> int:
        """Count total words across all lines.

        Returns:
            Total number of words in the page.
        """
        return sum(len(line.words) for line in self.lines)

    @property
    def line_count(self) -> int:
        """Count total text lines.

        Returns:
            Number of text lines in the page.
        """
        return len(self.lines)


__all__ = [
    "BoundingBox",
    "Line",
    "PageResult",
    "Word",
]
