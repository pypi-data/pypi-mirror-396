# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Test ranks."""

from fractions import Fraction
import pytest
from .. import ranks


def check_rank_function(rank_f, size: int, pos: int, expected):
    """Check rank function."""
    value = rank_f(size, pos)
    assert value == expected, {"size": size, "pos": pos, "expected": expected, "value": value}


@pytest.mark.parametrize(
    "size,pos,expected",
    [
        (10, 0, 10),
        (10, 1, 9),
        (10, 2, 8),
        (10, 3, 7),
        (10, 4, 6),
        (10, 5, 5),
        (10, 6, 4),
        (10, 7, 3),
        (10, 8, 2),
        (10, 9, 1),
        (10, 10, 0),
        (10, 20, 0),
        (10, -1, 0),
        (4, 0, 4),
        (4, 1, 3),
        (4, 2, 2),
        (4, 3, 1),
        (4, 4, 0),
        (4, -1, 0),
    ],
)
def test_rank_n(size, pos, expected):
    """Test rank_n function."""
    check_rank_function(ranks.rank_n, size, pos, expected)


@pytest.mark.parametrize(
    "size,pos,expected",
    [
        (10, 0, 9),
        (10, 1, 8),
        (10, 2, 7),
        (10, 3, 6),
        (10, 4, 5),
        (10, 5, 4),
        (10, 6, 3),
        (10, 7, 2),
        (10, 8, 1),
        (10, 9, 0),
        (10, 10, 0),
        (10, 20, 0),
        (10, -1, 0),
        (4, 0, 3),
        (4, 1, 2),
        (4, 2, 1),
        (4, 3, 0),
        (4, 4, 0),
        (4, -1, 0),
    ],
)
def test_rank_n_1(size, pos, expected):
    """Test rank_n_1 function."""
    check_rank_function(ranks.rank_n_1, size, pos, expected)


@pytest.mark.parametrize(
    "size,pos,expected",
    [
        (10, 0, Fraction(1, 1)),
        (10, 1, Fraction(1, 2)),
        (10, 2, Fraction(1, 3)),
        (10, 3, Fraction(1, 4)),
        (10, 4, Fraction(1, 5)),
        (10, 5, Fraction(1, 6)),
        (10, 6, Fraction(1, 7)),
        (10, 7, Fraction(1, 8)),
        (10, 8, Fraction(1, 9)),
        (10, 9, Fraction(1, 10)),
        (10, 10, Fraction(1, 11)),
        (10, 20, Fraction(1, 21)),
        (10, -1, Fraction(0)),
        (4, 0, Fraction(1, 1)),
        (4, 1, Fraction(1, 2)),
        (4, 2, Fraction(1, 3)),
        (4, 3, Fraction(1, 4)),
        (4, 4, Fraction(1, 5)),
        (4, -1, Fraction(0)),
    ],
)
def test_rank_nauru(size, pos, expected):
    """Test rank_nauru function."""
    check_rank_function(ranks.rank_nauru, size, pos, expected)
