#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Dump an electoral system schema to file."""
from __future__ import annotations
import argparse
from pathlib import Path

from .. import district as ds
from . import files as fl


def update_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Update parser with this command."""
    parser.add_argument(
        "-s", "--skeleton", action="store_true", help="do not dump ballots or results"
    )
    parser.add_argument("source", type=Path, help="original electoral system")
    parser.add_argument("target", type=Path, help="destination file")
    parser.add_argument("--src-encoding", type=str, default="utf-8", help="source char encoding")
    parser.add_argument("--tgt-encoding", type=str, default="utf-8", help="target char encoding")
    parser.set_defaults(func=command)

    return parser


def command(args: argparse.Namespace) -> None:
    """Dump an electoral system schema."""
    root = ds.unserialize_node(
        fl.read_dict_file(args.source, args.src_encoding), cwd=args.source.parent
    )
    assert isinstance(root, ds.Node)
    if args.skeleton:
        root.clear_data()

    fl.write_electoral_system(root, args.target, args.decimals, encoding=args.tgt_encoding)
