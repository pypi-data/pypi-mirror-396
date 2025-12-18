# tests/test_font.py

# import sys
# sys.path.append("/data/tianzhen/my_packages/cobra-color/src")

from cobra_color.render import fonttext_to_ansi, FontName


def test_fmt_font():
    result = fonttext_to_ansi(
        "Hello, cobra color!",
        font=FontName.LLDISCO,
        trim_border=True,
        mode="ascii",
        font_size=10,
        # fore_rgb=(255, 120, 0),
        # back_rgb=(0, 120, 0)
    )
    assert isinstance(result, str)
    print(result)


if __name__ == "__main__":
    test_fmt_font()
