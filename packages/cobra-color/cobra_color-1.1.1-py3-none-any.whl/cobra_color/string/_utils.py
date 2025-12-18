# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from functools import wraps
import re
from typing import (Optional, Sequence, Iterable, Iterator, Tuple, Set, Any)


def wrap_exc(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            args_repr = ", ".join(repr(a) for a in args)
            kwargs_repr = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
            raise e.__class__(f"Error When Calling {func.__module__}.{func.__name__}({args_repr}, {kwargs_repr}): {e}.")
    return wrapper


# --------------- ANSI Code Utils ---------------
# code of colors
__STANDARD_COLOR_MAP = {
    "d": "0",  # dark/black
    "r": "1",  # red
    "g": "2",  # green
    "y": "3",  # yellow
    "b": "4",  # blue
    "m": "5",  # magenta
    "c": "6",  # cyan
    "w": "7",  # white
}
__HIGHLIGHT_COLOR_MAP = {
    "ld": "0",  # highlight dark/black
    "lr": "1",  # highlight red
    "lg": "2",  # highlight green
    "ly": "3",  # highlight yellow
    "lb": "4",  # highlight blue
    "lm": "5",  # highlight magenta
    "lc": "6",  # highlight cyan
    "lw": "7",  # highlight white
}
# code of styles
__STYLE_MAP = {
    "bold": "1",
    "dim": "2",
    "italic": "3",
    "udl": "4",
    "underline": "4",
    "blink": "5",
    "selected": "7",
    "disappear": "8",
    "del": "9",
    "delete": "9"
}
__STYLE_CODE = set(__STYLE_MAP.values())

__ANSI_RE = re.compile(r"\x1b\[([\d;]+)m")
__STYLE_RE = re.compile(rf"(?<![34]8;)\b[{''.join(__STYLE_CODE)}]\b")
# __FG_RE = re.compile(r"[39][0-7]|38;(?:5(?:;\d{1,3})?|2(?:;\d{1,3}){0,3})")
# __BG_RE = re.compile(r"(?:4|10)[0-7]|48;(?:5(?:;\d{1,3})?|2(?:;\d{1,3}){0,3})")
__COLOR_RE = re.compile(r"([39][0-7])|((?:4|10)[0-7])")


def _fmt_ansicolor(
    code_iter: Iterator[Any],
    /,
    c_code: Any = "",
    c_mode: Any = "",
) -> Tuple[Optional[str], Optional[str]]:
    r"""Format ANSI color code from an iterator of codes.
    Return foreground and background color codes."""
    def _fmt_args(code: str):
        r"""Format the arguments for ANSI color code."""
        mode = str(c_mode or next(code_iter, ""))
        if mode == "5":
            # 256 color
            val_256 = int(next(code_iter, "0") or "0") % 256
            return f"{code};5;{val_256}"
        elif mode == "2":
            # true color
            val_r = int(next(code_iter, "0") or "0") % 256
            val_g = int(next(code_iter, "0") or "0") % 256
            val_b = int(next(code_iter, "0") or "0") % 256
            return f"{code};2;{val_r};{val_g};{val_b}"

    code = str(c_code or next(code_iter, ""))
    if code:
        if code == "38":
            # foreground color
            return (_fmt_args("38"), None)
        elif code == "48":
            # background color
            return (None, _fmt_args("48"))
        else:
            # try basic or highlight color
            m = __COLOR_RE.fullmatch(code)
            if m:
                return (m.group(1), m.group(2))
    return (None, None)


def _to_color_code(c: Any, /, is_fg: bool) -> Optional[str]:
    r"""Parse the color input into ANSI color code."""
    if isinstance(c, str):
        # Basic 8 color OR Light 8 color
        if c in __STANDARD_COLOR_MAP:  # "d"
            # Basic 8 color. e.g.: 31, 42
            return ("3" if is_fg else "4") + __STANDARD_COLOR_MAP[c]
        elif c in __HIGHLIGHT_COLOR_MAP:  # "ld"
            # Light 8 color. e.g.: 91, 102
            return ("9" if is_fg else "10") + __HIGHLIGHT_COLOR_MAP[c]
        else:
            # try ANSI color code
            fg, bg = _fmt_ansicolor(iter(c.split(";")))
            return fg if is_fg else bg
    elif isinstance(c, int) or isinstance(c, Sequence):
        # 256 color. e.g.: 38;5;196 OR True color. e.g.: 38;2;255;0;0
        fg, bg = _fmt_ansicolor(
            iter((c,) if isinstance(c, int) else c),
            c_code="38" if is_fg else "48",
            c_mode="5" if isinstance(c, int) else "2"
        )
        return fg if is_fg else bg


def to_fgcode(c: Any, /) -> Optional[str]:
    r"""
    Parse the color input into ANSI foreground color code.
    """
    return _to_color_code(c, is_fg=True)


def to_bgcode(c: Any, /) -> Optional[str]:
    r"""
    Parse the color input into ANSI background color code.
    """
    return _to_color_code(c, is_fg=False)


def to_style_codes(styles: Any, /) -> Set[str]:
    r"""
    Parse the styles into ANSI style codes.
    """
    if isinstance(styles, str):
        if styles in __STYLE_MAP:
            # style name
            return {__STYLE_MAP[styles]}
        # try ANSI style codes directly
        return set(__STYLE_RE.findall(styles))
    elif isinstance(styles, Iterable):
        style_codes = styles if isinstance(styles, Set) else set(styles)
        result = __STYLE_CODE.intersection(style_codes)
        if result:
            return result
        return {__STYLE_MAP[s] for s in style_codes if s in __STYLE_MAP}
    return set()
