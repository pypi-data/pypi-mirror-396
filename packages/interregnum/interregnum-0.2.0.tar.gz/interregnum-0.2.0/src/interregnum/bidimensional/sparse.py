#!/usr/bin/source python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""A sparse bi-dimensional table."""

from __future__ import annotations
from typing import (
    TypeVar,
    ItemsView,
    KeysView,
    Iterator,
)

from collections import defaultdict
from typing_extensions import override

from . import Bidimensional, AnyValue
from ..types import SortHash
from ..tabulate import tabulate


_Row = TypeVar("_Row", bound=SortHash)
_Col = TypeVar("_Col", bound=SortHash)


class SparseTable(Bidimensional[_Row, _Col, AnyValue]):
    """Bi-dimensional table which initialises missing values.

    Rows and cols keys are added dynamically.
    """

    _data: dict[_Row, dict[_Col, AnyValue]]
    _default: AnyValue

    def __init__(self, default: AnyValue):
        """Create a sparse table with a `default` value for empty cells."""
        self._default = default
        self._data = defaultdict(lambda: defaultdict(lambda: default))

    @override
    def empty(self):
        return not self._data

    @override
    def col_size(self):
        return max(len(c) for c in self._data.values())

    @override
    def row_size(self):
        return len(self._data)

    def __getitem__(self, idx: tuple[_Row, _Col]) -> AnyValue:
        """Return the element at `idx`.

        Args
        ----
        idx
            a row-column tuple

        Return
        ------
        :
            the element at `idx`

        >>> t = SparseTable(0)
        >>> a = t[0, 3]
        """
        row, col = idx

        columns = self._data.get(row)
        if not columns:
            return self._default

        return columns.get(col, self._default)

    def __setitem__(self, idx: tuple[_Row, _Col], value: AnyValue):
        """Set a value at element `idx`.

        Args
        ----

        idx
            a row-column tuple
        value
            new value for the element at `idx`

        >>> t = SparseTable(0)
        >>> t[0, 3] = 5
        """
        row, col = idx

        col_values = self.row(row)
        if value == self._default:
            if col in col_values:
                del col_values[col]
        else:
            col_values[col] = value
        self._data[row] = col_values

    def __delitem__(self, idx: tuple[_Row, _Col]):
        """Delete a cell."""
        row, col = idx
        if row not in self._data:
            return
        col_values = self.row(row)
        if col not in col_values:
            return
        del col_values[col]
        if not col_values:
            del self._data[row]

    def remove_row(self, row: _Row):
        """Remove elements from row."""
        if row in self._data:
            del self._data[row]

    def remove_col(self, col: _Col):
        """Remove elements from col."""
        for _, columns in self.rows():
            if col in columns:
                del columns[col]

    def row(self, idx: _Row) -> dict[_Col, AnyValue]:
        """Get items in row (non-empty columns).

        Args
        ----
        idx
            row index

        Return
        ------
        :
            row at `idx`

        >>> t = SparseTable(0)
        >>> t[5, 2] = 2
        >>> r5 = t.row(5)
        """
        return self._data[idx]

    def rows(self) -> ItemsView[_Row, dict[_Col, AnyValue]]:
        """Iterate existing rows.

        Return
        ------
        :
            iterator of (row key, row defaultdict)
        """
        return self._data.items()

    @override
    def iter_row(self, row: _Row, sparse=False) -> Iterator[tuple[_Col, AnyValue]]:
        return iter(self._data[row].items())

    def iter_col(self, col: _Col, sparse=False) -> Iterator[tuple[_Row, AnyValue]]:
        """Iterate existing elements in a column.

        If an element does not exist and not `sparse`, yield default value

        Args
        ----
        col
            column index
        sparse
            if True, return only non-default values

        >>> t = SparseTable(0)
        >>> t[2, 3] = 1
        >>> t[5, 3] = 2
        >>> for x in t.iter_col(3):
        >>>     print(x)
        """
        for row, columns in self.rows():
            if col in columns:
                yield (row, columns[col])
            elif not sparse:
                yield (row, self._default)

    def __iter__(self) -> Iterator[tuple[_Row, _Col, AnyValue]]:
        """Iterate table elements row-wise.

        Return
        ------
        :
            generator (r, c, element)

        >>> t = SparseTable(0)
        >>> t[2, 3] = 1
        >>> t[5, 3] = 2
        >>> t[1, 1] = 4
        >>> for x in iter(t):
        >>>     print(x)
        """
        for row, columns in self.rows():
            for col, value in columns.items():
                yield (row, col, value)

    def row_keys(self) -> KeysView[_Row]:
        """Return keys from existing rows.

        >>> t = SparseTable(0)
        >>> t['Alice', 'Bob'] = 5
        >>> t['Bob', 'Charles'] = 3
        >>> # 'Alice', 'Bob'
        >>> print(t.row_keys())
        """
        return self._data.keys()

    @override
    def iter_row_keys(self) -> Iterator[_Row]:
        return iter(self._data.keys())

    def iter_col_keys(self) -> Iterator[_Col]:
        """Return keys from existing columns.

        >>> t = SparseTable(0)
        >>> t['Alice', 'Bob'] = 5
        >>> t['Bob', 'Charles'] = 3
        >>> # 'Bob', 'Charles'
        >>> print(t.col_keys())
        """
        keys = set()
        for columns in self._data.values():
            for col in columns:
                if col not in keys:
                    yield col
                    keys.add(col)

    def keys(self) -> Iterator[_Row | _Col]:
        """Return different existing keys in table.

        >>> t = SparseTable(0)
        >>> t['Alice', 'Bob'] = 5
        >>> t['Bob', 'Charles'] = 3
        >>> # 'Alice', 'Bob', 'Charles'
        >>> print(t.keys())
        """
        keys: set[_Row | _Col] = set()
        for row, columns in self.rows():
            if row not in keys:
                yield row
                keys.add(row)
            for col in columns.keys():
                if col not in keys:
                    yield col
                    keys.add(col)

    @override
    def __repr__(self):
        return repr(self._data)

    @override
    def __str__(self):
        out = []
        row = ["-"]
        keys = list(self.keys())
        try:
            keys = sorted(keys)
        except TypeError:
            pass
        row.extend(f"{key}" for key in keys)
        out.append(row)
        for r_key in keys:
            row = [f"{r_key}"]
            row.extend(f"{self[r_key, c_key]}" for c_key in keys)
            out.append(row)
        return tabulate(out)
