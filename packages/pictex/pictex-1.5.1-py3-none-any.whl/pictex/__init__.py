"""
pictex: A Python library for creating complex visual compositions and beautifully styled images.
"""

from . import __skia_init
__skia_init.prime_skia_icu_engine()

from .builders import Canvas, Text, Row, Column, Image, Element
from .models.public import *
from .bitmap_image import BitmapImage
from .vector_image import VectorImage

__version__ = "1.5.1"

__all__ = [
    "Canvas", "Text", "Row", "Column", "Image", "Element",
    
    "Shadow", "OutlineStroke",
    "Style",
    "FontStyle", "FontWeight", "FontSmoothing", "TextAlign", "TextWrap",
    "PaintSource",
    "SolidColor", "NamedColor",
    "LinearGradient",
    "RadialGradient",
    "SweepGradient",
    "TwoPointConicalGradient",
    "TextDecoration",
    "CropMode",
    "Box",
    "Position", "PositionMode",
    "SizeValue", "SizeValueMode",
    "Margin", "Padding", "HorizontalDistribution", "VerticalAlignment", "HorizontalAlignment", "VerticalDistribution",
    "BackgroundImage", "BackgroundImageSizeMode",
    "Border", "BorderStyle", "BorderRadiusValue", "BorderRadius",
    "RenderNode",
    "NodeType",

    "BitmapImage",
    "VectorImage",
]