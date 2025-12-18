<div align="center">

<h2 id="title">🐱‍👤 cobra-color 🐱‍👤</h2>

[![PyPI version](https://img.shields.io/pypi/v/cobra-color.svg)](https://pypi.org/project/cobra-color/)
![Python](https://img.shields.io/pypi/pyversions/cobra-color?color=brightgreen)
[![codecov](https://codecov.io/gh/tinchen777/cobra-color/branch/main/graph/badge.svg)](https://codecov.io/gh/tinchen777/cobra-color)
![License](https://img.shields.io/github/license/tinchen777/cobra-color.svg)

[![Tests](https://github.com/tinchen777/cobra-color/actions/workflows/test.yml/badge.svg)](https://github.com/tinchen777/cobra-color/actions/workflows/test.yml)
![Github stars](https://img.shields.io/github/stars/tinchen777/cobra-color.svg)

<!-- [![Pull Requests Welcome](https://img.shields.io/badge/pull%20requests-welcome-brightgreen.svg)](https://github.com/tinchen777/cobra-color/pulls) -->

</div>

## About

A lightweight Python library for enhanced terminal display: simple text color/style conventions and image-to-terminal rendering.

- Python: 3.9+
- Runtime deps: Pillow (>=9,<11), NumPy (>=1.21,<2)

## Features

- 🚀 Concise color/style names for terminal text.
- 🚀 Image rendering in multiple modes: ASCII, color, half-color, gray, half-gray.
- 🚀 Minimal dependencies and easy integration.

## Installation

Stable (once published):

```bash
pip install cobra-color
```

## Quick Start

- Render a text in the terminal:

    ```python
    from cobra_color import cstr, safe_print

    c_text_1 = cstr("Hello World!", fg="r", styles=["bold"])
    # Print directly from the terminal
    print(c_text_1)

    c_text_2 = cstr("Hello World!", fg=(255, 255, 255), styles=["udl", "bold"])
    # Alternatively, you can use safe_print() to automatically support progress bar modes like tqdm and rich.
    safe_print(c_text_2)

    # Merge `c_text_1` and `c_text_2` while preserving their colors and style formatting.
    c_text_3 = c_text_1 + c_text_2

    # You can continue to use str's proprietary functions and keep the existing colors and styles.
    c_text_1.upper()
    ```

- Render an image in the terminal:

    ```python
    from cobra_color.render import imgfile_to_ansi, safe_print

    # ASCII art
    safe_print(imgfile_to_ansi("example.jpg", width=80, mode="ascii"))

    # Half-block color (recommended for truecolor terminals)
    imgfile_to_ansi("example.jpg", width=80, mode="half-color", display=True)
    ```

- Render some text with fonts in the terminal:

    ```python
    from cobra_color.draw import fonttext_to_ansi, FontName, safe_print

    # Borderless grayscale font
    safe_print(fonttext_to_ansi(
        "Hello World!",
        font=FontName.LLDISCO,
        mode="half-gray",
        trim_border=True
    ))
    ```

## Image Modes

- `ascii`: monochrome ASCII using a density charset.
- `color`: colorized character fill.
- `half-color`: half-block characters with color (higher density, good visual quality).
- `gray`: grayscale characters.
- `half-gray`: half-block grayscale.

Tip: For best results, use a TrueColor-capable terminal and a monospaced font.

## Requirements

- Python >= 3.9
- `Pillow` >= 9.0, < 11
- `NumPy` >= 1.21, < 2.0

## License

See LICENSE in the repository.

## Links

- Homepage/Repo: https://github.com/tinchen777/cobra-color.git
- Issues: https://github.com/tinchen777/cobra-color.git/issues
