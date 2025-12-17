# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Tally computations for bi-proportional allocators."""

from __future__ import annotations
from typing import (
    Iterable,
    Generic,
    TypeVar,
    Callable,
)
from dataclasses import dataclass
from collections import deque

from ...quotas import (
    QuotaResolver,
    QuotaStatus,
)
from ..singlevote.iterative_divisor import (
    IterativeDivisorAllocator,
    Discrepancy,
)
from ..types import (
    Score,
    Candidate,
    SortHash,
    AnyName,
)
from ...logging import logger

from .table import (
    AbstractTable,
    Vertex,
    MatrixCell,
)


PartyName = TypeVar("PartyName", bound=SortHash)
DistrictName = TypeVar("DistrictName", bound=SortHash)


@dataclass
class BPTallyBoard(Generic[AnyName, PartyName, DistrictName]):
    """Bi-proportional allocator tally board.

    Args
    ----

    quota_f
        a quota resolver
    method_f
        a iterative divisor method
    tuple_f
        function that split a candidate name into party and district name
    """

    quota_f: QuotaResolver
    method_f: IterativeDivisorAllocator
    tuple_f: Callable[[AnyName], tuple[PartyName, DistrictName]]
    table: AbstractTable

    def exclude(self, candidates: Iterable[Candidate[AnyName]] | None = None):
        """Exclude candidates in this list from winning seats."""
        if candidates is None:
            return
        excluded = [c.with_name(self.tuple_f(c.name)) for c in Candidate.make_input(candidates)]
        for cand in excluded:
            party, district = cand.name
            # remove cell
            self.table.matrix[district, party].votes = 0
            # decrease district seats
            self.table.row_data[district].seats -= cand.seats
            # decrease party seats
            self.table.col_data[party].seats -= cand.seats

    def allocate_rows(self, under: frozenset[Vertex], over: frozenset[Vertex], is_row: bool):
        """Allocate row candidates and compute discrepancies."""
        for idx_row, row_data, row_cells in self.table.iter_rows():
            candidates = [
                (cand, cell.votes / self.table.col_data[cand].qrange.divisor)
                for (cand, cell) in row_cells.items()
                if cell.votes
            ]

            # row allocation
            result = self.method_f.calc(candidates, row_data.seats)
            assert result.data
            v_row = Vertex(is_row, idx_row)
            if v_row in under:
                status = QuotaStatus.UNDER
            elif v_row in over:
                status = QuotaStatus.OVER
            else:
                status = QuotaStatus.EXACT
            assert not isinstance(result.data.min_quota, float)
            quota: Score = self.quota_f.find(
                result.data.min_quota, result.data.max_quota, status=status
            )

            row_data.qrange.divisor = quota
            row_data.qrange.min_divisor = result.data.min_quota
            row_data.qrange.max_divisor = result.data.max_quota

            for party in result.allocation:
                row_cells[party.name].seats = party.seats
                row_cells[party.name].sign = result.data.ties[party.name]

        self.table.update_share()

    def transfer_ties(self) -> int:
        """Transfer ties to other candidates in order to reduce discrepancies."""
        n_transfers = 0
        while True:
            _r_seats, col_seats = self.table.seats_by_axis()
            under, over = self.table.col_discrepancies(col_seats)
            predecessor: dict[Vertex, Vertex]
            labeled_vertices, predecessor = self.find_transfer_paths(under)

            # transfer
            transfers = labeled_vertices.intersection(over)

            if not transfers:
                break

            # increase and decrease path
            for transfer in transfers:
                n_transfers += self.transfer(under, transfer, predecessor)

        return n_transfers

    def find_transfer_paths(
        self, initial_labels: Iterable[Vertex]
    ) -> tuple[set[Vertex], dict[Vertex, Vertex]]:
        """Breadth first search."""
        labels = set(initial_labels)
        predecessor: dict[Vertex, Vertex] = {}

        if not labels:
            return labels, predecessor

        queue = deque(labels)

        while queue:
            current = queue.popleft()

            status: Discrepancy
            if current.is_row:
                vertices = self.table.matrix.row(current.index)
                status = Discrepancy.DECREMENTABLE
            else:
                vertices = self.table.matrix.col(current.index)
                status = Discrepancy.INCREMENTABLE

            for name, cell in vertices.items():
                vertex = Vertex(not current.is_row, name)
                if vertex not in labels and cell.votes > 0:
                    if cell.sign == status:
                        queue.append(vertex)
                        labels.add(vertex)
                        predecessor[vertex] = current

        assert labels

        return labels, predecessor

    def transfer(
        self, under: frozenset[Vertex], vertex_from: Vertex, predecessor: dict[Vertex, Vertex]
    ) -> int:
        """Transfer a discrepancy.

        Return number of transfers.
        """
        n_transfers: int = 0

        table = self.table.matrix
        cand: MatrixCell
        while True:
            # r1 -> c1 (-1) -> r2 (+1)
            assert not vertex_from.is_row
            vertex_to = predecessor[vertex_from]
            cand = table[vertex_to.index, vertex_from.index]
            cand.seats -= 1
            cand.sign = Discrepancy.INCREMENTABLE

            logger.debug("biprop transfer from %s to %s: %d", vertex_to, vertex_from, -1)

            vertex_from = predecessor[vertex_to]
            cand = table[vertex_to.index, vertex_from.index]
            cand.seats += 1
            cand.sign = Discrepancy.DECREMENTABLE

            logger.debug("biprop transfer from %s to %s: %d", vertex_to, vertex_from, 1)

            n_transfers += 1

            if vertex_from in under:
                break

        return n_transfers
