# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Tests for highest-averages methods."""

from pathlib import Path
import pytest
from .common import iter_problem_filenames

from ..methods.singlevote.highest_averages import HighestAveragesAllocator
from ..methods.types import PreconditionError, Input


PROBLEM_DIR = Path("fixtures") / "highest_averages"


@pytest.mark.parametrize(
    "problem", list(iter_problem_filenames(PROBLEM_DIR)), ids=lambda x: x.name, indirect=True
)
def test_allocator(problem):
    """Check problems defined in files."""
    method = HighestAveragesAllocator(**problem["params"])
    result = method.calc(problem["votes"], problem["seats"], random_seed=1)
    assert result.deterministic == problem["deterministic"]
    expected = frozenset(tuple(x) for x in problem["winners"] if x[-1])

    elected = set()
    for cand in result.allocation:
        if cand.seats > 0:
            elected.add((cand.name, cand.seats))

    assert expected == elected, (expected, elected)


@pytest.fixture(
    name="divisor", params=["dhondt", "sainte_lague", "sainte_lague_1.4", "imperiali", "danish"]
)
def fixture_divisor(request):
    """Return a divisor function."""
    return request.param


@pytest.fixture(name="method")
def fixture_method(divisor):
    """Return a method."""
    return HighestAveragesAllocator(divisor)


@pytest.fixture(name="input_type")
def fixture_input_type(method: HighestAveragesAllocator):
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

    Result with ties.
    """
    candidates = [["a", 5], ["b", 4], ["c", 4], ["d", 1]]
    seats = 2

    o1 = frozenset(["a", "b"])
    o2 = frozenset(["a", "c"])

    for rseed in range(100):
        result = method.calc(candidates, seats, random_seed=rseed)
        assert not result.deterministic
        assert len(result.allocation) == 4
        assert sum(x.seats for x in result.allocation) == seats
        elected = frozenset(x.name for x in result.allocation if x.seats)
        assert (o1 == elected) or (o2 == elected)


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
