from dataclasses import dataclass
from typing import Optional
import skia

@dataclass
class TextRun:
    """Represents a segment of text that can be rendered with a single font."""
    text: str
    font: skia.Font
    blob: Optional[skia.TextBlob] = None
    width: float = 0.0

@dataclass
class Line:
    """Represents a full line composed of multiple TextRuns."""
    runs: list[TextRun]
    width: float
    height: float
    bounds: skia.Rect
