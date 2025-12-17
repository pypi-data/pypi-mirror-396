#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Depth First Search."""

from __future__ import annotations
from typing import (
    TypeVar,
    Callable,
    Any,
    Iterator,
    Hashable,
)

_Node = TypeVar("_Node", bound=Hashable)


class CycleDetectedError(Exception):
    """Raised when a depth first search has found a cycle."""


def depth_first_search(
    edges: Callable[[_Node], Iterator[_Node]], action: Callable[[_Node], Any], root: _Node
):
    """Depth first search algorithm for acyclic directed graphs.

    Args
    ----
    edges
        function that returns all reachable nodes from one node.
    action
        action to perform for a node
    root
        node where the search begins

    Raises
    ------
    CycleDetectedError
        when a cycle is found
    """
    marks: dict[_Node, int] = {}

    def visit(node: _Node):
        status = marks.get(node)
        if status == 1:
            # permanent mark
            return
        if status == -1:
            # temporary mark
            raise CycleDetectedError(f"cycle detected: {node}")

        marks[node] = -1

        for other in frozenset(edges(node)):
            visit(other)

        marks[node] = 1
        action(node)

    visit(root)
