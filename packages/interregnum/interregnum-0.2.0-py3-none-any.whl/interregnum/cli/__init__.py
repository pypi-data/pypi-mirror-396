#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Command line tool."""
from __future__ import annotations

import argparse
import logging
import sys

from .._version import __version__
from ..logging import logger

from . import cmd_dump
from . import cmd_calculate
from . import cmd_list
from . import cmd_graph


def getparser() -> argparse.ArgumentParser:
    """Get argument parser."""
    parser = argparse.ArgumentParser(
        description="Calculate election results",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--version", dest="version", action="version", version="%(prog)s " + __version__
    )
    parser.add_argument(
        "--decimals",
        type=int,
        help=(
            "show rational numbers using floating point notation rounded "
            "to this number of decimals, otherwise use original fractions."
        ),
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="show additional info")
    subparsers = parser.add_subparsers()
    subparsers.required = True
    # calc
    cmd_calculate.update_parser(
        subparsers.add_parser(
            "calculate",
            aliases=["c", "calc", "allocate", "alloc"],
            help=cmd_calculate.__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
    )

    # dump schema
    cmd_dump.update_parser(
        subparsers.add_parser(
            "dump",
            aliases=["d"],
            help=cmd_dump.__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
    )

    # list collection
    cmd_list.update_parser(
        subparsers.add_parser(
            "list",
            aliases=["l", "collection"],
            help=cmd_list.__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
    )

    # dump dependency graph
    cmd_graph.update_parser(
        subparsers.add_parser(
            "graph",
            aliases=["g", "dot", "deps"],
            help=cmd_graph.__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
    )

    return parser


def main() -> None:
    """CLI main invokation."""
    parser = getparser()
    args = parser.parse_args()
    if len(args.__dict__) < 1:
        parser.print_help()
        parser.exit(2)

    if args.verbose:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter("%(levelname)s: %(asctime)s: %(message)s")
        handler.setFormatter(formatter)
        logger.setLevel(logging.DEBUG)
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.propagate = False

    args.func(args)


if __name__ == "__main__":
    main()
