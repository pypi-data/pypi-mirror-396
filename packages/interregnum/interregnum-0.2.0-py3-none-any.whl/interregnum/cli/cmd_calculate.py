#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Allocate seats for an electoral system."""

from __future__ import annotations
from typing import (
    Iterable,
    Generator,
    Sequence,
)
import argparse
from pathlib import Path

from .. import district as ds
from . import files as fl
from ..district import io
from ..district import serialize as sr
from ..district.district import BallotsNode
from ..district.contenders import ContenderId
from ..methods.types import Candidate


def update_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Update parser with this command."""
    parser.add_argument(
        "source", type=Path, help="electoral system (supported formats: json, yaml)"
    )
    parser.add_argument(
        "target", type=Path, help="electoral system with results (supported formats: json, yaml)"
    )
    parser.add_argument("--src-encoding", type=str, default="utf-8", help="source char encoding")
    parser.add_argument("--tgt-encoding", type=str, default="utf-8", help="target char encoding")
    parser.add_argument(
        "--decimals",
        type=int,
        help=(
            "show rational numbers using floating point notation rounded "
            "to this number of decimals, otherwise use original fractions."
        ),
    )

    input_data = parser.add_argument_group("optional input data")
    input_data.add_argument(
        "-c",
        "--candidates",
        nargs="+",
        type=str,
        help="""Populate candidates with data from this files.

        If the target node is not specified in the files, prefix the node key to
        the filename: <node key>:<file name>.

        If no node key is found, all data will be populated to the root node.

        Supported formats: json, yaml, csv, tsv.
        """,
    )
    input_data.add_argument(
        "-p",
        "--preferences",
        nargs="+",
        type=str,
        help="""Populate preferences with data from this files.

        The target node can be specified prefixing it to the filename: <node key>:<file name>.

        If no node key is found, all data will be populated to the root node.

        Supported formats: pref, yaml, json.
        """,
    )
    output_data = parser.add_argument_group("optional output data")
    output_data.add_argument(
        "-r",
        "--results",
        type=Path,
        help="""Dump results to this file.

        Supported formats: json, yaml, csv, tsv
        """,
    )
    parser.set_defaults(func=command)

    return parser


def _split_data_nodes(paths: Iterable[Path] | None) -> Generator[tuple[str | None, Path]]:
    if not paths:
        return
    for path in paths:
        node, _, realpath = str(path).rpartition(":")
        yield node or None, Path(realpath)


def command(args: argparse.Namespace) -> None:
    """Allocate seats for an electoral system."""
    cwd: Path = args.source.parent
    root = ds.unserialize_node(fl.read_dict_file(args.source, args.src_encoding), cwd=cwd)
    assert isinstance(root, ds.Node)
    root_id = root.get_id()

    # fill candidates
    for node_id, path in _split_data_nodes(args.candidates):
        node = root.find_district(node_id or root_id)
        if not node:
            raise ValueError(f"node {node_id} not found")
        sr.fill_node_candidates(node, io.CandidatesFile.from_path(path, cwd))

    # fill preferences
    for node_id, path in _split_data_nodes(args.preferences):
        node = root.find_district(node_id or root_id)
        if not node:
            raise ValueError(f"node {node_id} not found")
        if not isinstance(node, BallotsNode):
            raise ValueError(f"could not set preferences to node {node_id}")
        node.preferences = io.PreferencesFile.from_path(path, cwd)

    root.calculate()

    if args.results:
        dumpfile = io.CandidatesFile.from_path(args.results, args.target.parent)
        dumpfile.encoding = args.tgt_encoding
        dumpfile.write_data(_iter_results(root))

    fl.write_electoral_system(root, args.target, args.decimals, encoding=args.tgt_encoding)


def _iter_results(root: ds.Node) -> Generator[tuple[str, Sequence[Candidate[ContenderId]]]]:
    if root.result:
        yield root.get_id(), root.result.allocation
    for node in root.local_children():
        yield from _iter_results(node)
