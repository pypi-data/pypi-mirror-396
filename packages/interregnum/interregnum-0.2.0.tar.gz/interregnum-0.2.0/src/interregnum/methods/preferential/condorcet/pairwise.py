#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Table for Condorcet methods' auxiliary operations.

:ref:`References <interregnum_biblio>`
--------------------------------------

* [Schulze:2011]_

----
"""
from __future__ import annotations
from typing import (
    Iterable,
)
from ..types import (
    Preference,
    is_tie,
)
from ... import inputs as ipt
from ...types import Score, AnyName
from ....graphs import (
    UnweightedGraph,
    WeightedGraph,
)


class PairwiseTable(WeightedGraph[AnyName, Score]):
    """Bi-dimensional sparse table for Condorcet."""

    def __init__(self, nodes: ipt.INames):
        """Create a table with this `nodes`."""
        super().__init__(nodes, default=0)

    @classmethod
    def from_preferences(
        cls,
        preferences: Iterable[Preference[AnyName]],
        *,
        fill_truncated=False,
        all_nodes: ipt.INames | None = None,
    ) -> PairwiseTable[AnyName]:
        """Create a :class:`PairwiseTable` from a list of preferential votes.

        Each preferential vote is preceded by the number of occurrences.

        >>> votes = [
                (42, ('Memphis', 'Nashville', 'Chattanooga', 'Knoxville')),
                (26, ('Nashville', 'Chattanooga', 'Knoxville', 'Memphis')),
                (15, ('Chattanooga', 'Knoxville', 'Nashville', 'Memphis')),
                (17, ('Knoxville', 'Chattanooga', 'Nashville', 'Memphis'))
            ]
        >>> t = PairwiseTable.from_preferences(votes)
        """
        if not all_nodes:
            nodes: set[AnyName] = set()
            for group in preferences:
                nodes.update(group.specified_candidates())
        else:
            nodes = set(all_nodes)

        table = cls(nodes)

        for group in preferences:
            if fill_truncated:
                rivals = set(nodes)
            else:
                rivals = set(group.specified_candidates())

            for position in group.preference:
                if is_tie(position):
                    rivals.difference_update(position)
                else:
                    rivals.remove(position)
                    position = (position,)
                for name in position:
                    for rival in rivals:
                        table[name, rival] += group.votes

        return table

    def compare(self, cand1: AnyName, cand2: AnyName) -> tuple[AnyName, AnyName] | None:
        """Compare the elements at `cand1`-`cand2` and `cand2`-`cand1`.

        If the value of (x,y) is greater than the value of (y, x), return
        (x, y). If both values are equal, return `None`. Otherwise, return (y, x).

        >>> t = PairwiseTable()
        >>> t['Alice', 'Bob'] = 5
        >>> t['Bob', 'Alice'] = 7
        >>> t['Bob', 'Charles'] = 3
        >>> # ('Bob', 'Alice')
        >>> t.compare('Alice', 'Bob')
        >>> # ('Bob', 'Charles')
        >>> t.compare('Bob', 'Charles')
        >>> # None
        >>> t.compare('Alex', 'Zoe')
        """
        gain1 = self[cand1, cand2]
        gain2 = self[cand2, cand1]
        if gain1 > gain2:
            return (cand1, cand2)
        if gain1 < gain2:
            return (cand2, cand1)
        return None

    def margin(self, cand1: AnyName, cand2: AnyName) -> Score:
        """Return margin value between `cand1` and `cand2`.

        Return value at (cand1, cand2) minus value at (cand2, cand1)

        >>> t = PairwiseTable()
        >>> t['Alice', 'Bob'] = 5
        >>> t['Bob', 'Alice'] = 7
        >>> # -2
        >>> t.margin('Alice', 'Bob')
        """
        return self[cand1, cand2] - self[cand2, cand1]

    def margins(self) -> WeightedGraph[AnyName, Score | float]:
        """Return a weighted graph from margin values.

        The weight of an edge (x, y) will be `margin(x, y)`.
        """
        nodes = list(self.keys())
        table: WeightedGraph[AnyName, Score | float] = WeightedGraph(nodes, default=float("nan"))
        for cand_x in nodes:
            for cand_y in nodes:
                if cand_x == cand_y:
                    continue
                table[cand_x, cand_y] = self.margin(cand_x, cand_y)
        return table

    def win(self, cand1: AnyName, cand2: AnyName) -> Score:
        """Winner votes of (cand1, cand2) against (cand2, cand1).

        If cand1 does not win cand2, return 0.

        >>> t = PairwiseTable()
        >>> t['Alice', 'Bob'] = 5
        >>> t['Bob', 'Alice'] = 7
        >>> # 0
        >>> t.win('Alice', 'Bob')
        >>> # 7
        >>> t.win('Bob', 'Alice')
        """
        gain = self[cand1, cand2]
        if gain > self[cand2, cand1]:
            return gain
        return 0

    def wins(self) -> WeightedGraph[AnyName, Score | float]:
        """Return a weighted graph from win values.

        The weight of an edege (x, y) will be `win(x, y)`
        """
        nodes = list(self.keys())
        table: WeightedGraph[AnyName, Score | float] = WeightedGraph(nodes, default=float("nan"))
        for cand_x in nodes:
            for cand_y in nodes:
                if cand_x == cand_y:
                    continue
                table[cand_x, cand_y] = self.win(cand_x, cand_y)
        return table

    def purge(self, cand: AnyName):
        """Purge candidate from table."""
        self.remove_row(cand)
        self.remove_col(cand)

    def smith_set(self) -> set[AnyName]:
        """Compute Smith set."""
        nodes = list(self.keys())
        unbeaten = UnweightedGraph(nodes)
        for idx, cand1 in enumerate(nodes):
            for cand2 in nodes[(idx + 1) :]:
                value = self.margin(cand1, cand2)
                if value <= 0:
                    unbeaten.connect(cand1, cand2)
                if value >= 0:
                    unbeaten.connect(cand2, cand1)
        unbeaten.transitive_closure()
        smith = set(self.keys())
        size = len(smith)
        for cand in nodes:
            path = set(unbeaten.heads_for(cand))
            path.add(cand)
            new_size = len(path)
            if new_size < size:
                smith = path
                size = new_size
        return smith

    def schwartz_set(self) -> set[AnyName]:
        """Compute Schwartz set."""
        nodes = list(self.keys())
        wins = UnweightedGraph(nodes, loops=False)
        for idx, cand1 in enumerate(nodes):
            for cand2 in nodes[(idx + 1) :]:
                value = self.margin(cand1, cand2)
                if value > 0:
                    wins.connect(cand1, cand2)
                elif value < 0:
                    wins.connect(cand2, cand1)
        wins.transitive_closure()
        schwartz = set(nodes)
        for cand1 in nodes:
            for cand2 in nodes:
                if cand1 == cand2:
                    continue
                if wins[cand2, cand1] and not wins[cand1, cand2]:
                    if cand1 in schwartz:
                        schwartz.remove(cand1)
        return schwartz
