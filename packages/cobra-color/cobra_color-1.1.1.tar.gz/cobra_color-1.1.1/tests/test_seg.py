# tests/test_cstr.py

import sys
sys.path.append("/data/tianzhen/my_packages/cobra-color/src")

import copy
from cobra_color.string import ColorSeg


def test_ColorSeg():
    a = ColorSeg.from_raw("123", fg="lb", bg="g", styles=["bold", "udl", "italic"])
    b = ColorSeg.from_raw("45", fg=(255, 0, 0), styles=["italic", "delete"])
    c = ColorSeg(a.plain, a.fg, a.bg, a.styles)
    d = ColorSeg.empty()
    e = a.copy()
    e = copy.deepcopy(a)

    print(len(a))
    print(a.isequal(c))
    print(a != c)
    print(a == c)

    print(a.assemble("fg", "styles"))
    print("===")
    print(a.to_str())
    print(a("222222222222").to_str())
    print(a.istart, a.iend, a.isfgcolored, a.isbgcolored, a.isstyled, a.isplain)
    print(a.plain, a.fg, a.bg, a.styles)

    f = a % ("modified", "lr", "m", ["bold", "italic"], 100)

    print(repr(a))
    print(a.to_str())
    print(f)
    print(f.to_str())

    print("====")

    f = f % {"+plain": "123", "+fg": "ly", "@fg": ("lr", "m"), "@bg": "44", "-bg": "m", "-styles": ["bold"], "+styles": ["dim"], "@styles": ["dim", "blink"]}
    print(f)
    print(f.to_str())
    f._update_plain("modified again", mode="=")
    f._update(fg="y", bg="m", styles=[({"bold"}, {"udl"})])
    print(f)

    print(f.to_subseg(105, 110))
    print(f.to_subseg(111))


if __name__ == "__main__":
    test_ColorSeg()
