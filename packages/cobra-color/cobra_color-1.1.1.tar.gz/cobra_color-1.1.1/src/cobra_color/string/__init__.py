# src/cobra_color/string/__init__.py
"""
String utilities for :pkg:`cobra_color` package.

Functions
---------
- :func:`cstr()`: Generate an easy-to-use `rich str` instance with perfect support for :class:`str`.
- :func:`to_ansi()`: Convert an object to an ANSI formatted :class:`ExtStr`.
- :func:`to_plain()`: Convert an object to a plain :class:`str`.
- :func:`to_cstr()`: Convert an object to a :class:`ColorStr`.
- :func:`ansi_to_segments()`: Parse an ANSI formatted string into a list of :class:`ColorSeg` segments.
Classes
-------
- :class:`ColorStr`: An easy-to-use `rich str` class with perfect support for :class:`str`.
- :class:`ExtStr`: An `extended str` class that extends the built-in :class:`str` class.
- :class:`ColorSeg`: A segment of color and style information for :class:`ColorStr`.
"""

from ._color import (cstr, to_ansi, to_plain, to_cstr, ColorStr)
from ._extension import ExtStr
from ._segment import (ColorSeg, ansi_to_segments)

__all__ = [
    "cstr",
    "to_ansi",
    "to_plain",
    "to_cstr",
    "ColorStr",
    "ExtStr",
    "ColorSeg",
    "ansi_to_segments"
]
