# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Test for Condorcet pair-wise table."""

from pathlib import Path
import pytest

from ..methods.preferential.condorcet.pairwise import PairwiseTable
from ..methods.preferential.types import Preference
from .common import iter_problem_filenames, read_data


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


def _make_pairwise(data):
    votes = data["votes"]
    fill = data.get("fill", False)
    return PairwiseTable.from_preferences(
        Preference.make_input(votes, allow_ties=True, fill_truncated=fill)
    )


def test_pairwise_table(sample):
    """Check results for a pairwise table."""
    if "pairs" not in sample:
        raise pytest.skip(f"pairs not available in {sample['name']}")
    pairs = _make_pairwise(sample)
    for row, col, value in sample["pairs"]:
        assert pairs[row, col] == value, (value, pairs[row, col])


def test_smith_set(sample):
    """Check Smith sets."""
    if "smith" not in sample:
        raise pytest.skip(f"smith not available in {sample['name']}")
    expected = sample["smith"]
    pairs = _make_pairwise(sample)
    result = pairs.smith_set()
    assert result == expected, (expected, result)


def test_schwartz_set(sample):
    """Check Schwartz sets."""
    if "schwartz" not in sample:
        raise pytest.skip(f"schwartz not available in {sample['name']}")
    expected = sample["schwartz"]
    pairs = _make_pairwise(sample)
    result = pairs.schwartz_set()
    assert result == expected, (expected, result)
