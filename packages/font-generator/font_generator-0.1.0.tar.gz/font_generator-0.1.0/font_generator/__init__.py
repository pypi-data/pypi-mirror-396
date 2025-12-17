"""
Font Generator - A Python package for font manipulation and conversion.

This package provides tools for:
- Converting TTF fonts to SVG format
- Converting SVG files back to TTF fonts
- Adding handwritten effects to fonts
"""

__version__ = "0.1.0"
__author__ = "Chandra Bahadur Khadka"

from .handwritten import make_handwritten
from .ttf_to_svg import ttf_to_svg
from .svg_to_ttf import svg_to_ttf

__all__ = ['make_handwritten', 'ttf_to_svg', 'svg_to_ttf']
