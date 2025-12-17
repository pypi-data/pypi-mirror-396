#!/usr/bin/source python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Matrix structure with indices of a hashable type and values of any type."""
from __future__ import annotations
from typing import (
    Iterator,
    Iterable,
    Callable,
    TypeVar,
)
from collections import OrderedDict
from typing_extensions import override

from . import Bidimensional, AnyValue
from ..tabulate import tabulate
from ..types import SortHash


_Row = TypeVar("_Row", bound=SortHash)
_Col = TypeVar("_Col", bound=SortHash)


class AbstractMatrix(Bidimensional[_Row, _Col, AnyValue]):
    """Abstract matrix."""

    _rows: dict[_Row, dict[_Col, AnyValue]]
    _cols: dict[_Col, dict[_Row, AnyValue]]

    def iter_row_keys(self):
        """Return row keys."""
        return self._rows.keys()

    def iter_col_keys(self):
        """Return col keys."""
        return self._cols.keys()

    @override
    def col_size(self):
        return len(self._cols)

    @override
    def row_size(self):
        return len(self._rows)

    @override
    def empty(self):
        return not self._rows or not self._cols

    @override
    def __getitem__(self, idx: tuple[_Row, _Col]):
        row, col = idx
        return self._rows[row][col]

    @override
    def __setitem__(self, idx: tuple[_Row, _Col], value):
        row, col = idx

        self._rows[row][col] = value
        self._cols[col][row] = value

    def row(self, idx: _Row):
        """Return row."""
        return self._rows[idx]

    def col(self, idx: _Col):
        """Return col."""
        return self._cols[idx]

    def __iter__(self) -> Iterator[tuple[tuple[_Row, _Col], AnyValue]]:
        """Iterate cell values.

        Yields
        ------
        :
            (cell index, cell value)
        """
        for row, col_items in self.iter_rows():
            for col, value in col_items.items():
                yield (row, col), value

    def iter_rows(self):
        """Iterate rows."""
        return self._rows.items()

    def iter_cols(self):
        """Iterate cols."""
        return self._cols.items()

    @override
    def iter_col(self, col: _Col, sparse=False) -> Iterator[tuple[_Row, AnyValue]]:
        return iter(self._cols[col].items())

    @override
    def iter_row(self, row: _Row, sparse=False) -> Iterator[tuple[_Col, AnyValue]]:
        return iter(self._rows[row].items())

    @override
    def remove_row(self, row: _Row) -> None:
        if row in self._rows:
            del self._rows[row]
        for col in self._cols.values():
            if row in col:
                del col[row]

    def remove_col(self, col: _Col) -> None:
        """Remove column `col`."""
        if col in self._cols:
            del self._cols[col]
        for row in self._rows.values():
            if col in row:
                del row[col]

    def transpose(self) -> AbstractMatrix[_Col, _Row, AnyValue]:
        """Transpose matrix."""
        raise NotImplementedError()

    @override
    def __str__(self) -> str:
        out = []
        row = ["-"]
        col_keys = sorted(self._cols.keys())
        row.extend(f"{c_key}" for c_key in col_keys)
        out.append(row)

        for r_key in sorted(self._rows.keys()):
            row = [f"{r_key}"]
            row.extend(f"{self[r_key, c_key]}" for c_key in col_keys)
            out.append(row)
        return tabulate(out)


class TransposableMatrix(AbstractMatrix[_Row, _Col, AnyValue]):
    """A matrix that can be transposed."""

    def __delitem__(self, idx: tuple[_Row, _Col]):
        """Delete a cell."""
        raise NotImplementedError()

    def transpose(self) -> TransposableMatrix[_Col, _Row, AnyValue]:
        """Return a transposed matrix from this one."""
        raise NotImplementedError()


class Matrix(TransposableMatrix[_Row, _Col, AnyValue]):
    """Dict based matrix."""

    def __init__(
        self,
        default_value_f: Callable[[_Row, _Col], AnyValue],
        row_keys: Iterable[_Row],
        col_keys: Iterable[_Col],
    ):
        self._default_value_f = default_value_f
        # row-wise
        self._rows = OrderedDict(
            (r, OrderedDict((c, self._default_value_f(r, c)) for c in col_keys)) for r in row_keys
        )

        # col-wise
        self._cols = OrderedDict(
            (c, OrderedDict((r, self._rows[r][c]) for r in row_keys)) for c in col_keys
        )

    @override
    def transpose(self) -> TransposableMatrix[_Col, _Row, AnyValue]:
        return TransposedMatrix(self)

    @override
    def __delitem__(self, idx: tuple[_Row, _Col]):
        row, col = idx
        if row not in self._rows:
            return
        if col not in self._cols:
            return
        self[row, col] = self._default_value_f(row, col)


class TransposedMatrix(TransposableMatrix[_Row, _Col, AnyValue]):
    """Transposed view of a matrix."""

    def __init__(self, matrix: TransposableMatrix[_Col, _Row, AnyValue]):
        self._matrix = matrix
        self._rows = matrix._cols
        self._cols = matrix._rows

    @override
    def transpose(self) -> TransposableMatrix[_Col, _Row, AnyValue]:
        return self._matrix

    @override
    def __delitem__(self, idx: tuple[_Row, _Col]):
        row, col = idx
        del self._matrix[col, row]
