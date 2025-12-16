from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional

@dataclass
class Word:
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int] # x, y, w, h

@dataclass
class Line:
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    words: List[Word] = field(default_factory=list)

@dataclass
class PageResult:
    full_text: str
    lines: List[Line]
    language: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for JSON serialization."""
        return {
            "full_text": self.full_text,
            "language": self.language,
            "lines": [
                {
                    "text": l.text,
                    "confidence": l.confidence,
                    "bbox": l.bbox,
                    "words": [{"text": w.text, "bbox": w.bbox} for w in l.words]
                }
                for l in self.lines
            ],
            "metadata": self.metadata
        }
