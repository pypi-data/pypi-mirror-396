# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Tests for Single Transferable Vote method."""

from pathlib import Path
import pytest
from .common import iter_problem_filenames

from ..methods.types import PreconditionError, Input
from ..methods.preferential.transferable_vote import SingleTransferableVoteAllocator


PROBLEM_DIR = Path("fixtures") / "single_transferable_vote"


@pytest.mark.parametrize(
    "problem", list(iter_problem_filenames(PROBLEM_DIR)), ids=lambda x: x.name, indirect=True
)
def test_single_transferable_vote_allocator(problem):
    """Check problems defined in files."""
    method = SingleTransferableVoteAllocator(**problem["params"])
    result = method.calc(problem["votes"], problem["seats"], random_seed=1)
    assert result.deterministic == problem["deterministic"]
    expected = set(problem["winners"])
    elected = set()
    for cand in result.allocation:
        assert cand.seats in (0, 1)
        if cand.seats > 0:
            elected.add(cand.name)
    assert expected == elected, (expected, elected)


TRANSFERS = ["inclusive_gregory", "weighted_inclusive_gregory", "last_parcel"]
TIE_BREAKS = ["from_first_vote", "from_last_vote", "random"]


@pytest.fixture(
    name="empty_prefs",
    params=[
        [[0, []]],
        [],
    ],
    ids=["null_ballots", "no_ballots"],
)
def fixture_empty_prefs(request):
    """Return a strategy for empty preference ballots."""
    return request.param


@pytest.fixture(name="quota_f", params=["droop", "droop_fractional", "hare"])
def fixture_quota_f(request):
    """Return a quota."""
    return request.param


@pytest.fixture(name="round_f", params=["int", "noop"])
def fixture_round_f(request):
    """Return a rounding function."""
    return request.param


@pytest.fixture(
    name="transfer_f", params=["inclusive_gregory", "weighted_inclusive_gregory", "last_parcel"]
)
def fixture_transfer_f(request):
    """Return a transfer function."""
    return request.param


@pytest.fixture(name="tie_break", params=["from_first_vote", "from_last_vote", "random"])
def fixture_tie_break(request):
    """Return a tie-break strategy."""
    return request.param


@pytest.fixture(name="method")
def fixture_method(quota_f, transfer_f, round_f, tie_break):
    """Return a method."""
    return SingleTransferableVoteAllocator(
        quota_f, transfer_f, round_f=round_f, tie_break=tie_break
    )


@pytest.fixture(name="input_type")
def fixture_input_type(method: SingleTransferableVoteAllocator):
    """Return admitted inputs."""
    return method.admitted_input


def test_allocator_input_seats(input_type):
    """Seats should be admitted."""
    assert Input.SEATS in input_type


def test_allocator_input_random_generator(input_type):
    """Random seed should be admitted."""
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


def test_allocator_s3_c3_b_null(empty_prefs, method):
    """Test calc.

    3 seats, 3 cands, empty ballot.
    """
    seats = 3
    candidates = ["A", "B", "C"]

    result = method.calc(empty_prefs, seats, candidate_list=candidates)
    assert result.deterministic

    elected = frozenset(x.name for x in result.allocation)
    assert frozenset(candidates) == elected


def test_allocator_s3_c0_b_null(empty_prefs, method):
    """Test calc.

    3 seats, no cands, empty ballot.
    """
    seats = 3

    with pytest.raises(PreconditionError):
        method.calc(empty_prefs, seats)


def test_allocator_s3_c1_b_null(empty_prefs, method):
    """Test calc.

    3 seats, 1 cand, empty ballot.
    """
    seats = 3
    candidates = ["A"]

    result = method.calc(empty_prefs, seats, candidate_list=candidates)
    assert result.deterministic

    elected = frozenset(x.name for x in result.allocation)
    assert frozenset(candidates) == elected


def test_allocator_s0_c1(method):
    """Test calc.

    No seats, 1 cand, 1 ballot.
    """
    prefs = [[4, ["A"]]]
    seats = 0
    candidates = ["A"]

    with pytest.raises(PreconditionError):
        method.calc(prefs, seats, candidate_list=candidates)
