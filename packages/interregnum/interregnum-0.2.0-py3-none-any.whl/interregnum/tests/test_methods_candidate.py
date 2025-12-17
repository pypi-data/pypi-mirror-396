# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Tests for candidates."""

import pytest
from ..methods.types import Candidate


def check_values(candidate: Candidate, votes: int, seats: int):
    """Check votes and seats for a candidate."""
    assert candidate.votes == votes, candidate
    assert candidate.seats == seats, candidate


@pytest.mark.parametrize(
    "cand,new_seats,expected",
    [
        (Candidate("a", 123), 2, 2),
        (Candidate("b", 123, 5), 2, 2),
    ],
)
def test_with_seats(cand, new_seats, expected):
    """Check that a candidate store seats correctly."""
    new_cand = cand.with_seats(new_seats)
    check_values(new_cand, cand.votes, expected)


@pytest.mark.parametrize(
    "cand,new_seats,expected",
    [
        (Candidate("a", 123), 2, 2),
        (Candidate("b", 123, 5), 2, 7),
    ],
)
def test_add_seats(cand, new_seats, expected):
    """Check that a candidate store votes correctly."""
    new_cand = cand.add_seats(new_seats)
    check_values(new_cand, cand.votes, expected)
