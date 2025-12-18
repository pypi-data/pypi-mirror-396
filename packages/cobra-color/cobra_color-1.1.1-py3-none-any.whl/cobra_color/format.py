# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen
"""
Formatting utilities for for :pkg:`cobra_color` package.

Functions
---------
- :func:`fmt_dict()`: Format and display a dictionary or object's attributes in a structured manner.
- :func:`fmt_list()`: Format and display a list in a structured manner.
"""

from typing import (Any, Mapping, Sequence, List)

from .string import ColorSeg
from .output import safe_print


_STYLES = {
    "title": ColorSeg.from_raw("", fg="y", styles={"bold"}),
    "key": ColorSeg.from_raw("", styles={"bold", "selected"}),  # Normal key
    "key_param": ColorSeg.from_raw("", styles={"bold", "selected"}),  # param
    "key_protected": ColorSeg.from_raw("", styles={"bold"}),  # _param
    "key_class_private": ColorSeg.from_raw("", styles={"dim"}),  # _Class__param
    "key_inherited_private": ColorSeg.from_raw("", styles={"dim", "del"}),  # _FatherClass__param
    "type": ColorSeg.from_raw("", fg="c", styles={"italic"}),
    "placeholder": ColorSeg.from_raw("", styles={"udl"})
}


def fmt_dict(
    target: Any,
    /,
    omits: Sequence[str] = [],
    title: str = "",
    display: bool = True
) -> str:
    r"""
    Format and display a dictionary or object's attributes in a structured manner.

    Parameters
    ----------
        target : Any
            The target dictionary or object whose attributes are to be formatted.

        omits : Sequence[str], default to `[]`
            A list of parameter names to be replaced with a placeholder.

        title : str, default to `""`
            An optional title to be displayed at the top of the formatted output.

        display : bool, default to `True`
            Whether to print the formatted output to the terminal using :func:`safe_print()`.

    Returns
    -------
        str
            The formatted string representation of the dictionary or object's attributes.
    """
    class_name = None
    father_classes = []
    legend = ""
    if hasattr(target, "__dict__"):
        class_name = str(target.__class__.__name__)
        father_classes = [father_class.__name__ for father_class in target.__class__.__bases__]
        legend = '  '.join([
            _STYLES["key_param"]("[param]").to_str(),
            _STYLES["key_protected"]("[_param]").to_str(),
            _STYLES["key_class_private"](f"[_{class_name}__param]").to_str(),
            _STYLES["key_inherited_private"](f"[_{father_classes[0]}__param]").to_str()
        ])
        target = target.__dict__
    elif not isinstance(target, Mapping):
        target = {"Error": f"Input target should be a Mapping type, got {type(target)}."}

    lines: List[str] = []
    if target:
        # indent
        indent = len(str(len(target)))
        # title
        if title:
            lines.append((" " * (indent + 2)) + _STYLES["title"](f"< {title} >").to_str())
        # legend
        if legend:
            lines.append((" " * (indent + 2)) + legend)
        # content
        for idex, (key, val) in enumerate(target.items(), start=1):
            key = str(key)
            type_str = _STYLES["type"](type(val).__name__).to_str()
            if class_name:
                # class attributes
                if key.startswith("_"):
                    # _param, _Class__param, _FatherClass__param
                    if key.startswith(f"_{class_name}__"):
                        # _Class__param
                        param_name = key.lstrip(f"_{class_name}__")
                        key_temp = _STYLES["key_class_private"]
                    elif any(key.startswith(f"_{father}__") for father in father_classes):
                        # _FatherClass__param
                        _, _, param_name = key.partition("__")
                        key_temp = _STYLES["key_inherited_private"]
                    else:
                        # _param
                        param_name = key.lstrip("_")
                        key_temp = _STYLES["key_protected"]
                else:
                    # param
                    param_name = key
                    key_temp = _STYLES["key_param"]
            else:
                # non-class dict
                param_name = key
                key_temp = _STYLES["key"]
            # omit items
            if param_name in omits and val:
                val = _STYLES["placeholder"]("PLACEHOLDER").to_str()

            lines.append(f"#{str(idex).zfill(indent)} {key_temp(f'[{param_name}]').to_str()}{type_str}: {val}")
    result = "\n".join(lines)
    if display:
        safe_print(result)

    return result


def fmt_list(target: Sequence[Any], /, display: bool = True) -> str:
    r"""
    Format and display a list in a structured manner.

    Parameters
    ----------
        target : Sequence[Any]
            The target list to be formatted.

        display : bool, default to `True`
            Whether to print the formatted output to the terminal using :func:`safe_print()`.

    Returns
    -------
        str
            The formatted string representation of the list.
    """
    lines = []
    if target and isinstance(target, Sequence):
        indent = len(str(len(target)))
        for idex, item in enumerate(target, start=1):
            lines.append(f"#{str(idex).zfill(indent)} {item}")
    result = "\n".join(lines)
    if display:
        safe_print(result)

    return result
