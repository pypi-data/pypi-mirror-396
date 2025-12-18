# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
import os
import importlib.resources as pkg_resources
from PIL import (Image, ImageDraw, ImageFont)
from typing import (Tuple, Optional, Any, Union, overload, Literal)

from . import fonts
from .fonts import FontName
from ._utils import (image_to_ansi, binarize_image, trim_image_border)
from ..types import (T_ImgFillingMode, T_ImgBlockFillingMode)


@overload
def imgfile_to_ansi(
    img_path: str,
    /,
    width: Optional[int] = None,
    height: Optional[int] = None,
    mode: T_ImgBlockFillingMode = "half-color",
    display: bool = False
) -> str: ...


@overload
def imgfile_to_ansi(
    img_path: str,
    /,
    width: Optional[int] = None,
    height: Optional[int] = None,
    mode: Literal["ascii"] = "ascii",
    display: bool = False,
    charset: str = "@%#*+=-:. ",
) -> str: ...


def imgfile_to_ansi(
    img_path: str,
    /,
    width: Optional[int] = None,
    height: Optional[int] = None,
    mode: T_ImgFillingMode = "half-color",
    display: bool = False,
    charset: str = "@%#*+=-:. "
) -> str:
    r"""
    Convert an image file to a string representation based on the specified mode.

    Parameters
    ----------
        img_path : str
            Path to the image file.

        width : Optional[int], default to `None`
            Width of the rendered image.
            - `None`: Use original width, unless :param:`height` is specified to maintain aspect ratio.

        height : Optional[int], default to `None`
            Height of the rendered image.
            - `None`: Use original height, unless :param:`width` is specified to maintain aspect ratio.

        mode : ImgFillingModeName, default to `"half-color"`
            The rendering mode, which can be one of the following:
            - `"ascii"`: Render using ASCII characters, mapping pixel brightness to characters in :param:`charset`.
            - `"color"`: Render using full block characters with color.
            - `"half-color"`: Render using half block characters with color, combining two pixels vertically.
            - `"gray"`: Render using full block characters in grayscale.
            - `"half-gray"`: Render using half block characters in grayscale, combining two pixels vertically.

        display : bool, default to `False`
            Whether to print the rendered string to the terminal using :func:`safe_print()`.

        charset : str, default to `"@%#*+=-:. "`
            Characters used for `"ascii"` representation, ordered from darkest to lightest.

    Returns
    -------
        str
            String representation of the rendered image.
    """
    img = Image.open(img_path)

    aspect_ratio = img.height / img.width
    if height is not None or width is not None:
        if height is None and width is not None:
            height = int(aspect_ratio * width)
        elif width is None and height is not None:
            width = int(height / aspect_ratio)
        img = img.resize((width, height))

    return image_to_ansi(img, mode=mode, charset=charset, display=display)


@overload
def fonttext_to_ansi(
    text: str,
    /,
    font: Union[FontName, str] = FontName.LLDISCO,
    mode: Literal["gray", "half-gray"] = "gray",
    trim_border: bool = False,
    threshold: int = 5,
    font_size: int = 10,
    size: Optional[Tuple[int, int]] = None,
    left_top: Tuple[int, int] = (0, 0),
    display: bool = False
) -> str: ...


@overload
def fonttext_to_ansi(
    text: str,
    /,
    font: Union[FontName, str] = FontName.LLDISCO,
    mode: Literal["ascii"] = "ascii",
    trim_border: bool = False,
    threshold: int = 5,
    font_size: int = 10,
    size: Optional[Tuple[int, int]] = None,
    left_top: Tuple[int, int] = (0, 0),
    display: bool = False,
    charset: str = " #"
) -> str: ...


def fonttext_to_ansi(
    text: str,
    /,
    font: Union[FontName, str] = FontName.LLDISCO,
    mode: T_ImgFillingMode = "half-color",
    trim_border: bool = False,
    threshold: int = 5,
    font_size: int = 10,
    size: Optional[Tuple[int, int]] = None,
    left_top: Tuple[int, int] = (0, 0),
    display: bool = False,
    charset: str = " #",
    fore_rgb: Tuple[int, int, int] = (255, 255, 255),
    back_rgb: Tuple[int, int, int] = (0, 0, 0)
) -> str:
    r"""
    Render colored text based on a specified font into a string representation.

    Parameters
    ----------
        text : str
            The text to be rendered.

        font : Union[FontName, str], default to `FontName.LLDISCO`
            The font to be used for rendering the text.
            - `FontName` Enum: Use built-in fonts.
            - `str`: Path to a TTF/OTF font file.

        mode : ImgFillingModeName, default to `"half-color"`
            The rendering mode, which can be one of the following:
            - `"ascii"`: Render using ASCII characters, mapping pixel brightness to characters in :param:`charset`.
            - `"color"`: Render using full block characters with color.
            - `"half-color"`: Render using half block characters with color, combining two pixels vertically.
            - `"gray"`: Render using full block characters in grayscale.
            - `"half-gray"`: Render using half block characters in grayscale, combining two pixels vertically.

        trim_border : bool, default to `False`
            Whether to trim the border of the rendered image.

        threshold : int, default to `5`
            Threshold for converting grayscale to binary image (0-255). Specifically, pixels with brightness above this value are considered foreground, and those below are background.

        font_size : int, default to `10`
            Size of the font.

        size : Optional[Tuple[int, int]], default to `None`
            Size of the image canvas as (width, height).
            - `None`: Automatically determine size based on text length and font size.

        left_top : Tuple[int, int], default to `(0, 0)`
            Left top position to start drawing text on the image canvas.

        display : bool, default to `False`
            Whether to print the rendered string to the terminal using :func:`safe_print()`.

        charset : str, default to `" #"`
            Characters used for `"ascii"` representation. The first character represents the background, and the last character represents the foreground.

        fore_rgb : Tuple[int, int, int], default to `(255, 255, 255)`
            RGB color for the foreground (text color).

        back_rgb : Tuple[int, int, int], default to `(0, 0, 0)`
            RGB color for the background.

    Returns
    -------
        str
            String representation of the rendered colored text.
    """
    def _check(size: Any, default: Tuple[int, int], /) -> Tuple[int, int]:
        if (isinstance(size, tuple)
                and len(size) == 2
                and all(isinstance(v, int) and v > 0 for v in size)):
            return size
        return default

    text = str(text)
    # size of font
    if not (isinstance(font_size, int) and font_size > 0):
        font_size = 10
    font_size = int(font_size)
    # size of the image canvas
    img_size = _check(size, (len(text) * font_size, font_size * 2))
    # left top position
    left_top = _check(left_top, (0, 0))

    img = Image.new("L", img_size, color=0)
    draw = ImageDraw.Draw(img)
    # font
    if os.path.isfile(font):
        try:
            pil_font = ImageFont.truetype(font, size=font_size)
        except Exception:
            raise ValueError(f"Param `font` Of fonttext_to_ansi() Load Font Error From File Path: {font!r}.")

    elif isinstance(font, FontName):
        with pkg_resources.path(fonts, font.value) as font_path:
            pil_font = ImageFont.truetype(str(font_path), size=font_size)
    else:
        raise ValueError(f"Param `font` Of fonttext_to_ansi() Should Be FontName Enum Or Valid Font File Path, Got {font!r}.")

    draw.text(left_top, text, font=pil_font, fill=255)

    if trim_border:
        img = trim_image_border(img, value=0)

    binary_img = binarize_image(
        img,
        threshold=threshold,
        upper_rgb=fore_rgb,
        lower_rgb=back_rgb
    )
    return image_to_ansi(binary_img, mode=mode, charset=charset, display=display)
