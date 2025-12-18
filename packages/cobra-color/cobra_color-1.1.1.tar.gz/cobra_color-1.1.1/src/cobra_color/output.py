# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen
"""
Output utilities for :pkg:`cobra_color` package.
"""

from __future__ import annotations
import builtins
from typing import (Any, Optional, Callable, Union)

# import
try:
    from tqdm import tqdm  # type: ignore
except ImportError:
    tqdm = None

try:
    from rich.console import Console as richConsole  # type: ignore
except ImportError:
    richConsole = None


_GLOBAL_CONSOLE: Optional[Console] = None  # output function


def set_console(func: Callable[..., Any], **kwargs: Any):
    r"""
    Set a global console for :func:`safe_print()`.

    Parameters
    ----------
        func : Callable[..., Any]
            A console output function or method, which should accept string input as the first argument.

        **kwargs : Any
            Additional keyword arguments to be passed to the console function during each call.
    """
    global _GLOBAL_CONSOLE
    _GLOBAL_CONSOLE = Console(func, **kwargs)


class Console():
    r"""
    A wrapper for console output functions with preset keyword arguments.
    """
    def __init__(self, func: Callable[..., Any], **kwargs: Any):
        self.__func = func
        self.__kwargs = kwargs

    def __call__(self, *args, **kwargs) -> Any:
        return self.__func(*args, **{**self.__kwargs, **kwargs})


def safe_print(
    *values: object,
    sep: str = " ",
    end: str = "\n",
    file: Optional[Any] = None,
    flush: bool = False,
    console: Optional[Union[Callable[..., Any], Console, Any]] = None
):
    r"""
    A safe print function that works well with progress bars from :pkg:`tqdm` and :pkg:`rich` consoles.

    Parameters
    ----------
        *values : object
            Values to be printed.

        sep : str, default to `" "`
            Separator between values.

        end : str, default to `"\n"`
            End character after printing.

        file : Optional[Any], default to `None`
            The file-like object to write to. If `None`, defaults to `sys.stdout`.

        flush : bool, default to `False`
            Whether to forcibly flush the stream.

        console : Optional[Union[Callable[..., Any], ConsoleFunc]], default to `None`
            A console output function or method to use for printing.
            - `None`: Use the global console if set;
            - `Callable[..., Any]` or :class:`ConsoleFunc`: Use the provided function.
    """
    # determine output function and kwargs
    func = None
    if console is not None:
        if tqdm is not None and isinstance(console, tqdm) and getattr(tqdm, "_instances", None):
            func = Console(tqdm.write, end=end)
        elif richConsole is not None and isinstance(console, richConsole):
            func = Console(console.print, end=end, markup=False, highlight=False, overflow="ignore", crop=False)
        elif isinstance(console, Callable):
            func = Console(console, end=end)
        elif isinstance(console, Console):
            func = console
    else:
        if tqdm is not None and getattr(tqdm, "_instances", None):
            # Use tqdm write
            func = Console(tqdm.write, end=end)
        else:
            # Use global console
            func = _GLOBAL_CONSOLE

    def _default_print():
        builtins.print(*values, sep=sep, end=end, file=file, flush=flush)

    # output
    if func is None:
        _default_print()
    else:
        try:
            func(sep.join(map(str, values)))
        except Exception:
            _default_print()
