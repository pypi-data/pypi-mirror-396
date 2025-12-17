# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Test for limited voting."""

from pathlib import Path
import pytest
from .common import iter_problem_filenames

from ..methods.singlevote.limited_voting import LimitedVotingAllocator
from ..methods.types import PreconditionError, Input


PROBLEM_DIR = Path("fixtures") / "limited_voting"


@pytest.fixture(name="method")
def fixture_method():
    """Return an allocator."""
    return LimitedVotingAllocator()


@pytest.mark.parametrize(
    "problem", list(iter_problem_filenames(PROBLEM_DIR)), ids=lambda x: x.name, indirect=True
)
def test_allocator(problem, method):
    """Check problems defined in files."""
    if problem["deterministic"]:
        result = method.calc(problem["votes"], problem["seats"], random_seed=1)
        assert result.deterministic
        expected = frozenset(problem["winners"])
        elected = set()
        for cand in result.allocation:
            if cand.seats > 0:
                assert cand.seats == 1
                elected.add(cand.name)
        assert expected == elected, (expected, elected)
    else:
        expected = frozenset(problem["hopeful"])
        all_elected = set()
        for rseed in range(100):
            result = method.calc(problem["votes"], problem["seats"], random_seed=rseed)
            assert not result.deterministic
            elected = set()
            for cand in result.allocation:
                if cand.seats > 0:
                    assert cand.seats == 1
                    elected.add(cand.name)
            assert len(elected) == problem["seats"]
            all_elected.update(elected)
        assert expected.issuperset(all_elected)


@pytest.fixture(name="input_type")
def fixture_input_type(method: LimitedVotingAllocator):
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
