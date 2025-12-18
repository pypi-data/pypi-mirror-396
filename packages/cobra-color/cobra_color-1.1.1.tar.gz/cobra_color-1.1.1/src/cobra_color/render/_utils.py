# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
from PIL import (Image, ImageChops)
import numpy as np
from typing import (Tuple, List, Union, Iterable)

from ..string import to_ansi
from ..output import safe_print
from ..types import T_ImgFillingMode


VALID_MODES = ("ascii", "color", "half-color", "gray", "half-gray")


def image_to_ansi(
    img: Image.Image,
    /,
    mode: T_ImgFillingMode = "half-color",
    charset: str = "@%#*+=-:. ",
    display: bool = False
) -> str:
    r"""
    Render an image (:class:`PIL.Image.Image`) into a string representation based on the specified mode.

    Parameters
    ----------
        img : Image.Image
            The PIL Image to be rendered.

        mode : ImgFillingModeName, default to `"half-color"`
            The rendering mode.
            (Ref to :func:`imgfile_to_ansi()`)

        charset : str, default to `"@%#*+=-:. "`
            Characters used for `"ascii"` representation, ordered from darkest to lightest.

        display : bool, default to `False`
            Whether to print the rendered string to the terminal using :func:`safe_print()`.

    Returns
    -------
        str
            String representation of the rendered image.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"Param `mode` Of image_to_ansi() Must Be In {VALID_MODES}, Got {mode!r}.")
    if "color" not in mode:
        # Convert to grayscale
        img = img.convert("L")
    pixel_arr = np.array(img)
    height, width = pixel_arr.shape[:2]

    out_lines: List[str] = []
    if mode == "half-color" or mode == "half-gray":
        # Mode: `half-color` or `half-gray`
        for y in range(0, height, 2):
            upper_row = pixel_arr[y]
            lower_row = pixel_arr[y + 1] if (y + 1) < height else None
            line_str = ""
            if mode == "half-color":
                # Mode: `half-color`
                for x in range(width):
                    line_str += to_ansi(
                        "\u2580",
                        fg=tuple(upper_row[x]),
                        bg=None if lower_row is None else tuple(lower_row[x])
                    )
            else:
                # Mode: `half-gray`
                for x in range(width):
                    upper = int(upper_row[x])
                    fore = (upper, upper, upper)
                    if lower_row is not None:
                        lower = int(lower_row[x])
                        back = (lower, lower, lower)
                    else:
                        back = None
                    line_str += to_ansi("\u2580", fg=fore, bg=back)
            out_lines.append(line_str)
    elif mode == "ascii":
        # Mode: `ascii`
        char_arr = np.array(list(charset))
        pixel_arr_max = pixel_arr.max()
        pixel_arr_min = pixel_arr.min()
        if pixel_arr_max == pixel_arr_min:
            indices = np.zeros_like(pixel_arr, dtype=int)
        else:
            ratio = (pixel_arr - pixel_arr_min) / (pixel_arr_max - pixel_arr_min)
            indices = np.round(ratio * (len(charset) - 1)).astype(int)
        out_lines = ["".join(char_arr[indices[row]]) for row in range(height)]
    elif mode == "color":
        # Mode: `color`
        for row in pixel_arr:
            line_str = ""
            for pixel_val in row:
                line_str += to_ansi(" ", bg=tuple(pixel_val))
            out_lines.append(line_str)
    elif mode == "gray":
        # Mode: `gray`
        for row in pixel_arr:
            line_str = ""
            for pixel_val in row:
                line_str += to_ansi(" ", bg=(pixel_val, pixel_val, pixel_val))
            out_lines.append(line_str)

    output_str = "\n".join(out_lines)
    if display:
        safe_print(output_str)

    return output_str


def binarize_image(
    src: Union[Iterable, Image.Image],
    /,
    threshold: int = 128,
    upper_rgb: Tuple[int, int, int] = (255, 255, 255),
    lower_rgb: Tuple[int, int, int] = (0, 0, 0)
) -> Image.Image:
    r"""
    Create a binary image from the given source based on the specified threshold and RGB colors.

    Parameters
    ----------
        src : Union[Iterable, Image.Image]
            The source image data, which can be a 2-D or 3-D array-like structure or a PIL Image.

        threshold : int, default to `128`
            The threshold value to binarize the image.

        upper_rgb : Tuple[int, int, int], default to `(255, 255, 255)`
            The RGB color for pixels above the threshold.

        lower_rgb : Tuple[int, int, int], default to `(0, 0, 0)`
            The RGB color for pixels below and equal to the threshold.

    Returns
    -------
        Image.Image
            A PIL Image representing the binary image with specified RGB colors.
    """
    if isinstance(src, Image.Image):
        # as a PIL Image
        arr = np.array(src.convert("L"))
    else:
        arr = src if isinstance(src, np.ndarray) else np.array(src, copy=False)
        # Check array dimensions
        arr_shape = arr.shape
        if len(arr_shape) == 3:
            if arr_shape[-1] == 3:
                img = Image.fromarray(arr.astype(np.uint8), mode="RGB")
                arr = np.array(img.convert("L"))
            elif arr_shape[-1] == 1:
                arr = arr.reshape(arr_shape[0], arr_shape[1])
            else:
                raise ValueError(f"Param `src` Of binarize_image() For 3-D Image, Last Dimension Must Be 1 (Grayscale) Or 3 (RGB), Got {arr_shape[-1]}.")
        if len(arr_shape) != 2:
            raise ValueError(f"Param `src` Of binarize_image() Must Be 2-D (Grayscale Image) Or 3-D (RGB Image) Image, Got {arr_shape}.")
    arr = arr.astype(np.uint8)
    rgb_arr = np.where(
        (arr > threshold)[..., None],  # mask expanded to 3-D
        np.array(upper_rgb, dtype=np.uint8),  # upper_rgb
        np.array(lower_rgb, dtype=np.uint8)  # lower_rgb
    )

    return Image.fromarray(rgb_arr, mode="RGB")


def trim_image_border(img: Image.Image, /, value: int = 0):
    r"""
    Trim the border of the image that matches the specified value.

    Parameters
    ----------
        img : Image.Image
            The PIL Image to be trimmed.

        value : int, default to `0`
            The pixel value to be trimmed from the borders.

    Returns
    -------
        Image.Image
            The trimmed PIL Image.
    """
    bg = Image.new(img.mode, img.size, value)
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        return img.crop(bbox)
    return img
