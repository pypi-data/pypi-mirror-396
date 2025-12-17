#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Generate a dependency graph in dot format."""

from __future__ import annotations
from typing import IO
import argparse
from pathlib import Path
from collections import defaultdict

from .. import district as ds
from ..district.node import AllocationContext
from ..graphs import WeightedGraph
from . import files as fl


_FILE_TYPE = argparse.FileType("wt", encoding="utf-8")

V_NESTED = 2
V_REF = 1


def update_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Update parser with this command."""
    parser.add_argument("source", type=Path, help="electoral system")
    parser.add_argument("dotfile", nargs="?", type=_FILE_TYPE, help="dot file")
    parser.add_argument("--src-encoding", type=str, default="utf-8", help="source char encoding")
    parser.set_defaults(func=command)

    return parser


def build_dependency_graph(
    context: AllocationContext,
) -> tuple[dict[str, list[str]], WeightedGraph[str, int]]:
    """Create a dependency graph from an electoral system.

    Args
    ----
    context
        an allocation context

    Return
    ------
    :
        Group of nodes by parent and weighted graph. Arcs with weight=2 indicate a parent-child
        relation. Arcs with weight=1 indicate a result dependency.
    """
    graph: WeightedGraph[str, int] = WeightedGraph(nodes=list(context.keys), default=0)
    clusters: dict[str, list[str]] = {}
    for node_id, info in context.keys.items():
        # hard deps
        if divisions := info.node.local_divisions():
            nested = [n.get_id() for n in divisions if isinstance(n, ds.Node)]
            for dep_id in nested:
                graph[node_id, dep_id] = V_NESTED
            if nested:
                clusters[node_id] = nested

        for dep_id in context.dependencies(node_id, restrictions=True):
            graph[node_id, dep_id] = max(graph[node_id, dep_id], V_REF)

    return clusters, graph


def safe_key(text: str) -> str:
    """Return a key compatible with DOT format."""
    return '"' + text.replace('"', r"\"") + '"'


def print_graph(
    stream: IO[str], graph: WeightedGraph[str, int], clusters: dict[str, list[str]]
) -> None:
    """Print a dependency graph using the DOT format.

    Args
    ----
    stream
        output stream
    graph
        dependency graph
    clusters
        groups of nodes
    """
    print("digraph {", file=stream)
    for node_id in graph.iter_row_keys():
        source_key = safe_key(node_id)
        if node_id in clusters:
            rank = ", ".join(safe_key(x) for x in clusters[node_id])
            print(f"{{ rank=same; {rank} }}", file=stream)
        groups = defaultdict(list)
        for dest_id, value in graph.iter_row(node_id):
            dest_key = safe_key(dest_id)
            if not value:
                continue
            suffix = "" if value == V_NESTED else " [style=dashed]"
            groups[suffix].append(dest_key)
        for suffix, heads in groups.items():
            if not heads:
                continue
            body = ", ".join(heads)
            print(f"{source_key} -> {{ {body} }}{suffix}", file=stream)
    print("}", file=stream)


def command(args: argparse.Namespace) -> None:
    """Generate graph."""
    output = args.dotfile or _FILE_TYPE("-")
    root = ds.unserialize_node(
        fl.read_dict_file(args.source, args.src_encoding), cwd=args.source.parent
    )
    assert isinstance(root, ds.Node)
    clusters, graph = build_dependency_graph(root.build())

    print_graph(output, graph, clusters)
