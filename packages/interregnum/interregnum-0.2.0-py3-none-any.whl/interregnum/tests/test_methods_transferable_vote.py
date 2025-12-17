# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Tests for Instant Run-Off method."""

from pathlib import Path
import pytest
from .common import iter_problem_filenames

from ..methods.preferential.transferable_vote import InstantRunOffAllocator
from ..methods.types import PreconditionError, Input


PROBLEM_DIR = Path("fixtures") / "transferable_vote"


@pytest.mark.parametrize(
    "problem", list(iter_problem_filenames(PROBLEM_DIR)), ids=lambda x: x.name, indirect=True
)
def test_instant_runoff_allocator(problem):
    """Check problems defined in files."""
    method = InstantRunOffAllocator()
    result = method.calc(problem["votes"], random_seed=1)
    assert result.deterministic == problem["deterministic"]
    expected = {problem["winner"]}
    elected = set()
    for cand in result.allocation:
        assert cand.seats in (0, 1)
        if cand.seats > 0:
            elected.add(cand.name)
    assert expected == elected, (expected, elected)


TIE_BREAKS = ["from_first_vote", "from_last_vote", "random"]


@pytest.fixture(name="tie_break", params=["from_first_vote", "from_last_vote", "random"])
def fixture_tie_break(request):
    """Return tie break strategies."""
    return request.param


@pytest.fixture(name="method")
def fixture_method(tie_break):
    """Return an allocator."""
    return InstantRunOffAllocator(tie_break)


@pytest.fixture(name="input_type")
def fixture_input_type(method: InstantRunOffAllocator):
    """Return admitted inputs."""
    return method.admitted_input


def test_allocator_input_seats(input_type):
    """Seats should not be admitted."""
    assert Input.SEATS not in input_type


def test_allocator_input_random_generator(input_type):
    """Random seed sould be admitted."""
    assert Input.RANDOM_SEED in input_type


def test_allocator_input_candidate_list(input_type):
    """Candidate list should be admitted."""
    assert Input.CANDIDATE_LIST in input_type


def test_allocator_input_preference(input_type):
    """Preferences should be admitted."""
    assert Input.PREFERENCES in input_type


def test_allocator_input_biprop(input_type):
    """Bi-proportional input should not be admitted."""
    assert (Input.PARTY_SEATS not in input_type) and (Input.DISTRICT_SEATS not in input_type)


def test_allocator_c3_b0(method):
    """Test calc.

    3 cands, no ballots.
    """
    prefs = []
    candidates = ["A", "B", "C"]

    res = method.calc(prefs, candidate_list=candidates)
    assert not res.deterministic
    allocated = sum(x.seats for x in res.allocation)
    assert allocated == 1


def test_allocator_c3_b_null(method):
    """Test calc.

    3 cands, empty ballot.
    """
    prefs = [[0, []]]
    candidates = ["A", "B", "C"]

    res = method.calc(prefs, candidate_list=candidates)
    assert not res.deterministic
    allocated = sum(x.seats for x in res.allocation)
    assert allocated == 1


def test_allocator_c0_b_null(method):
    """Test calc.

    No cands, empty ballot.
    """
    prefs = [[0, []]]

    with pytest.raises(PreconditionError):
        method.calc(prefs)


def test_allocator_c1_b1(method):
    """Test calc.

    1 cand, empty ballot.
    """
    prefs = [[0, []]]
    candidates = ["A"]

    result = method.calc(prefs, candidate_list=candidates)
    assert result.deterministic

    elected = frozenset(x.name for x in result.allocation)
    assert frozenset(candidates) == elected
