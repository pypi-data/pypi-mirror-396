# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
from functools import (cached_property, wraps)
from typing import (Any, List, Tuple, Optional, Sequence, Iterable, Literal, Union, final, overload)

from ._extension import (ExtStr, to_ExtStr)
from ._segment import (ColorSeg, ansi_to_segments)
from ._utils import (wrap_exc, to_fgcode, to_bgcode, to_style_codes)
from ..types import (T_ColorSpec, T_ColorDesc, T_StyleDesc, T_StyleSpec)


def to_plain(obj: Any, default: Optional[str] = None, /) -> ExtStr:
    r"""
    Convert a single object to :class:`ExtStr`, with default value if empty.
    Minimize copying.
    """
    plain = obj.plain if isinstance(obj, (ColorSeg, ColorStr)) else to_ExtStr(obj)
    return to_plain(default) if default is not None and len(plain) == 0 else plain


def to_cstr(obj: Any, default: Optional[str] = None, /) -> ColorStr:
    r"""
    Convert a single object to :class:`ColorStr`, with default value if empty.
    Minimize copying.
    """
    if isinstance(obj, ColorStr):
        c_str = obj
    elif isinstance(obj, ColorSeg):
        c_str = ColorStr(obj)
    else:
        c_str = ColorStr.from_str(obj)
    return to_cstr(default) if default is not None and len(c_str) == 0 else c_str


def to_segments(obj: Any, /) -> List[ColorSeg]:
    r"""
    Convert a single object to a list of :class:`ColorSeg` segments.
    Minimize copying.
    """
    if isinstance(obj, ColorSeg):
        return [obj]
    elif isinstance(obj, ColorStr):
        return obj._SEGMENTS
    else:
        return ansi_to_segments(to_plain(obj))


def cstr(
    *objects: Any,
    fg: Optional[Union[T_ColorDesc, Literal["clear", ""]]] = None,
    bg: Optional[Union[T_ColorDesc, Literal["clear", ""]]] = None,
    styles: Optional[Union[T_StyleDesc, Literal["clear"]]] = None,
    sep: Any = ""
) -> ColorStr:
    r"""
    Generate an easy-to-use :class:`ColorStr` instance, `rich str`, with perfect support for :class:`str`, containing :class:`ColorStr` versions of almost all native :class:`str` features.

    Parameters
    ----------
        *objects: Any
            Objects concatenated in order to a new :class:`ColorStr` instance.

            NOTE: `"\033["` in string will be treated as ANSI escape codes, other objects will automatically converted to :class:`ColorStr`.

        fg : Optional[Union[T_ColorDesc, Literal["clear", ""]]], default to `None`
            The foreground color of the `rich str`.
            - _ColorSpec_: A `single value`, the foreground color of the entire `rich str` to be applied. (Ref to :type:`T_ColorSpec`);
            - `""` or `"clear"`: Clear foreground color for the entire `rich str`;
            - `None`: No change to foreground color;
            - _Seq(Tuple(Any, Any))_: A sequence of `mapping pairs`, each pair defines a mapping from _key_ to _value_, the foreground color of the entire `rich str` will be replaced according to the mapping:
            1. For each mapping _key_:
            - _ColorSpec_: A `single value` to match. (Ref to :type:`T_ColorSpec`);
            - `""`: Match segments without foreground color.
            2. For each mapping _value_:
            - _ColorSpec_: A `single value` to apply. (Ref to :type:`T_ColorSpec`);
            - `""`: Remove the foreground color.

        bg : Optional[Union[T_ColorDesc, Literal["clear", ""]]], default to `None`
            The background color of the `rich str`.
            (Ref to :param:`fg`)

        styles : Optional[Union[T_StyleDesc, Literal["clear"]]]
            The styles combination of the `rich str`.
            - _StyleSpec_: A `single value`, the styles of the entire `rich str` to be applied. (Ref to :type:`T_StyleSpec`);
            - `""` or `"clear"`: Clear styles for the entire `rich str`;
            - `None`: No change to styles;
            - _Seq(Tuple(Any, Any))_: A sequence of `mapping pairs`, each pair defines a mapping from _key_ to _value_, the styles of the entire `rich str` will be replaced according to the mapping:
            1. For each mapping _key_:
            - _StyleSpec_: A `single value` to match. (Ref to :type:`T_StyleSpec`);
            - `"all"`: Match any styles;
            - `None`: No match, add new styles to the entire `rich str`.
            2. For each mapping _value_:
            - _StyleSpec_: A `single value` to apply. (Ref to :type:`T_StyleSpec`);
            - `None`: Remove matched styles.

            NOTE: For styles mapping, the _key_ is a set of styles. If all styles in the _key_ are present in the segment, they will be replaced.

        sep : Any, default to `""`
            The separator used when concatenating multiple objects.

    Returns
    -------
        ColorStr
            A :class:`ColorStr` instance with the specified color and style.

    Useages
    --------
    >>> # 1. Create a simple colored string.
    >>> cstr("\x1b[4m下划线\x1b[0m")
    >>> # 2. Create a colored string with foreground color, background color or styles.
    >>> cstr("Hello World!", fg="r", styles=["bold", "udl"])
    >>> # 3. Rebuild a colored string with mapping rules.
    >>> cstr(c_str, fg=[("r", "lg"), (None, (255, 1, 92))], bg="", styles=[("del", None), (None, ["bold", "udl"])])
    >>> # 4. Combine multiple objects into a colored string with sep.
    >>> cstr("a", c_str, 1243, sep=cstr("sep", fg="y"))
    """
    c_str = ColorStr.from_iter(*objects, sep=sep)
    if fg is not None or bg is not None or styles is not None:
        c_str._update(fg=fg, bg=bg, styles=styles)
    return c_str


def to_ansi(
    text: Any,
    /,
    fg: Optional[T_ColorSpec] = None,
    bg: Optional[T_ColorSpec] = None,
    styles: Optional[T_StyleSpec] = None
) -> ExtStr:
    r"""
    Convert an object to an ANSI formatted :class:`ExtStr` with specified color and style.
    (Parameter ref to :func:`cstr()`)

    Returns
    -------
        ExtStr
            An ANSI formatted :class:`ExtStr` instance.
    """
    if fg is None and bg is None and styles is None:
        return to_plain(text)
    return ColorSeg.from_raw(to_plain(text), fg=fg, bg=bg, styles=styles).to_str()


@wrap_exc
def _fixed_method(func):
    @wraps(func)
    def wrapper(obj: ColorStr):
        return obj.apply(getattr(obj.plain, func.__name__)())
    return wrapper


@wrap_exc
def _extend_method(func):
    @wraps(func)
    def wrapper(obj: ColorStr, width, fillchar=" ", /, extend=None):
        # width
        if not isinstance(width, int):
            raise TypeError(f"Param 'width' Of ColorStr.{func.__name__}() Must Be An Integer, Got {type(width)}.")
        if width <= len(obj):
            return obj.copy()
        # fillchar
        fillchar = to_cstr(fillchar, " ")
        fillchar_len = len(fillchar)

        left_len, right_len = func(obj, width)
        # left part
        left = fillchar * ((left_len // fillchar_len) + 1)
        # right part
        right = fillchar * ((right_len // fillchar_len) + 1)

        return obj.apply(left[:left_len] + obj + right[:right_len], start_idx=left_len, extend=extend)
    return wrapper


@wrap_exc
def _clip_method(func):
    @wraps(func)
    def wrapper(obj: ColorStr, *args):
        str_result = getattr(obj.plain, func.__name__)(*args)
        return obj.apply(str_result, start_idx=-obj.find(str_result))
    return wrapper


@final
class ColorStr(ExtStr):
    r"""
    An easy-to-use `rich str` with perfect support for :class:`str`, containing :class:`ColorStr` versions of almost all native :class:`str` features.
    """
    _SEGMENTS: List[ColorSeg]
    _plain: ExtStr

    @classmethod
    def from_str(
        cls,
        str_: Any,
        /,
        fg: Optional[T_ColorSpec] = None,
        bg: Optional[T_ColorSpec] = None,
        styles: Optional[T_StyleSpec] = None
    ):
        r"""
        Create a :class:`ColorStr` instance from a single string.
        (Parameter ref to :func:`cstr()`)
        """
        if fg is None and bg is None and styles is None:
            return cls(*ansi_to_segments(to_plain(str_)), copy=False)
        return cls(ColorSeg.from_raw(to_plain(str_), fg=fg, bg=bg, styles=styles), copy=False)

    @classmethod
    def from_iter(cls, *objects: Any, sep: Any = ""):
        r"""
        Create a :class:`ColorStr` instance from an iterable of objects.
        (Parameter ref to :func:`cstr()`)
        """
        sep_segments = to_segments(sep)
        first = True
        segments: List[ColorSeg] = []
        for obj in objects:
            if not first and sep_segments:
                segments.extend(sep_segments)
            first = False
            segments.extend(to_segments(obj))
        return cls(*segments)

    def __new__(cls, *segments: ColorSeg, copy: bool = True):
        r"""
        Create a :class:`ColorStr` instance from :class:`ColorSeg` instances.
        """
        if len(segments) == 0:
            # no segments provided
            new_segments = [ColorSeg.empty()]
        else:
            # segments provided
            if any(not isinstance(seg, ColorSeg) for seg in segments):
                raise TypeError("All Arguments Of ColorStr() Must Be ColorSeg Instances, Try To Use `ColorStr.from_iter()` For Other Types.")
            new_segments = [segments[0].copy() if copy else segments[0]]
            new_segments[-1].set_istart(0)
            for seg in segments[1:]:
                if seg.plain:
                    if seg.isequal(new_segments[-1], ("fg", "bg", "styles")):
                        # merge with last segment
                        new_segments[-1]._update_plain(seg.plain, mode="+=")
                    else:
                        # append new segment
                        seg = seg.copy() if copy else seg
                        seg.set_istart(new_segments[-1].iend)
                        new_segments.append(seg)

        plain = ExtStr.from_iter(*(seg.plain for seg in new_segments))
        obj = super().__new__(cls, plain)
        obj._add_judgment(new_segments)
        obj._SEGMENTS = new_segments
        obj._plain = plain

        return obj

    def rebuild(
        self,
        apply_range: Optional[slice] = None,
        /,
        fg: Optional[Union[T_ColorDesc, Literal["clear", ""]]] = None,
        bg: Optional[Union[T_ColorDesc, Literal["clear", ""]]] = None,
        styles: Optional[Union[T_StyleDesc, Literal["clear"]]] = None
    ):
        r"""
        Rebuild A new :class:`ColorStr` according to the specified mapping rules.

        Parameters
        ----------
            apply_range : Optional[slice], default to `None`
                The range to which the rebuild will be applied.
                - `None`: Apply to the entire :class:`ColorStr`.
                - `slice`: A slice object defining the range.

            fg : Optional[Union[T_ColorDesc, Literal["clear", ""]]], default to `None`
                (Ref to :param:`fg` in :func:`cstr()`)

            bg : Optional[Union[Sequence[Tuple[Any, Any]], str]], default to `None`
                (Ref to :param:`bg` in :func:`cstr()`)

            styles : Optional[Union[Sequence[Tuple[Any, Any]], Set[str]]], default to `None`
                (Ref to :param:`styles` in :func:`cstr()`)

        Returns
        -------
            ColorStr
                A new recolored and restyled :class:`ColorStr`.
        """
        if apply_range is None:
            start, stop = 0, len(self)
        else:
            start, stop, _ = self._loc(apply_range)
        new_sub = self[start: stop]
        new_sub._update(fg=fg, bg=bg, styles=styles)

        if start == 0 and stop == len(self):
            return new_sub
        return self.insert(start, new_sub, overwrite=True)

    def pieces(self) -> List[ColorStr]:
        r"""
        Segmented into :class:`ColorStr` pieces according to segments.

        Returns
        -------
            List[ColorStr]
                A list of :class:`ColorStr` pieces.
        """
        return [ColorStr(seg) for seg in self._SEGMENTS]

    def apply(
        self,
        text: Any,
        /,
        _from_left: bool = True,
        start_idx: int = 0,
        extend: Optional[Literal["left", "right", "all"]] = None
    ) -> ColorStr:
        r"""
        Apply the color and style pattern of this :class:`ColorStr` to another :class:`str` from the `left`.

        Parameters
        ----------
            text : Any
                The text content to which the color and style pattern will be applied.

            start_idx : int, default to `0`
                The starting index from `left` in the text where the pattern will be applied.

            extend : Optional[Literal["left", "right", "all"]], default to `None`
                How to extend the pattern when the text is longer than the pattern.
                - `"left"`: Extend the leftmost segment of the pattern to the left.
                - `"right"`: Extend the rightmost segment of the pattern to the right.
                - `"all"`: Extend both sides.
                - `None`: No extension.

        Returns
        -------
            ColorStr
                A new colored string with the applied pattern.
        """
        c_text = to_cstr(text)
        # text length
        text_len = len(c_text)
        if text_len == 0:
            return c_text
        # check start_idx
        if not isinstance(start_idx, int):
            raise TypeError(f"Param 'start_idx' Of ColorStr.apply() Must Be An Integer, Got {type(start_idx)}.")
        # pattern
        src_str_len = len(self)
        if _from_left:
            pl = start_idx
            pr = pl + src_str_len
        else:
            pr = text_len - start_idx
            pl = pr - src_str_len
        pattern = self[
            max(-pl, 0): min(src_str_len-(pr-text_len), src_str_len)
        ]._SEGMENTS

        new_segments: List[ColorSeg] = []
        # left piece
        if pl > 0:
            if extend in ("left", "all"):
                new_segments.append(pattern[0](c_text.plain[0: pl]))
            else:
                new_segments.extend(c_text[0: pl]._SEGMENTS)
        # middle piece
        if pl < text_len and pr > 0:
            mid_text = c_text.plain[max(pl, 0): pr]
            for seg in pattern:
                new_segments.append(seg(mid_text[seg.istart: seg.iend]))
        # right piece
        if pr < text_len:
            index = max(pr, 0)
            if extend in ("right", "all"):
                new_segments.append(pattern[-1](c_text.plain[index:]))
            else:
                new_segments.extend(c_text[index:]._SEGMENTS)

        return ColorStr(*new_segments, copy=False)

    def rapply(
        self,
        text: Any,
        /,
        start_idx: int = 0,
        extend: Optional[Literal["left", "right", "all"]] = None
    ) -> ColorStr:
        r"""
        Apply the color and style pattern of this :class:`ColorStr` to another :class:`str` from the `right`.

        Parameter Reference: :func:`apply()`
        """
        return self.apply(text, start_idx=start_idx, extend=extend, _from_left=False)

    def findall(
        self,
        sub: Any,
        start: int = 0,
        end: Optional[int] = None,
        /,
        maxsplit: int = -1,
        _reverse: bool = False
    ) -> List[int]:
        r"""
        Find all occurrences of a substring in the :class:`ColorStr`.
        """
        if isinstance(sub, ColorStr) and not sub.isplain:
            # for ColorStr
            if _reverse:
                all_indices = self.plain.rfindall(sub.plain, start, end)
                all_indices.reverse()
            else:
                all_indices = self.plain.findall(sub.plain, start, end)
            indices: List[int] = []
            count = 0
            for start_idx in all_indices:
                if sub == self[start_idx: start_idx + len(sub)]:
                    indices.append(start_idx)
                    count += 1
                    if maxsplit != -1 and count >= maxsplit:
                        break
            if _reverse:
                indices.reverse()
            return indices
        else:
            # for non-ColorStr
            if _reverse:
                return self.plain.rfindall(sub, start, end, maxsplit=maxsplit)
            else:
                return self.plain.findall(sub, start, end, maxsplit=maxsplit)

    def rfindall(
        self,
        sub: Any,
        start: int = 0,
        end: Optional[int] = None,
        /,
        maxsplit: int = -1
    ) -> List[int]:
        r"""
        Find all occurrences of a substring in the :class:`ColorStr` in reverse order.
        """
        return self.findall(sub, start, end, maxsplit=maxsplit, _reverse=True)

    def find(self, sub: Any, /, start: int = 0, end: Optional[int] = None) -> int:  # type: ignore
        idx_list = self.findall(sub, start, end, maxsplit=1)
        return idx_list[0] if idx_list else -1

    def rfind(self, sub: Any, /, start: int = 0, end: Optional[int] = None) -> int:  # type: ignore
        idx_list = self.rfindall(sub, start, end, maxsplit=1)
        return idx_list[0] if idx_list else -1

    def join(self, iterable: Iterable[Any], /) -> ColorStr:
        return ColorStr.from_iter(*iterable, sep=self)

    def split(self, sep: Any = " ", /, maxsplit: int = -1) -> List[ColorStr]:  # type: ignore
        sep_ = to_ExtStr(sep)
        new_subs: List[ColorStr] = []
        count = 0
        start_idx = 0
        end_idx = -1
        while maxsplit == -1 or count < maxsplit:
            end_idx = self.find(sep_, start_idx)
            if end_idx == -1:
                break
            # segment
            new_subs.append(self[start_idx: end_idx])
            # update
            start_idx = end_idx + len(sep_)
            count += 1
        # last segment
        new_subs.append(self[start_idx:])

        return new_subs

    def rsplit(self, sep: Any = " ", /, maxsplit: int = -1) -> List[ColorStr]:  # type: ignore
        sep_ = to_ExtStr(sep)
        new_subs: List[ColorStr] = []
        count = 0
        end_idx = len(self)
        start_idx = -1
        while maxsplit == -1 or count < maxsplit:
            start_idx = self.rfind(sep_, 0, end_idx)
            if start_idx == -1:
                break
            # segment
            new_subs.append(self[start_idx + len(sep_): end_idx])
            # update
            end_idx = start_idx
            count += 1
        # last segment
        new_subs.append(self[0: end_idx])
        new_subs.reverse()

        return new_subs

    def splitlines(self, keepends: bool = False) -> List[ColorStr]:  # type: ignore[misc]
        new_subs = self.split("\n")
        if keepends:
            for i in range(len(new_subs) - 1):
                new_subs[i] += "\n"
        return new_subs

    def partition(self, sep: Any, /, _reverse: bool = False) -> Tuple[ColorStr, ColorStr, ColorStr]:  # type: ignore
        sep_ = to_ExtStr(sep)
        idx = self.rfind(sep_) if _reverse else self.find(sep_)
        if idx == -1:
            if _reverse:
                return (ColorStr(), ColorStr(), self.copy())
            else:
                return (self.copy(), ColorStr(), ColorStr())
        else:
            return (
                self[0: idx],
                self[idx: idx + len(sep_)],
                self[idx + len(sep_):]
            )

    def rpartition(self, sep: Any, /) -> Tuple[ColorStr, ColorStr, ColorStr]:  # type: ignore
        return self.partition(sep, _reverse=True)

    def replace(self, old: Any, new: Any, /, count: Any = -1) -> ColorStr:
        return ColorStr.from_iter(*self.split(old, maxsplit=count), sep=new)

    def insert(
        self,
        index: int,
        sub: Any,
        /,
        overwrite: bool = False,
        keep_pattern: bool = True
    ) -> ColorStr:
        r"""
        Insert a substring into the :class:`ColorStr` at the specified index.

        Parameters
        ----------
            index : int
                The index at which to insert the substring.

            sub : Any
                The substring to insert.

            overwrite : bool, default to `False`
                Whether to overwrite existing content at the insertion point.

            keep_pattern : bool, default to `True`
                Whether to keep the original pattern of the string.

        Returns
        -------
            ColorStr
                A new :class:`ColorStr` with the substring inserted.
        """
        index = self._loc(index)
        sub_ = to_cstr(sub)
        if not keep_pattern:
            if overwrite:
                sub_ = self.apply(sub_, start_idx=-index)
            else:
                sub_ = self[index].apply(sub_, extend="all")

        if overwrite:
            return self[0: index] + sub_ + self[index + len(sub_):]
        return self[0: index] + sub_ + self[index:]

    @_fixed_method
    def capitalize(self) -> ColorStr: ...

    @_fixed_method
    def casefold(self) -> ColorStr: ...

    @_fixed_method
    def lower(self) -> ColorStr: ...

    @_fixed_method
    def swapcase(self) -> ColorStr: ...

    @_fixed_method
    def title(self) -> ColorStr: ...

    @_fixed_method
    def upper(self) -> ColorStr: ...

    @_extend_method
    def center(
        self,
        width: Any,
        fillchar: str = " ",
        /,
        extend: Optional[Literal["left", "right", "all"]] = None
    ) -> ColorStr:
        padding = width - len(self)
        left = padding // 2 + (padding % 2)
        right = padding // 2
        return left, right  # type: ignore

    @_extend_method
    def ljust(
        self,
        width: Any,
        fillchar: str = " ",
        /,
        extend: Optional[Literal["right"]] = None
    ) -> ColorStr:
        return 0, width - len(self)  # type: ignore

    @_extend_method
    def rjust(
        self,
        width: Any,
        fillchar: str = " ",
        /,
        extend: Optional[Literal["left"]] = None
    ) -> ColorStr:
        return width - len(self), 0  # type: ignore

    def zfill(
        self,
        width: Any,
        /,
        extend: Optional[Literal["left"]] = None
    ) -> ColorStr:
        return self.rjust(width, "0", extend=extend)

    @_clip_method
    def strip(self, chars: str | None = None, /) -> ColorStr: ...

    @_clip_method
    def lstrip(self, chars: str | None = None, /) -> ColorStr: ...

    @_clip_method
    def rstrip(self, chars: str | None = None, /) -> ColorStr: ...

    @_clip_method
    def removeprefix(self, prefix: str, /) -> ColorStr: ...

    @_clip_method
    def removesuffix(self, suffix: str, /) -> ColorStr: ...

    def copy(self):
        r"""
        Create a copy of the :class:`ColorStr`.
        """
        return ColorStr(*self._SEGMENTS)

    def _update(
        self,
        fg: Optional[Union[T_ColorDesc, Literal["clear", ""]]] = None,
        bg: Optional[Union[T_ColorDesc, Literal["clear", ""]]] = None,
        styles: Optional[Union[T_StyleDesc, Literal["clear"]]] = None
    ):
        r"""Update the color and style mapping of the :class:`ColorStr` in place.
        (Ref to :func:`ColorStr.rebuild()`)

        NOTE: Adjacent segments with the same pattern in the updated :class:`ColorStr` will not be automatically merged."""

        def _fmt_c_mapping(m: Any, func: Any, /):
            r"""Format the color mapping input."""
            if m is None:
                return
            elif m == "clear":
                return ""
            elif isinstance(m, Sequence) and not isinstance(m, str):
                tuple_m = [i for i in m if (isinstance(i, (Tuple, List)) and len(i) >= 2)]
                if tuple_m:
                    return [(func(i[0]), func(i[1])) for i in tuple_m]
            return func(m)

        def _fmt_s_mapping(m: Any, func: Any, /) -> Optional[List[Any]]:
            r"""Format the style mapping input."""
            if m is None:
                return
            elif m == "clear":
                return [("all", None)]
            elif isinstance(m, Sequence) and not isinstance(m, str):
                if not m:
                    return [("all", None)]
                tuple_m = [i for i in m if (isinstance(i, (Tuple, List)) and len(i) >= 2)]
                if tuple_m:
                    return [(func(i[0]), func(i[1])) for i in tuple_m]
            return [("all", func(m))]

        # foreground mapping
        _fg = _fmt_c_mapping(fg, lambda x: "" if x == "" else to_fgcode(x))
        # background mapping
        _bg = _fmt_c_mapping(bg, lambda x: "" if x == "" else to_bgcode(x))
        # styles mapping
        _styles = _fmt_s_mapping(styles, lambda x: None if x is None else to_style_codes(x))
        # update
        for seg in self._SEGMENTS:
            seg._update(fg=_fg, bg=_bg, styles=_styles)
        # update pattern judgement
        self._add_judgment(self._SEGMENTS)
        # clear cached rich
        self.__dict__.pop("rich", None)

    @overload
    def _loc(self, s: slice, /) -> Tuple[int, int, int]: ...

    @overload
    def _loc(self, idx: int, /) -> int: ...

    @overload
    def _loc(self, start: int, end: int, /) -> Tuple[int, int]: ...

    def _loc(self, start: Union[slice, int], end: Optional[int] = None, /):
        r"""
        Get the valid start and end indices for slicing.
        """
        # slice
        if isinstance(start, slice):
            start_idx, end_idx, step = start.indices(len(self))
            return start_idx, end_idx, step
        # single index
        if end is None:
            if start < 0:
                start += len(self)
            if start < 0 or start >= len(self):
                raise IndexError(f"Index {start} Of ColorStr Out Range [-{len(self)}, {len(self)}).")
            return start
        # slice indices
        start_idx, end_idx, _ = slice(start, end).indices(len(self))
        return start_idx, end_idx

    def __call__(self, text: Any, /) -> ColorStr:
        return self.apply(text)

    def __add__(self, other: Any, /):
        return ColorStr(*(self._SEGMENTS + to_cstr(other)._SEGMENTS))

    def __mul__(self, n: Any, /):
        assert isinstance(n, int), "Can Only Multiply ColorStr By An Integer."
        if n <= 0:
            return ColorStr()
        return ColorStr(*[seg for _ in range(n) for seg in self._SEGMENTS])

    def __eq__(self, value: Any, /):
        if isinstance(value, str):
            val = to_ExtStr(value)
            if self.isplain and val.isplain:
                # self isplain, value isplain
                return super().__eq__(value)
            elif not self.isplain and not val.isplain and isinstance(val, ColorStr):
                # self iscolored, value iscolored
                return self._SEGMENTS == val._SEGMENTS
        return False

    def __ne__(self, value: Any, /):
        return not self.__eq__(value)

    def __contains__(self, value: Any, /):
        return self.find(value) != -1

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __getitem__(self, key: Any, /):
        if isinstance(key, slice):
            start, stop, step = self._loc(key)
            if step != 1:
                return ColorStr.from_str(super().__getitem__(key))
            # slice segments for non-step slices
            new_segments: List[ColorSeg] = []
            for seg in self._SEGMENTS:
                if start >= seg.iend or stop <= seg.istart:
                    continue
                left_idx = max(seg.istart, start)
                right_idx = min(stop, seg.iend)
                if left_idx <= right_idx:
                    new_segments.append(seg(self.plain[left_idx: right_idx]))
            return ColorStr(*new_segments, copy=False)
        elif isinstance(key, int):
            key = self._loc(key)
            # find segment
            for seg in self._SEGMENTS:
                if seg.istart <= key < seg.iend:
                    return ColorStr(seg(self.plain[key]), copy=False)
            # should not reach here
            raise IndexError(f"Can Not Match Index {key} In ColorStr Segments.")
        else:
            return ColorStr.from_str(super().__getitem__(key))

    def __str__(self):
        return self.rich

    def __repr__(self):
        return repr(self.rich)

    @property
    def iscombined(self) -> bool:
        r"""
        Check if the :class:`ColorStr` is combined from multiple segments.
        """
        return len(self._SEGMENTS) > 1

    @property
    def plain(self) -> ExtStr:
        r"""
        The plain :class:`ExtStr` string without any color or style.
        """
        return self._plain

    @cached_property
    def rich(self) -> ExtStr:
        r"""
        The rich text with colors and styles.
        """
        return ExtStr.from_iter(*(seg.to_str() for seg in self._SEGMENTS))
