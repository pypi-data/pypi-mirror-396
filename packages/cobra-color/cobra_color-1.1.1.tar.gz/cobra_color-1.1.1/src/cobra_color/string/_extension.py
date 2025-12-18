# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
from typing import (Optional, List, Any)


def to_ExtStr(obj: Any, /) -> ExtStr:
    r"""
    Convert a single object to :class:`ExtStr`.
    Ensure it is a subclass of :class:`ExtStr`.
    """
    return obj if isinstance(obj, ExtStr) else ExtStr(obj)


class ExtStr(str):
    r"""
    An `extended str` class that extends the built-in :class:`str` class.
    """
    _is_fg_colored: bool = False
    _is_bg_colored: bool = False
    _is_styled: bool = False
    _is_plain: bool = True

    @classmethod
    def from_iter(cls, *objects: Any):
        r"""
        Create an :class:`ExtStr` instance from an iterable of objects.
        """
        return cls("".join(map(to_ExtStr, objects)))

    def findall(
        self,
        sub: str,
        start: int = 0,
        end: Optional[int] = None,
        /,
        maxsplit: int = -1,
        _reverse: bool = False
    ) -> List[int]:
        r"""
        Find all occurrences of a substring in the :class:`ExtStr`.
        """
        sub_ = to_ExtStr(sub)
        indices: List[int] = []
        count = 0
        start_idx = start
        end_idx = end if end is not None else len(self)
        while maxsplit == -1 or count < maxsplit:
            if _reverse:
                idx = super().rfind(sub_, start_idx, end_idx)
                end_idx = idx
            else:
                idx = super().find(sub_, start_idx, end_idx)
                start_idx = idx + len(sub_)
            if idx == -1:
                break
            indices.append(idx)
            count += 1
        if _reverse:
            indices.reverse()

        return indices

    def rfindall(
        self,
        sub: str,
        start: int = 0,
        end: Optional[int] = None,
        /,
        maxsplit: int = -1
    ) -> List[int]:
        r"""
        Find all occurrences of a substring in the :class:`ExtStr` in reverse order.
        """
        return self.findall(sub, start, end, maxsplit=maxsplit, _reverse=True)

    def _add_judgment(self, segments: List[Any], /):
        r"""Add pattern judgment attributes to the :class:`ExtStr` object."""
        self._is_fg_colored = any(seg.isfgcolored for seg in segments)
        self._is_bg_colored = any(seg.isbgcolored for seg in segments)
        self._is_styled = any(seg.isstyled for seg in segments)
        self._is_plain = not any((self.isfgcolored, self.isbgcolored, self.isstyled))

    def __add__(self, other: Any, /) -> ExtStr:
        return ExtStr(super().__add__(other))

    def __mul__(self, n: Any, /) -> ExtStr:
        return ExtStr(super().__mul__(n))

    def __rmul__(self, n: Any, /):
        return self.__mul__(n)

    @property
    def isfgcolored(self) -> bool:
        r"""
        Whether the :class:`ExtStr` has any foreground color applied.
        """
        return self._is_fg_colored

    @property
    def isbgcolored(self) -> bool:
        r"""
        Whether the :class:`ExtStr` has any background color applied.
        """
        return self._is_bg_colored

    @property
    def isstyled(self) -> bool:
        r"""
        Whether the :class:`ExtStr` has any style applied.
        """
        return self._is_styled

    @property
    def isplain(self) -> bool:
        r"""
        Whether the :class:`ExtStr` is plain (no color or style applied).
        """
        return self._is_plain
