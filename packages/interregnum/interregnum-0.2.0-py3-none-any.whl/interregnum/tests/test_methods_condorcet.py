# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Tests for Condorcet methods."""

from pathlib import Path
from functools import partial

import pytest

from ..methods.types import PreconditionError, Input
from ..methods.preferential.condorcet import (
    rankings,
    CondorcetRankedPairsAllocator,
)
from ..methods.preferential import condorcet
from ..methods.preferential.types import Preference
from .common import iter_problem_filenames, read_data

# https://www.starvoting.org/ties
# condorcet.ca

PROBLEM_DIR = Path("fixtures") / "condorcet"


@pytest.fixture(
    name="sample",
    params=list(iter_problem_filenames(PROBLEM_DIR)),
    ids=lambda x: x.name,
    scope="module",
)
def fixture_sample(request):
    """Return a sample."""
    data = read_data(request.param)

    for key, value in data.items():
        if key not in ("name", "votes", "fill", "url", "pairs"):
            data[key] = frozenset(value)
    return data


def minimax_margin(data):
    """Minimax margin function."""
    return rankings.Minimax(data, margin=True)


def minimax_gain(data):
    """Minimax gain function."""
    return rankings.Minimax(data, margin=False)


@pytest.mark.parametrize(
    "system_name,system",
    [
        ("copeland", rankings.Copeland),
        ("minimax_margin", minimax_margin),
        ("minimax_gain", minimax_gain),
    ],
)
def test_condorcet_rankings(system_name, system, sample):
    """Check expected output for a ranking."""
    if len(sample["schwartz"]) == 1:
        expected = sample["schwartz"]
    elif system_name in sample:
        expected = sample[system_name]
    else:
        pytest.skip(f"{system_name} not defined in {sample['name']}")

    score = system(
        Preference.make_input(
            sample["votes"], allow_ties=True, fill_truncated=sample.get("fill", False)
        )
    )
    result = frozenset(cand.name for cand in score.winners())
    assert expected == result


@pytest.mark.parametrize(
    "system_name,system_f",
    [
        ("ranked_pairs", CondorcetRankedPairsAllocator),
    ],
)
def test_ranked_pairs_allocator(system_name, system_f, sample):
    """Check expected values for a condorcet allocator.

    - winners must be in the smith set
    - rounds must be between 1 and the number of seats
    - the expected values (one instance) must be in the generated subset
    """
    if len(sample["schwartz"]) == 1:
        n_seeds = 1
        expected = sample["schwartz"]
    elif system_name in sample:
        expected = sample[system_name]
        n_seeds = 100
    else:
        pytest.skip(f"{system_name} not defined in {sample['name']}")

    system = system_f(fill_truncated=sample.get("fill", False))

    name = sample["name"]

    generated = set()
    seats = len(expected)
    for seed in range(n_seeds):
        result = system(sample["votes"], seats=seats, random_seed=seed)
        assert 1 <= result.data.rounds <= seats
        for cand in result.allocation:
            assert 0 <= cand.seats <= 1
            if cand.seats > 0:
                generated.add(cand.name)
    generated = frozenset(generated)
    assert "smith" in sample, name
    assert generated.issubset(sample["smith"]), (expected, generated, name)
    assert (expected == generated) or generated.issuperset(expected), (expected, generated, name)


@pytest.mark.parametrize(
    "system_name,system_f",
    [
        ("copeland", condorcet.CondorcetCopelandAllocator),
        ("minimax_margin", partial(condorcet.CondorcetMinimaxAllocator, margin=True)),
        ("minimax_gain", partial(condorcet.CondorcetMinimaxAllocator, margin=False)),
    ],
)
def test_condorcet_allocator(system_name, system_f, sample):
    """Check expected values for a condorcet allocator.

    - winners must be in the smith set
    - rounds must be between 1 and the number of seats
    - the expected values (one instance) must be in the generated subset
    """
    if len(sample["schwartz"]) == 1:
        n_seeds = 1
        expected = sample["schwartz"]
    elif system_name in sample:
        expected = sample[system_name]
        n_seeds = 100
    else:
        pytest.skip(f"{system_name} not defined in {sample['name']}")

    system = system_f(fill_truncated=sample.get("fill", False))

    name = sample["name"]

    generated = set()
    seats = len(expected)
    for seed in range(n_seeds):
        result = system(sample["votes"], seats=seats, random_seed=seed)
        assert 1 <= result.data.rounds <= seats
        for cand in result.allocation:
            assert 0 <= cand.seats <= 1
            if cand.seats > 0:
                generated.add(cand.name)
    generated = frozenset(generated)
    assert (expected == generated) or generated.issubset(expected), (expected, generated, name)


@pytest.fixture(
    name="allocator",
    params=[
        CondorcetRankedPairsAllocator,
        condorcet.CondorcetCopelandAllocator,
        partial(condorcet.CondorcetMinimaxAllocator, margin=True),
        partial(condorcet.CondorcetMinimaxAllocator, margin=False),
    ],
    ids=["ranked_pairs", "copeland", "minimax_margin", "minimax_gain"],
)
def fixture_allocator(request):
    """Return a method."""
    return request.param


@pytest.fixture(name="input_type")
def fixture_input_type(allocator):
    """Return admitted inputs."""
    return allocator().admitted_input


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
    assert (Input.DISTRICT_SEATS not in input_type) and (Input.PARTY_SEATS not in input_type)


@pytest.fixture(
    name="fill_truncated", params=[True, False], ids=["fill_truncated", "dont_fill_truncated"]
)
def fixture_fill_truncated(request):
    """Return a truncation strategy."""
    return request.param


@pytest.fixture(
    name="empty_prefs",
    params=[
        [[0, []]],
        [],
    ],
    ids=["null_ballots", "no_ballots"],
)
def fixture_empty_prefs(request):
    """Return empty ballots."""
    return request.param


def test_allocator_s3_c3_b_null(empty_prefs, allocator, fill_truncated):
    """Test calc.

    3 seats, 3 candidates, empty ballots.
    """
    seats = 3
    candidates = ["A", "B", "C"]

    method = allocator(fill_truncated=fill_truncated)
    result = method.calc(empty_prefs, seats, candidate_list=candidates)
    assert result.deterministic

    elected = frozenset(x.name for x in result.allocation)
    assert frozenset(candidates) == elected


def test_allocator_s3_c0_b_null(empty_prefs, allocator, fill_truncated):
    """Test calc.

    3 seats, no candidates, empty ballots.
    """
    seats = 3
    method = allocator(fill_truncated=fill_truncated)

    with pytest.raises(PreconditionError):
        method.calc(empty_prefs, seats)


def test_allocator_s0_c1_b_null(allocator, fill_truncated):
    """Test calc.

    No seats, 1 candidate, empty ballots.
    """
    prefs = [[4, ["A"]]]
    seats = 0
    candidates = ["A"]
    method = allocator(fill_truncated=fill_truncated)

    with pytest.raises(PreconditionError):
        method.calc(prefs, seats, candidate_list=candidates)


def test_ranked_pairs_allocator_multiseat_ties():
    """Test calc.

    Ranked-pairs, multi-seat allocation with ties.
    """
    method = CondorcetRankedPairsAllocator()
    for _ in range(10):
        # ref: O'Neill, Jeffrey (2004). Tie-Breaking with the Single Transferable Vote
        result = method(
            [
                [4, ["A", "B", "C"]],
                [5, ["B", "C"]],
                [5, ["C", "B"]],
                [2, ["D", "A", "B", "C"]],
                [11, ["F"]],
            ],
            seats=2,
        )

        winners = [c.name for c in result.allocation if c.seats]
        assert "D" in winners
        assert "F" in winners
        assert not result.deterministic
