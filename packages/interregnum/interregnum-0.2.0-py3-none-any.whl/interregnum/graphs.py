#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Weighted and unweighted directed graphs."""

from __future__ import annotations
from typing import (
    Iterable,
    Iterator,
    TypeVar,
    Generic,
)
from collections import defaultdict
from .bidimensional.sparse import SparseTable, AnyValue
from .types import SortHash
from .tabulate import tabulate

_Key = TypeVar("_Key", bound=SortHash)


class WeightedGraph(SparseTable[_Key, _Key, AnyValue], Generic[_Key, AnyValue]):
    """A weighted directed graph."""

    def __init__(self, nodes: Iterable[_Key], default: AnyValue):
        """Create a graph with this set of `nodes` and use a `default` weight for edges."""
        super().__init__(default)
        self._nodes = list(nodes)

    def reachable(self, cand_from: _Key, cand_to: _Key) -> bool:
        """Return True if `cand_to` is reachable from `cand_from`.

        >>> t = PairwiseTable(["Alice", "Alex", "Bob", "Charles", "Zoe"], 0)

        >>> t['Alice', 'Bob'] = 5
        >>> t['Bob', 'Alice'] = 7
        >>> t['Bob', 'Charles'] = 3
        >>> t['Alex', 'Zoe'] = 1
        >>> # True
        >>> t.reachable('Alice', 'Charles')
        >>> # False
        >>> t.reachable('Alice', 'Zoe')
        """
        if cand_from not in self.row_keys():
            return False

        if (cand_to in self.row(cand_from).keys()) and (self[cand_from, cand_to] != self._default):
            return True

        middle = frozenset(self.row(cand_from).keys()).difference((cand_to,))
        return any(self.reachable(cand_from, m) and self.reachable(m, cand_to) for m in middle)

    def keys(self) -> Iterator[_Key]:
        """Return node set."""
        return iter(frozenset(self._nodes))

    def source(self) -> frozenset[_Key]:
        """Return set of source nodes.

        >>> t = PairwiseTable(["Alice", "Alex", "Bob", "Charles", "Zoe"], 0)
        >>> t['Alice', 'Bob'] = 5
        >>> t['Bob', 'Alice'] = 7
        >>> t['Bob', 'Charles'] = 3
        >>> t['Alex', 'Zoe'] = 1
        >>> # ['Alex']
        >>> t.source()
        """
        row_set = frozenset(self.row_keys()).union(self._nodes)
        return row_set.difference(self.iter_col_keys())

    def sink(self) -> frozenset[_Key]:
        """Return set of sink nodes.

        >>> t = PairwiseTable(["Alice", "Alex", "Bob", "Charles", "Zoe"], 0)
        >>> t['Alice', 'Bob'] = 5
        >>> t['Bob', 'Alice'] = 7
        >>> t['Bob', 'Charles'] = 3
        >>> t['Alex', 'Zoe'] = 1
        >>> # ['Charles', 'Zoe']
        >>> t.sink()
        """
        col_set = frozenset(self.iter_col_keys()).union(self._nodes)
        return col_set.difference(self.row_keys())


class UnweightedGraph(Generic[_Key]):
    """Unweighted directed graph."""

    _data: dict[_Key, set[_Key]]

    def __init__(self, nodes: Iterable[_Key] | None = None, *, loops=False):
        """Create a graph with this set of `nodes`.

        If `loops` is False, trying to create a loop will raise a ValueError exception.
        """
        self._data = defaultdict(set)
        self._loops = loops
        self._nodes = list(nodes) if nodes else None

    def __getitem__(self, idx: tuple[_Key, _Key]) -> bool:
        """Return `True` if there is an edge from `idx[0]` to `idx[1]`."""
        tail, head = idx

        heads = self._data.get(tail)
        return (heads is not None) and (head in heads)

    def __contains__(self, idx: tuple[_Key, _Key]) -> bool:
        """Return `True` if the edge `idx` is in this graph."""
        return self[idx]

    def __delitem__(self, idx: tuple[_Key, _Key]) -> None:
        """Remove the edge `idx`."""
        tail, head = idx
        heads = self._data.get(tail)
        if heads and (head in heads):
            heads.remove(head)
            if not heads:
                del self._data[tail]

    def connect(self, tail: _Key, head: _Key) -> None:
        """Set an arc from tail to head."""
        if not self._loops and (tail == head):
            raise ValueError("Loops are forbidden")
        self._data[tail].add(head)

    def heads_for(self, tail: _Key) -> Iterator[_Key]:
        """Iterate heads for connections given a 'tail'."""
        if tail in self._data:
            yield from self._data[tail]

    def tails(self):
        """Return nodes in the tails set."""
        return self._data.keys()

    def heads(self) -> Iterator[_Key]:
        """Return nodes in the heads set."""
        seen = set()
        for items in self._data.values():
            for head in items:
                if head not in seen:
                    yield head
                    seen.add(head)

    def reachable(self, node_x, node_y, closure=False) -> bool:
        """Return True if there is a path from node_x to node_y.

        If closure is True, transitive arcs are created. That is,
        if a path is discovered from node_x to m, and a path is discovered
        from m to node_y, a new arc (node_x, node_y) is created.
        """
        if node_x not in self._data:
            return False

        reachable_x = self._data[node_x]
        if node_y in reachable_x:
            return True

        for middle in reachable_x:
            if middle == node_x:
                continue
            if self.reachable(node_x, middle, closure) and self.reachable(middle, node_y, closure):
                if closure:
                    self.connect(node_x, node_y)
                return True
        return False

    def sources(self) -> frozenset[_Key]:
        """Return set of source keys.

        >>> t = PairwiseTable()
        >>> t.connect('Alice', 'Bob')
        >>> t.connect('Bob', 'Alice')
        >>> t.connect('Bob', 'Charles')
        >>> t.connect('Alex', 'Zoe')
        >>> # ['Alex']
        >>> t.source()
        """
        if self._nodes is not None:
            nodes = frozenset(self._nodes)
        else:
            nodes = frozenset(self.tails())
        return nodes.difference(self.heads())

    def sinks(self) -> frozenset[_Key]:
        """Return set of sink keys.

        >>> t = PairwiseTable()
        >>> t.connect('Alice', 'Bob')
        >>> t.connect('Bob', 'Alice')
        >>> t.connect('Bob', 'Charles')
        >>> t.connect('Alex', 'Zoe')
        >>> # ['Charles', 'Zoe']
        >>> t.sink()
        """
        if self._nodes is not None:
            nodes = frozenset(self._nodes)
        else:
            nodes = frozenset(self.heads())
        return nodes.difference(self.tails())

    def existing_nodes(self) -> frozenset[_Key]:
        """Return the subset of nodes with arcs."""
        return frozenset(self.tails()).union(self.heads())

    def all_nodes(self) -> frozenset[_Key]:
        """Set of all known nodes."""
        if self._nodes is not None:
            return frozenset(self._nodes)
        return self.existing_nodes()

    def printable(self, all_nodes: Iterable[_Key] | None = None) -> str:
        """Return a printable representation."""
        if all_nodes:
            nodes = list(all_nodes)
        else:
            nodes = sorted(self.all_nodes())
        out = []
        row = ["-"]
        row.extend(f"{c_key}" for c_key in nodes)
        out.append(row)

        for r_key in nodes:
            row = [f"{r_key}"]
            for c_key in nodes:
                val = "*" if self[r_key, c_key] else " "
                row.append(f"{val}")
            out.append(row)

        return tabulate(out)

    def transitive_closure(self, all_nodes: Iterable[_Key] | None = None):
        """Compute in-site the transitive closure of this graph."""
        if all_nodes:
            nodes = list(all_nodes)
        else:
            nodes = sorted(self.all_nodes())
        for middle in nodes:
            for node_x in nodes:
                if not self._loops and (middle == node_x):
                    continue
                for node_y in nodes:
                    if not self._loops and (node_y in (middle, node_x)):
                        continue
                    if self[node_x, node_y]:
                        continue
                    if self[node_x, middle] and self[middle, node_y]:
                        self.connect(node_x, node_y)

    def __str__(self):
        """Return `printable()`."""
        return self.printable()
