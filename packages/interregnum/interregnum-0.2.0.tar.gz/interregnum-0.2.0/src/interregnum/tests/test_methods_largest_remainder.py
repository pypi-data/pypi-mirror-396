# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Tests for largest-remainder methods."""

from pathlib import Path
import pytest
from .common import iter_problem_filenames

from ..methods.singlevote.largest_remainder import LargestRemainderAllocator
from ..methods.types import PreconditionError, Input


PROBLEM_DIR = Path("fixtures") / "largest_remainder"


@pytest.mark.parametrize(
    "problem", list(iter_problem_filenames(PROBLEM_DIR)), ids=lambda x: x.name, indirect=True
)
def test_allocator(problem):
    """Check problems defined in files."""
    method = LargestRemainderAllocator(**problem["params"])
    result = method.calc(problem["votes"], problem["seats"], random_seed=1)
    assert result.deterministic == problem["deterministic"]
    expected = frozenset(tuple(x) for x in problem["winners"])

    elected = set()
    for cand in result.allocation:
        if cand.seats > 0:
            elected.add((cand.name, cand.seats))

    assert expected == elected, (expected, elected)


@pytest.fixture(name="quota", params=["hare", "droop"])
def fixture_quota(request):
    """Return a quota."""
    return request.param


@pytest.fixture(name="method")
def fixture_method(quota):
    """Return a method."""
    return LargestRemainderAllocator(quota)


@pytest.fixture(name="input_type")
def fixture_input_type(method: LargestRemainderAllocator):
    """Return admitted inputs."""
    return method.admitted_input


def test_allocator_input_seats(input_type):
    """Seats should be admitted."""
    assert Input.SEATS in input_type


def test_allocator_input_random_generator(input_type):
    """Random seed should be admitted."""
    assert Input.RANDOM_SEED in input_type


def test_allocator_input_candidates(input_type):
    """Candidates should be admitted."""
    assert Input.CANDIDATES in input_type


def test_allocator_input_preference(input_type):
    """Preferences should not be admitted."""
    assert Input.PREFERENCES not in input_type


def test_allocator_input_biprop(input_type):
    """Bi-proportional input should not be admitted."""
    assert (Input.PARTY_SEATS not in input_type) and (Input.DISTRICT_SEATS not in input_type)


def test_tie_non_deterministic(method):
    """Test calc.

    Result with ties is non-deterministic.
    """
    candidates = [["a", 100], ["b", 100], ["c", 100]]
    seats = 4

    for rseed in range(100):
        result = method.calc(candidates, seats, random_seed=rseed)
        assert not result.deterministic
        assert len(result.allocation) == 3
        assert sum(x.seats for x in result.allocation) == seats
        for cand in result.allocation:
            assert 1 <= cand.seats <= 2


def test_allocator_s3_c0(method):
    """Test calc.

    3 seats, no candidates.
    """
    seats = 3
    candidates = []

    result = method.calc(candidates, seats)
    assert result.allocation is not None and not result.allocation


def test_allocator_s0_c2(method):
    """Test calc.

    No seats, 2 candidates.
    """
    seats = 0
    candidates = [
        ["A", 50],
        ["B", 20],
    ]

    with pytest.raises(PreconditionError):
        method.calc(candidates, seats)


def test_single_candidate(method):
    """Test calc.

    3 seats, 1 candidate.
    """
    seats = 3
    candidates = [
        ["A", 100],
    ]

    result = method.calc(candidates, seats)
    assert result.deterministic
    assert len(result.allocation) == 1
    assert sum(x.seats for x in result.allocation) == seats
    assert result.allocation[0].name == "A"


def test_single_candidate_excluded(method):
    """Test calc.

    3 seats, 1 candidate.
    """
    seats = 3
    candidates = [["A", 100], ["B", 100], ["C", 100]]

    result = method.calc(candidates, seats, exclude_candidates=(x[0] for x in candidates[1:]))
    assert result.deterministic
    assert len(result.allocation) == 1
    assert sum(x.seats for x in result.allocation) == seats
    assert result.allocation[0].name == "A"
