# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Tests for bi-proportional method."""

from pathlib import Path
import pytest
from .common import iter_problem_filenames

from ..methods.biproportional import BiproportionalAllocator
from ..methods.types import PreconditionError, Input


PROBLEM_DIR = Path("fixtures") / "biproportional"


@pytest.mark.parametrize(
    "problem", list(iter_problem_filenames(PROBLEM_DIR)), ids=lambda x: x.name, indirect=True
)
def test_biproportional_allocator(problem):
    """Check problems defined in files."""
    method = BiproportionalAllocator(**problem["params"])
    candidates = []
    expected = set()
    for party, district, votes, seats in problem["votes"]:
        candidates.append(((party, district), votes))
        expected.add(((party, district), seats))

    result = method.calc(problem["party_seats"], problem["district_seats"], candidates)

    elected = set()
    for cand in result.allocation:
        elected.add((cand.name, cand.seats))

    assert expected == elected, (expected, elected)


@pytest.fixture(
    name="round_f",
    params=[
        "dhondt",
        "sainte_lague",
    ],
)
def fixture_round_f(request):
    """Return rounding functions."""
    return request.param


@pytest.fixture(name="method")
def fixture_method(round_f):
    """Return a method."""
    return BiproportionalAllocator(round_f)


@pytest.fixture(name="input_type")
def fixture_input_type(method):
    """Return admitted inputs."""
    return method.admitted_input


def test_allocator_input_seats(input_type):
    """Seats should not be admitted."""
    assert Input.SEATS not in input_type


def test_allocator_input_random_generator(input_type):
    """Random seed should not be admitted."""
    assert Input.RANDOM_SEED not in input_type


def test_allocator_input_candidates(input_type):
    """Candidates should be admitted."""
    assert Input.CANDIDATES in input_type


def test_allocator_input_preference(input_type):
    """Preferences should not be admitted."""
    assert Input.PREFERENCES not in input_type


def test_allocator_input_biprop(input_type):
    """Bi-proportional input should be admitted."""
    assert (Input.PARTY_SEATS in input_type) and (Input.DISTRICT_SEATS in input_type)


def test_different_votes(method):
    """Test calc.

    Votes do not match party votes or district votes.
    """
    pvotes = [["A", 4], ["B", 3], ["C", 1]]
    dvotes = [["D1", 3], ["D2", 2], ["D3", 5]]
    candidates = [
        ["A", "D1", 123],
        ["A", "D2", 12],
        ["A", "D3", 28],
        ["B", "D1", 100],
        ["B", "D2", 98],
        ["B", "D3", 45],
        ["C", "D1", 50],
        ["C", "D2", 48],
        ["C", "D3", 25],
    ]

    with pytest.raises(PreconditionError):
        method.calc(pvotes, dvotes, candidates)


def test_different_candidates(method):
    """Test calc.

    Candidates are not present in party votes or district votes.
    """
    pvotes = [["A", 4], ["B", 3], ["C", 1]]
    dvotes = [["D1", 3], ["D2", 2], ["D3", 3]]
    candidates = [
        [("A", "D1"), 123],
        [("A", "D2"), 12],
        [("A", "D3"), 28],
        [("B", "D1"), 100],
        [("B", "D2"), 98],
        [("B", "D3"), 45],
        [("C", "D1"), 50],
        [("C", "D2"), 48],
        [("F", "D3"), 25],
    ]

    with pytest.raises(PreconditionError):
        method.calc(pvotes, dvotes, candidates)
