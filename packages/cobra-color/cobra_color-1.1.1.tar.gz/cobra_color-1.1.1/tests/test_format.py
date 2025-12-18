# tests/test_format.py

# import sys
# sys.path.append("/data/tianzhen/my_packages/cobra-color/src")

from cobra_color.format import fmt_dict, fmt_list


class A:
    def __init__(self):
        self.a = 1
        self._b = 2
        self.__c = 3


class B(A):
    def __init__(self):
        super().__init__()
        self.d = 4
        self._e = 5
        self.__f = 6


def test_fmt_dict():
    d = {"a": 1, "b": [1, 2, 3], "c": {"d": 4, "e": 5}}
    result = fmt_dict(d, title="Sample Dict", omits=["b"])
    assert isinstance(result, str)
    print(result)


def test_fmt_dict_2():
    b = B()
    result = fmt_dict(b, title="Class B Instance", omits=["_b", "d"])
    assert isinstance(result, str)
    print(result)


def test_fmt_list():
    _l = [1, 2, 3, {"a": 4, "b": [5, 6]}, [7, 8, 9], "text"]
    result = fmt_list(_l)
    assert isinstance(result, str)
    print(result)


if __name__ == "__main__":
    test_fmt_dict()
    test_fmt_dict_2()
    test_fmt_list()
