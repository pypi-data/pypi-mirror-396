#!/usr/bin/source python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Functions for ranked ballots."""
from __future__ import annotations
from typing import (
    Callable,
)

from fractions import Fraction

from .collections import FunctionCollection
from .types import Score


RankFunction = Callable[[int, int], Score]
"A function for ranking. Return a score from a position and a ballot size"

ranks: FunctionCollection[RankFunction] = FunctionCollection()
"Collection for ranking functions."


@ranks.register("borda", "n")
def rank_n(ballot_size: int, pos: int) -> int:
    """Borda ranking.

    :math:`rank(ballotsize, pos) = ballotsize - pos`

    >>> [rank_n(10, n) for n in range(10)]
    [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    """
    if 0 <= pos <= ballot_size:
        return ballot_size - pos
    return 0


@ranks.register("tournament", "n_1", "n-1")
def rank_n_1(ballot_size: int, pos: int) -> int:
    """Tournament ranking.

    :math:`rank(ballotsize, pos) = ballotsize - pos - 1`

    >>> [rank_n_1(10, n) for n in range(10)]
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    """
    if 0 <= pos < ballot_size:
        return ballot_size - pos - 1
    return 0


@ranks.register("nauru", "dowdall")
def rank_nauru(_ballot_size: int, pos: int) -> Fraction:
    r"""Dowdall ranking, used in Nauru's electoral system.

    :math:`rank(ballotsize, pos) = \frac{1}{pos + 1}`

    >>> [float(rank_nauru(10, n)) for n in range(10)]
    [1.0, 0.5, 0.3333333333333333, 0.25, 0.2, 0.16666666666666666,
        0.14285714285714285, 0.125, 0.1111111111111111, 0.1]
    """
    if pos < 0:
        return Fraction(0)
    return Fraction(1, pos + 1)
