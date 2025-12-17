# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Tests for Winner-Takes-All method."""

from pathlib import Path
import pytest
from .common import iter_problem_filenames

from ..methods.singlevote.winner_takes_all import WinnerTakesAllAllocator
from ..methods.types import PreconditionError, Input


PROBLEM_DIR = Path("fixtures") / "winner_takes_all"


@pytest.fixture(name="method")
def fixture_method():
    """Return a winner-taks-all method."""
    return WinnerTakesAllAllocator()


@pytest.mark.parametrize(
    "problem", list(iter_problem_filenames(PROBLEM_DIR)), ids=lambda x: x.name, indirect=True
)
def test_instant_runoff_allocator(problem, method):
    """Check results for problems defined in files."""
    result = method.calc(problem["votes"], problem["seats"], random_seed=1)

    assert result.deterministic == problem["deterministic"]

    expected = frozenset(tuple(x) for x in problem["winners"])

    elected = set()
    for cand in result.allocation:
        if cand.seats > 0:
            elected.add((cand.name, cand.seats))

    assert expected == elected, (expected, elected)


@pytest.fixture(name="input_type")
def fixture_input_type(method: WinnerTakesAllAllocator):
    """Return admitted inputs for a method."""
    return method.admitted_input


def test_allocator_input_seats(input_type):
    """Check that the method admits seats."""
    assert Input.SEATS in input_type


def test_allocator_input_random_generator(input_type):
    """Check that the method admits random generators."""
    assert Input.RANDOM_SEED in input_type


def test_allocator_input_candidates(input_type):
    """Check that the method admits candidates."""
    assert Input.CANDIDATES in input_type


def test_allocator_input_preference(input_type):
    """Check that the method does not admit preferences."""
    assert Input.PREFERENCES not in input_type


def test_allocator_input_biprop(input_type):
    """Check that the method doest not admit biproportional input."""
    assert (Input.PARTY_SEATS not in input_type) and (Input.DISTRICT_SEATS not in input_type)


def test_allocator_tie(method):
    """Test calc.

    Winners tie.
    """
    seats = 3
    candidates = [["A", 50], ["B", 50], ["C", 20], ["D", 10]]
    hopeful = frozenset(["A", "B"])
    winners = set()
    for rseed in range(100):
        result = method.calc(candidates, seats, random_seed=rseed)
        assert not result.deterministic
        elected = [x for x in result.allocation if x.seats]
        assert len(elected) == 1
        assert elected[0].seats == seats
        winners.add(elected[0].name)

    assert hopeful.issuperset(winners)


def test_allocator_s3_c0(method):
    """Test calc.

    No candidates.
    """
    seats = 3
    candidates = []

    result = method.calc(candidates, seats)
    assert result.allocation is not None and not result.allocation


def test_allocator_s0_c2(method):
    """Test calc.

    No seats.
    """
    seats = 0
    candidates = [
        ["A", 50],
        ["B", 20],
    ]

    with pytest.raises(PreconditionError):
        method.calc(candidates, seats)
