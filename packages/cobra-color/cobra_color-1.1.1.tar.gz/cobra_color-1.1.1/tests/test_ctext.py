# tests/test_cstr.py

import sys
sys.path.append("/data/tianzhen/my_packages/cobra-color/src")

from cobra_color import cstr
from cobra_color.string import (ColorStr, to_ansi)


def test_ColorStr():
    text = """正常文本 \x1b[1m加粗\x1b[0m 继续普通文本 \
    \x1b[4m下划线\x1b[0m \
    \x1b[31m红色前景\x1b[0m \
    \x1b[42m绿色背景\x1b[0m \
    \x1b[1;2;33;44m加粗+黄字+蓝底\x1b[0m \
    \x1b[1;38;5;200m256色前景 \
    \x1b[;38;2;255;mTrueColor红色背景\x1b[0m \
    结束文本"""

    a = ColorStr.from_str("abcd", bg="lm", styles={"bold", "udl"})
    b = cstr("abcc", bg="g", styles={"dim", "udl"})
    c = cstr(text)
    print(c)
    b.copy()
    print(a)
    print(b)
    print(to_ansi("abcc", bg="g", styles={"dim", "udl"}))
    print(a._SEGMENTS)

    print(3*a)
    print(a[1: 40])
    print(a == "abcd", a != b, a > b, a < b, a <= b, a >= b)
    b = cstr("123b4ff", fg="r", styles={"italic", "delete"})
    a += b
    a *= 2

    print(a)
    print(a._SEGMENTS)
    print(a[3:10])
    print(a._loc(-22))

    print(a.apply("modified"*3, start_idx=3, extend="left"))
    print(a.rapply("modified"*3, start_idx=3, extend=None))
    print(a.plain)
    print(a.iscombined, a.isfgcolored, a.isbgcolored, a.isstyled, a.isplain)
    print(a.pieces())
    print(a.capitalize())
    print(a.casefold())
    print(a.lower())
    print(a.swapcase())
    print(a.title())
    print(a.upper())
    print(a.center(30, cstr("-2", bg="g")))
    print(a.ljust(30, "*", extend="right"))
    print(a.rjust(30, "+", extend="left"))
    print(a.zfill(30))
    print(a.find(cstr("b", bg="lm", styles=["bold", "udl"])))
    print(a.rfind(cstr("a", fg="y").plain))

    seg = a.pieces()[2]
    print(seg)
    seg2 = a.pieces()[3]
    print(seg2)
    f = seg2.join([seg, seg, seg])
    print("JOIN: ", f)
    print(f._SEGMENTS)

    print(a[:5].pieces()[-1])
    print(a)
    print(a._SEGMENTS)
    print("===================")

    for seg in a.split(cstr("b", fg="r", styles=["italic", "delete"])):
        print(seg, end="     ")
    print()
    print(a.plain.split("b"))
    print(a.split(cstr("b", fg="y")))
    print(a.rsplit(cstr("b", fg="y"), maxsplit=1))
    print(a.splitlines(keepends=True))

    print(a.replace(cstr("b", bg="lm", styles=["bold", "udl"]), cstr("BB", fg="y"), count=1))

    print(a.strip("a"))
    print(a.rstrip("f"))
    print(a.removesuffix("4ff"))
    print(a.removeprefix("abcd1"))

    print(a.partition(cstr("fab")))
    print(a.rpartition("fab1"))

    print(a.splitlines())

    print(a.insert(-1, cstr("123456", fg="g"), overwrite=True))
    print(a.insert(-1, cstr("123456", fg="g")))
    print(a.insert(-1, cstr("123456", fg="g"), overwrite=True, keep_pattern=False))
    print(a.insert(-1, cstr("123456", fg="g"), keep_pattern=False))

    print(cstr("2", fg="d") in a)

    for i in a:
        print(i, end="|")
    print()
    print("fs" in a)
    print(cstr("2") == "2")
    print(cstr("2", bg="b") == cstr("2"))
    print(cstr("2", bg="b") == cstr("2", bg="b"))
    print("2" == cstr("2", bg="r"))
    print("2" == 1)
    print("====")
    print(cstr("2", bg="b") != "2")
    print(cstr("2") != cstr("2"))
    print("2" != cstr("2"))

    print("====")
    a += "999"
    print("static", a)
    print(a._SEGMENTS)
    b = a.rebuild(fg=[("r", "lg"), (None, (255, 1, 92))], bg="", styles=[("del", None), (None, ["bold", "udl"])])
    print(b)
    print(b._SEGMENTS)
    print("static", a)
    c = a.rebuild(slice(4, 7), fg="y", bg="m")
    print(c)
    print(c._SEGMENTS)
    print("static", a)

    print(cstr("\u2580", fg=(42, 42, 42), bg=(31, 31, 31)))
    print(a("123"))

    print(str(121))
    f = cstr(f"()12{a}dada", fg=[("", "b")])
    print(type(f))
    print(repr(f))
    print(len(f))
    print(f)
    print(f.pieces())
    # print("\x1b[4m下划线")
    f = cstr(f, a, "\x1b[4m下划线", 434, fg=[("", "g")])
    print(f)
    print(f._SEGMENTS)

    f._update(fg=[("b", "y")], styles=["1"])

    print(f)
    print(f._SEGMENTS)
    f._update(bg="clear")

    print(f)
    print(f._SEGMENTS)

    print(cstr("a", a, 1243, sep=cstr("sep", fg="y")))


if __name__ == "__main__":
    test_ColorStr()
