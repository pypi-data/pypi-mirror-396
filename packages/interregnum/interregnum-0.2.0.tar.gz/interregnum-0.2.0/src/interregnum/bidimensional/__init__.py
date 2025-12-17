#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""A bi-dimensional structure useful for graph or table operations."""
from __future__ import annotations
from typing import (
    TypeVar,
    Generic,
    Iterator,
    Hashable,
)


_Row = TypeVar("_Row")
_Col = TypeVar("_Col")
AnyValue = TypeVar("AnyValue")
AnyKey = TypeVar("AnyKey", bound=Hashable)


class Bidimensional(Generic[_Row, _Col, AnyValue]):
    """Bi-dimensional structure."""

    def empty(self) -> bool:
        """Return True if the object is empty."""
        raise NotImplementedError()

    def col_size(self) -> int:
        """Return the number of columns."""
        raise NotImplementedError()

    def row_size(self) -> int:
        """Return the number of rows."""
        raise NotImplementedError()

    def __getitem__(self, idx: tuple[_Row, _Col]) -> AnyValue:
        """Return the value at position `idx` (row index, col index)."""
        raise NotImplementedError()

    def __setitem__(self, idx: tuple[_Row, _Col], value: AnyValue):
        """Set a `value` at position `idx` (row index, col index)."""
        raise NotImplementedError()

    def iter_row_keys(self) -> Iterator[_Row]:
        """Iterate row keys."""
        raise NotImplementedError()

    def iter_col_keys(self) -> Iterator[_Col]:
        """Iterate column keys."""
        raise NotImplementedError()

    def iter_row(self, row: _Row, sparse=False) -> Iterator[tuple[_Col, AnyValue]]:
        """Iterate row _Row elements."""
        raise NotImplementedError()

    def iter_col(self, col: _Col, sparse=False) -> Iterator[tuple[_Row, AnyValue]]:
        """Iterate column _Col elements."""
        raise NotImplementedError()

    def remove_row(self, row: _Row) -> None:
        """Remove row _Row."""
        raise NotImplementedError()
