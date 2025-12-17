#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Enumerate a collection."""
from __future__ import annotations
import argparse
from collections import defaultdict

from ..collections import FunctionCollection
from ..methods import allocators
from ..divisors import (
    divisors,
    divisor_iterators,
)
from ..quotas import quotas
from ..ranks import ranks
from ..rounding import (
    roundings,
    signposts,
)
from ..methods.preferential import transfers


COLLECTIONS: dict[str, FunctionCollection] = {
    "allocators": allocators,
    "divisors": divisors,
    "divisor_iterators": divisor_iterators,
    "quotas": quotas,
    "ranks": ranks,
    "roundings": roundings,
    "signposts": signposts,
    "transfers": transfers,
}


def update_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Update parser with this command."""
    parser.add_argument(
        "collection", nargs="?", choices=sorted(COLLECTIONS), help="collection name"
    )
    parser.set_defaults(func=command)

    return parser


def command(args: argparse.Namespace) -> None:
    """List collections."""
    collections: list[str]
    if args.collection:
        collections = [args.collection]
    else:
        collections = sorted(COLLECTIONS)

    for colname in collections:
        print_collection(colname)


def print_collection(name: str) -> None:
    """Print collection items to stdout."""
    print()
    print(name)
    print("-" * len(name))

    aliases = defaultdict(list)
    for key, function in COLLECTIONS[name].items.items():
        aliases[function].append(key)

    for names in aliases.values():
        line = ",".join(f"'{x}'" for x in sorted(names))
        print(f"* {line}")
