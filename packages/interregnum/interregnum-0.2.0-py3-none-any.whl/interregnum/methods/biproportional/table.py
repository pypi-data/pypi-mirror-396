#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Auxiliar table for the bi-proportional allocator."""

from __future__ import annotations
from typing import (
    Any,
    Generic,
    Tuple,
    FrozenSet,
    NamedTuple,
    TypeVar,
)
from dataclasses import dataclass
from fractions import Fraction
from collections import (
    OrderedDict,
    defaultdict,
)
from ...quotas import QuotaResolver
from ..singlevote.iterative_divisor import (
    Discrepancy,
)
from ..types import (
    # AnyName,
    Score,
    SortHash,
    AnyName,
)
from ...rounding import FRAC_ZERO
from ...bidimensional.matrix import Matrix, TransposableMatrix
from ...tabulate import tabulate


RowName = TypeVar("RowName", bound=SortHash)
ColName = TypeVar("ColName", bound=SortHash)


class Vertex(NamedTuple):
    """Row or column element."""

    is_row: bool
    index: Any


class MatrixCell:
    """A matrix cell with info about votes, seats, share and discrepancies."""

    __slots__ = "votes", "seats", "share", "sign"

    def __init__(
        self,
        votes: int = 0,
        seats: int = 0,
        share: Fraction = FRAC_ZERO,
        sign: Discrepancy = Discrepancy.EXACT,
    ):
        self.votes = votes
        self.seats = seats
        self.share = share
        self.sign = sign

    @classmethod
    def empty(cls, *_args) -> MatrixCell:
        """Return an empty cell."""
        return cls()

    def __str__(self):
        """Return a human-readable representation."""
        if self.sign == Discrepancy.EXACT:
            sign = ""
        elif self.sign == Discrepancy.DECREMENTABLE:
            sign = "-"
        else:
            sign = "+"
        return f"{self.seats}{sign} [{float(self.share):0.3f}] ({self.votes})"


@dataclass
class DivisorRange:
    """A divisor range.

    Store a representative divisor, minimum and maximum.
    """

    divisor: Score
    min_divisor: Score
    max_divisor: Score

    def nice(self) -> None:
        """Set `divisor` as a nice value easy to read."""
        self.divisor = QuotaResolver.nice(self.divisor, self.min_divisor, self.max_divisor)


class VectorSummary:
    """Summary for a vector (row or column)."""

    __slots__ = "seats", "qrange"

    def __init__(self, seats: int = 0, divisor: DivisorRange | None = None):
        """Create a vector summary.

        Args
        ----
        seats
            allocated seats
        divisor
            divisor range
        """
        self.seats = seats
        self.qrange = divisor or DivisorRange(Fraction(1), Fraction(1), Fraction(1))

    def __repr__(self):
        """Return a human-readable representation."""
        return f"(s: {self.seats}, div: {self.qrange})"


TSplit = Tuple[FrozenSet[Vertex], FrozenSet[Vertex]]


def _axis_discrepancies(
    axis_seats: dict[AnyName, int], axis_data: dict[AnyName, VectorSummary], is_row: bool
) -> TSplit:
    under = []
    over = []

    for index, seats in axis_seats.items():
        final_seats = axis_data[index].seats
        if seats < final_seats:
            under.append(Vertex(is_row=is_row, index=index))
        elif seats > final_seats:
            over.append(Vertex(is_row=is_row, index=index))

    return frozenset(under), frozenset(over)


class AbstractTable(Generic[RowName, ColName]):
    """Definition for a bi-proportional allocator calculation matrix."""

    __slots__ = "row_data", "col_data", "matrix"

    matrix: TransposableMatrix[RowName, ColName, MatrixCell]
    col_data: dict[ColName, VectorSummary]
    row_data: dict[RowName, VectorSummary]

    def transpose(self) -> AbstractTable[ColName, RowName]:
        """Return a transposed table."""
        raise NotImplementedError()

    def original(self) -> AbstractTable:
        """Return the original table, without transpositions."""
        raise NotImplementedError()

    def seats_by_axis(self) -> tuple[dict[RowName, int], dict[ColName, int]]:
        """Return sums per rows and cols."""
        r_sums: dict[RowName, int] = defaultdict(lambda: 0)
        c_sums: dict[ColName, int] = defaultdict(lambda: 0)

        for (r_idx, c_idx), value in self.matrix:
            r_sums[r_idx] += value.seats
            c_sums[c_idx] += value.seats

        return r_sums, c_sums

    def __str__(self):
        """Return a human-readable representation."""
        headers = [""]
        for c_idx, value in self.col_data.items():
            real_seats = sum(x.seats for x in self.matrix.col(c_idx).values())
            headers.append(f"{c_idx} [{value.seats}]{real_seats - value.seats:+d}")
        headers.append("div")

        rows = []
        for r_idx, data in self.row_data.items():
            p_row = self.matrix.row(r_idx)
            p_cells = [p_row[c] for c in self.col_data.keys()]
            real_seats = sum(v.seats for v in p_cells)
            row = (
                [f"{r_idx} [{data.seats}]{real_seats - data.seats:+d}"]
                + [str(v) for v in p_cells]
                + [f"{float(data.qrange.divisor):0.5f}"]
            )
            rows.append(row)

        rows.append(
            ["div"] + [f"{float(v.qrange.divisor):0.3f}" for v in self.col_data.values()] + [""]
        )

        return tabulate([headers] + rows)

    def row_discrepancies(self, row_seats: dict[RowName, int]) -> TSplit:
        """Split rows by under and over apportioned."""
        return _axis_discrepancies(row_seats, self.row_data, is_row=True)

    def col_discrepancies(self, col_seats: dict[ColName, int]) -> TSplit:
        """Split cols by under and over apportioned."""
        return _axis_discrepancies(col_seats, self.col_data, is_row=False)

    def iter_rows(self):
        """Iterate items by row."""
        for r_idx, r_cells in self.matrix.iter_rows():
            v_cell = self.row_data[r_idx]
            yield r_idx, v_cell, r_cells

    def update_share(self) -> None:
        """Update share for every cell."""
        for (r_idx, c_idx), cell in self.matrix:
            if cell.votes > 0:
                r_divisor = self.row_data[r_idx].qrange.divisor
                c_divisor = self.col_data[c_idx].qrange.divisor
                cell.share = Fraction(cell.votes, (r_divisor * c_divisor))


class Table(AbstractTable[RowName, ColName]):
    """Transposable table for bi-proportional allocator calculation."""

    def __init__(self, row_seats: dict[RowName, int], col_seats: dict[ColName, int]):
        """Create a table.

        `row_seats` and `col_seats` store the two proportional allocations.
        """
        self.row_data = OrderedDict(
            (r, VectorSummary(seats)) for r, seats in row_seats.items()  # sorted(row_seats.items())
        )
        self.col_data = OrderedDict(
            (c, VectorSummary(seats)) for c, seats in col_seats.items()  # sorted(col_seats.items())
        )
        self.matrix: TransposableMatrix[RowName, ColName, MatrixCell] = Matrix(
            default_value_f=MatrixCell.empty,
            row_keys=row_seats.keys(),
            col_keys=col_seats.keys(),
        )

    def transpose(self) -> AbstractTable[ColName, RowName]:
        """Return a transposed matrix."""
        return _TransposedTable(self)

    def original(self) -> Table[RowName, ColName]:
        """Return the original matrix, not a transposed one."""
        return self


class _TransposedTable(AbstractTable[RowName, ColName]):

    __slots__ = ("source",)

    def __init__(self, matrix: Table[ColName, RowName]):
        self.source: Table[ColName, RowName] = matrix
        self.matrix = matrix.matrix.transpose()
        self.row_data = matrix.col_data
        self.col_data = matrix.row_data

    def transpose(self) -> Table[ColName, RowName]:
        return self.source

    def original(self) -> Table[ColName, RowName]:
        return self.source
