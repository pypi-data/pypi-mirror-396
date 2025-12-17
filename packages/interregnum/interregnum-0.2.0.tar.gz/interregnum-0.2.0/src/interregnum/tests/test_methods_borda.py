# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Tests for Borda methods."""

from pathlib import Path
import pytest
from .common import iter_problem_filenames

from ..methods.preferential.borda_count import BordaCountAllocator
from ..methods.types import PreconditionError


PROBLEM_DIR = Path("fixtures") / "borda"


@pytest.mark.parametrize(
    "problem", list(iter_problem_filenames(PROBLEM_DIR)), ids=lambda x: x.name, indirect=True
)
def test_borda_count_allocator(problem):
    """Check problems defined in files."""
    method = BordaCountAllocator(**problem["params"])
    result = method.calc(problem["votes"], problem["seats"], random_seed=1)
    assert result.deterministic == problem["deterministic"]
    expected = set(problem["winners"])
    elected = set()
    for cand in result.allocation:
        assert cand.seats in (0, 1)
        if cand.seats > 0:
            elected.add(cand.name)
    assert expected == elected, (expected, elected)


@pytest.fixture(params=["borda", "tournament", "nauru"])
def rank(request):
    """Return ranking functions."""
    return request.param


@pytest.fixture(params=["up", "down", "average", None])
def counting(request):
    """Return counting strategies."""
    return request.param


def test_borda_count_allocator_s3_c3_b_null_no_ballotsize(rank):
    """Test calc.

    3 seats, 3 candidates, empty ballots, no ballot size.
    """
    prefs = [[0, []]]
    seats = 3
    candidates = ["A", "B", "C"]
    method = BordaCountAllocator(rank)

    with pytest.raises(PreconditionError):
        method.calc(prefs, seats, candidate_list=candidates)


def test_borda_count_allocator_s3_c3_bs3_b_null(rank, counting):
    """Test calc.

    3 seats, 3 candidates, empty ballots, ballot size=3.
    """
    prefs = [[0, []]]
    seats = 3
    candidates = ["A", "B", "C"]
    method = BordaCountAllocator(rank, tie_counting=counting)

    result = method.calc(prefs, seats, candidate_list=candidates, max_ballot_size=3)
    assert result.deterministic

    elected = frozenset(x.name for x in result.allocation)
    assert frozenset(candidates) == elected


def test_borda_count_allocator_s3_c0_bs3_b_null(rank, counting):
    """Test calc.

    3 seats, no candidates, empty ballots, ballot size=3
    """
    prefs = [[0, []]]
    seats = 3
    method = BordaCountAllocator(rank, tie_counting=counting)

    with pytest.raises(PreconditionError):
        method.calc(prefs, seats, max_ballot_size=3)


def test_borda_count_allocator_s3_c1_bs3_b_null(rank, counting):
    """Test calc.

    3 seats, 1 candidate, empty ballots, ballot size=3
    """
    prefs = [[0, []]]
    seats = 3
    candidates = ["A"]
    method = BordaCountAllocator(rank, tie_counting=counting)

    result = method.calc(prefs, seats, candidate_list=candidates, max_ballot_size=3)
    assert result.deterministic

    elected = frozenset(x.name for x in result.allocation)
    assert frozenset(candidates) == elected


def test_borda_count_allocator_s0_c1_bs1_b1(rank, counting):
    """Test calc.

    No seats, 1 candidate, 1 ballot, ballot size=1
    """
    prefs = [[3, ["A"]]]
    seats = 0
    candidates = ["A"]
    method = BordaCountAllocator(rank, tie_counting=counting)

    with pytest.raises(PreconditionError):
        method.calc(prefs, seats, max_ballot_size=1)
